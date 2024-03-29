# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
from about_time import about_time
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
    DCODE,
    NODE,
    NOTHING,
    RESERVED_VLANS,
    retcode_type_map,
    node_type_map,
    mac_type_map,
    bridge_status_map,
    stp_state_map,
    entphyclass_type_map,
    int_oper_status_map,
    int_type_map,
    int_admin_status_map,
)
from nettopo.core.data import (
    BaseData,
    DataTable,
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
    normalize_host,
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
    get_oid_index,
    oid_endswith,
)
from nettopo.oids import Oids, CiscoOids, GeneralOids

# Typing shortcuts
_ULSIN = Union[list, str, int, None]
_UIS = Union[int, str]
_USN = Union[str, None]
_UISO = Union[int, str, ObjectIdentity]
_UAN = Union[Any, None]
_ULN = Union[list, None]
_UEN = Union[EntData, None]

# Easy access to our OIDs
o = Oids()
g = GeneralOids()
c = CiscoOids()
# Global defaults for alive-progress bar
config_handler.set_global(theme='smooth')


class Node(BaseData):
    def __init__(self, ip: str, immediate_query: bool=False, **kwargs) -> None:
        self.ip = ip
        self.snmp = SNMP(self.ip, **kwargs)
        self.queried = False
        self.show_items = ['name', 'ip', 'plat', 'ios', 'serial',
                           'router', 'vss', 'stack']
        self.name = None
        self.descr = None
        self.os = None
        self.model = None
        self.vendor = None
        self.version = None
        self.ips = None
        self.router = False
        self.ospf = None
        self.ospf_id = None
        self.bgp_las = None
        self.hsrp_pri = None
        self.hsrp_vip = None
        self.stack = None
        self.vss = None
        self.serial = None
        self.svis = None
        self.vlans = None
        self.loopbacks = None
        self.bootfile = None
        self.ent = None
        self.vpc = None
        self.interfaces = None
        self.if_table = None
        self.ip_table = None
        self.arp_table = None
        self.mac_table = None
        self.cdp = None
        self.lldp = None
        self.links = []
        if immediate_query:
            self.query_node()

    @staticmethod
    def _has_value(thing: Any) -> bool:
        if not hasattr(thing, 'value'):
            return False
        elif thing.value in [o.ERR, o.ERR_INST, '0', '']:
            return False
        else:
            return True

    @staticmethod
    def _link_ios(ios, link: LinkData) -> LinkData:
        if ios.startswith('0x'):
            try:
                ios = binascii.unhexlify(ios[2:])
            except:
                pass
        if isinstance(ios, bytes):
            ios = ios.decode('utf-8')
        link.remote_desc = ios
        try:
            sys = sysdescrparser(ios)
            link.remote_os = sys.os
            link.remote_model = sys.model
            link.remote_vendor = sys.vendor
            link.remote_version = sys.version
        except:
            pass
        link.remote_ios = format_ios_ver(ios)
        return link

    def use_vlan_community(self, vlan: _UIS) -> _USN:
        original_community = self.snmp.community
        community = f"{original_community}@{str(vlan)}"
        if self.snmp.check_community(community):
            return original_community
        else:
            raise NettopoSNMPError(f"ERROR: {community} failed {self.ip}")

    def snmp_get(self, item: _UISO, is_bulk: bool=False,
                                vlan: _UIS=None) -> _UAN:
        results = None
        error = False
        if vlan:
            old_community = self.use_vlan_community(vlan)
        try:
            if is_bulk:
                results = self.snmp.get_bulk(item)
            else:
                results = self.snmp.get_val(item)
        except Exception as e:
            error = e
        finally:
            if vlan:
                self.snmp.community = old_community
            if error:
                return error
            return results

    def query_node(self) -> None:
        """ Query this node with option to reset
        """
        if self.queried:
            print(f"{self.name} has already been queried.")
            return
        with alive_bar(title='Node Query') as bar:
            self.queried = True
            snmp_name = self.snmp_get(o.SYSNAME)
            if self._has_value(snmp_name):
                self.name = normalize_host(
                    snmp_name.value,
                    self.snmp.config.host_domains,
                )
            bar()
            # Description
            snmp_descr = self.snmp_get(o.SYSDESC)
            if self._has_value(snmp_descr):
                self.descr = snmp_descr.value
                sys = sysdescrparser(snmp_descr.value)
                self.os = sys.os
                self.model = sys.model
                self.vendor = sys.vendor
                self.version = sys.version
            bar()
            # Interfaces
            self.interfaces = self.build_interface_table()
            bar()
            # IPs
            self.ips = self.get_ips()
            bar()
            # Vlans
            self.vlans = self.get_vlans()
            bar()
            # SVIs
            self.svis = self.get_svis()
            bar()
            # loopback
            self.loopbacks = self.get_loopbacks()
            bar()
            # bootfile
            bootfile = self.snmp_get(o.SYS_BOOT)
            if self._has_value(bootfile):
                self.bootfile = bootfile.value
            bar()
            # Ent chassis info (serial, ios, platform)
            self.ent = self.get_ent()
            bar()
            # stack
            self.stack = self.get_stack()
            bar()
            # vss
            self.vss = self.get_vss()
            bar()
            # serial
            if self.vss:
                if self.vss.enabled and self.vss.serial:
                    self.serial = self.vss.serial
            else:
                serial = self.snmp_get(o.SYS_SERIAL)
                if self._has_value(serial):
                    self.serial = serial.value
            bar()
            # VPC peerlink polulates self.vpc
            self.vpc = self.get_vpc()
            bar()
            # Populates self.arp_table
            self.arp_table = self.get_arp()
            bar()
            # Populates self.mac_table
            self.mac_table = self.get_cam()
            bar()
            # CDP neighbors
            self.cdp = self.get_cdp()
            bar()
            # LLDP neighbors
            self.lldp = self.get_lldp()
            bar()
            self.links = self.create_links()
            bar()
            # Routing
            snmp_router = self.snmp_get(o.IP_ROUTING)
            if self._has_value(snmp_router) and snmp_router.value == '1':
                self.router = True
            bar()
            if self.router:
                # OSPF
                snmp_ospf = self.snmp_get(o.OSPF)
                if self._has_value(snmp_ospf):
                    self.ospf = snmp_ospf.value
                bar()
                snmp_ospf_id = self.snmp_get(o.OSPF_ID)
                if self._has_value(snmp_ospf_id):
                    self.ospf_id = snmp_ospf_id.value
                bar()
                # BGP
                bgp_las = self.snmp_get(o.BGP_LAS)
                if self._has_value(bgp_las) and bgp_las.value != '0':
                    # 4500x reports 0 as disabled
                    self.bgp_las = bgp_las.value
                bar()
                # HSRP
                snmp_hsrp_pri = self.snmp_get(o.HSRP_PRI)
                if self._has_value(snmp_hsrp_pri):
                    self.hsrp_pri = snmp_hsrp_pri.value
                bar()
                snmp_hsrp_vip = self.snmp_get(o.HSRP_VIP)
                if self._has_value(snmp_hsrp_vip):
                    self.hsrp_vip = snmp_hsrp_vip.value
                bar()

    def create_links(self) -> List[LinkData]:
        # Combine CDP and LLDP to create links
        links = self.cdp.copy()
        for cdp in links:
            for lldp in self.lldp:
                if cdp.is_same_link(lldp):
                    # Remove CDP
                    links.remove(cdp)
                    # Injest lldp
                    cdp.injest_link(lldp)
                    # Add CDP back
                    links.append(cdp)
        # Add LLDP
        for lldp in self.lldp:
            if lldp.local_port not in [l.local_port for l in links]:
                links.append(lldp)
        return links

    def find_interface(self, item: _UIS, name: str=None) -> InterfaceData:
        if not name:
            if isinstance(item, int):
                name = 'idx'
            elif isinstance(item, str):
                name = 'name'
        for entry in self.interfaces:
            if item == getattr(entry, name):
                return entry

    def get_cidr_from_oid(self, oid: str) -> str:
        ip = ".".join(oid.split('.')[-4:])
        if is_ipv4_address(ip):
            mask = self.snmp_get(f"{o.IF_IP_NETM}.{ip}")
            if self._has_value(mask):
                mbits = bits_from_mask(mask.value)
                return f"{ip}/{mbits}"
            else:
                return f"{ip}/32"

    def lookup_ifname_index(self, idx: int,
                                 normalize: bool=False) -> _USN:
        ifname = self.snmp_get(f"{o.IFNAME}.{idx}")
        if not self._has_value(ifname):
            ifindex = self.snmp_get(f"{o.IFINDEX}.{idx}")
            if self._has_value(ifindex):
                ifname = self.snmp_get(f"{o.IFNAME}.{ifindex.value}")
        if self._has_value(ifname):
            if normalize:
                return normalize_port(ifname.value)
            else:
                return ifname.value

    def get_ifname_index(self, idx: int,
                              normalize: bool=True) -> _USN:
        # Look in interfaces first
        if self.interfaces:
            interface = self.find_interface(idx, 'idx')
            if interface:
                return interface.name
        else:
            return self.lookup_ifname_index(idx=idx, normalize=normalize)

    def lookup_cidr_index(self, idx: int) -> _ULN:
        """
        # From IP-MIB
        ipAdEntTable = "1.3.6.1.2.1.4.20.1"
        ipAdEntAddr = "1.3.6.1.2.1.4.20.1.1"
        ipAdEntIfIndex = "1.3.6.1.2.1.4.20.1.2"
        ipAdEntNetMask = "1.3.6.1.2.1.4.20.1.3"
        """
        cidrs = []
        if not self.ip_table:
            # Ip table
            self.ip_table = self.snmp_get(g.ipAdEntTable, is_bulk=True)
        ip_entries = self.ip_table.search(g.ipAdEntIfIndex)
        for ip_oid, ip_idx in ip_entries.items():
            if int(ip_idx) == idx:
                ip = ".".join(ip_oid.split('.')[-4:])
                if is_ipv4_address(ip):
                    mask = self.ip_table.table.get(f"{g.ipAdEntNetMask}.{ip}",
                                                   None)
                    if mask:
                        subnet_mask = bits_from_mask(mask)
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
        indexed_table = [
            ('1.3.6.1.2.1.2.2.1.1.3', '3'),
            ('1.3.6.1.2.1.2.2.1.2.3', 'GigabitEthernet1/0/1'),
            ('1.3.6.1.2.1.2.2.1.3.3', '6'),
            ('1.3.6.1.2.1.2.2.1.4.3', '9000'),
            ('1.3.6.1.2.1.2.2.1.5.3', '1000000000'),
            ('1.3.6.1.2.1.2.2.1.6.3', '0x88908d1b1781'),
            ('1.3.6.1.2.1.2.2.1.7.3', '1'),
            ('1.3.6.1.2.1.2.2.1.8.3', '1'),
            ('1.3.6.1.2.1.2.2.1.9.3', '6773'),
            ('1.3.6.1.2.1.2.2.1.10.3', '3428545753'),
            ('1.3.6.1.2.1.2.2.1.11.3', '12200292'),
            ('1.3.6.1.2.1.2.2.1.13.3', '0'),
            ('1.3.6.1.2.1.2.2.1.14.3', '0'),
            ('1.3.6.1.2.1.2.2.1.15.3', '0'),
            ('1.3.6.1.2.1.2.2.1.16.3', '528472411'),
            ('1.3.6.1.2.1.2.2.1.17.3', '14091342'),
            ('1.3.6.1.2.1.2.2.1.19.3', '0'),
            ('1.3.6.1.2.1.2.2.1.20.3', '0')
        ]
        """
        interfaces = []
        if not self.if_table:
            # If table
            self.if_table = self.snmp_get(g.ifTable, is_bulk=True)
        if_entries = self.if_table.search(
            g.ifIndex,
            return_type='val',
        )
        for if_entry in if_entries:
            idx = int(if_entry)
            idx_table = self.if_table.index_table(idx)
            if_name = idx_table.get(f"{g.ifDescr}.{idx}")
            # Skip unrouted VLAN ports and Stack ports
            if if_name.startswith(('unrouted', 'Null', 'Stack')):
                continue
            if_mac = idx_table.get(f"{g.ifPhysAddress}.{idx}")
            mac = mac_hex_to_ascii(if_mac)
            # Skip interfaces we do not have a MAC.
            # Such as previously stacked switches.
            if mac == '0000.0000.0000':
                continue
            # We have an interface let's build
            interface = InterfaceData()
            interface.idx = idx
            interface.name = normalize_port(if_name)
            interface.mac = mac
            interface.cidrs = self.lookup_cidr_index(idx)
            if_type = idx_table.get(f"{g.ifType}.{idx}")
            interface.media = int_type_map.get(int(if_type))
            if_admin_status = idx_table.get(f"{g.ifAdminStatus}.{idx}")
            interface.admin_status = int_admin_status_map.get(int(if_admin_status))
            if_oper_status = idx_table.get(f"{g.ifOperStatus}.{idx}")
            interface.oper_status = int_oper_status_map.get(int(if_oper_status))
            interfaces.append(interface)
        return interfaces

    def get_ips(self) -> list:
        """ Collects and stores all the IPs for Node
        returns - list of IPs
        """
        ips = []
        for entry in self.interfaces:
            if entry.cidrs:
                ips.extend([cidr.split('/')[0] for cidr in entry.cidrs])
        ips.sort()
        return ips

    def get_ent_from_index(self, idx: int):
        snmp_serial = self.snmp_get(f"{o.ENTPHYENTRY_SERIAL}.{idx}")
        serial = snmp_serial.value if self._has_value(snmp_serial) else None
        snmp_plat = self.snmp_get(f"{o.ENTPHYENTRY_PLAT}.{idx}")
        plat = snmp_plat.value if self._has_value(snmp_plat) else None
        snmp_ios = self.snmp_get(f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        ios = snmp_ios.value if self._has_value(snmp_ios) else None
        return serial, plat, ios

    def build_ent_from_oid(self, oid, ent_snmp) -> _UEN:
        idx = get_oid_index(oid, 12)
        serial, plat, ios = self.get_ent_from_index(idx)
        # Modular switches have IOS on module
        if not ios:
            # Search modules '9'
            mod_oids = ent_snmp.search('9', item_type='val',
                                        return_type='oid')
            if mod_oids:
                for mod_oid in mod_oids:
                    mod_idx = get_oid_index(mod_oid, 12)
                    mod_ios = self.snmp_get(f"{o.ENTPHYENTRY_SOFTWARE}.{mod_idx}")
                    if self._has_value(mod_ios):
                        ios = mod_ios.value
                        break
        ios = format_ios_ver(ios)
        if all([serial, plat, ios]):
            return EntData(serial, plat, ios)

    def get_ent(self) -> _UEN:
        # TODO: IOS is incorrect for IOS-XE at least.
        ent_snmp = self.snmp_get(o.ENTPHYENTRY_CLASS, is_bulk=True)
        # Search chassis '3'
        chs_oids = ent_snmp.search('3', item_type='val', return_type='oid')
        if chs_oids:
            for chs_oid in chs_oids:
                ent = self.build_ent_from_oid(chs_oid, ent_snmp)
                if ent:
                    return ent

    def get_loopbacks(self) -> List[InterfaceData]:
        return [entry for entry in self.interfaces \
                if entry.media == 'softwareLoopback']

    def get_svis(self) -> List[SVIData]:
        svis = []
        svi_table = self.snmp_get(o.SVI_VLANIF, is_bulk=True)
        for oid, val in svi_table.table.items():
            vlan = get_oid_index(oid, 14)
            svi = SVIData(vlan)
            interface = self.find_interface(int(val), 'idx')
            if interface:
                svi.ips = interface.cidrs
            svis.append(svi)
        return svis

    def get_vlans(self) -> List[VLANData]:
        vlans = []
        vlan_table = self.snmp_get(o.VLANS_NEW, is_bulk=True)
        for oid, name in vlan_table.table.items():
            # get VLAN ID from OID
            vid = get_oid_index(oid)
            if vid not in RESERVED_VLANS:
                vlans.append(VLANData(vid, name))
        return vlans

    def get_stack(self)-> StackData:
        stack_roles = ['master', 'member', 'notMember', 'standby']
        stack = StackData()
        stack_snmp = self.snmp_get(o.STACK, is_bulk=True)
        for oid, val in stack_snmp.table.items():
            if oid.startswith(f"{o.STACK_NUM}."):
                idx = get_oid_index(oid, 14)
                mem = StackMemberData()
                mem.num = int(val)
                role_num = stack_snmp.table.get(f"{o.STACK_ROLE}.{idx}", "")
                for role in enumerate(stack_roles, start=1):
                    if int(role_num) == role[0]:
                        mem.role = role[1]
                if mem.role and mem.role != 'notMember':
                    mem.pri = stack_snmp.table.get(f"{o.STACK_PRI}.{idx}", "")
                    mem.img = stack_snmp.table.get(f"{o.STACK_IMG}.{idx}", "")
                    mem.serial, mem.plat, mem.ios = self.get_ent_from_index(idx)
                    mac = stack_snmp.table.get(f"{o.STACK_MAC}.{idx}", "")
                    if mac:
                        mem.mac = mac_hex_to_ascii(mac)
                    stack.members.append(mem)
        if len(stack.members) > 1:
            stack.enabled = True
            stack.count = len(stack.members)
            return stack

    def get_vss(self) -> VssData:
        vss_snmp = self.snmp_get(o.VSS, is_bulk=True)
        if not vss_snmp.table:
            return
        vss_mode = vss_snmp.table.get(o.VSS_MODE, "")
        if vss_mode == '2':
            vss = VssData()
            vss.enabled = True
            vss.domain = vss_snmp.table.get(o.VSS_DOMAIN, "")
            chassis = 0
            vss_mod_snmp = self.snmp_get(o.VSS_MODULES, is_bulk=True)
            vss_mods = vss_mod_snmp.search('1', item_type='val')
            if vss_mods:
                for _oid, _val in vss_mods.items():
                    modidx = get_oid_index(_oid, 14)
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

    def get_vpc(self) -> Union[VPCData, None]:
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        vpc_table = self.snmp_get(o.VPC_PEERLINK_IF, is_bulk=True)
        if vpc_table.table:
            for oid, val in vpc_table.table.items():
                vpc = VPCData()
                vpc.domain = get_oid_index(oid)
                vpc.ifname = self.get_ifname_index(int(val))
            return vpc

    def get_arp(self) -> List[ARPData]:
        """
            {'1.3.6.1.2.1.3.1.1.2.45.1.10.0.20.1': '0x88908d1b17d6',
             '1.3.6.1.2.1.3.1.1.2.45.1.10.0.20.10': '0x843497a26eee',
             '1.3.6.1.2.1.3.1.1.2.45.1.10.0.20.105': '0x0026552a2b10',
             '1.3.6.1.2.1.3.1.1.2.45.1.10.0.20.106': '0x78e7d18f87bc',
             '1.3.6.1.2.1.3.1.1.2.45.1.10.0.20.112': '0x843dc69858d6',
             '1.3.6.1.2.1.3.1.1.2.46.1.10.0.21.1': '0x88908d1b17e8',
             '1.3.6.1.2.1.3.1.1.2.47.1.10.0.23.1': '0x88908d1b17c4',
             '1.3.6.1.2.1.3.1.1.2.47.1.10.0.23.20': '0x1803731622e1',
             '1.3.6.1.2.1.3.1.1.2.47.1.10.0.23.113': '0x843dc69858da',
             '1.3.6.1.2.1.3.1.1.2.47.1.10.0.23.220': '0x000c29b53a59',
             '1.3.6.1.2.1.3.1.1.2.47.1.10.0.23.246': '0x84b51708b63e',
             '1.3.6.1.2.1.3.1.1.2.48.1.10.0.24.1': '0x88908d1b17c1',
             '1.3.6.1.2.1.3.1.1.2.49.1.10.0.25.1': '0x88908d1b17f1',
             '1.3.6.1.2.1.3.1.1.2.50.1.10.0.26.1': '0x88908d1b17e5',
             '1.3.6.1.2.1.3.1.1.2.51.1.10.0.27.1': '0x88908d1b17d5',
             '1.3.6.1.2.1.3.1.1.2.52.1.10.0.28.1': '0x88908d1b17d9',
             '1.3.6.1.2.1.3.1.1.2.53.1.10.0.29.1': '0x88908d1b17e8',
             '1.3.6.1.2.1.3.1.1.2.54.1.10.0.30.1': '0x88908d1b17e5',
             '1.3.6.1.2.1.3.1.1.2.55.1.10.0.0.1': '0x88908d1b17d1',
             '1.3.6.1.2.1.3.1.1.2.55.1.10.0.0.2': '0x28940fe5fac1',
             '1.3.6.1.2.1.3.1.1.2.55.1.10.0.0.5': '0x001c7f707f0f',
             '1.3.6.1.2.1.3.1.1.2.56.1.172.16.1.1': '0x88908d1b17c1',
             '1.3.6.1.2.1.3.1.1.2.57.1.172.16.2.1': '0x88908d1b17cd',
             '1.3.6.1.2.1.3.1.1.2.58.1.172.16.3.1': '0x88908d1b17dd',
             '1.3.6.1.2.1.3.1.1.2.59.1.10.10.0.1': '0x88908d1b17e9',
             '1.3.6.1.2.1.3.1.1.2.60.1.10.20.0.1': '0x88908d1b17f9',
             '1.3.6.1.2.1.3.1.1.2.61.1.172.16.10.1': '0x88908d1b17cd',
             '1.3.6.1.2.1.3.1.1.2.65.1.10.0.31.1': '0x88908d1b17d5',
             '1.3.6.1.2.1.3.1.1.2.66.1.10.0.32.1': '0x88908d1b17d5',
             '1.3.6.1.2.1.3.1.1.2.67.1.10.0.33.1': '0x88908d1b17c5',
             '1.3.6.1.2.1.3.1.1.2.71.1.10.0.11.1': '0x88908d1b17d4',
             '1.3.6.1.2.1.3.1.1.2.72.1.10.0.37.1': '0x88908d1b17c5',
             '1.3.6.1.2.1.3.1.1.2.75.1.10.0.34.1': '0x88908d1b17c9',
             '1.3.6.1.2.1.3.1.1.2.76.1.10.0.35.1': '0x88908d1b17d9',
             '1.3.6.1.2.1.3.1.1.2.77.1.10.0.36.1': '0x88908d1b17d5',
             '1.3.6.1.2.1.3.1.1.2.115.1.10.0.124.1': '0x88908d1b17c0',
             '1.3.6.1.2.1.3.1.1.2.116.1.10.0.125.1': '0x88908d1b17f2',
             '1.3.6.1.2.1.3.1.1.2.117.1.10.0.126.1': '0x88908d1b17ec',
             '1.3.6.1.2.1.3.1.1.2.121.1.10.0.127.1': '0x88908d1b17d2',
             '1.3.6.1.2.1.3.1.1.2.122.1.10.0.128.1': '0x88908d1b17de',
             '1.3.6.1.2.1.3.1.1.2.123.1.10.0.129.1': '0x88908d1b17c8',
             '1.3.6.1.2.1.3.1.1.2.124.1.10.0.130.1': '0x88908d1b17fe'}
        """
        _arp_oid = '1.3.6.1.2.1.3.1.1.2'
        arps = []
        arp_table = self.snmp_get(_arp_oid, is_bulk=True)
        for oid, val in arp_table.table.items():
            oid_end = oid.split(f"{_arp_oid}.")[1]
            end_list = oid_end.split('.')
            idx = end_list.pop(0)
            _ = end_list.pop(0)
            ip = '.'.join(end_list)
            interface = self.get_ifname_index(int(idx))
            mac = mac_hex_to_ascii(val)
            arps.append(ARPData(ip, mac, interface))
        return arps

    def get_macs_for_vlan(self, vlan: int) -> List[MACData]:
        ''' MAC addresses for a single VLAN
        _stp = '1.3.6.1.2.1.17.2.15.1'
        _stp_port = f'{_stp}.1'
        _stp_priority = f'{_stp}.2'
        _stp_state = f'{_stp}.3'
        _mac = '1.3.6.1.2.1.4.22.1'
        _mac_vlan = '1.3.6.1.2.1.4.22.1.1'
        _mac_mac = '1.3.6.1.2.1.4.22.1.2'
        _mac_ip = '1.3.6.1.2.1.4.22.1.3'
        _mac_type_map = '1.3.6.1.2.1.4.22.1.4'
        '''
        _cam = '1.3.6.1.2.1.17.4.3.1'
        _bridge_mac = '1.3.6.1.2.1.17.4.3.1.1'
        _bridge_port = '1.3.6.1.2.1.17.4.3.1.2'
        _bridge_stat = '1.3.6.1.2.1.17.4.3.1.3'
        _bridge_if = '1.3.6.1.2.1.17.1.4.1.2'
        macs = []
        # Get the dynamic CAM table for this VLAN
        cam_table = self.snmp_get(_cam, is_bulk=True, vlan=vlan)
        if not cam_table.table:
            return macs
        ifindex_table = self.snmp_get(_bridge_if, is_bulk=True, vlan=vlan)
        for oid, val in cam_table.search(_bridge_mac).items():
            idx = oid.split(f"{_bridge_mac}.")[1]
            index_cam = cam_table.index_table(idx)
            mac = mac_hex_to_ascii(val)
            portnum = index_cam.get(f"{_bridge_port}.{idx}")
            status_num = index_cam.get(f"{_bridge_stat}.{idx}")
            status = bridge_status_map.get(status_num)
            if portnum == '0':
                port = 'NotLearned'
            else:
                ifidx = ifindex_table.search(
                    f"{_bridge_if}.{portnum}",
                    return_type='val',
                )[0]
                port = self.get_ifname_index(int(ifidx))
            entry = MACData(vlan, mac, port, status)
            macs.append(entry)
        return macs

    def get_cam(self) -> List[MACData]:
        ''' MAC address table from this node
        '''
        mac_table = []
        # Grab CAM table for each VLAN
        for vlan in self.vlans:
            macs = self.get_macs_for_vlan(vlan.vid)
            if macs:
                mac_table.extend(macs)
        return mac_table

    def get_link(self, ifidx: int, link: LinkData=None) -> LinkData:
        if not link:
            link = LinkData()
            link.discovered_proto = 'Unknown'
        if not link.local_interface:
            if link.local_port:
                # Check local interfaces for name
                interface = self.find_interface(link.local_port, 'name')
            else:
                # Check local interfaces for index
                interface = self.find_interface(ifidx, 'idx')
            if interface:
                link.add_local_interface(interface)
        if not link.local_port:
            local_port = self.get_ifname_index(ifidx)
            if local_port:
                link.local_port = local_port
        link_type = self.snmp_get(f"{o.TRUNK_VTP}.{ifidx}")
        if self._has_value(link_type):
            if link_type.value == '2':
                link.link_type = 'trunk'
            elif link_type.value == '1':
                link.link_type = 'access'
            else:
                link.link_type = 'unknown'
        # trunk
        if link.link_type == 'trunk':
            native_vlan = self.snmp_get(f"{o.TRUNK_NATIVE}.{ifidx}")
            if self._has_value(native_vlan):
                link.local_native_vlan = native_vlan.value
            trunk_allowed = self.snmp_get(f"{o.TRUNK_ALLOW}.{ifidx}")
            if self._has_value(trunk_allowed):
                link.local_allowed_vlans = parse_allowed_vlans(trunk_allowed.value)
        # LAG membership
        lag = self.snmp_get(f"{o.LAG_LACP}.{ifidx}")
        if self._has_value(lag):
            interface = self.find_interface(int(lag.value), 'idx')
            if interface:
                link.local_lag = interface.name
                link.local_lag_ips = interface.cidrs
                link.remote_lag_ips = []
        # VLAN info
        vlan = self.snmp_get(f"{o.IF_VLAN}.{ifidx}")
        if self._has_value(vlan):
            link.vlan = vlan.value
        return link

    def get_cdp(self) -> List[LinkData]:
        """ Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        # CDP (BULK)
        CDP: str = '1.3.6.1.4.1.9.9.23.1.2.1.1'
        CDP_IPADDR: str = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
        CDP_IOS: str = '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
        # CDP_DEVID + .ifidx.53
        CDP_DEVID: str = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
        CDP_DEVPORT: str = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
        CDP_DEVPLAT: str = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'
        # CDP_INT 6.ifidx
        CDP_INT: str = '1.3.6.1.4.1.9.9.23.1.1.1.1.'
        """
        _cdp_mib = '1.3.6.1.4.1.9.9.23.1'
        _cdp_ipaddr = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
        _cdp_ios = '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
        _cdp_devname = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
        _cdp_devport = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
        _cdp_devplat = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'
        # CDP_INT 6.ifidx
        _cdp_int = '1.3.6.1.4.1.9.9.23.1.1.1.1.'
        # get list of CDP neighbors
        neighbors = []
        cdp = self.snmp_get(_cdp_mib, is_bulk=True)
        # process only if this row is a _cdp_devname
        for oid, name in cdp.search(_cdp_devname).items():
            link = LinkData()
            link.discovered_proto = 'cdp'
            link.remote_name = normalize_host(
                name,
                self.snmp.config.host_domains,
            )
            idx1 = get_oid_index(oid, 14)
            idx2 = get_oid_index(oid, 15)
            idx = ".".join([str(idx1), str(idx2)])
            link = self.get_link(idx1, link)
            index_cdp = cdp.index_table(idx)
            # get remote IP
            rip = index_cdp.get(f"{_cdp_ipaddr}.{idx}")
            link.remote_ip = ip_2_str(rip)
            # Lookup MAC with IP from arp_table
            if link.remote_ip:
                for arp in self.arp_table:
                    if link.remote_ip == arp.ip:
                        link.remote_mac = arp.mac
            # get remote port
            rport = index_cdp.get(f"{_cdp_devport}.{idx}")
            link.remote_port = normalize_port(rport)
            # get remote platform
            remote_plat = index_cdp.get(f"{_cdp_devplat}.{idx}")
            link.remote_plat = remote_plat
            # get IOS version
            rios_bytes = index_cdp.get(f"{_cdp_ios}.{idx}")
            link = self._link_ios(rios_bytes, link)
            neighbors.append(link)
        return neighbors

    def get_lldp(self) -> List[LinkData]:
        """ Get a list of LLDP neighbors.
        Returns a list of LinkData's
        Will always return an array.
        NEW_LLDP_MIB: str = '1.0.8802.1.1.2'
        LLDP: str = '1.0.8802.1.1.2.1.4'
        LLDP_TYPE: str = '1.0.8802.1.1.2.1.4.1.1.6.0'
        LLDP_DEVID: str = '1.0.8802.1.1.2.1.4.1.1.5.0'
        LLDP_DEVPORT: str = '1.0.8802.1.1.2.1.4.1.1.7.0'
        LLDP_DEVPDSC: str = '1.0.8802.1.1.2.1.4.1.1.8.0'
        LLDP_DEVNAME: str = '1.0.8802.1.1.2.1.4.1.1.9.0'
        LLDP_DEVDESC: str = '1.0.8802.1.1.2.1.4.1.1.10.0'
        LLDP_DEVADDR: str = '1.0.8802.1.1.2.1.4.2.1.5.0'
        """
        _lldp_mib = '1.0.8802.1.1.2'
        _lldp_devaddr = '1.0.8802.1.1.2.1.4.2.1.5.0'
        _lldp_devid = '1.0.8802.1.1.2.1.4.1.1.5.0'
        _lldp_devport = '1.0.8802.1.1.2.1.4.1.1.7.0'
        _lldp_devpdsc = '1.0.8802.1.1.2.1.4.1.1.8.0'
        _lldp_port_name = '1.0.8802.1.1.2.1.3.7.1.4'
        _lldp_remote_descr = '1.0.8802.1.1.2.1.4.1.1.10.0'
        _lldp_remote_name = '1.0.8802.1.1.2.1.4.1.1.9.0'
        neighbors = []
        lldp = self.snmp_get(_lldp_mib, is_bulk=True)
        lld_dev_names = lldp.search(_lldp_remote_name)
        for oid, name in lld_dev_names.items():
            link = LinkData()
            link.discovered_proto = 'lldp'
            link.remote_name = normalize_host(
                name,
                self.snmp.config.host_domains,
            )
            idx1 = get_oid_index(oid, -2)
            idx2 = get_oid_index(oid, -1)
            idx = ".".join(oid.split('.')[-2:])
            lldp_port = lldp.table.get(f"{_lldp_port_name}.{idx1}")
            link.local_port = normalize_port(lldp_port)
            link = self.get_link(idx1, link)
            rip_oid = f"{_lldp_devaddr}.{idx}"
            link.remote_ip = self.get_cidr_from_oid(rip_oid)
            # Lookup MAC with IP from arp_table
            for arp in self.arp_table:
                if arp.ip == link.remote_ip:
                    link.remote_mac = arp.mac
            rport = lldp.table.get(f"{_lldp_devport}.{idx}")
            link.remote_port = normalize_port(rport)
            link.remote_port_desc = lldp.table.get(f"{_lldp_devpdsc}.{idx}")
            # devid = lldp.table.get(f"{_lldp_devid}.{idx}")
            # link.remote_mac = mac_hex_to_ascii(devid)
            rios_bytes = lldp.table.get(f"{_lldp_remote_descr}.{idx}")
            link = self._link_ios(rios_bytes, link)
            neighbors.append(link)
        return neighbors

""" SNMP Queries Saved
ospf = self.snmp_get(o.OSPF)
ospf_id = self.snmp_get(o.OSPF_ID)

