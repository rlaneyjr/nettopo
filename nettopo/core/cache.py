# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              cache.py
Description:        cache.py
Author:             Ricky Laney
Version:            0.1.1
'''
from functools import cached_property
from .constants import OID, ARP, DCODE, NODE
from .snmp import SNMP


class Cache:
    def __init__(self, snmp_object: SNMP) -> None:
        self.snmp = snmp_object

    @cached_property
    def name(self):
        return self.snmp.get_val(OID.SYSNAME)

    @cached_property
    def cdp(self):
        return self.snmp.get_bulk(OID.CDP)

    @cached_property
    def lldp(self):
        return self.snmp.get_bulk(OID.LLDP)

    @cached_property
    def link_type(self):
        return self.snmp.get_bulk(OID.TRUNK_VTP)

    @cached_property
    def lag(self):
        return self.snmp.get_bulk(OID.LAG_LACP)

    @cached_property
    def vlan(self):
        return self.snmp.get_bulk(OID.VLANS)

    @cached_property
    def vlandesc(self):
        return self.snmp.get_bulk(OID.VLAN_DESC)

    @cached_property
    def ifname(self):
        return self.snmp.get_bulk(OID.IFNAME)

    @cached_property
    def svi(self):
        return self.snmp.get_bulk(OID.SVI_VLANIF)

    @cached_property
    def ifip(self):
        return self.snmp.get_bulk(OID.IF_IP)

    @cached_property
    def ethif(self):
        return self.snmp.get_bulk(OID.ETH_IF)

    @cached_property
    def trunk_allowed(self):
        return self.snmp.get_bulk(OID.TRUNK_ALLOW)

    @cached_property
    def trunk_native(self):
        return self.snmp.get_bulk(OID.TRUNK_NATIVE)

    @cached_property
    def vpc(self):
        return self.snmp.get_bulk(OID.VPC_PEERLINK_IF)

    @cached_property
    def arp(self):
        return self.snmp.get_bulk(OID.ARP)

    @cached_property
    def stack(self):
        return StackCache(self.snmp)

    @cached_property
    def vss(self):
        return VSSCache(self.snmp)

    @cached_property
    def serial(self):
        return self.snmp.get_val(OID.SYS_SERIAL)

    @cached_property
    def bootfile(self):
        return self.snmp.get_val(OID.SYS_BOOT)

    @cached_property
    def ent_class(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_CLASS)

    @cached_property
    def ent_serial(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_SERIAL)

    @cached_property
    def ent_plat(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_PLAT)

    @cached_property
    def ent_ios(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_SOFTWARE)

    @cached_property
    def router(self):
        if self.snmp.get_val(OID.IP_ROUTING) == '1':
            return True
        else:
            return False

    @cached_property
    def ospf(self):
        if self.router:
            return self.snmp.get_val(OID.OSPF)

    @cached_property
    def ospf_id(self):
        if self.ospf:
            return self.snmp.get_val(OID.OSPF_ID)

    @cached_property
    def bgp(self):
        if self.router:
            bgp_las = self.snmp.get_val(OID.BGP_LAS)
            # 4500x reports 0 as disabled
            return bgp_las if self.bgp_las != '0' else None

    @cached_property
    def hsrp(self):
        if self.router:
            return self.snmp.get_val(OID.HSRP_PRI)

    @cached_property
    def hsrp_vip(self):
        if self.hsrp:
            return self.snmp.get_val(OID.HSRP_VIP)

    @cached_property
    def stack(self):
        return StackCache(self.snmp)

    @cached_property
    def vss(self):
        return VSSCache(self.snmp)


class StackCache:
    def __init__(self, snmp_object: SNMP) -> None:
        self.snmp = snmp_object

    @cached_property
    def stack(self):
        return self.snmp.get_bulk(OID.STACK)

    @cached_property
    def serial(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_SERIAL)

    @cached_property
    def platform(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_PLAT)


class VSSCache:
    def __init__(self, snmp_object: SNMP) -> None:
        self.snmp = snmp_object

    @cached_property
    def mode(self):
        return self.snmp.get_val(OID.VSS_MODE)

    @cached_property
    def domain(self):
        return self.snmp.get_val(OID.VSS_DOMAIN)

    @cached_property
    def module(self):
        return self.snmp.get_bulk(OID.VSS_MODULES)

    @cached_property
    def ios(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_SOFTWARE)

    @cached_property
    def serial(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_SERIAL)

    @cached_property
    def platform(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_PLAT)
