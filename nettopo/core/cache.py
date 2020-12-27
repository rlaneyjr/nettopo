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
        if self.snmp.check_community(community):
            results = getattr(self, prop)
        else:
            raise NettopoSNMPError(f"ERROR: {community} failed {self.snmp.ip}")
        prop_entry = {
            "vlan": str(vlan),
            "community": community,
            "prop": prop,
            "results": results,
        }
        for item in self._props_for_vlan:
            if item['vlan'] == prop_entry['vlan']:
                self._props_for_vlan.remove(item)
        self._props_for_vlan.append(prop_entry)
        self.snmp.community = old_community
        return results


    # Physical properties
    @property
    def name(self):
        return self._value(o.SYSNAME)


    @property
    def descr(self):
        return self._value(o.SYSDESC)


    @property
    def serial(self):
        return self._value(o.SYS_SERIAL)


    @property
    def bootfile(self):
        return self._value(o.SYS_BOOT)


    @property
    def ent_class(self):
        return self._bulk(o.ENTPHYENTRY_CLASS)


    @property
    def ent_serial(self):
        return self._bulk(o.ENTPHYENTRY_SERIAL)


    @property
    def ent_plat(self):
        return self._bulk(o.ENTPHYENTRY_PLAT)


    @property
    def ent_ios(self):
        return self._bulk(o.ENTPHYENTRY_SOFTWARE)


    # Physical Interface properties
    @property
    def link_type(self):
        return self._bulk(o.TRUNK_VTP)


    @property
    def lag(self):
        return self._bulk(o.LAG_LACP)


    @property
    def ifname(self):
        return self._bulk(o.IFNAME)


    @property
    def ifip(self):
        return self._bulk(o.IF_IP)


    @property
    def ethif(self):
        return self._bulk(o.ETH_IF)


    @property
    def trunk_allowed(self):
        return self._bulk(o.TRUNK_ALLOW)


    @property
    def trunk_native(self):
        return self._bulk(o.TRUNK_NATIVE)


    @property
    def portnums(self):
        return self._bulk(o.BRIDGE_PORTNUMS)


    @property
    def ifindex(self):
        return self._bulk(o.IFINDEX)


    # Virtual Interface properties
    @property
    def vlan(self):
        return self._bulk(o.VLANS)


    @property
    def vlandesc(self):
        return self._bulk(o.VLAN_DESC)


    @property
    def svi(self):
        return self._bulk(o.SVI_VLANIF)


    # IP properties
    @property
    def router(self):
        return self._value(o.IP_ROUTING)


    @property
    def ospf(self):
        return self._value(o.OSPF)


    @property
    def ospf_id(self):
        return self._value(o.OSPF_ID)


    @property
    def bgp(self):
        return  self._value(o.BGP_LAS)


    # Multi-chassis properties
    @property
    def vpc(self):
        return self._bulk(o.VPC_PEERLINK_IF)


    @property
    def hsrp(self):
        return self._value(o.HSRP_PRI)


    @property
    def hsrp_vip(self):
        return self._value(o.HSRP_VIP)


    @property
    def stack(self):
        return self._bulk(o.STACK)


    @property
    def vss_mode(self):
        return self._value(o.VSS_MODE)


    @property
    def vss_domain(self):
        return self._value(o.VSS_DOMAIN)


    @property
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