ent_class = self.snmp_get(o.ENTPHYENTRY_CLASS, is_bulk=True)
ent_serial = self.snmp_get(o.ENTPHYENTRY_SERIAL, is_bulk=True)
ent_plat = self.snmp_get(o.ENTPHYENTRY_PLAT, is_bulk=True)
ent_ios = self.snmp_get(o.ENTPHYENTRY_SOFTWARE, is_bulk=True)
link_type = self.snmp_get(o.TRUNK_VTP, is_bulk=True)
lag = self.snmp_get(o.LAG_LACP, is_bulk=True)
ifname = self.snmp_get(o.IFNAME, is_bulk=True)
ifip = self.snmp_get(o.IF_IP, is_bulk=True)
ethif = self.snmp_get(o.ETH_IF, is_bulk=True)
trunk_allowed = self.snmp_get(o.TRUNK_ALLOW, is_bulk=True)
trunk_native = self.snmp_get(o.TRUNK_NATIVE, is_bulk=True)
portnums = self.snmp_get(o.BRIDGE_PORTNUMS, is_bulk=True)
ifindex = self.snmp_get(o.IFINDEX, is_bulk=True)
vlan = self.snmp_get(o.VLANS, is_bulk=True)
vlandesc = self.snmp_get(o.VLAN_DESC, is_bulk=True)
svi = self.snmp_get(o.SVI_VLANIF, is_bulk=True)
vpc = self.snmp_get(o.VPC_PEERLINK_IF, is_bulk=True)
stack = self.snmp_get(o.STACK, is_bulk=True)
cdp = self.snmp_get(o.CDP, is_bulk=True)
lldp = self.snmp_get(o.LLDP, is_bulk=True)
route = self.snmp_get(o.IP_ROUTE_TABLE, is_bulk=True)
arp = self.snmp_get(o.ARP, is_bulk=True)
cam = self.snmp_get(o.VLAN_CAM, is_bulk=True)

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
