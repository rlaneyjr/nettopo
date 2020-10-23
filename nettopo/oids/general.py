# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              general.py
Description:        General OIDs
Author:             Ricky Laney
Version:            0.1.4

1 - ISO assigned OIDs
1.3 - ISO Identified Organization
1.3.6 - US Department of Defense
1.3.6.1 - OID assignments from 1.3.6.1 - Internet
1.3.6.1.2 - IETF Management
1.3.6.1.2.1 - SNMP MIB-2
1.3.6.1.2.1.4 - ip
1.3.6.1.2.1.4.21 - ipRouteTable
'''


class GeneralOids:
    """Statically define general oids
    """
    # From SNMPv2-MIB
    sysDescr = '1.3.6.1.2.1.1.1'
    sysObjectId = '1.3.6.1.2.1.1.2'
    sysUpTime = '1.3.6.1.2.1.1.3'
    sysContact = '1.3.6.1.2.1.1.4'
    sysName = '1.3.6.1.2.1.1.5'
    sysLocation = '1.3.6.1.2.1.1.6'
    sysORTable = '1.3.6.1.2.1.1.9'
    sysOREntry = '1.3.6.1.2.1.1.9.1'
    sysORIndex = '1.3.6.1.2.1.1.9.1.1'
    sysORID = '1.3.6.1.2.1.1.9.1.2'
    sysORDescr = '1.3.6.1.2.1.1.9.1.3'
    sysORUpTime = '1.3.6.1.2.1.1.9.1.4'
    # From IF-MIB
    ifTable = "1.3.6.1.2.1.2.2"
    ifEntry = "1.3.6.1.2.1.2.2.1"
    ifIndex = "1.3.6.1.2.1.2.2.1.1"
    ifDescr = "1.3.6.1.2.1.2.2.1.2"
    ifMtu = "1.3.6.1.2.1.2.2.1.4"
    ifSpeed = "1.3.6.1.2.1.2.2.1.5"
    ifPhysAddress = "1.3.6.1.2.1.2.2.1.6"
    ifAdminStatus = "1.3.6.1.2.1.2.2.1.7"
    ifOperStatus = "1.3.6.1.2.1.2.2.1.8"
    ifAlias = "1.3.6.1.2.1.31.1.1.1.18"
    # From IP-MIB
    ipAdEntAddr = "1.3.6.1.2.1.4.20.1.1"
    ipAdEntIfIndex = "1.3.6.1.2.1.4.20.1.2"
    ipAdEntNetMask = "1.3.6.1.2.1.4.20.1.3"
    # From HOST-RESOURCES-MIB
    hrStorageIndex = "1.3.6.1.2.1.25.2.3.1.1"
    hrStorageType = "1.3.6.1.2.1.25.2.3.1.2"
    hrStorageDescr = "1.3.6.1.2.1.25.2.3.1.3"
    hrStorageAllocationUnits = "1.3.6.1.2.1.25.2.3.1.4"
    hrStorageSize = "1.3.6.1.2.1.25.2.3.1.5"
    hrStorageUsed = "1.3.6.1.2.1.25.2.3.1.6"
    hrStorageAllocationFailures = "1.3.6.1.2.1.25.2.3.1.7"
    hrSWInstalledName = '1.3.6.1.2.1.25.6.3.1.2'
    # From ENTITY-MIB
    entPhysicalDescr = "1.3.6.1.2.1.47.1.1.1.1.2"
    entPhysicalName = "1.3.6.1.2.1.47.1.1.1.1.7"
    entPhysicalHardwareRev = "1.3.6.1.2.1.47.1.1.1.1.8"
    entPhysicalFirmwareRev = "1.3.6.1.2.1.47.1.1.1.1.9"
    entPhysicalSoftwareRev = "1.3.6.1.2.1.47.1.1.1.1.10"
    entPhysicalSerialNum = "1.3.6.1.2.1.47.1.1.1.1.11"
    entPhysicalMfgName = "1.3.6.1.2.1.47.1.1.1.1.12"
    entPhysicalModelName = "1.3.6.1.2.1.47.1.1.1.1.13"


class Oids:
    """ Oids defined for core classes
    """
    SNMP_MIB_2: str = '1.3.6.1.2.1'
    IP: str = '1.3.6.1.2.1.4'
    # ipRouteTable (.1.3.6.1.2.1.4.21) from the RFC1213-MIB
    IP_ROUTE_TABLE: str = '1.3.6.1.2.1.4.21'
    SYSNAME: str = '1.3.6.1.2.1.1.5.0'
    SYSDESC: str = '1.3.6.1.2.1.1.1.0'
    SYS_SERIAL: str = '1.3.6.1.4.1.9.3.6.3.0'
    SYS_BOOT: str = '1.3.6.1.4.1.9.2.1.73.0'
    SYS_BOOT2: str = '1.3.6.1.2.1.16.19.6.0'
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
    # LLDP_TYPE: str = '1.0.8802.1.1.2.1.4.1.1.4.0'
    LLDP_TYPE: str = '1.0.8802.1.1.2.1.4.1.1.6.0'
    LLDP_DEVID: str = '1.0.8802.1.1.2.1.4.1.1.5.0'
    LLDP_DEVPORT: str = '1.0.8802.1.1.2.1.4.1.1.7.0'
    LLDP_DEVPDSC: str = '1.0.8802.1.1.2.1.4.1.1.8.0'
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
    IF_IP_NETM: str = '1.3.6.1.2.1.4.20.1.3'
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
