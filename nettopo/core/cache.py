# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              cache.py
Description:        cache.py
Author:             Ricky Laney
Version:            0.1.1
'''
from functools import cached_property
from typing import Union, Any
from nettopo.core.constants import ARP, DCODE, NODE
from nettopo.core.exceptions import NettopoCacheError, NettopoSNMPError
from nettopo.core.snmp import SNMP, SnmpHandler
from nettopo.oids import Oids

o = Oids()


class Cache:
    ''' Class that stores our SNMP calls

    :param:SNMP: Initialized SNMP object (required)
    :return: None
    '''
    def __init__(self, snmp_object: Union[SNMP, SnmpHandler]) -> None:
        self.snmp = snmp_object
        if not self.snmp.success:
            raise NettopoCacheError(f"ERROR: SNMP object {self.snmp.ip} creds")


    def _value(self, oid: str) -> Any:
        results = self.snmp.get_val(oid)
        return results


    def _bulk(self, oid: str) -> Any:
        results = self.snmp.get_bulk(oid)
        return results


    def vlan_prop(self, vlan: Union[str, int], prop: str) -> None:
        if prop not in dir(self):
            raise NettopoCacheError(f"ERROR: {prop} invalid property")
        if not hasattr(self, "_props_for_vlan"):
            self._props_for_vlan = []
        old_community = self.snmp.community
        # Change community
        community = f"{old_community}@{str(vlan)}"
        self.snmp.community = community
        if not self.snmp.check_community(community):
            raise NettopoSNMPError(f"ERROR: {community} failed {self.snmp.ip}")
        results = getattr(self, prop)
        self._props_for_vlan.append(
            {
                "vlan": str(vlan),
                "community": community,
                "prop": prop,
                "results": results,
            }
        )
        self.snmp.community = old_community
        return results


    # Physical properties
    @cached_property
    def name(self):
        return self._value(o.SYSNAME)


    @cached_property
    def descr(self):
        return self._value(o.SYSDESC)


    @cached_property
    def serial(self):
        return self._value(o.SYS_SERIAL)


    @cached_property
    def bootfile(self):
        return self._value(o.SYS_BOOT)


    @cached_property
    def ent_class(self):
        return self._bulk(o.ENTPHYENTRY_CLASS)


    @cached_property
    def ent_serial(self):
        return self._bulk(o.ENTPHYENTRY_SERIAL)


    @cached_property
    def ent_plat(self):
        return self._bulk(o.ENTPHYENTRY_PLAT)


    @cached_property
    def ent_ios(self):
        return self._bulk(o.ENTPHYENTRY_SOFTWARE)


    # Physical Interface properties
    @cached_property
    def link_type(self):
        return self._bulk(o.TRUNK_VTP)


    @cached_property
    def lag(self):
        return self._bulk(o.LAG_LACP)


    @cached_property
    def ifname(self):
        return self._bulk(o.IFNAME)


    @cached_property
    def ifip(self):
        return self._bulk(o.IF_IP)


    @cached_property
    def ethif(self):
        return self._bulk(o.ETH_IF)


    @cached_property
    def trunk_allowed(self):
        return self._bulk(o.TRUNK_ALLOW)


    @cached_property
    def trunk_native(self):
        return self._bulk(o.TRUNK_NATIVE)


    @cached_property
    def portnums(self):
        return self._bulk(o.BRIDGE_PORTNUMS)


    @cached_property
    def ifindex(self):
        return self._bulk(o.IFINDEX)


    # Virtual Interface properties
    @cached_property
    def vlan(self):
        return self._bulk(o.VLANS)


    @cached_property
    def vlandesc(self):
        return self._bulk(o.VLAN_DESC)


    @cached_property
    def svi(self):
        return self._bulk(o.SVI_VLANIF)


    # IP properties
    @cached_property
    def router(self):
        return self._value(o.IP_ROUTING)


    @cached_property
    def ospf(self):
        return self._value(o.OSPF)


    @cached_property
    def ospf_id(self):
        return self._value(o.OSPF_ID)


    @cached_property
    def bgp(self):
        return  self._value(o.BGP_LAS)


    # Multi-chassis properties
    @cached_property
    def vpc(self):
        return self._bulk(o.VPC_PEERLINK_IF)


    @cached_property
    def hsrp(self):
        return self._value(o.HSRP_PRI)


    @cached_property
    def hsrp_vip(self):
        return self._value(o.HSRP_VIP)


    @cached_property
    def stack(self):
        return self._bulk(o.STACK)


    @cached_property
    def vss_mode(self):
        return self._value(o.VSS_MODE)


    @cached_property
    def vss_domain(self):
        return self._value(o.VSS_DOMAIN)


    @cached_property
    def vss_module(self):
        return self._bulk(o.VSS_MODULES)


    # We don't cache data that changes often
    @property
    def cdp(self):
        return self._bulk(o.CDP)


    @property
    def lldp(self):
        return self._bulk(o.LLDP)


    @property
    def route(self):
        return self._bulk(o.IP_ROUTE_TABLE)


    @property
    def arp(self):
        return self._bulk(o.ARP)


    @property
    def cam(self):
        return self._bulk(o.VLAN_CAM)
