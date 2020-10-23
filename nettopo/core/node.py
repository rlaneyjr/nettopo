# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
from alive_progress import alive_bar
import binascii
from collections import namedtuple
from dataclasses import dataclass
from functools import cached_property
from pysnmp.smi.rfc1902 import ObjectIdentity
from sysdescrparser import sysdescrparser
from typing import Union, List, Any
from tqdm import tqdm
# Nettopo Imports
from nettopo.core.cache import Cache
from nettopo.core.constants import ARP, DCODE, ENTPHYCLASS, NODE, NOTHING
from nettopo.core.data import (
    BaseData,
    IntData,
    LinkData,
    VssData,
    VssMemberData,
    StackData,
    StackMemberData,
    EntData,
    VPCData,
    SVIData,
    LoopBackData,
    VLANData,
    ARPData,
    MACData,
)
from nettopo.core.exceptions import NettopoSNMPError, NettopoNodeError
from nettopo.core.snmp import SNMP
from nettopo.core.util import (
    timethis,
    bits_from_mask,
    # normalize_host,
    normalize_port,
    ip_2_str,
    ip_from_cidr,
    format_ios_ver,
    mac_hex_to_ascii,
    mac_format_ascii,
    parse_allowed_vlans,
    lookup_table,
    oid_last_token,
    is_ipv4_address,
    return_pretty_val,
    return_snmptype_val,
)
from nettopo.oids import Oids

# Typing shortcuts
ULSIN = Union[list, str, int, None]
UIS = Union[int, str]

# Easy access to our OIDs
o = Oids()


