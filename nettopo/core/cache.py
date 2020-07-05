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
from .data import NodeActions
from .snmp import SNMP
from .stack import Stack
from .vss import VSS


class Cache:
    def __init__(self, snmp_object: SNMP, node_actions: NodeActions):
        self.snmp = snmp_object
        self.actions = node_actions

    @cached_property
    def cdp(self):


    @cached_property
    def ldp(self):


    @cached_property
    def link_type(self):
        return self.snmp.get_bulk(OID.TRUNK_VTP)


    @cached_property
    def lag(self):
        return self.snmp.get_bulk(OID.LAG_LACP)


    @cached_property
    def vlan(self):
        return self.snmp.get_bulk(OID.IF_VLAN)


    @cached_property
    def ifname(self):
        return self.snmp.get_bulk(OID.IFNAME)


    @cached_property
    def ifip(self):
        return self.snmp.get_bulk(OID.IF_IP)


    @cached_property
    def svi(self):
        return self.snmp.get_bulk(OID.SVI_VLANIF)


    @cached_property
    def ethif(self):


    @cached_property
    def trunk_allowed(self):
        return self.snmp.get_bulk(OID.TRUNK_ALLOW)


    @cached_property
    def trunk_native(self):
        return self.snmp.get_bulk(OID.TRUNK_NATIVE)


    @cached_property
    def vpc(self):


    @cached_property
    def vlandesc(self):


    @cached_property
    def arp(self):


    @cached_property
    def stack(self):
        if self.actions.get_stack:
            return Stack(self.snmp, self.actions)
        else:
            return None

    @cached_property
    def stack_details(self):
        if self.actions.get_stack_details:
            return Stack(self.snmp, self.actions)
        else:
            return None

    @cached_property
    def vss(self):
        if self.actions.get_vss:
            return VSS(self.snmp, self.actions)
        else:
            return None

    @cached_property
    def ent_class(self):
        return self.snmp.get_bulk(OID.ENTPHYENTRY_CLASS)

    @cached_property
    def serial(self):
        if self.actions.get_serial:
            return self.snmp.get_bulk(OID.ENTPHYENTRY_SERIAL)
        else:
            return None

    @cached_property
    def plat(self):
        if self.actions.get_plat:
            return self.snmp.get_bulk(OID.ENTPHYENTRY_PLAT)
        else:
            return None

    @cached_property
    def ios(self):
        if self.actions.get_ios:
            return self.snmp.get_bulk(OID.ENTPHYENTRY_SOFTWARE)
        else:
            return None

