# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
nettopo.py
'''
from dataclasses import dataclass

__all__ = [
    'RETCODE',
    'OID',
    'ENTPHYCLASS',
    'ARP',
    'DCODE',
    'NODE',
]


@dataclass
class RETCODE:
    # module return codes
    OK = 0
    ERR = 1
    SYNTAXERR = 2


@dataclass
class OID:
    SYSNAME = '1.3.6.1.2.1.1.5.0'
    SYS_SERIAL = '1.3.6.1.4.1.9.3.6.3.0'
    SYS_BOOT = '1.3.6.1.4.1.9.2.1.73.0'
    IFNAME = '1.3.6.1.2.1.31.1.1.1.1'                  # + ifidx (BULK)
    CDP = '1.3.6.1.4.1.9.9.23.1.2.1.1'              # (BULK)
    CDP_IPADDR = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
    CDP_IOS = '1.3.6.1.4.1.9.9.23.1.2.1.1.5'
    CDP_DEVID = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'            # + .ifidx.53
    CDP_DEVPORT = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
    CDP_DEVPLAT = '1.3.6.1.4.1.9.9.23.1.2.1.1.8'
    CDP_INT = '1.3.6.1.4.1.9.9.23.1.1.1.1.'             # 6.ifidx
    LLDP = '1.0.8802.1.1.2.1.4'
    LLDP_TYPE = '1.0.8802.1.1.2.1.4.1.1.4.0'
    LLDP_DEVID = '1.0.8802.1.1.2.1.4.1.1.5.0'
    LLDP_DEVPORT = '1.0.8802.1.1.2.1.4.1.1.7.0'
    LLDP_DEVNAME = '1.0.8802.1.1.2.1.4.1.1.9.0'
    LLDP_DEVDESC = '1.0.8802.1.1.2.1.4.1.1.10.0'
    LLDP_DEVADDR = '1.0.8802.1.1.2.1.4.2.1.5.0'
    TRUNK_ALLOW = '1.3.6.1.4.1.9.9.46.1.6.1.1.4'            # + ifidx (Allowed VLANs)
    TRUNK_NATIVE = '1.3.6.1.4.1.9.9.46.1.6.1.1.5'            # + ifidx (Native VLAN)
    TRUNK_VTP = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'           # + ifidx (VTP Status)
    LAG_LACP = '1.2.840.10006.300.43.1.2.1.1.12'         # + ifidx (BULK)
    IP_ROUTING = '1.3.6.1.2.1.4.1.0'
    IF_VLAN = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'            # + ifidx (BULK)
    IF_IP = '1.3.6.1.2.1.4.20.1'                      # (BULK)
    IF_IP_ADDR = '1.3.6.1.2.1.4.20.1.2'                    # + a.b.c.d = ifid
    IF_IP_NETM = '1.3.6.1.2.1.4.20.1.3.'                   # + a.b.c.d
    SVI_VLANIF = '1.3.6.1.4.1.9.9.128.1.1.1.1.3'           # cviRoutedVlanIfIndex
    ETH_IF = '1.3.6.1.2.1.2.2.1'                       # ifEntry
    ETH_IF_TYPE = '1.3.6.1.2.1.2.2.1.3'                     # ifEntry.ifType        24=loopback
    ETH_IF_DESC = '1.3.6.1.2.1.2.2.1.2'                     # ifEntry.ifDescr
    OSPF = '1.3.6.1.2.1.14.1.2.0'
    OSPF_ID = '1.3.6.1.2.1.14.1.1.0'
    BGP_LAS = '1.3.6.1.2.1.15.2.0'
    HSRP_PRI = '1.3.6.1.4.1.9.9.106.1.2.1.1.3.1.10'
    HSRP_VIP = '1.3.6.1.4.1.9.9.106.1.2.1.1.11.1.10'
    STACK = '1.3.6.1.4.1.9.9.500'
    STACK_NUM = '1.3.6.1.4.1.9.9.500.1.2.1.1.1'
    STACK_ROLE = '1.3.6.1.4.1.9.9.500.1.2.1.1.3'
    STACK_PRI = '1.3.6.1.4.1.9.9.500.1.2.1.1.4'
    STACK_MAC = '1.3.6.1.4.1.9.9.500.1.2.1.1.7'
    STACK_IMG = '1.3.6.1.4.1.9.9.500.1.2.1.1.8'
    VSS_MODULES = '1.3.6.1.4.1.9.9.388.1.4.1.1.1'           # .modidx = 1
    VSS_MODE = '1.3.6.1.4.1.9.9.388.1.1.4.0'
    VSS_DOMAIN = '1.3.6.1.4.1.9.9.388.1.1.1.0'
    ENTPHYENTRY_CLASS = '1.3.6.1.2.1.47.1.1.1.1.5'               # + .modifx (3=chassis) (9=module)
    ENTPHYENTRY_SOFTWARE = '1.3.6.1.2.1.47.1.1.1.1.9'               # + .modidx
    ENTPHYENTRY_SERIAL = '1.3.6.1.2.1.47.1.1.1.1.11'              # + .modidx
    ENTPHYENTRY_PLAT = '1.3.6.1.2.1.47.1.1.1.1.13'              # + .modidx
    VPC_PEERLINK_IF = '1.3.6.1.4.1.9.9.807.1.4.1.1.2'
    VLANS = '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
    VLAN_DESC = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
    VLAN_CAM = '1.3.6.1.2.1.17.4.3.1.1'
    BRIDGE_PORTNUMS = '1.3.6.1.2.1.17.4.3.1.2'
    IFINDEX = '1.3.6.1.2.1.17.1.4.1.2'
    ARP = '1.3.6.1.2.1.4.22.1'
    ARP_VLAN = '1.3.6.1.2.1.4.22.1.1'
    ARP_MAC = '1.3.6.1.2.1.4.22.1.2'
    ARP_IP = '1.3.6.1.2.1.4.22.1.3'
    ARP_TYPE = '1.3.6.1.2.1.4.22.1.4'
    ERR = 'No Such Object currently exists at this OID'
    ERR_INST = 'No Such Instance currently exists at this OID'


@dataclass
class ENTPHYCLASS:
    # OID_ENTPHYENTRY_CLASS values
    OTHER = 1
    UNKNOWN = 2
    CHASSIS = 3
    BACKPLANE = 4
    CONTAINER = 5
    POWERSUPPLY = 6
    FAN = 7
    SENSOR = 8
    MODULE = 9
    PORT = 10
    STACK = 11
    PDU = 12


@dataclass
class ARP:
    # ARP TYPES
    OTHER = 1
    INVALID = 2
    DYNAMIC = 3
    STATIC = 4


@dataclass
class DCODE:
    ROOT = 0x01
    ERR_SNMP = 0x02
    DISCOVERED = 0x04
    STEP_INTO = 0x08
    CDP = 0x10
    LLDP = 0x20
    INCLUDE = 0x40
    LEAF = 0x80
    ROOT_STR = '[root]'
    ERR_SNMP_STR = '!'
    DISCOVERED_STR = '+'
    STEP_INTO_STR = '>'
    CDP_STR = '[cdp]'
    LLDP_STR = '[lldp]'
    INCLUDE_STR = 'i'
    LEAF_STR = 'L'


@dataclass
class NODE:
    KNOWN = 0
    NEW = 1
    NEWIP = 2
