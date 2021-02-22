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
import re
from sysdescrparser import sysdescrparser
from typing import Union, List, Any
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


    def use_vlan_community(self, vlan: Union[int, str]) -> Union[str, None]:
        original_community = self.snmp.community
        community = f"{original_community}@{str(vlan)}"
        if self.snmp.check_community(community):
            return original_community
        else:
            raise NettopoSNMPError(f"ERROR: {community} failed {self.ip}")


    def process_table(
        self,
        item: Union[int, str, ObjectIdentity],
        table: List[Any],
        item_type: str='oid',
        return_both: bool=False,
        return_pretty: bool=True,
    ) -> Union[Any, None]:
        results = []
        for row in table:
            for o, v in row:
                oid = str(o) if return_pretty else o
                value = v.prettyPrint() if return_pretty else v
                if item_type == 'oid':
                    # Oid matching is string based
                    item = item if isinstance(item, str) else str(item)
                    # Use regex to ensure we do not match ending digit
                    # like '1' to '10', '100', etc.
                    item_re = re.compile(item + r'(?!\d)')
                    # Match re with oid. Return value.
                    if item_re.match(str(o)):
                        res = (oid, value) if return_both else value
                        results.append(res)
                elif item_type == 'val':
                    # Match item to val using type. Return oid.
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
        if results:
            if len(results) == 1:
                return results[0]
            else:
                return results
        else:
            return None


    def snmp_value(
        self,
        item: Union[int, str, ObjectIdentity],
        vlan: Union[int, str]=None,
        *,
        return_pretty: bool=True,
    ) -> Union[Any, None]:
        results = None
        if vlan:
            old_community = self.use_vlan_community(vlan)
        try:
            value = self.snmp.get_val(item)
        except Exception as e:
            error = e
        finally:
            if vlan:
                self.snmp.community = old_community
            if error:
                return error
            if value:
                return value.prettyPrint() if return_pretty else value


    def snmp_bulk(
        self,
        item: Union[int, str, ObjectIdentity],
        vlan: Union[int, str]=None,
        *,
        item_type: str='oid',
        return_both: bool=False,
        return_pretty: bool=True,
    ) -> Union[Any, None]:
        if vlan:
            old_community = self.use_vlan_community(vlan)
        try:
            table = self.snmp.get_bulk(item)
        except Exception as e:
            error = e
        finally:
            if vlan:
                self.snmp.community = old_community
            if error:
                return error
            if table:
                return self.process_table(
                    item=item,
                    table=table,
                    item_type=item_type,
                    return_both=return_both,
                    return_pretty=return_pretty
                )


    @timethis
    def query_node(self, reset: bool=False) -> None:
        """ Query this node with option to reset
        """
        if self.queried:
            print(f"{self.name} has already been queried.")
            return
        self.queried = True
        self.name = self.get_system_name()
        self.descr = self.snmp_value(o.SYSDESC)
        # Sys info (vendor, model, os, version)
        self.sys = sysdescrparser(self.descr)
        self.ips = self.get_ips()
        # router
        router = self.snmp_value(o.IP_ROUTING)
        self.router = True if router == '1' else False
        if self.router:
            # OSPF
            self.ospf = self.snmp_value(o.OSPF)
            self.ospf_id = self.snmp_value(o.OSPF_ID)
            # BGP
            bgp_las = self.snmp_value(o.BGP_LAS)
            # 4500x reports 0 as disabled
            self.bgp_las = bgp_las if bgp_las != '0' else None
            # HSRP
            self.hsrp_pri = self.snmp_value(o.HSRP_PRI)
            self.hsrp_vip = self.snmp_value(o.HSRP_VIP)
        # stack
        self.stack = self.get_stack()
        # vss
        self.vss = self.get_vss()
        # serial
        if self.vss:
            if self.vss.enabled and self.vss.serial:
                self.serial = self.vss.serial
        elif self.stack:
            if self.stack.enabled and self.stack.serial:
                self.serial = self.stack.serial
        else:
            self.serial = self.snmp_value(o.SYS_SERIAL)
        # SVI
        self.svis = self.get_svis()
        # loopback
        self.loopbacks = self.get_loopbacks()
        # bootfile
        self.bootfile = self.snmp_value(o.SYS_BOOT)
        # Ent chassis info (serial, ios, platform)
        self.ent = self.get_ent()
        # VPC peerlink polulates self.vpc
        self.vpc = self.get_vpc()
        # Populates self.arp_table
        self.arp_table = self.get_arp()
        # Populates self.mac_table
        self.mac_table = self.get_cam()
        # Get the neighbors combining CDP and LLDP
        self.cdp_neighbors = self.get_cdp_neighbors()
        self.lldp_neighbors = self.get_lldp_neighbors()
        neighbors = self.cdp_neighbors
        for nb in self.lldp_neighbors:
            if nb not in neighbors:
                neighbors.append(nb)
        self.neighbors = neighbors


    def get_system_name(self):
        name_raw = self.snmp_value(o.SYSNAME)
        name = name_raw.split('.')
        if len(name) == 3:
            return name[0]
        else:
            return name_raw


    def cidr_from_oid(self, oid: Union[str, int, ObjectIdentity]) -> str:
        ip = ".".join(str(oid).split('.')[-4:])
        if is_ipv4_address(ip):
            mask = self.snmp_value(f"{o.IF_IP_NETM}.{ip}")
            if mask:
                mask = bits_from_mask(mask)
                return f"{ip}/{mask}"
            else:
                return f"{ip}/32"


    def get_ifname(self, idx: int) -> str:
        ifname = self.snmp_value(f"{o.IFNAME}.{idx}")
        if ifname in [o.ERR, o.ERR_INST]:
            ifindex = self.snmp_value(f"{o.IFINDEX}.{idx}")
            ifname = self.snmp_value(f"{o.IFNAME}.{ifindex}")
        return normalize_port(ifname)


    def get_ips(self):
        """ Collects and stores all the IPs for Node
        """
        ips = []
        for entry in self.int_index:
            if entry.cidrs:
                ips.extend([cidr.split('/')[0] for cidr in entry.cidrs])
        ips = set(ips)
        ips = list(ips)
        ips.sort()
        return ips


    def get_ips_from_index(self, num: UIS, ip_only: bool=False) -> ULSIN:
        ips = []
        for entry in self.int_index:
            if int(num) == int(entry.idx):
                if entry.cidrs:
                    if ip_only:
                        cidrs = [cidr.split('/')[0] for cidr in entry.cidrs]
                    else:
                        cidrs = [cidr for cidr in entry.cidrs]
                    ips.extend(cidrs)
        if len(ips) == 1:
            return ips[0]
        else:
            return ips


    def build_ent_from_oid(self, oid):
        idx = oid.split('.')[12]
        serial = self.snmp_bulk(f"{o.ENTPHYENTRY_SERIAL}.{idx}")
        plat = self.snmp_bulk(f"{o.ENTPHYENTRY_PLAT}.{idx}")
        ios = self.snmp_bulk(f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
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
            return EntData(serial, plat, ios)


    # TODO: IOS is incorrect for IOS-XE at least.
    def get_ent(self) -> tuple:
        results = []
        ent_class = self.snmp_bulk(o.ENTPHYENTRY_CLASS, item_type='val')
        chs_oids = self.get_cached_item(
            'ent_class',
            ENTPHYCLASS.CHASSIS,
            item_type='val',
        )
        if isinstance(chs_oids, list):
            for chs_oid in chs_oids:
                ent = self.build_ent_from_oid(chs_oid)
                if ent:
                    results.append(ent)
        else:
            ent = self.build_ent_from_oid(chs_oids)
            if ent:
                results.append(ent)
        return results


    def get_loopbacks(self) -> List[LoopBackData]:
        loopbacks = []
        ethif = self.snmp_bulk(o.ETH_IF)
        with alive_bar(
            len(ethif),
            title=f"Building Loopbacks for {self.name}",
            bar='smooth',
        ) as bar:
            for row in ethif:
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
        with alive_bar(
            len(self.cache.svi),
            title=f"Building SVIs for {self.name}",
            bar='smooth',
        ) as bar:
            for row in self.cache.svi:
                for n, v in row:
                    vlan = str(n).split('.')[14]
                    svi = SVIData(vlan)
                    svi.ips = self.get_ips_from_index(v)
                    svis.append(svi)
                    bar()
        return svis


    def get_vlans(self) -> List[VLANData]:
        vlans = []
        with alive_bar(
            len(self.cache.vlan),
            title=f"Building VLANs for {self.name}",
            bar='smooth',
        ) as bar:
            i = 0
            for row in self.cache.vlan:
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
                        mem.mac = mac_hex_to_ascii(mac)
                    stack.members.append(mem)
        if len(stack.members) > 1:
            stack.enabled = True
            stack.count = len(stack.members)
        return stack if stack.enabled else None


    def get_vss(self) -> VssData:
        vss_mode = self.snmp_value(o.VSS_MODE)
        if vss_mode != '2':
            return None
        vss = VssData()
        vss.enabled = True
        vss.domain = self.snmp_value(o.VSS_DOMAIN)
        chassis = 0
        for row in self.snmp_bulk(o.VSS_MODULES):
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
        if not self.cache.vpc:
            return None
        vpc = VPCData()
        vpc.domain = oid_last_token(self.cache.vpc[0][0][0])
        ifidx = str(self.cache.vpc[0][0][1])
        ifname = self.get_cached_item('ethif', f"{o.ETH_IF_DESC}.{ifidx}")
        vpc.ifname = normalize_port(ifname)
        return vpc


    def get_arp(self) -> List[ARPData]:
        arp_table = []
        with alive_bar(
            len(self.cache.arp),
            title=f"Building ARP table for {self.name}",
            bar='smooth',
        ) as bar:
            for row in self.cache.arp:
                for n, v in row:
                    oid = str(n)
                    if oid.startswith(o.ARP_VLAN):
                        ip = '.'.join(oid.split('.')[-4:])
                        interf = self.get_ifname(v)
                        mac_hex = self.get_cached_item('arp',
                                        f"{o.ARP_MAC}.{v}.{ip}")
                        mac = mac_hex_to_ascii(mac_hex)
                        atype = self.get_cached_item('arp',
                                        f"{o.ARP_TYPE}.{v}.{ip}")
                        arp_type = int(atype)
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
        with alive_bar(
            len(self.cache.vlan),
            title=f"Building MAC table for {self.name}",
            bar='smooth',
        ) as bar:
            # Grab CAM table for each VLAN
            for row in self.cache.vlan:
                for n, v in row:
                    vlan = oid_last_token(n)
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
        # CAM table for this VLAN
        cam_cache = self.cache.vlan_prop(vlan, 'cam')
        if not cam_cache:
            return macs
        portnum_cache = self.cache.vlan_prop(vlan, 'portnums')
        ifindex_cache = self.cache.vlan_prop(vlan, 'ifindex')
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
                    port = self.get_ifname(ifidx)
                except TypeError:
                    port = 'local'
                finally:
                    port = str(port).lower() or 'local'
                mac_addr = mac_hex_to_ascii(cam_v.prettyPrint())
                entry = MACData(vlan, mac_addr, port)
                macs.append(entry)
        return macs


    def get_cdp_neighbors(self) -> List[LinkData]:
        """ Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        """
        # get list of CDP neighbors
        neighbors = []
        if not self.cache.cdp:
            print('No CDP Neighbors Found.')
            return neighbors
        with alive_bar(
            len(self.cache.cdp),
            title=f"Building CDP neighbors for {self.name}",
            bar='smooth',
        ) as bar:
            for row in self.cache.cdp:
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
                        rip = self.get_cached_item(
                                    'cdp',
                                    f"{o.CDP_IPADDR}.{idx}",
                                    return_pretty=False,
                                )
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
        if not self.cache.lldp:
            print('No LLDP Neighbors Found.')
            return neighbors
        with alive_bar(
            len(self.cache.lldp),
            title=f"Building LLDP neighbors for {self.name}",
            bar='smooth',
        ) as bar:
            for row in self.cache.lldp:
                for n, v in row:
                    oid = str(n)
                    if oid.startswith(o.LLDP_TYPE):
                        t = oid.split('.')
                        ifidx = t[-2]
                        ifidx2 = t[-1]
                        idx = ".".join(t[-2:])
                        link = self.get_link(ifidx)
                        link.discovered_proto = 'lldp'
                        link.local_port = self.get_ifname(int(ifidx))
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
                                                     f"{o.LLDP_DEVID}.{idx}")
                        link.remote_mac = mac_hex_to_ascii(devid)
                        rios = self.get_cached_item('lldp',
                                                    f"{o.LLDP_DEVDESC}.{idx}")
                        if rios and rios.startswith('0x'):
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