class Node(BaseData):
    def __init__(self, ip: str, immediate_query: bool=False) -> None:
        self.ip = ip
        self.snmp = SNMP(self.ip)
        self.queried = False
        self.items_2_show = ['name', 'ip', 'plat', 'ios',
                             'serial', 'router', 'vss', 'stack']
        if immediate_query:
            self.query_node()


    def get_snmp_creds(self, snmp_creds):
        """ find valid credentials for this node.
        try each known IP until one works
        """
        orig_snmp_ip = self.snmp.ip
        if self.snmp.success:
            return True
        if self.ip in NOTHING:
            self.snmp.ip = self.get_ips()
        if self.snmp.get_creds(snmp_creds):
            self.ip = self.snmp.ip
            return True
        for ip in self.ips:
            self.snmp.ip = ip
            if self.snmp.get_creds(snmp_creds):
                self.ip = self.snmp.ip
                return True
        if self.snmp.ip != orig_snmp_ip:
            print(f"Reseting SNMP IP {self.snmp.ip} back to {orig_snmp_ip}")
            self.snmp.ip = orig_snmp_ip
        return False


    def reset_cache(self) -> None:
        del self.cache
        self.queried = False


    def build_cache(self) -> None:
        cache = Cache(self.snmp)
        props = [word for word in dir(cache) if not word.startswith('_')]
        with alive_bar(
            len(props),
            title=f"Building Cache for {self.ip}",
            bar='smooth',
        ) as bar:
            for prop in props:
                getattr(cache, prop)
                bar()
        self.cache = cache


    @timethis
    def query_node(self, reset: bool=False) -> None:
        """ Query this node with option to reset

        :param:bool: reset
            Reset the cache on this node prior to query (default=False)
        """
        if reset:
            self.reset_cache()
        if self.queried:
            print(f"{self.name} has already been queried.")
            return
        if not hasattr(self, 'cache'):
            self.build_cache()
        self.queried = True
        self.name_raw = self.cache.name
        self.name = self.get_system_name()
        self.descr = self.cache.descr
        # Sys info (vendor, model, os, version)
        self.sys = sysdescrparser(self.descr)
        self.int_index = self.build_int_index()
        self.ips = self.get_ips()
        # router
        router = self.cache.router
        self.router = True if router == '1' else False
        if self.router:
            # OSPF
            self.ospf_id = self.cache.ospf_id
            # BGP
            bgp_las = self.cache.bgp
            # 4500x reports 0 as disabled
            self.bgp_las = bgp_las if bgp_las != '0' else None
            # HSRP
            self.hsrp_pri = self.cache.hsrp
            self.hsrp_vip = self.cache.hsrp_vip
        # stack
        stack = self.get_stack()
        if stack.enabled:
            self.stack = stack
        # vss
        vss = self.get_vss()
        if vss.enabled:
            self.vss = vss
        # serial
        if hasattr(self, 'vss'):
            if self.vss.enabled and self.vss.serial:
                self.serial = self.vss.serial
        elif hasattr(self, 'stack'):
            if self.stack.enabled and self.stack.serial:
                self.serial = self.stack.serial
        else:
            self.serial = self.cache.serial
        # SVI
        self.svis = self.get_svis()
        # loopback
        self.loopbacks = self.get_loopbacks()
        # bootfile
        self.bootfile = self.cache.bootfile
        # Ent chassis info (serial, ios, platform)
        self.ent = self.get_ent()
        # VPC peerlink polulates self.vpc
        self.vpc = self.get_vpc()
        # Get the neighbors combining CDP and LLDP
        self.neighbors = []
        self.cdp_neighbors = self.get_cdp_neighbors()
        self.lldp_neighbors = self.get_lldp_neighbors()
        self.neighbors.extend(self.cdp_neighbors)
        self.neighbors.extend(self.lldp_neighbors)
        # Populates self.arp_table
        self.arp_table = self.get_arp()
        # Populates self.mac_table
        self.mac_table = self.get_cam()


    def get_cached_item(self,
                    cache_name: str,
                    item: Union[int, str, ObjectIdentity],
                    *,
                    item_type: str='oid',
                    return_both: bool=False,
                    return_pretty: bool=True,
                ) -> Union[Any, None]:
        results = []
        try:
            table = getattr(self.cache, cache_name)
            for row in table:
                for o, v in row:
                    oid = str(o) if return_pretty else o
                    value = return_pretty_val(v) if return_pretty else v
                    if item_type == 'oid':
                        # Match item in start of oid. Return value.
                        if str(o).startswith(item):
                            res = (oid, value) if return_both else value
                            results.append(res)
                    elif item_type == 'val':
                        # Match item to val using the item's type. Return oid.
                        itype = type(item)
                        if item == itype(value):
                            res = (oid, value) if return_both else oid
                            results.append(res)
                    elif item_type == 'idx':
                        # Match item to last token in oid as integers. Return value.
                        idx = oid_last_token(o)
                        if int(item) == int(idx):
                            res = (oid, value) if return_both else value
                            results.append(res)
                    else:
                        raise NettopoNodeError(f"Invalid item_type: {item_type}")
        except Exception:
            pass
        finally:
            # # Always return as list of tuples if returning both
            # if return_both:
            #     return results
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                return results
            else:
                return None


    def cidr_from_oid(self, oid: Union[str, int, ObjectIdentity]) -> str:
        ip = ".".join(str(oid).split('.')[-4:])
        if is_ipv4_address(ip):
            mask = self.get_cached_item('ifip',
                                        f"{o.IF_IP_NETM}.{ip}")
            if mask:
                mask = bits_from_mask(mask)
                return f"{ip}/{mask}"
            else:
                return f"{ip}/32"


    def build_int_index(self) -> List[IntData]:
        int_index = []
        cache = self.cache.ifname
        with alive_bar(
            len(cache),
            title=f"Building Int_Index for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for oid, val in row:
                    port = return_pretty_val(val)
                    # Skip unrouted VLAN ports
                    if port.startswith('VLAN-'):
                        continue
                    idx = oid_last_token(oid)
                    name = normalize_port(port)
                    ip_oids = self.get_cached_item(
                                    'ifip',
                                    str(idx),
                                    item_type='val',
                                )
                    cidrs = []
                    if ip_oids:
                        if isinstance(ip_oids, list):
                            cidr = [self.cidr_from_oid(ip_oid) \
                                    for ip_oid in ip_oids \
                                    if str(ip_oid).startswith(o.IF_IP_ADDR)]
                            cidrs.extend(cidr)
                        else:
                            if str(ip_oids).startswith(o.IF_IP_ADDR):
                                cidr = self.cidr_from_oid(ip_oids)
                                cidrs.append(cidr)
                    int_data = IntData(idx, name, cidrs)
                    int_index.append(int_data)
                    bar()
        return int_index


    def get_ifname(self, idx):
        if idx != o.ERR:
            for entry in self.int_index:
                if int(idx) == int(entry.idx):
                    return entry.name
        return 'Unknown'


    def get_ips_from_index(self, num: int) -> ULSIN:
        ips = []
        for entry in self.int_index:
            if num == entry.idx:
                if entry.cidrs:
                    ips.extend([cidr for cidr in entry.cidrs])
        if len(ips) == 1:
            return ips[0]
        elif len(ips) > 1:
            return ips
        else:
            return None


    def get_system_name(self):
        name = self.name_raw.split('.')[0]
        return name


    def _build_ent_from_oid(self, oid):
        idx = oid.split('.')[12]
        serial = self.get_cached_item('ent_serial',
                                      f"{o.ENTPHYENTRY_SERIAL}.{idx}")
        plat = self.get_cached_item('ent_plat',
                                    f"{o.ENTPHYENTRY_PLAT}.{idx}")
        ios = self.get_cached_item('ent_ios',
                                   f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        # Modular switches have IOS on module
        if not ios:
            mod_oids = self.get_cached_item(
                            'ent_class',
                            ENTPHYCLASS.MODULE,
                            item_type='val'
                        )
            if isinstance(mod_oids, list):
                for mod_oid in mod_oids:
                    idx = mod_oid.split('.')[12]
                    ios = self.get_cached_item('ent_ios',
                                               f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
                    if ios:
                        break
            else:
                idx = mod_oids.split('.')[12]
                ios = self.get_cached_item('ent_ios',
                                           f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        ios = format_ios_ver(ios)
        if any([serial, plat, ios]):
            ent = EntData(serial, plat, ios)
        else:
            ent = None
        return ent


    # TODO: IOS is incorrect for IOS-XE at least.
    def get_ent(self) -> tuple:
        results = []
        cache = self.cache.ent_class
        chs_oids = self.get_cached_item('ent_class', ENTPHYCLASS.CHASSIS, item_type='val')
        if isinstance(chs_oids, list):
            for chs_oid in chs_oids:
                ent = self._build_ent_from_oid(chs_oid)
                if ent:
                    results.append(ent)
        else:
            ent = self._build_ent_from_oid(chs_oids)
            if ent:
                results.append(ent)
        return results


    def get_ips(self):
        """ Collects and stores all the IPs for Node
        Return the lowest numbered IP of all interfaces
        """
        ips = []
        for entry in self.int_index:
            if entry.cidrs:
                ips.extend([cidr for cidr in entry.cidrs])
        ips.sort()
        return ips


    def get_loopbacks(self) -> List[LoopBackData]:
        loopbacks = []
        cache = self.cache.ethif
        with alive_bar(
            len(cache),
            title=f"Building Loopbacks for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for n, v in row:
                    oid = str(n)
                    if oid.startswith(o.ETH_IF_TYPE) and v == 24:
                        ifidx = oid.split('.')[10]
                        lo_name = self.get_cached_item('ethif',
                                        f"{o.ETH_IF_DESC}.{ifidx}")
                        lo_ip = self.get_ips_from_index(ifidx)
                        lo = LoopBackData(lo_name, lo_ip)
                        loopbacks.append(lo)
                    bar()
        return loopbacks


    def get_svis(self) -> List[SVIData]:
        svis = []
        cache = self.cache.svi
        with alive_bar(
            len(cache),
            title=f"Building SVIs for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for n, v in row:
                    vlan = str(n).split('.')[14]
                    svi = SVIData(vlan)
                    svi.ips = self.get_ips_from_index(v)
                    svis.append(svi)
                    bar()
        return svis


    def get_vlans(self) -> List[VLANData]:
        vlans = []
        cache = self.cache.vlan
        with alive_bar(
            len(cache),
            title=f"Building VLANs for {self.name}",
            bar='smooth',
        ) as bar:
            i = 0
            for row in cache:
                for n, v in row:
                    # get VLAN ID from OID
                    vlan = oid_last_token(n)
                    if vlan >= 1002:
                        continue
                    vlans.append(VLANData(
                            vlan,
                            str(self.cache.vlandesc[i][0][1])
                        ))
                    i += 1
                    bar()
        return vlans


    def add_link(self, link):
        if not isinstance(link, LinkData):
            link = LinkData(link)
        if link not in self.links:
            self.links.append(link)


    def get_link(self, ifidx) -> LinkData:
        link = LinkData()
        link.link_type = self.get_cached_item('link_type',
                                          f"{o.TRUNK_VTP}.{ifidx}")
        # trunk
        if link.link_type == '2':
            link.local_native_vlan = self.get_cached_item('trunk_native',
                                                      f"{o.TRUNK_NATIVE}.{ifidx}")
            trunk_allowed = self.get_cached_item('trunk_allowed',
                                             f"{o.TRUNK_ALLOW}.{ifidx}")
            link.local_allowed_vlans = parse_allowed_vlans(trunk_allowed)
        # LAG membership
        lag = self.get_cached_item('lag', f"{o.LAG_LACP}.{ifidx}")
        if lag:
            link.local_lag = self.get_ifname(lag)
            link.local_lag_ips = self.get_ips_from_index(lag)
            link.remote_lag_ips = []
        # VLAN info
        link.vlan = self.get_cached_item('vlan', f"{o.IF_VLAN}.{ifidx}")
        # IP address
        link.local_if_ip = self.get_ips_from_index(ifidx)
        return link


    def get_stack(self)-> StackData:
        stack_roles = ['master', 'member', 'notMember', 'standby']
        stack = StackData()
        for row in self.cache.stack:
            for n, v in row:
                oid = str(n)
                if oid.startswith(f"{o.STACK_NUM}."):
                    idx = oid.split('.')[14]
                    # Get info on this stack member and add to the list
                    mem = StackMemberData()
                    mem.num = v
                    role_num = self.get_cached_item('stack',
                                          f"{o.STACK_ROLE}.{idx}")
                    for role in enumerate(stack_roles, start=1):
                        if role_num == role[0]:
                            mem.role = role[1]
                    if hasattr(mem, 'role'):
                        continue
                    mem.pri = self.get_cached_item('stack',
                                        f"{o.STACK_PRI}.{idx}")
                    mem.img = self.get_cached_item('stack',
                                        f"{o.STACK_IMG}.{idx}")
                    mem.serial = self.get_cached_item('ent_serial',
                                        f"{o.ENTPHYENTRY_SERIAL}.{idx}")
                    mem.plat = self.get_cached_item('ent_plat',
                                        f"{o.ENTPHYENTRY_PLAT}.{idx}")
                    mac = self.get_cached_item('stack', f"{o.STACK_MAC}.{idx}")
                    if mac:
                        mem.mac = mac_format_ascii(mac)
                    stack.members.append(mem)
        if len(stack.members) > 1:
            stack.enabled = True
            stack.count = len(stack.members)
        return stack


    def get_vss(self) -> VssData:
        vss = VssData()
        if self.cache.vss_mode != '2':
            return vss
        vss.enabled = True
        vss.domain = self.cache.vss_domain
        chassis = 0
        for row in self.cache.vss_module:
            for n, v in row:
                if v == 1:
                    modidx = str(n).split('.')[14]
                    # we want only chassis - line card module have no software
                    ios = self.get_cached_item('ent_ios',
                                       f"{o.ENTPHYENTRY_SOFTWARE}.{modidx}")
                    if ios:
                        member = VssMemberData()
                        member.ios = ios
                        member.plat = self.get_cached_item('ent_plat',
                                                   f"{o.ENTPHYENTRY_PLAT}.{modidx}")
                        member.serial = self.get_cached_item('ent_serial',
                                                     f"{o.ENTPHYENTRY_SERIAL}.{modidx}")
                        vss.members.append(member)
                        chassis += 1
            if chassis > 1:
                break
        return vss


    def get_vpc(self):
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        vpc = VPCData()
        if not self.cache.vpc:
            return vpc
        vpc.domain = oid_last_token(self.cache.vpc[0][0][0])
        ifidx = str(self.cache.vpc[0][0][1])
        ifname = self.get_cached_item('ethif', f"{o.ETH_IF_DESC}.{ifidx}")
        vpc.ifname = normalize_port(ifname)
        return vpc


    def get_cdp_neighbors(self) -> List[LinkData]:
        """ Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        """
        # get list of CDP neighbors
        neighbors = []
        cache = self.cache.cdp
        if not cache:
            print('No CDP Neighbors Found.')
            return neighbors
        with alive_bar(
            len(cache),
            title=f"Building CDP neighbors for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for oid, val in row:
                    oid = str(oid)
                    # process only if this row is a CDP_DEVID
                    if oid.startswith(o.CDP_DEVID):
                        t = oid.split('.')
                        ifidx = t[14]
                        ifidx2 = t[15]
                        idx = ".".join([ifidx, ifidx2])
                        link = self.get_link(ifidx)
                        link.discovered_proto = 'cdp'
                        link.remote_name = val.prettyPrint()
                        # get remote IP
                        rip = self.get_cached_item('cdp', f"{o.CDP_IPADDR}.{idx}")
                        link.remote_ip = ip_2_str(rip)
                        # get local port
                        link.local_port = self.get_ifname(ifidx)
                        # get remote port
                        rport = self.get_cached_item(
                                    'cdp',
                                    f"{o.CDP_DEVPORT}.{idx}"
                                )
                        link.remote_port = normalize_port(rport)
                        # get remote platform
                        link.remote_plat = self.get_cached_item(
                                    'cdp',
                                    f"{o.CDP_DEVPLAT}.{idx}"
                                )
                        # get IOS version
                        rios = self.get_cached_item('cdp', f"{o.CDP_IOS}.{idx}")
                        try:
                            rios = binascii.unhexlify(rios[2:])
                        except:
                            pass
                        link.remote_ios = format_ios_ver(rios)
                        neighbors.append(link)
                    bar()
        return neighbors


    def get_lldp_neighbors(self) -> List[LinkData]:
        """ Get a list of LLDP neighbors.
        Returns a list of LinkData's
        Will always return an array.
        """
        neighbors = []
        cache = self.cache.lldp
        if not cache:
            print('No LLDP Neighbors Found.')
            return neighbors
        with alive_bar(
            len(cache),
            title=f"Building LLDP neighbors for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for oid, val in row:
                    oid = str(oid)
                    if oid.startswith(o.LLDP_TYPE):
                        t = oid.split('.')
                        ifidx = t[-2]
                        ifidx2 = t[-1]
                        idx = ".".join(t[-2:])
                        link = self.get_link(ifidx)
                        link.discovered_proto = 'lldp'
                        link.local_port = self.get_ifname(int(ifidx) + 2)
                        rip_oid, _ = self.get_cached_item(
                                        'lldp',
                                        f"{o.LLDP_DEVADDR}.{idx}",
                                        return_both=True
                                    )
                        link.remote_ip = self.cidr_from_oid(rip_oid)
                        rport = self.get_cached_item('lldp',
                                             f"{o.LLDP_DEVPORT}.{idx}")
                        link.remote_port = normalize_port(rport)
                        link.remote_port_desc = self.get_cached_item('lldp',
                                                 f"{o.LLDP_DEVPDSC}.{idx}")
                        devid = self.get_cached_item('lldp',
                                                f"{o.LLDP_DEVID}.{idx}",
                                                return_pretty=False)
                        link.remote_mac = mac_hex_to_ascii(devid)
                        rios = self.get_cached_item('lldp',
                                            f"{o.LLDP_DEVDESC}.{idx}")
                        if rios.startswith('0x'):
                            try:
                                rios = binascii.unhexlify(rios[2:])
                            except:
                                pass
                        link.remote_desc = rios
                        link.remote_ios = format_ios_ver(rios)
                        link.remote_name = self.get_cached_item('lldp',
                                            f"{o.LLDP_DEVNAME}.{idx}")
                        neighbors.append(link)
                    bar()
        return neighbors


    def get_arp(self) -> List[ARPData]:
        arp_table = []
        cache = self.cache.arp
        with alive_bar(
            len(cache),
            title=f"Building ARP table for {self.name}",
            bar='smooth',
        ) as bar:
            for row in cache:
                for n, v in row:
                    oid = str(n)
                    if oid.startswith(o.ARP_VLAN):
                        ip = '.'.join(oid.split('.')[-4:])
                        interf = self.get_ifname(v)
                        mac_hex = lookup_table(self.cache.arp,
                                        f"{o.ARP_MAC}.{v}.{ip}")
                        mac = mac_hex_to_ascii(mac_hex)
                        atype = lookup_table(self.cache.arp,
                                        f"{o.ARP_TYPE}.{v}.{ip}")
                        arp_type = atype if isinstance(atype, int) else int(atype)
                        type_str = 'unknown'
                        if arp_type == ARP.OTHER:
                            type_str = 'other'
                        elif arp_type == ARP.INVALID:
                            type_str = 'invalid'
                        elif arp_type == ARP.DYNAMIC:
                            type_str = 'dynamic'
                        elif arp_type == ARP.STATIC:
                            type_str = 'static'
                        arp_table.append(ARPData(ip, mac, interf, type_str))
                    bar()
        return arp_table


    def get_cam(self) -> List[List[MACData]]:
        ''' MAC address table from this node
        '''
        mac_table = []
        cache = self.cache.vlan
        with alive_bar(
            len(cache),
            title=f"Building MAC table for {self.name}",
            bar='smooth',
        ) as bar:
            # Grab CAM table for each VLAN
            for vlan_row in cache:
                for vlan_n, vlan_v in vlan_row:
                    vlan = oid_last_token(vlan_n)
                    if vlan not in [1002, 1003, 1004, 1005]:
                        vmacs = self.get_macs_for_vlan(vlan)
                        if vmacs:
                            mac_table.extend(vmacs)
                    bar()
        return mac_table


    def get_macs_for_vlan(self, vlan: UIS) -> List[MACData]:
        ''' MAC addresses for a single VLAN
        '''
        macs = []
        old_community = self.snmp.community
        # Change community
        community = f"{old_community}@{str(vlan)}"
        new_snmp = SNMP(self.ip)
        if not new_snmp.check_community(community):
            raise NettopoSNMPError(f"ERROR: {community} failed for {self.ip}")
        new_cache = Cache(new_snmp)
        # CAM table for this VLAN
        cam_cache = new_cache.cam
        if not cam_cache:
            return macs
        portnum_cache = new_cache.portnums
        ifindex_cache = new_cache.ifindex
        for cam_row in cam_cache:
            for cam_n, cam_v in cam_row:
                # find the interface index
                p = cam_n.getOid()
                idx = f"{p[11]}.{p[12]}.{p[13]}.{p[14]}.{p[15]}.{p[16]}"
                bridge_portnum = lookup_table(portnum_cache,
                                                f"{o.BRIDGE_PORTNUMS}.{idx}")
                # get the interface index and description
                try:
                    ifidx = lookup_table(ifindex_cache,
                                            f"{o.IFINDEX}.{bridge_portnum}")
                    port = self.get_cached_item('ifname', f"{o.IFNAME}.{ifidx}")
                except TypeError:
                    port = 'Local'
                finally:
                    port = port or 'Local'
                mac_addr = mac_format_ascii(cam_v)
                entry = MACData(vlan, mac_addr, port)
                macs.append(entry)
        return macs
