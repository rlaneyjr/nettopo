# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        node_vss.py
'''
from .cache import VSSCache
from .constants import OID
from .data import BaseData, NodeActions, VSSData
from .util import lookup_table


class VSS(BaseData):
    def __init__(self, snmpobj, actions: NodeActions=None):
        self.members = []
        self.domain = None
        self.actions = actions or NodeActions()
        self.items_2_show = ['enabled', 'domain', 'members']
        if snmpobj.cache.vss:
            self.cache = snmpobj.cache.vss
        else:
            self.cache = VSSCache(snmpobj)

        if self.actions.get_stack_details:
            self.get_members()

    @property
    def enabled(self):
        # check if VSS is enabled
        if self.cache.vss_mode == '2':
            return True
        else:
            return False

    def get_members(self):
        self.domain = snmpobj.get_val(OID.VSS_DOMAIN)
        # pull some VSS-related info
        module_cache = snmpobj.get_bulk(OID.VSS_MODULES)
        if self.actions.get_ios:
            ios_cache = snmpobj.get_bulk(OID.ENTPHYENTRY_SOFTWARE)
        if self.actions.get_serial:
            serial_cache = snmpobj.get_bulk(OID.ENTPHYENTRY_SERIAL)
        if self.actions.get_plat:
            plat_cache = snmpobj.get_bulk(OID.ENTPHYENTRY_PLAT)
        # enumerate VSS modules and find chassis info
        chassis = 0
        for row in module_cache:
            for n,v in row:
                if v == 1:
                    modidx = str(n).split('.')[14]
                    # we want only chassis - line card module have no software
                    ios = snmpobj.table_lookup(ios_cache, f"{OID.ENTPHYENTRY_SOFTWARE}.{modidx}")
                    if ios != '':
                        if self.actions.get_ios:
                            self.members[chassis].ios = ios
                        if self.actions.get_plat:
                            self.members[chassis].plat = snmpobj.table_lookup(plat_cache, f"{OID.ENTPHYENTRY_PLAT}.{modidx}")
                        if self.actions.get_serial:
                            self.members[chassis].serial = snmpobj.table_lookup(serial_cache, f"{OID.ENTPHYENTRY_SERIAL}.{modidx}")
                        chassis += 1
                if chassis > 1:
                    return

