# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        node_vss.py
'''
from nettopo.core.cache import VSSCache
from nettopo.core.data import BaseData, NodeActions, VSSData
from nettopo.core.util import lookup_table
from nettopo.oids import Oids
o = Oids()


class VSS(BaseData):
    """ Holds VSS info and details
    Performs all duties upon initialization
    """
    def __init__(self, snmp, actions=None):
        self.domain = None
        self.members = []
        self.actions = actions or NodeActions()
        self.items_2_show = ['enabled', 'domain', 'members']
        self.cache = VSSCache(snmp)
        if self.actions.get_vss_details:
            self.get_members()


    @property
    def enabled(self):
        return True if self.cache.mode == '2' else False


    def get_members(self):
        if not self.actions.get_vss_details or not self.enabled:
            return []
        self.domain = self.cache.domain
        # pull some VSS-related info
        module_cache = self.cache.module
        ios_cache = self.cache.ios
        serial_cache = self.cache.serial
        plat_cache = self.cache.platform
        # enumerate VSS modules and find chassis info
        chassis = 0
        for row in module_cache:
            for n, v in row:
                if v == 1:
                    modidx = str(n).split('.')[14]
                    # we want only chassis - line card module have no software
                    ios = lookup_table(ios_cache,
                                       f"{o.ENTPHYENTRY_SOFTWARE}.{modidx}")
                    if ios:
                        member = VSSData()
                        if self.actions.get_ios:
                            member.ios = ios
                        if self.actions.get_plat:
                            member.plat = lookup_table(plat_cache,
                                            f"{o.ENTPHYENTRY_PLAT}.{modidx}")
                        if self.actions.get_serial:
                            member.serial = lookup_table(serial_cache,
                                        f"{o.ENTPHYENTRY_SERIAL}.{modidx}")
                        self.members.append(member)
                        chassis += 1
            if chassis > 1:
                break
