# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              cache.py
Description:        cache.py
Author:             Ricky Laney
Version:            0.1.1
'''
from functools import cached_property
from nettopo.core.constants import ARP, DCODE, NODE
from nettopo.core.exceptions import NettopoCacheError
from nettopo.core.snmp import SNMP
from nettopo.oids import Oids

o = Oids()


class Cache:
    def __init__(self, snmp_object: SNMP) -> None:
        self.snmp = snmp_object
        if not self.snmp.success:
            raise NettopoCacheError(f"ERROR: SNMP object {self.snmp.ip} creds")

    # Physical properties
    @cached_property
    def name(self):
        return self.snmp.get_val(o.SYSNAME)

    @cached_property
    def desc(self):
        return self.snmp.get_val(o.SYSDESC)

    @cached_property
    def serial(self):
        return self.snmp.get_val(o.SYS_SERIAL)

    @cached_property
    def bootfile(self):
        return self.snmp.get_val(o.SYS_BOOT)

    @cached_property
    def ent_class(self):
        return self.snmp.get_bulk(o.ENTPHYENTRY_CLASS)

    @cached_property
    def ent_serial(self):
        return self.snmp.get_bulk(o.ENTPHYENTRY_SERIAL)

    @cached_property
    def ent_plat(self):
        return self.snmp.get_bulk(o.ENTPHYENTRY_PLAT)

    @cached_property
    def ent_ios(self):
        return self.snmp.get_bulk(o.ENTPHYENTRY_SOFTWARE)

    # Physical Interface properties
    @cached_property
    def link_type(self):
        return self.snmp.get_bulk(o.TRUNK_VTP)

    @cached_property
    def lag(self):
        return self.snmp.get_bulk(o.LAG_LACP)

    @cached_property
    def ifname(self):
        return self.snmp.get_bulk(o.IFNAME)

    @cached_property
    def ifip(self):
        return self.snmp.get_bulk(o.IF_IP)

    @cached_property
    def ethif(self):
        return self.snmp.get_bulk(o.ETH_IF)

    @cached_property
    def trunk_allowed(self):
        return self.snmp.get_bulk(o.TRUNK_ALLOW)

    @cached_property
    def trunk_native(self):
        return self.snmp.get_bulk(o.TRUNK_NATIVE)

    @cached_property
    def portnums(self):
        return self.snmp.get_bulk(o.BRIDGE_PORTNUMS)

    @cached_property
    def ifindex(self):
        return self.snmp.get_bulk(o.IFINDEX)

    # Virtual Interface properties
    @cached_property
    def vlan(self):
        return self.snmp.get_bulk(o.VLANS)

    @cached_property
    def vlandesc(self):
        return self.snmp.get_bulk(o.VLAN_DESC)

    @cached_property
    def svi(self):
        return self.snmp.get_bulk(o.SVI_VLANIF)

    # IP properties
    @cached_property
    def router(self):
        return self.snmp.get_val(o.IP_ROUTING)

    @cached_property
    def ospf(self):
        return self.snmp.get_val(o.OSPF)

    @cached_property
    def ospf_id(self):
        return self.snmp.get_val(o.OSPF_ID)

    @cached_property
    def bgp(self):
        return  self.snmp.get_val(o.BGP_LAS)

    # Multi-chassis properties
    @cached_property
    def vpc(self):
        return self.snmp.get_bulk(o.VPC_PEERLINK_IF)

    @cached_property
    def hsrp(self):
        return self.snmp.get_val(o.HSRP_PRI)

    @cached_property
    def hsrp_vip(self):
        return self.snmp.get_val(o.HSRP_VIP)

    @cached_property
    def stack(self):
        return self.snmp.get_bulk(o.STACK)

    @cached_property
    def vss_mode(self):
        return self.snmp.get_val(o.VSS_MODE)

    @cached_property
    def vss_domain(self):
        return self.snmp.get_val(o.VSS_DOMAIN)

    @cached_property
    def vss_module(self):
        return self.snmp.get_bulk(o.VSS_MODULES)

    # We don't cache data can change
    def cdp(self):
        return self.snmp.get_bulk(o.CDP)

    def lldp(self):
        return self.snmp.get_bulk(o.LLDP)

    def arp(self):
        return self.snmp.get_bulk(o.ARP)

    def cam(self, community: str=None):
        if community:
            old_com = self.snmp.community
            self.snmp.community = community
            cam = self.snmp.get_bulk(o.VLAN_CAM)
            self.snmp.community = old_com

