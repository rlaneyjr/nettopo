# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
# from about_time import about_time
from alive_progress import alive_bar, config_handler
import binascii
from copy import deepcopy
from netaddr import IPAddress
from pysnmp.smi.rfc1902 import ObjectIdentity
import re
from sysdescrparser import sysdescrparser
from typing import Union, List, Any, Optional
# Nettopo Imports
from nettopo.core.constants import (
    DCODE,
    NODE,
    NOTHING,
    RESERVED_VLANS,
    retcode_type_map,
    node_type_map,
    arp_type_map,
    bridge_status_map,
    stp_state_map,
    entphyclass_type_map,
    int_oper_status_map,
    int_type_map,
    int_admin_status_map,
)
from nettopo.core.data import (
    Secret,
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
from nettopo.utils import build_uuid

# Typing shortcuts
_IP = Union[str, IPAddress]
_UDL = Union[dict, list]
_UDLS = Union[dict, list, str]
_ULS = Union[list, str]
_UIS = Union[int, str]
_USN = Union[str, None]
_UISO = Union[int, str, ObjectIdentity]
_OA = Optional[Any]
_OL = Optional[list]
_OEd = Optional[EntData]
_OId = Optional[InterfaceData]
_OLSIN = Optional[Union[list, str, int]]

# Easy access to our OIDs
o = Oids()
g = GeneralOids()
c = CiscoOids()
# Global defaults for alive-progress bar
config_handler.set_global(theme='smooth')


class Nodes(DataTable):
    """ Store a list of nodes with our DataTable class.
        Use this just like a list but with Nodes only.
    """
    def get_node(self, node_id: str, key='_id') -> Optional[object]:
        return self.get_item(key, node_id, True)

    def append(self, node: object) -> None:
        if node not in self:
            super().append(node)

    def extend(self, nodes: List[object]) -> None:
        for node in nodes:
            self.append(node)


class Node(BaseData):
    """ Node class that builds data from SNMP queries.
    """
    show_items = ['name', 'ip', 'plat', 'ios', 'serial', 'router']
    def __init__(self, ip: str, immediate_query: bool=False, **kwargs) -> None:
        self._id = build_uuid()
        self.ip = ip
        self.snmp = SNMP(self.ip, **kwargs)
        self.domains = self.snmp.config.host_domains
        self.queried = False
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
        self.links = None
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
        vlan_community = Secret(f"{original_community.show}@{str(vlan)}")
        if self.snmp.check_community(vlan_community):
            return original_community
        else:
            raise NettopoSNMPError(f"{vlan_community} failed for {self.ip}")

    def snmp_get(self, item: _UISO, is_bulk: bool=False,
                                vlan: _UIS=None) -> _OA:
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

    def query_node(self, bar: bool=True) -> None:
        """ Query this node
        """
        _all_query_funcs_ = [
            'get_name',
            'get_descr',
            'build_interface_table',
            'get_ips',
            'get_vlans',
            'get_svis',
            'get_loopbacks',
            'get_bootfile',
            'get_ent',
            'get_stack',
            'get_vss',
            'get_serial',
            'get_vpc',
            'get_arp',
            'get_cam',
            'create_links',
            'get_routing',
        ]
        if self.queried:
            print(f"{self.name} has already been queried.")
            return
        if bar:
            with alive_bar(title=f"Node Query for {self.ip}") as bar:
                for qfunc in _all_query_funcs_:
                    do_func = getattr(self, qfunc)
                    do_func()
                    bar()
        else:
            for qfunc in _all_query_funcs_:
                do_func = getattr(self, qfunc)
                do_func()
        self.queried = True

    def query_no_bar(self) -> None:
        """ Query this node without a status bar
        """
        # Name
        self.get_name()
        # Description
        self.get_descr()
        # Interfaces
        self.build_interface_table()
        # IPs
        self.get_ips()
        # Vlans
        self.get_vlans()
        # SVIs
        self.get_svis()
        # loopback
        self.get_loopbacks()
        # bootfile
        self.get_bootfile()
        # Ent chassis info (serial, ios, platform)
        self.get_ent()
        # stack
        self.get_stack()
        # vss
        self.get_vss()
        # serial
        self.get_serial()
        # VPC peerlink polulates self.vpc
        self.get_vpc()
        # Populates ARP DataTable
        self.get_arp()
        # Populates MAC DataTable
        self.get_cam()
        self.create_links()
        # Routing
        self.get_routing()

    def get_name(self):
        snmp_name = self.snmp_get(o.SYSNAME)
        if self._has_value(snmp_name):
            self.name = normalize_host(snmp_name.value, self.domains)
        # Finally, if we still don't have a name, use the IP.
        # A blank name can break Dot.
        if self.name in NOTHING:
            self.name = self.ip.replace('.', '_')

    def get_descr(self):
        # Description
        snmp_descr = self.snmp_get(o.SYSDESC)
        if self._has_value(snmp_descr):
            self.descr = snmp_descr.value
            sys = sysdescrparser(snmp_descr.value)
            self.os = sys.os
            self.model = sys.model
            self.vendor = sys.vendor
            self.version = sys.version

    def get_bootfile(self):
        # bootfile
        bootfile = self.snmp_get(o.SYS_BOOT)
        if self._has_value(bootfile):
            self.bootfile = bootfile.value

    def get_serial(self):
        # serial
        if self.vss:
            if self.vss.enabled and self.vss.serial:
                self.serial = self.vss.serial
        else:
            serial = self.snmp_get(o.SYS_SERIAL)
            if self._has_value(serial):
                self.serial = serial.value

    def get_routing(self):
        # Routing
        snmp_router = self.snmp_get(o.IP_ROUTING)
        if self._has_value(snmp_router) and snmp_router.value == '1':
            self.router = True
            # OSPF
            snmp_ospf = self.snmp_get(o.OSPF)
            if self._has_value(snmp_ospf):
                self.ospf = snmp_ospf.value
            snmp_ospf_id = self.snmp_get(o.OSPF_ID)
            if self._has_value(snmp_ospf_id):
                self.ospf_id = snmp_ospf_id.value
            # BGP
            bgp_las = self.snmp_get(o.BGP_LAS)
            if self._has_value(bgp_las) and bgp_las.value != '0':
                # 4500x reports 0 as disabled
                self.bgp_las = bgp_las.value
            # HSRP
            snmp_hsrp_pri = self.snmp_get(o.HSRP_PRI)
            if self._has_value(snmp_hsrp_pri):
                self.hsrp_pri = snmp_hsrp_pri.value
            snmp_hsrp_vip = self.snmp_get(o.HSRP_VIP)
            if self._has_value(snmp_hsrp_vip):
                self.hsrp_vip = snmp_hsrp_vip.value

    def get_cidr_from_oid(self, oid: str) -> str:
        ip = ".".join(oid.split('.')[-4:])
        if is_ipv4_address(ip):
            mask = self.snmp_get(f"{o.IF_IP_NETM}.{ip}")
            if self._has_value(mask):
                mbits = bits_from_mask(mask.value)
                return f"{ip}/{mbits}"
            else:
                return f"{ip}/32"

    def lookup_ifname_index(self, idx: int, normalize: bool=True) -> _USN:
        ifname = self.snmp_get(f"{g.ifName}.{idx}")
        if not self._has_value(ifname):
            ifindex = self.snmp_get(f"{g.ifAlias}.{idx}")
            if self._has_value(ifindex):
                ifname = self.snmp_get(f"{o.IFNAME}.{ifindex.value}")
        if self._has_value(ifname):
            if normalize:
                return normalize_port(ifname.value)
            else:
                return ifname.value

    def get_ifname_index(self, idx: int, normalize: bool=True) -> _USN:
        # Look in interfaces first
        if self.interfaces:
            interface = self.get_interface_entry('idx', idx)
            if interface:
                return interface.name
        else:
            return self.lookup_ifname_index(idx=idx, normalize=normalize)

    def lookup_cidr_index(self, idx: int) -> _OL:
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

    def lookup_vlan_interface(self, interface: InterfaceData) -> InterfaceData:
        _vlan_oid = '1.3.6.1.4.1.9.9.68.1.2.2.1'
        _vlan_mem_type_oid = f"{_vlan_oid}.1"
        _vlan_mem_type_map = {1: 'static', 2: 'dynamic', 3: 'multiVlan'}
        _vlan_id_oid = f"{_vlan_oid}.2"
        _vlan_status_oid = f"{_vlan_oid}.3"
        _vlan_status_map = {1: 'Inactive', 2: 'Active', 3: 'Shutdown'}
        if interface.media == 'ethernetCsmacd':
            # Ethernet port get vlan details
            idx = interface.idx
            vlan_id = self.snmp_get(f"{_vlan_id_oid}.{idx}")
            if self._has_value(vlan_id):
                interface.port_type = 'access'
                interface.port_vlan = vlan_id.value
                vlan_mem = self.snmp_get(f"{_vlan_mem_type_oid}.{idx}")
                if self._has_value(vlan_mem):
                    interface.port_vlan_mem = _vlan_mem_type_map.get(
                        int(vlan_mem.value)
                    )
                vlan_status = self.snmp_get(f"{_vlan_status_oid}.{idx}")
                if self._has_value(vlan_status):
                    interface.port_vlan_status = _vlan_status_map.get(
                        int(vlan_status.value)
                    )
            else:
                link_type = self.snmp_get(f"{o.TRUNK_VTP}.{idx}")
                if self._has_value(link_type) and link_type.value == '2':
                    interface.port_type = 'trunk'
                    native_vlan = self.snmp_get(f"{o.TRUNK_NATIVE}.{idx}")
                    if self._has_value(native_vlan):
                        interface.port_native_vlan = native_vlan.value
                    trunk_allowed = self.snmp_get(f"{o.TRUNK_ALLOW}.{idx}")
                    if self._has_value(trunk_allowed):
                        interface.port_allowed_vlans = parse_allowed_vlans(
                            trunk_allowed.value
                        )
        return interface
        # LAG membership
        # lag = self.snmp_get(f"{o.LAG_LACP}.{idx}")
        # if self._has_value(lag):
        # lag_interface = self.get_interface_entry('idx', int(lag.value))
        # if lag_interface:
        #         port_lag = lag_interface.name
        #         port_lag_ips = lag_interface.cidrs
        #         port_remote_lag_ips = []

    def build_interface_table(self) -> DataTable:
        """
        """
        # From IF-MIB
        _ifTable = "1.3.6.1.2.1.2.2"
        _ifEntry = f"{_ifTable}.1"
        _ifIndex = f"{_ifEntry}.1"
        _ifDescr = f"{_ifEntry}.2"
        _ifType = f"{_ifEntry}.3"
        _ifMtu = f"{_ifEntry}.4"
        _ifSpeed = f"{_ifEntry}.5"
        _ifPhysAddress = f"{_ifEntry}.6"
        _ifAdminStatus = f"{_ifEntry}.7"
        _ifOperStatus = f"{_ifEntry}.8"
        interfaces = []
        # If table
        if not self.if_table:
            self.if_table = self.snmp_get(_ifTable, is_bulk=True)
        if_entries = self.if_table.search(
            _ifIndex,
            return_type='val',
        )
        for if_entry in if_entries:
            idx = int(if_entry)
            idx_table = self.if_table.index_table(idx)
            if_name = idx_table.get(f"{_ifDescr}.{idx}")
            # Skip unrouted VLAN ports and Stack ports
            if if_name.startswith(('unrouted', 'Null', 'Stack')):
                continue
            if_mac = idx_table.get(f"{_ifPhysAddress}.{idx}")
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
            if_type = idx_table.get(f"{_ifType}.{idx}")
            interface.media = int_type_map.get(int(if_type))
            if_admin_status = idx_table.get(f"{_ifAdminStatus}.{idx}")
            interface.admin_status = int_admin_status_map.get(
                int(if_admin_status)
            )
            if_oper_status = idx_table.get(f"{_ifOperStatus}.{idx}")
            interface.oper_status = int_oper_status_map.get(
                int(if_oper_status)
            )
            interface.mtu = idx_table.get(f"{_ifMtu}.{idx}")
            interface.speed = idx_table.get(f"{_ifSpeed}.{idx}")
            interface = self.lookup_vlan_interface(interface)
            interfaces.append(interface)
        self.interfaces = DataTable(interfaces)

    def get_interface_entry(self, key: str, value: str) -> _OId:
        if not self.interfaces:
            self.build_interface_table()
        if value in self.interfaces.column(key):
            return self.interfaces.get_item(key, value, no_list=True)

    def get_ips(self) -> list:
        """ Collects and stores all the IPs for Node
        returns - list of IPs
        """
        ips = []
        for cidrs in self.interfaces.cidrs:
            if cidrs:
                ips.extend([cidr.split('/')[0] for cidr in cidrs])
        ips.sort()
        self.ips = ips

    def get_ent_from_index(self, idx: int):
        snmp_serial = self.snmp_get(f"{o.ENTPHYENTRY_SERIAL}.{idx}")
        serial = snmp_serial.value if self._has_value(snmp_serial) else None
        snmp_plat = self.snmp_get(f"{o.ENTPHYENTRY_PLAT}.{idx}")
        plat = snmp_plat.value if self._has_value(snmp_plat) else None
        snmp_ios = self.snmp_get(f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        ios = snmp_ios.value if self._has_value(snmp_ios) else None
        return serial, plat, ios

    def build_ent_from_oid(self, oid, ent_snmp) -> _OEd:
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

    def get_ent(self) -> _OEd:
        # TODO: IOS is incorrect for IOS-XE at least.
        ent_snmp = self.snmp_get(o.ENTPHYENTRY_CLASS, is_bulk=True)
        # Search chassis '3'
        chs_oids = ent_snmp.search('3', item_type='val', return_type='oid')
        if chs_oids:
            for chs_oid in chs_oids:
                ent = self.build_ent_from_oid(chs_oid, ent_snmp)
                if ent:
                    self.ent = ent

    def get_loopbacks(self) -> List[InterfaceData]:
        self.loopbacks = self.interfaces.rows('media', 'softwareLoopback')

    def get_svis(self) -> DataTable:
        svis = []
        svi_table = self.snmp_get(o.SVI_VLANIF, is_bulk=True)
        for oid, val in svi_table.table.items():
            vlan = get_oid_index(oid, 14)
            svi = SVIData(vlan)
            interface = self.get_interface_entry('idx', int(val))
            if interface:
                svi.ips = interface.cidrs
            svis.append(svi)
        self.svis = DataTable(svis)

    def get_vlans(self) -> DataTable:
        vlans = []
        vlan_table = self.snmp_get(o.VLANS_NEW, is_bulk=True)
        for oid, name in vlan_table.table.items():
            # get VLAN ID from OID
            vid = get_oid_index(oid)
            if vid not in RESERVED_VLANS:
                vlans.append(VLANData(vid, name))
        self.vlans = DataTable(vlans)

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
        self.stack = stack

    def get_vss(self) -> Optional[VssData]:
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
            self.vss = vss

    def get_vpc(self) -> Optional[VPCData]:
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        vpc_table = self.snmp_get(o.VPC_PEERLINK_IF, is_bulk=True)
        if vpc_table.table:
            for oid, val in vpc_table.table.items():
                vpc = VPCData()
                vpc.domain = get_oid_index(oid)
                vpc.ifname = self.get_interface_entry('idx', val).name
            self.vpc = vpc

    def get_arp(self) -> DataTable:
        """
        """
        _arp_table = '1.3.6.1.2.1.4.22'
        _arp_entry = '1.3.6.1.2.1.4.22.1'
        _arp_vlan = '1.3.6.1.2.1.4.22.1.1'
        _arp_mac = '1.3.6.1.2.1.4.22.1.2'
        _arp_ip = '1.3.6.1.2.1.4.22.1.3'
        _arp_type = '1.3.6.1.2.1.4.22.1.4'
        arp_table = []
        arps = self.snmp_get(_arp_table, is_bulk=True)
        for oid, val in arps.search(_arp_mac).items():
            oid_idx = oid.split(f"{_arp_mac}.")[1]
            index_arp = arps.index_table(oid_idx)
            mac = mac_hex_to_ascii(val)
            idx = index_arp.get(f"{_arp_vlan}.{oid_idx}")
            interface = self.get_ifname_index(int(idx), normalize=True)
            ip = index_arp.get(f"{_arp_ip}.{oid_idx}")
            arpt = index_arp.get(f"{_arp_type}.{oid_idx}")
            arp_type = arp_type_map.get(int(arpt))
            arp_table.append(ARPData(ip, mac, interface, arp_type))
        self.arp_table = DataTable(arp_table)

    def get_arp_entry(self, key: str, value: str) -> Optional[ARPData]:
        if not self.arp_table:
            self.get_arp()
        if value in self.arp_table.column(key):
            return self.arp_table.get_item(key, value, no_list=True)

    def get_macs_for_vlan(self, vlan: int) -> List[MACData]:
        """ MAC addresses for a single VLAN
        _stp = '1.3.6.1.2.1.17.2.15.1'
        _stp_port = f'{_stp}.1'
        _stp_priority = f'{_stp}.2'
        _stp_state = f'{_stp}.3'
        """
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
            status = bridge_status_map.get(int(status_num))
            ifidx = ifindex_table.search(
                f"{_bridge_if}.{portnum}",
                return_type='val',
            )
            if ifidx:
                port = self.get_ifname_index(int(ifidx[0]), normalize=True)
            else:
                arp_row = self.get_arp_entry('mac', mac)
                if arp_row:
                    port = arp_row.interface
                else:
                    int_item = self.get_interface_entry('mac', mac)
                    if int_item:
                        port = int_item.name
                    else:
                        port = 'NotLearned'
            entry = MACData(vlan, mac, port, status)
            macs.append(entry)
        return macs

    def get_cam(self) -> DataTable:
        """ MAC address table from this node
        """
        mac_table = []
        # Grab CAM table for each VLAN
        for vlan in self.vlans:
            macs = self.get_macs_for_vlan(vlan.vid)
            if macs:
                mac_table.extend(macs)
        self.mac_table = DataTable(mac_table)

    def get_mac_entry(self, key: str, value: str) -> Optional[MACData]:
        if not self.mac_table:
            self.get_cam()
        if value in self.mac_table.column(key):
            return self.mac_table.get_item(key, value, no_list=True)

    def get_link(self, ifidx: int, link: LinkData=None, details: bool=True) -> LinkData:
        if not link:
            link = LinkData()
            link.discovered_proto = 'Unknown'
        link.local_node = self._id
        # Check local interfaces for index
        interface = self.get_interface_entry('idx', ifidx)
        if interface:
            link.interface = interface
            if not link.local_port:
                link.local_port = interface.name
            if not link.local_if_ip and interface.ip:
                link.local_if_ip = interface.ip
            if not link.link_type and interface.port_type:
                link.link_type = interface.port_type
                if link.link_type == 'trunk':
                    link.local_native_vlan = interface.port_native_vlan
                    link.local_allowed_vlans = interface.port_allowed_vlans
                elif link.link_type == 'access':
                    link.local_vlan = interface.port_vlan
                    link.local_vlan_mem = interface.port_vlan_mem
                    link.local_vlan_status = interface.port_vlan_status
        else:
            local_port = self.lookup_ifname_index(ifidx, normalize=True)
            if local_port:
                link.local_port = local_port
        return link

    def get_cdp(self) -> List[LinkData]:
        """ Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
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
            idx1 = get_oid_index(oid, 14)
            idx2 = get_oid_index(oid, 15)
            idx = ".".join([str(idx1), str(idx2)])
            link = self.get_link(idx1)
            link.discovered_proto = 'cdp'
            link.remote_name = normalize_host(name, self.domains)
            index_cdp = cdp.index_table(idx)
            # get remote IP
            rip = index_cdp.get(f"{_cdp_ipaddr}.{idx}")
            link.remote_ip = ip_2_str(rip)
            # Lookup MAC with IP from arp_table
            if not link.remote_mac and link.remote_ip:
                arp_entry = self.get_arp_entry('ip', link.remote_ip)
                if arp_entry:
                    link.remote_mac = arp_entry.mac
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
            idx1 = get_oid_index(oid, -2)
            idx2 = get_oid_index(oid, -1)
            idx = ".".join(oid.split('.')[-2:])
            link = LinkData()
            link.discovered_proto = 'lldp'
            link.remote_name = normalize_host(name, self.domains)
            lldp_port = lldp.table.get(f"{_lldp_port_name}.{idx1}")
            link.local_port = normalize_port(lldp_port)
            link = self.get_link(idx1, link)
            rip_oid = f"{_lldp_devaddr}.{idx}"
            link.remote_ip = self.get_cidr_from_oid(rip_oid)
            devid = lldp.table.get(f"{_lldp_devid}.{idx}")
            link.remote_mac = mac_hex_to_ascii(devid)
            # Lookup MAC with IP from arp_table
            if not link.remote_mac and link.remote_ip:
                arp_entry = self.get_arp_entry('ip', link.remote_ip)
                if arp_entry:
                    link.remote_mac = arp_entry.mac
            rport = lldp.table.get(f"{_lldp_devport}.{idx}")
            link.remote_port = normalize_port(rport)
            link.remote_port_desc = lldp.table.get(f"{_lldp_devpdsc}.{idx}")
            rios_bytes = lldp.table.get(f"{_lldp_remote_descr}.{idx}")
            link = self._link_ios(rios_bytes, link)
            neighbors.append(link)
        return neighbors

    def create_links(self) -> DataTable:
        """ Combine CDP and LLDP to create links

        Using the following method:
            1. Gather CDP and LLDP links.
            2. Iterate though CDP and LLDP.
            3. If a match is found 'is_same_link'.
            4. Remove the CDP entry.
            5. From the CDP entry 'injest' the LLDP entry.
            6. Add this new CDP/LLDP entry back to the list.
            4. Iterate through LLDP again.
            8. Add LLDP entry if local_port not in 'links'.
        """
        # Start with CDP and build
        links = self.get_cdp()
        # LLDP links
        lldp_links = self.get_lldp()
        for cdp in links:
            for lldp in lldp_links:
                if cdp.is_same_link(lldp):
                    # Remove CDP
                    links.remove(cdp)
                    # From cdp injest lldp
                    cdp.injest_link(lldp)
                    # Add the combined cdp/lldp back
                    links.append(cdp)
        # Iterate again to add LLDP links not in CDP
        for lldp in lldp_links:
            if lldp.local_port not in [l.local_port for l in links]:
                links.append(lldp)
        self.links = DataTable(links)

