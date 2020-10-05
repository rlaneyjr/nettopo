# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
import binascii
from dataclasses import dataclass
from functools import cached_property
from typing import Union, List, Any
# Nettopo Imports
from nettopo.core.cache import Cache
from nettopo.core.constants import ARP, DCODE, NODE, NOTHING
from nettopo.core.data import (
    BaseData,
    LinkData,
    VssData,
    VssMemberData,
    StackData,
    StackMemberData,
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
    normalize_host,
    normalize_port,
    ip_2_str,
    ip_from_cidr,
    format_ios_ver,
    mac_hex_to_ascii,
    mac_format_cisco,
    parse_allowed_vlans,
    lookup_table,
    oid_last_token
)
from nettopo.oids import Oids
from typing import Union, List, Any

# Typing shortcuts
LSIN = Union[list, str, int, None]
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
        # Call all the cached properties that query SNMP here:
        for prop in dir(cache):
            if not prop.startswith('_'):
                getattr(cache, prop)
        self.cache = cache


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
        self.stack = self.get_stack()
        # vss
        self.vss = self.get_vss()
        # serial
        if self.vss.enabled:
            self.serial = self.vss.serial
        elif self.stack.enabled:
            self.serial = self.stack.serial
        else:
            self.serial = self.cache.serial
        # SVI
        self.svis = self.get_svis()
        # loopback
        self.loopbacks = self.get_loopbacks()
        # bootfile
        self.bootfile = self.cache.bootfile
        # chassis info (serial, IOS, platform)
        serial, plat, ios = self.get_chassis()
        if serial and not self.serial:
            self.serial = serial
        if plat:
            self.plat = plat
        if ios:
            self.ios = ios
        # VPC peerlink polulates self.vpc
        self.vpc = self.get_vpc()
        # Get the neighbors combining CDP and LLDP
        # Populates self.neighbors (CDP and LLDP combined) along with
        # self.cdp_neighbors and self.lldp_neighbors
        self.neighbors = self.get_neighbors()
        # Populates self.arp_table
        self.arp_table = self.get_arp()
        # Populates self.mac_table
        self.mac_table = self.get_cam()


    def cached_item(self, cache_name: str, item: str) -> Union[Any, None]:
        try:
            table = self.cache[cache_name]
            for row in table:
                for n, v in row:
                    if item in str(n):
                        return v.prettyPrint()
        except Exception:
            return None


    def get_ifname(self, ifidx=None):
        if not ifidx or ifidx == o.ERR:
            return 'Unknown'
        res = self.cached_item('ifname', f"{o.IFNAME}.{ifidx}")
        return normalize_port(res) or 'Unknown'


    def get_ips_from_index(self, idx) -> LSIN:
        ips = []
        for row in self.cache.ifip:
            for n, v in row:
                n = str(n)
                if n.startswith(o.IF_IP_ADDR):
                    if str(v) == str(idx):
                        t = n.split('.')
                        ip = ".".join(t[10:])
                        mask = self.cached_item('ifip',
                                            f"{o.IF_IP_NETM}{ip}")
                        mask = bits_from_mask(mask)
                        cidr = f"{ip}/{mask}"
                        ips.append(cidr)
        if len(ips) == 1:
            return ips[0]
        else:
            return ips


    def get_stack(self)-> StackData:
        stack_roles = ['master', 'member', 'notMember', 'standby']
        stack = StackData()
        for row in self.cache.stack:
            for k, v in row:
                k = str(k)
                if k.startswith(f"{o.STACK_NUM}."):
                    idx = k.split('.')[14]
                    # Get info on this stack member and add to the list
                    mem = StackMemberData()
                    mem.num = v
                    role_num = self.cached_item('stack',
                                          f"{o.STACK_ROLE}.{idx}")
                    for role in enumerate(stack_roles, start=1):
                        if role_num == role[0]:
                            mem.role = role[1]
                    mem.pri = self.cached_item('stack',
                                         f"{o.STACK_PRI}.{idx}")
                    mem.img = self.cached_item('stack',
                                         f"{o.STACK_IMG}.{idx}")
                    if self.cache.ent_serial:
                        mem.serial = self.cached_item('ent_serial',
                                            f"{o.ENTPHYENTRY_SERIAL}.{idx}")
                    if self.cache.ent_plat:
                        mem.plat = self.cached_item('ent_plat',
                                              f"{o.ENTPHYENTRY_PLAT}.{idx}")
                    mem.mac = self.cached_item('stack',
                                         f"{o.STACK_MAC}.{idx}")
                    mac_seg = [mem.mac[x:x+4] for x in range(2, len(mem.mac), 4)]
                    mem.mac = '.'.join(mac_seg)
                    if mem.role:
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
                    ios = self.cached_item('ent_ios',
                                       f"{o.ENTPHYENTRY_SOFTWARE}.{modidx}")
                    if ios:
                        member = VssMemberData()
                        member.ios = ios
                        member.plat = self.cached_item('ent_plat',
                                                   f"{o.ENTPHYENTRY_PLAT}.{modidx}")
                        member.serial = self.cached_item('ent_serial',
                                                     f"{o.ENTPHYENTRY_SERIAL}.{modidx}")
                        vss.members.append(member)
                        chassis += 1
            if chassis > 1:
                break
        return vss


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
        for row in self.cache.cdp:
            for oid, val in row:
                oid = str(oid)
                # process only if this row is a CDP_DEVID
                if oid.startswith(o.CDP_DEVID):
                    continue
                t = oid.split('.')
                ifidx = t[14]
                ifidx2 = t[15]
                idx = ".".join(ifidx, ifidx2)
                # get remote IP
                rip = self.cached_item('cdp', f"{o.CDP_IPADDR}.{idx}")
                remote_ip = ip_2_str(rip)
                # get local port
                local_port = self.get_ifname(ifidx)
                # get remote port
                rport = self.cached_item('cdp', f"{o.CDP_DEVPORT}.{idx}")
                remote_port = normalize_port(rport)
                # get remote platform
                remote_plat = self.cached_item('cdp', f"{o.CDP_DEVPLAT}.{idx}")
                # get IOS version
                rios = self.cached_item('cdp', f"{o.CDP_IOS}.{idx}")
                if rios:
                    try:
                        rios = binascii.unhexlify(rios[2:])
                    except:
                        pass
                    remote_ios = format_ios_ver(rios)
                link = self.get_link(ifidx)
                link.remote_name = val.prettyPrint()
                link.remote_ip = remote_ip
                link.discovered_proto = 'cdp'
                link.local_port = local_port
                link.remote_port = remote_port
                link.remote_plat = remote_plat
                link.remote_ios = remote_ios
                neighbors.append(link)
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
        for row in self.cache.lldp:
            for oid, val in row:
                oid = str(oid)
                if not oid.startswith(o.LLDP_TYPE):
                    continue
                t = oid.split('.')
                ifidx = t[12]
                ifidx2 = t[13]
                idx = ".".join(ifidx, ifidx2)
                local_port = self.get_ifname(ifidx)
                if oid.startswith(f"{o.LLDP_DEVADDR}.{idx}"):
                    remote_ip = '.'.join(t[16:])
                rport = self.cached_item('lldp',
                                     f"{o.LLDP_DEVPORT}.{idx}")
                remote_port = normalize_port(rport)
                devid = self.cached_item('lldp',
                                     f"{o.LLDP_DEVID}.{idx}")
                try:
                    remote_mac = mac_format_cisco(devid)
                except:
                    pass
                rios = self.cached_item('lldp',
                                    f"{o.LLDP_DEVDESC}.{idx}")
                if rios:
                    try:
                        rios = binascii.unhexlify(rios[2:])
                    except:
                        pass
                    remote_ios = format_ios_ver(rios)
                remote_name = self.cached_item('lldp',
                                    f"{o.LLDP_DEVNAME}.{idx}")
                link = self.get_link(ifidx)
                link.discovered_proto = 'lldp'
                link.remote_ip = remote_ip if remote_ip else ''
                link.remote_name = remote_name if remote_name else devid
                link.local_port = local_port
                link.remote_port = remote_port
                link.remote_plat = None
                link.remote_ios = remote_ios
                link.remote_mac = remote_mac if remote_mac else devid
                neighbors.append(link)
        return neighbors


    def get_neighbors(self, reset: bool=False) -> list:
        if hasattr(self, 'neighbors'):
            if not reset:
                return self.neighbors
            else:
                del self.neighbors
        neighbors = []
        neighbors.extend(self.get_cdp_neighbors())
        neighbors.extend(self.get_lldp_neighbors())
        self.neighbors = neighbors


    def add_link(self, link):
        if not isinstance(link, LinkData):
            link = LinkData(link)
        if link not in self.links:
            self.links.append(link)


    def get_link(self, ifidx) -> LinkData:
        link = LinkData()
        link.link_type = self.cached_item('link_type',
                                      f"{o.TRUNK_VTP}.{ifidx}")
        # trunk
        if link.link_type == '1':
            native_vlan = self.cached_item('trunk_native',
                                       f"{o.TRUNK_NATIVE}.{ifidx}")
            trunk_allowed = self.cached_item('trunk_allowed',
                                         f"{o.TRUNK_ALLOW}.{ifidx}")
            allowed_vlans = parse_allowed_vlans(trunk_allowed)
            link.local_native_vlan = native_vlan or None
            link.local_allowed_vlans = allowed_vlans or 'All'
        # LAG membership
        lag = self.cached_item('lag', f"{o.LAG_LACP}.{ifidx}")
        if lag:
            link.local_lag = self.get_ifname(lag)
            link.local_lag_ips = self.get_ips_from_index(lag)
            link.remote_lag_ips = []
        # VLAN info
        vlan = self.cached_item('vlan', f"{o.IF_VLAN}.{ifidx}")
        link.vlan = vlan or None
        # IP address
        local_if_ips = self.get_ips_from_index(ifidx)
        link.local_if_ip = local_if_ips or None
        return link


    def get_chassis(self) -> tuple:
        for row in self.cache.ent_class:
            for n, v in row:
                n = str(n)
                if v != 'ENTPHYCLASS_CHASSIS':
                    continue
                t = n.split('.')
                idx = t[12]
                serial = self.cached_item('ent_serial',
                                    f"{o.ENTPHYENTRY_SERIAL}.{idx}")
                plat = self.cached_item('ent_plat',
                                    f"{o.ENTPHYENTRY_PLAT}.{idx}")
                ios = self.cached_item('ent_ios',
                                    f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
                # Modular switches have IOS on module
                if not ios:
                    for row in self.cache.ent_class:
                        for n, v in row:
                            n = str(n)
                            if v != 'ENTPHYCLASS_MODULE':
                                continue
                            t = n.split('.')
                            idx = t[12]
                            ios = self.cached_item('ent_ios',
                                        f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
                            if ios:
                                break
                ios = format_ios_ver(ios)
        return (serial, plat, ios)


    def get_system_name(self, domains=None):
        if not self.queried:
            self.query_node()
        return normalize_host(self.name_raw, domains)


    def get_ips(self):
        """ Collects and stores all the IPs for Node
        Return the lowest numbered IP of all interfaces
        """
        self.ips = list(self.ip)
        if not self.queried:
            self.query_node()
        # Loopbacks
        if self.loopbacks:
            for lb in self.loopbacks:
                if lb.ip:
                    lb_ip = ip_from_cidr(lb.ip)
                    self.ips.append(lb_ip)
        # SVIs
        if self.svis:
            for svi in self.svis:
                if svi.ips:
                    svi_ips = [ip_from_cidr(ip) for ip in svi.ips]
                    self.ips.extend(svi_ips)
        self.ips.sort()
        return ip_from_cidr(self.ips[0])


    def get_vpc(self):
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        if not self.queried:
            self.query_node()
        if not self.cache.vpc:
            self.vpc.domain = None, None
        domain = oid_last_token(self.cache.vpc[0][0][0])
        ifidx = str(self.cache.vpc[0][0][1])
        ifname = self.cached_item('ethif', f"{o.ETH_IF_DESC}.{ifidx}")
        ifname = normalize_port(ifname)
        return domain, ifname


    def get_loopbacks(self) -> List[LoopBackData]:
        if not self.queried:
            self.query_node()
        loopbacks = []
        for row in self.cache.ethif:
            for k, v in row:
                k = str(k)
                if k.startswith(o.ETH_IF_TYPE) and v == 24:
                    ifidx = k.split('.')[10]
                    lo_name = self.cached_item('ethif',
                                           f"{o.ETH_IF_DESC}.{ifidx}")
                    lo_ip = self.get_ips_from_index(ifidx)
                    lo = LoopBackData(lo_name, lo_ip)
                    loopbacks.append(lo)
        return loopbacks


    def get_svis(self) -> List[SVIData]:
        if not self.queried:
            self.query_node()
        svis = []
        for row in self.cache.svi:
            for k, v in row:
                vlan = str(k).split('.')[14]
                svi = SVIData(vlan)
                svi.ips = self.get_ips_from_index(v)
                svis.append(svi)
        return svis


    def get_vlans(self) -> List[VLANData]:
        if not self.queried:
            self.query_node()
        vlans = []
        i = 0
        for vlan_row in self.cache.vlan:
            for vlan_n, vlan_v in vlan_row:
                # get VLAN ID from OID
                vlan = oid_last_token(vlan_n)
                if vlan >= 1002:
                    continue
                vlans.append(VLANData(vlan, str(self.cache.vlandesc[i][0][1])))
                i += 1
        return vlans


    def get_arp(self) -> List[ARPData]:
        if not self.queried:
            self.query_node()
        arp_table = []
        for r in self.cache.arp:
            for n, v in r:
                n = str(n)
                if n.startswith(o.ARP_VLAN):
                    tok = n.split('.')
                    ip = '.'.join(tok[11:])
                    interf = self.get_ifname(str(v))
                    mach = self.cached_item('arp',
                                            f"{o.ARP_MAC}.{str(v)}.{ip}")
                    mac = mac_hex_to_ascii(mach, True)
                    atype = self.cached_item('arp',
                                            f"{o.ARP_TYPE}.{str(v)}.{ip}")
                    atype = int(atype)
                    type_str = 'unknown'
                    if atype == ARP.OTHER:
                        type_str = 'other'
                    elif atype == ARP.INVALID:
                        type_str = 'invalid'
                    elif atype == ARP.DYNAMIC:
                        type_str = 'dynamic'
                    elif atype == ARP.STATIC:
                        type_str = 'static'
                    arp_table.append(ARPData(ip, mac, interf, type_str))
        return arp_table


    def get_cam(self) -> List[List[MACData]]:
        ''' MAC address table from this node
        '''
        if not self.queried:
            self.query_node()
        mac_table = []
        for vlan_row in self.cache.vlan:
            for vlan_n, vlan_v in vlan_row:
                vlan = oid_last_token(vlan_n)
                if vlan not in [1002, 1003, 1004, 1005]:
                    vmacs = self.get_macs_for_vlan(ip, vlan)
                    if vmacs:
                        mac_table.extend(vmacs)
        return mac_table


    def get_macs_for_vlan(self, ip: str, vlan: UIS) -> List[MACData]:
        ''' MAC addresses for a single VLAN
        '''
        macs = []
        # change our SNMP credentials
        old_cred = self.cache.snmp.community
        self.cache.snmp.community = f"{old_cred}@{str(vlan)}"
        # get CAM table for this VLAN
        cam_cache = self.cache.cam
        if not cam_cache:
            # error getting CAM for VLAN
            raise NettopoNodeError(f"ERROR: No CAM for {vlan} with {ip}")
            # return
        for cam_row in cam_cache:
            for cam_n, cam_v in cam_row:
                cam_entry = mac_format_ascii(cam_v, False)
                # find the interface index
                p = cam_n.getOid()
                idx = f"{p[11]}.{p[12]}.{p[13]}.{p[14]}.{p[15]}.{p[16]}"
                bridge_portnum = self.cached_item('portnum',
                                                f"{o.BRIDGE_PORTNUMS}.{idx}")
                # get the interface index and description
                try:
                    ifidx = self.cached_item('ifindex',
                                            f"{o.IFINDEX}.{bridge_portnum}")
                    port = self.cached_item('ifname', f"{o.IFNAME}.{ifidx}")
                except TypeError:
                    port = 'None'
                mac_addr = mac_format_ascii(cam_v, True)
                entry = MACData(system_name, ip, vlan, mac_addr, port)
                macs.append(entry)
        # restore SNMP credentials
        self.cache.snmp.community = old_cred
        return macs
