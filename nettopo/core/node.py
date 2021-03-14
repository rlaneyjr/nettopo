# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
from alive_progress import alive_bar, config_handler
import binascii
from dataclasses import dataclass
from functools import cached_property
from pysnmp.smi.rfc1902 import ObjectIdentity
import re
from sysdescrparser import sysdescrparser
from typing import Union, List, Any
# Nettopo Imports
from nettopo.core.constants import (
    ARP,
    DCODE,
    ENTPHYCLASS,
    NODE,
    NOTHING,
    int_oper_status,
    int_type,
    int_admin_status,
)
from nettopo.core.data import (
    BaseData,
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
    InterfaceData,
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
    is_ipv4_address,
    return_pretty_val,
    return_snmptype_val,
    bits_2_megabytes,
)
from nettopo.oids import Oids, CiscoOids, GeneralOids

# Typing shortcuts
ULSIN = Union[list, str, int, None]
UIS = Union[int, str]

# Easy access to our OIDs
o = Oids()
g = GeneralOids()
c = CiscoOids()
# Global defaults for alive-progress bar
config_handler.set_global(theme='smooth')


class Node(BaseData):
    def __init__(self, ip: str, immediate_query: bool=False) -> None:
        self.ip = ip
        self.snmp = SNMP(self.ip)
        self.queried = False
        self.items_2_show = ['name', 'ip', 'plat', 'ios',
                             'serial', 'router', 'vss', 'stack']
        self.name = None
        self.descr = None
        self.os = None
        self.model = None
        self.vendor = None
        self.version = None
        self.ips = None
        self.router = None
        self.ospf = None
        self.ospf_id = None
        self.bgp_las = None
        self.hsrp_pri = None
        self.hsrp_vip = None
        self.stack = None
        self.vss = None
        self.serial = None
        self.svis = None
        self.loopbacks = None
        self.bootfile = None
        self.ent = None
        self.vpc = None
        self.interfaces = None
        self.if_table = None
        self.arp_table = None
        self.mac_table = None
        self.cdp_neighbors = None
        self.lldp_neighbors = None
        self.neighbors = None
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


    def snmp_value(
        self,
        item: Union[int, str, ObjectIdentity],
        vlan: Union[int, str]=None,
        return_pretty: bool=True,
    ) -> Union[Any, None]:
        value = None
        error = False
        if vlan:
            old_community = self.use_vlan_community(vlan)
        try:
            value, time_taken = self.snmp.get_val(item)
        except Exception as e:
            error = e
        finally:
            if vlan:
                self.snmp.community = old_community
            if error:
                return error
            if value:
                if return_pretty:
                    return return_pretty_val(value), time_taken
                else:
                    return value, time_taken


    def snmp_bulk(
        self,
        item: Union[int, str, ObjectIdentity],
        vlan: Union[int, str]=None,
    ) -> Union[Any, None]:
        table = None
        error = False
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
                return table


    @timethis
    def query_node(self, reset: bool=False) -> None:
        """ Query this node with option to reset
        """
        if self.queried:
            print(f"{self.name} has already been queried.")
            return
        with alive_progress() as bar:
            self.queried = True
            name_raw, time_taken = self.snmp_value(o.SYSNAME)
            bar(time_taken)
            self.name = self.process_name(name_raw)
            self.descr = self.snmp_value(o.SYSDESC)
            # Sys info (vendor, model, os, version)
            sys = sysdescrparser(self.descr)
            self.os = sys.os
            self.model = sys.model
            self.vendor = sys.vendor
            self.version = sys.version
            self.if_table = self.snmp_bulk(g.ifTable)
            self.ip_table = self.snmp_bulk(g.ipAdEntTable)
            self.interfaces = self.build_interface_table()
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


    def process_name(self, name: str) -> str:
        split_name = name.split('.')
        if len(split_name) == 3:
            return split_name[0]
        else:
            return name


    def get_cidr_from_oid(self, oid: Union[str, int, ObjectIdentity]) -> str:
        ip = ".".join(str(oid).split('.')[-4:])
        if is_ipv4_address(ip):
            mask = self.snmp_value(f"{o.IF_IP_NETM}.{ip}")
            if mask:
                mask = bits_from_mask(mask)
                return f"{ip}/{mask}"
            else:
                return f"{ip}/32"


    def get_ifname_from_index(self, idx: int, normalize: bool=True) -> str:
        # Look in interfaces first if available
        if self.interfaces and idx in self.interfaces._as_dict().keys():
        ifname = self.snmp_value(f"{o.IFNAME}.{idx}")
        if ifname in [o.ERR, o.ERR_INST]:
            ifindex = self.snmp_value(f"{o.IFINDEX}.{idx}")
            ifname = self.snmp_value(f"{o.IFNAME}.{ifindex}")
        if normalize:
            return normalize_port(ifname)
        else:
            return ifname


    def get_cidrs_from_index(self, idx: int) -> Union[list, None]:
        """
        # From IP-MIB
        ipAdEntTable = "1.3.6.1.2.1.4.20.1"
        ipAdEntAddr = "1.3.6.1.2.1.4.20.1.1"
        ipAdEntIfIndex = "1.3.6.1.2.1.4.20.1.2"
        ipAdEntNetMask = "1.3.6.1.2.1.4.20.1.3"
        """
        cidrs = []
        ip_entries = self.ip_table.search(g.ipAdEntIfIndex, item_type='oid')
        for ip_oid, ip_idx in ip_entries:
            if int(ip_idx) == int(idx):
                ip = ".".join(str(ip_oid).split('.')[-4:])
                if is_ipv4_address(ip):
                    mask = self.ip_table.search(
                        f"{g.ipAdEntNetMask}.{ip}",
                        item_type='oid',
                        return_type='val',
                    )
                    if mask:
                        subnet_mask = bits_from_mask(mask[0])
                        cidrs.append(f"{ip}/{subnet_mask}")
                    else:
                        cidrs.append(f"{ip}/32")
        return cidrs


    def build_interface_table(self) -> List[InterfaceData]:
        """
        # From IF-MIB
        ifTable = "1.3.6.1.2.1.2.2"
        ifEntry = "1.3.6.1.2.1.2.2.1"
        ifIndex = "1.3.6.1.2.1.2.2.1.1"
        ifDescr = "1.3.6.1.2.1.2.2.1.2"
        ifType = "1.3.6.1.2.1.2.2.1.3"
        ifMtu = "1.3.6.1.2.1.2.2.1.4"
        ifSpeed = "1.3.6.1.2.1.2.2.1.5"
        ifPhysAddress = "1.3.6.1.2.1.2.2.1.6"
        ifAdminStatus = "1.3.6.1.2.1.2.2.1.7"
        ifOperStatus = "1.3.6.1.2.1.2.2.1.8"
        """
        interface_table = []
        if_entries = self.if_table.search(
            g.ifIndex,
            item_type='oid',
            return_type='val',
        )
        for if_entry in if_entries:
            idx = int(if_entry)
            non_if_name = self.get_ifname_from_index(idx, normalize=False)
            # Skip unrouted VLAN ports and Stack ports
            if not non_if_name.startswith(('VLAN-', 'Stack')):
                if_name = normalize_port(non_if_name)
                if_cidrs = self.get_cidrs_from_index(idx)
                idx_table = self.if_table.index_table(idx)
                for oid, val in idx_table:
                    if oid == g.ifDescr:
                        if_name_long = val
                    if oid == g.ifMtu:
                        if_mtu = int(val)
                    if oid == g.ifType:
                        if_type = int_type.get(int(val))
                    if oid == g.ifSpeed:
                        if_speed = bits_2_megabytes(int(val))
                    if oid == g.ifPhysAddress:
                        if_mac = mac_hex_to_ascii(val)
                    if oid == g.ifAdminStatus:
                        if_admin_status = int_admin_status.get(int(val))
                    if oid == g.ifOperStatus:
                        if_oper_status = int_oper_status.get(int(val))
                entry = InterfaceData(
                    idx=idx,
                    name=if_name,
                    name_long=if_name_long,
                    mtu=if_mtu,
                    media=if_type,
                    speed=if_speed,
                    mac=if_mac,
                    cidrs=if_cidrs,
                    admin_status=if_admin_status,
                    oper_status=if_oper_status,
                )
                interface_table.append(entry)
        return interface_table


    def get_ips(self) -> list:
        """ Collects and stores all the IPs for Node
        """
        _ips = []
        for entry in self.interfaces:
            if entry.cidrs:
                _ips.extend([cidr.split('/')[0] for cidr in entry.cidrs])
        s = set(_ips)
        ips = list(s)
        return ips


    def get_ips_from_index(
        self,
        num: UIS,
        *,
        no_mask: bool=False,
        sort: bool=True,
        return_first: bool=False,
    ) -> ULSIN:
        ips = []
        for entry in self.interfaces:
            if int(num) == int(entry.idx):
                if entry.cidrs:
                    if no_mask:
                        cidrs = [cidr.split('/')[0] for cidr in entry.cidrs]
                    else:
                        cidrs = entry.cidrs
                    ips.extend(cidrs)
        if ips:
            if sort:
                ips.sort()
            if return_first or len(ips) == 1:
                return ips[0]
            else:
                return ips
        else:
            return None


    def get_ent_from_index(self, index: Union[int, str]) -> dict:
        idx = int(index)
        serial = self.snmp_value(f"{o.ENTPHYENTRY_SERIAL}.{idx}")
        plat = self.snmp_value(f"{o.ENTPHYENTRY_PLAT}.{idx}")
        ios = self.snmp_value(f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        return serial, plat, ios


    def build_ent_from_oid(self, oid, ent_table) -> EntData:
        idx = oid.split('.')[12]
        serial, plat, ios = self.get_ent_from_index(idx)
        # Modular switches have IOS on module
        if not ios:
            mod_oids = ent_table.search(
                ENTPHYCLASS.MODULE,
                item_type='val',
                return_type='oid',
            )
            if mod_oids:
                for mod_oid in mod_oids:
                    idx = mod_oid.split('.')[12]
                    ios = self.snmp_value(f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
                    if ios:
                        break
        ios = format_ios_ver(ios)
        if all([serial, plat, ios]):
            return EntData(serial, plat, ios)


    # TODO: IOS is incorrect for IOS-XE at least.
    def get_ent(self) -> list:
        results = []
        ent_table = self.snmp_bulk(o.ENTPHYENTRY_CLASS)
        chs_oids = ent_table.search(
            ENTPHYCLASS.CHASSIS,
            item_type='val',
            return_type='oid',
        )
        if chs_oids:
            for chs_oid in chs_oids:
                ent = self.build_ent_from_oid(chs_oid, ent_table)
                results.append(ent)
        return results


    def get_loopbacks(self) -> List[InterfaceData]:
        return [entry for entry in self.interfaces \
                if entry.media == 'softwareLoopback']


    def get_svis(self) -> List[SVIData]:
        svis = []
        svi_table = self.snmp_bulk(o.SVI_VLANIF)
        for n, v in svi_table.table:
            vlan = n.split('.')[14]
            svi = SVIData(vlan)
            svi.ips = self.get_ips_from_index(v)
            svis.append(svi)
        return svis


    def get_vlans(self) -> List[VLANData]:
        vlans = []
        vlan_table = self.snmp_bulk(o.VLANS_NEW)
        for oid, vlandesc in vlan_table.table:
            # get VLAN ID from OID
            vlan = int(oid.split('.')[-1:][0])
            if vlan >= 1002:
                continue
            vlans.append(VLANData(vlan, vlandesc))
        return vlans


    def add_link(self, link):
        if not isinstance(link, LinkData):
            link = LinkData(link)
        if link not in self.links:
            self.links.append(link)


    def get_link(self, ifidx) -> LinkData:
        link = LinkData()
        link.link_type = self.snmp_value(f"{o.TRUNK_VTP}.{ifidx}")
        # trunk
        if link.link_type == '2':
            link.local_native_vlan = self.snmp_value(f"{o.TRUNK_NATIVE}.{ifidx}")
            trunk_allowed = self.snmp_value(f"{o.TRUNK_ALLOW}.{ifidx}")
            link.local_allowed_vlans = parse_allowed_vlans(trunk_allowed)
        # LAG membership
        lag = self.snmp_value(f"{o.LAG_LACP}.{ifidx}")
        if lag:
            link.local_lag = self.get_ifname_from_index(lag)
            link.local_lag_ips = self.get_ips_from_index(lag)
            link.remote_lag_ips = []
        # VLAN info
        link.vlan = self.snmp_value(f"{o.IF_VLAN}.{ifidx}")
        # IP address
        link.local_if_ip = self.get_ips_from_index(ifidx)
        return link


    def get_stack(self)-> StackData:
        stack_roles = ['master', 'member', 'notMember', 'standby']
        stack = StackData()
        stack_table = self.snmp_bulk(o.STACK)
        for _oid, _val in stack_table.table:
            oid = str(_oid)
            if oid.startswith(f"{o.STACK_NUM}."):
                idx = oid.split('.')[14]
                # Get info on this stack member and add to the list
                mem = StackMemberData()
                mem.num = int(_val)
                role_num = stack_table.search(
                    f"{o.STACK_ROLE}.{idx}",
                    item_type='oid',
                    return_type='val',
                )
                for role in enumerate(stack_roles, start=1):
                    if role_num == role[0]:
                        mem.role = role[1]
                if hasattr(mem, 'role'):
                    continue
                mem.pri = stack_table.search(
                    f"{o.STACK_PRI}.{idx}",
                    return_type='val',
                )
                mem.img = stack_table.search(
                    f"{o.STACK_IMG}.{idx}",
                    return_type='val',
                )
                mem.serial, mem.plat, mem.ios = self.get_ent_from_index(idx)
                mac = stack_table.search(
                    f"{o.STACK_MAC}.{idx}",
                    return_type='val',
                )
                if mac:
                    mem.mac = mac_hex_to_ascii(mac)
                stack.members.append(mem)
        if len(stack.members) > 1:
            stack.enabled = True
            stack.count = len(stack.members)
            return stack


    def get_vss(self) -> VssData:
        vss_table = self.snmp_bulk(o.VSS)
        if not vss_table:
            return
        vss_mode = vss_table.search(o.VSS_MODE, return_type='val')
        if vss_mode == '2':
            vss = VssData()
            vss.enabled = True
            vss.domain = vss_table.search(o.VSS_DOMAIN, return_type='val')
            chassis = 0
            vss_mod_table = self.snmp_bulk(o.VSS_MODULES)
            vss_mods = vss_mod_table.search(1, item_type='val')
            if vss_mods:
                for _oid, _val in vss_mods:
                    modidx = _oid.split('.')[14]
                    # we want only chassis - line card module have no software
                    serial, plat, ios = self.get_ent_from_index(modidx)
                    if ios:
                        member = VssMemberData()
                        member.ios = ios
                        member.plat = plat
                        member.serial = serial
                        vss.members.append(member)
                        chassis += 1
                    if chassis > 1:
                        break
            return vss


    def get_vpc(self) -> VPCData:
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        vpc_table = self.snmp_bulk(o.VPC_PEERLINK_IF)
        if not vpc_table:
            return
        for _oid, _val in vpc_table.table:
            vpc = VPCData()
            vpc.domain = _oid.split('.')[-1:][0]
            ifidx = str(_val)
            ifname = self.get_ifname_from_index(ifidx)
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
                        interf = self.get_ifname_from_index(v)
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
                    port = self.get_ifname_from_index(ifidx)
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
                        link.local_port = self.get_ifname_from_index(ifidx)
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
        lldp = self.snmp_bulk(o.LLDP)
        if not lldp:
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
                        link.local_port = self.get_ifname_from_index(int(ifidx))
                        rip_oid, _ = self.get_cached_item(
                            'lldp',
                            f"{o.LLDP_DEVADDR}.{idx}",
                            return_both=True
                        )
                        link.remote_ip = self.get_cidr_from_oid(rip_oid)
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

bulk_shit = {
    'ent_class': o.ENTPHYENTRY_CLASS,
    'ent_serial': o.ENTPHYENTRY_SERIAL,
    'ent_plat': o.ENTPHYENTRY_PLAT,
    'ent_ios': o.ENTPHYENTRY_SOFTWARE,
    'link_type': o.TRUNK_VTP,
    'lag': o.LAG_LACP,
    'ifname': o.IFNAME,
    'ifip': o.IF_IP,
    'ethif': o.ETH_IF,
    'trunk_allowed': o.TRUNK_ALLOW,
    'trunk_native': o.TRUNK_NATIVE,
    'portnums': o.BRIDGE_PORTNUMS,
    'ifindex': o.IFINDEX,
    'vlan': o.VLANS,
    'vlandesc': o.VLAN_DESC,
    'svi': o.SVI_VLANIF,
    'vpc': o.VPC_PEERLINK_IF,
    'stack': o.STACK,
    'cdp': o.CDP,
    'lldp': o.LLDP,
    'route': o.IP_ROUTE_TABLE,
    'arp': o.ARP,
    'cam': o.VLAN_CAM,
}
"""
