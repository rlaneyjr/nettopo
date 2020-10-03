# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
        stack.py
"""
from nettopo.core.cache import StackCache
from nettopo.core.data import BaseData, NodeActions, StackData
from nettopo.core.util import lookup_table
from nettopo.oids import Oids
o = Oids()


class Stack(BaseData):
    """ Holds switch stack info and details
    Performs all duties upon initialization
    """
    def __init__(self, snmp):
        self.members = []
        self.count = 0
        self.enabled = False
        self.items_2_show = ['enabled', 'count', 'members']
        self.cache = StackCache(snmp)
        self.get_members()


    @staticmethod
    def get_role(member):
        roles = ['master', 'member', 'notMember', 'standby']
        for role in enumerate(roles, start=1):
            if member.role == role[0]:
                return role[1]


    def get_members(self):
        stack_cache = self.cache.stack
        if not stack_cache:
            return None
        if self.actions.get_serial:
            serial_cache = self.cache.serial
        if self.actions.get_plat:
            platform_cache = self.cache.platform
        for row in stack_cache:
            for k, v in row:
                k = str(k)
                if k.startswith(f"{o.STACK_NUM}."):
                    idx = k.split('.')[14]
                    # Get info on this stack member and add to the list
                    m = StackData()
                    m.num = v
                    m.role = lookup_table(stack_cache,
                                          f"{o.STACK_ROLE}.{idx}")
                    m.role = self.get_role(m)
                    m.pri = lookup_table(stack_cache,
                                         f"{o.STACK_PRI}.{idx}")
                    m.img = lookup_table(stack_cache,
                                         f"{o.STACK_IMG}.{idx}")
                    if serial_cache:
                        m.serial = lookup_table(serial_cache,
                                            f"{o.ENTPHYENTRY_SERIAL}.{idx}")
                    if platform_cache:
                        m.plat = lookup_table(platform_cache,
                                              f"{o.ENTPHYENTRY_PLAT}.{idx}")
                    m.mac = lookup_table(stack_cache,
                                         f"{o.STACK_MAC}.{idx}")
                    mac_seg = [m.mac[x:x+4] for x in range(2, len(m.mac), 4)]
                    m.mac = '.'.join(mac_seg)
                    if m.role:
                        self.members.append(m)
        self.count = len(self.members)
        if self.count > 1:
            self.enabled = True
        else:
            self.enabled = False
            self.count = 0