""" SNMP Queries Saved
ospf = self.snmp_value(o.OSPF)
ospf_id = self.snmp_value(o.OSPF_ID)

ent_class = self.snmp_bulk(o.ENTPHYENTRY_CLASS)
ent_serial = self.snmp_bulk(o.ENTPHYENTRY_SERIAL)
ent_plat = self.snmp_bulk(o.ENTPHYENTRY_PLAT)
ent_ios = self.snmp_bulk(o.ENTPHYENTRY_SOFTWARE)
link_type = self.snmp_bulk(o.TRUNK_VTP)
lag = self.snmp_bulk(o.LAG_LACP)
ifname = self.snmp_bulk(o.IFNAME)
ifip = self.snmp_bulk(o.IF_IP)
ethif = self.snmp_bulk(o.ETH_IF)
trunk_allowed = self.snmp_bulk(o.TRUNK_ALLOW)
trunk_native = self.snmp_bulk(o.TRUNK_NATIVE)
portnums = self.snmp_bulk(o.BRIDGE_PORTNUMS)
ifindex = self.snmp_bulk(o.IFINDEX)
vlan = self.snmp_bulk(o.VLANS)
vlandesc = self.snmp_bulk(o.VLAN_DESC)
svi = self.snmp_bulk(o.SVI_VLANIF)
vpc = self.snmp_bulk(o.VPC_PEERLINK_IF)
stack = self.snmp_bulk(o.STACK)
cdp = self.snmp_bulk(o.CDP)
lldp = self.snmp_bulk(o.LLDP)
route = self.snmp_bulk(o.IP_ROUTE_TABLE)
arp = self.snmp_bulk(o.ARP)
cam = self.snmp_bulk(o.VLAN_CAM)
"""
