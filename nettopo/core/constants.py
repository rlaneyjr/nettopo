# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
nettopo.py
'''
from dataclasses import dataclass

__all__ = [
    'NOTHING',
    'RETCODE',
    'OID',
    'ENTPHYCLASS',
    'ARP',
    'DCODE',
    'NODE',
]

NOTHING = [None, '0.0.0.0', 'UNKNOWN', '']

@dataclass
class RETCODE:
    # module return codes
    OK: int = 0
    ERR: int = 1
    SYNTAXERR: int = 2


@dataclass
class NODE:
    KNOWN: int = 0
    NEW: int = 1
    NEWIP: int = 2


@dataclass
class ARP:
    # ARP TYPES
    OTHER: int = 1
    INVALID: int = 2
    DYNAMIC: int = 3
    STATIC: int = 4


@dataclass
class ENTPHYCLASS:
    # OID_ENTPHYENTRY_CLASS values
    OTHER: int = 1
    UNKNOWN: int = 2
    CHASSIS: int = 3
    BACKPLANE: int = 4
    CONTAINER: int = 5
    POWERSUPPLY: int = 6
    FAN: int = 7
    SENSOR: int = 8
    MODULE: int = 9
    PORT: int = 10
    STACK: int = 11
    PDU: int = 12


@dataclass
class DCODE:
    ROOT: int = 0x01
    ERR_SNMP: int = 0x02
    DISCOVERED: int = 0x04
    STEP_INTO: int = 0x08
    CDP: int = 0x10
    LLDP: int = 0x20
    INCLUDE: int = 0x40
    LEAF: int = 0x80
    ROOT_STR: str = '[root]'
    ERR_SNMP_STR: str = '!'
    DISCOVERED_STR: str = '+'
    STEP_INTO_STR: str = '>'
    CDP_STR: str = '[cdp]'
    LLDP_STR: str = '[lldp]'
    INCLUDE_STR: str = 'i'
    LEAF_STR: str = 'L'


@dataclass
class OID:
    SYSNAME: str = '1.3.6.1.2.1.1.5.0'
    SYS_SERIAL: str = '1.3.6.1.4.1.9.3.6.3.0'
    SYS_BOOT: str = '1.3.6.1.4.1.9.2.1.73.0'
    # IFNAME + ifidx (BULK)
    IFNAME: str = '1.3.6.1.2.1.31.1.1.1.1'
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
    LLDP: str = '1.0.8802.1.1.2.1.4'
    LLDP_TYPE: str = '1.0.8802.1.1.2.1.4.1.1.4.0'
    LLDP_DEVID: str = '1.0.8802.1.1.2.1.4.1.1.5.0'
    LLDP_DEVPORT: str = '1.0.8802.1.1.2.1.4.1.1.7.0'
    LLDP_DEVNAME: str = '1.0.8802.1.1.2.1.4.1.1.9.0'
    LLDP_DEVDESC: str = '1.0.8802.1.1.2.1.4.1.1.10.0'
    LLDP_DEVADDR: str = '1.0.8802.1.1.2.1.4.2.1.5.0'
    # TRUNK_ALLOW + ifidx (Allowed VLANs)
    TRUNK_ALLOW: str = '1.3.6.1.4.1.9.9.46.1.6.1.1.4'
    # TRUNK_NATIVE + ifidx (Native VLAN)
    TRUNK_NATIVE: str = '1.3.6.1.4.1.9.9.46.1.6.1.1.5'
    # TRUNK_VTP + ifidx (VTP Status)
    TRUNK_VTP: str = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'
    # LAG_LACP + ifidx (BULK)
    LAG_LACP: str = '1.2.840.10006.300.43.1.2.1.1.12'
    IP_ROUTING: str = '1.3.6.1.2.1.4.1.0'
    # IF_VLAN + ifidx (BULK)
    IF_VLAN: str = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
    # IF_IP (BULK)
    IF_IP: str = '1.3.6.1.2.1.4.20.1'
    # IF_IP_ADDR + a.b.c.d = ifid
    IF_IP_ADDR: str = '1.3.6.1.2.1.4.20.1.2'
    # IF_IP_NETM + a.b.c.d
    IF_IP_NETM: str = '1.3.6.1.2.1.4.20.1.3.'
    # SVI_VLANIF cviRoutedVlanIfIndex
    SVI_VLANIF: str = '1.3.6.1.4.1.9.9.128.1.1.1.1.3'
    # ETH_IF ifEntry
    ETH_IF: str = '1.3.6.1.2.1.2.2.1'
    # ETH_IF_TYPE ifEntry.ifType 24=loopback
    ETH_IF_TYPE: str = '1.3.6.1.2.1.2.2.1.3'
    # ETH_IF_DESC ifEntry.ifDescr
    ETH_IF_DESC: str = '1.3.6.1.2.1.2.2.1.2'
    OSPF: str = '1.3.6.1.2.1.14.1.2.0'
    OSPF_ID: str = '1.3.6.1.2.1.14.1.1.0'
    BGP_LAS: str = '1.3.6.1.2.1.15.2.0'
    HSRP_PRI: str = '1.3.6.1.4.1.9.9.106.1.2.1.1.3.1.10'
    HSRP_VIP: str = '1.3.6.1.4.1.9.9.106.1.2.1.1.11.1.10'
    STACK: str = '1.3.6.1.4.1.9.9.500'
    STACK_NUM: str = '1.3.6.1.4.1.9.9.500.1.2.1.1.1'
    STACK_ROLE: str = '1.3.6.1.4.1.9.9.500.1.2.1.1.3'
    STACK_PRI: str = '1.3.6.1.4.1.9.9.500.1.2.1.1.4'
    STACK_MAC: str = '1.3.6.1.4.1.9.9.500.1.2.1.1.7'
    STACK_IMG: str = '1.3.6.1.4.1.9.9.500.1.2.1.1.8'
    # VSS_MODULES .modidx = 1
    VSS_MODULES: str = '1.3.6.1.4.1.9.9.388.1.4.1.1.1'
    VSS_MODE: str = '1.3.6.1.4.1.9.9.388.1.1.4.0'
    VSS_DOMAIN: str = '1.3.6.1.4.1.9.9.388.1.1.1.0'
    # ENTPHYENTRY_CLASS + .modifx (3=chassis) (9=module)
    ENTPHYENTRY_CLASS: str = '1.3.6.1.2.1.47.1.1.1.1.5'
    # ENTPHYENTRY_SOFTWARE + .modidx
    ENTPHYENTRY_SOFTWARE: str = '1.3.6.1.2.1.47.1.1.1.1.9'
    # ENTPHYENTRY_SERIAL + .modidx
    ENTPHYENTRY_SERIAL: str = '1.3.6.1.2.1.47.1.1.1.1.11'
    # ENTPHYENTRY_PLAT + .modidx
    ENTPHYENTRY_PLAT: str = '1.3.6.1.2.1.47.1.1.1.1.13'
    VPC_PEERLINK_IF: str = '1.3.6.1.4.1.9.9.807.1.4.1.1.2'
    VLANS: str = '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
    VLAN_DESC: str = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
    VLAN_CAM: str = '1.3.6.1.2.1.17.4.3.1.1'
    BRIDGE_PORTNUMS: str = '1.3.6.1.2.1.17.4.3.1.2'
    IFINDEX: str = '1.3.6.1.2.1.17.1.4.1.2'
    ARP: str = '1.3.6.1.2.1.4.22.1'
    ARP_VLAN: str = '1.3.6.1.2.1.4.22.1.1'
    ARP_MAC: str = '1.3.6.1.2.1.4.22.1.2'
    ARP_IP: str = '1.3.6.1.2.1.4.22.1.3'
    ARP_TYPE: str = '1.3.6.1.2.1.4.22.1.4'
    ERR: str = 'No Such Object currently exists at this OID'
    ERR_INST: str = 'No Such Instance currently exists at this OID'
