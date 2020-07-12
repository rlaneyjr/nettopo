# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        stack.py
'''
from .cache import StackCache
from .constants import OID
from .data import BaseData, NodeActions, StackData
from .util import lookup_table


class Stack(BaseData):
    """ Holds switch stack info and details
    Performs all duties upon initialization
    """
    def __init__(self, snmp, actions=None):
        self.members = []
        self.count = 0
        self.enabled = False
        self.actions = actions or NodeActions()
        self.items_2_show = ['enabled', 'count', 'members']
        self.cache = StackCache(snmp)
        if self.actions.get_stack_details:
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
            for n, v in row:
                n = str(n)
                if n.startswith(f"{OID.STACK_NUM}."):
                    # Get info on this stack member and add to the list
                    m = StackData()
                    t = n.split('.')
                    idx = t[14]
                    m.num = v
                    m.role = lookup_table(stack_cache,
                                          f"{OID.STACK_ROLE}.{idx}")
                    m.role = get_role(m)
                    m.pri = lookup_table(stack_cache,
                                         f"{OID.STACK_PRI}.{idx}")
                    m.img = lookup_table(stack_cache,
                                         f"{OID.STACK_IMG}.{idx}")
                    if serial_cache:
                        m.serial = lookup_table(serial_cache,
                                            f"{OID.ENTPHYENTRY_SERIAL}.{idx}")
                    if platform_cache:
                        m.plat = lookup_table(platform_cache,
                                              f"{OID.ENTPHYENTRY_PLAT}.{idx}")
                    m.mac = lookup_table(stack_cache,
                                         f"{OID.STACK_MAC}.{idx}")
                    mac_seg = [m.mac[x:x+4] for x in range(2, len(m.mac), 4)]
                    m.mac = '.'.join(mac_seg)
                    self.members.append(m)
        self.count = len(self.members)
        if self.count > 1:
            self.enabled = True
        else:
            self.enabled = False
            self.count = 0
