# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        stack.py
'''
from .constants import OID
from .data import BaseData, StackData


class Stack:
    roles = enumerate(['master', 'member', 'notMember', 'standby'], start=1)
    def __init__(self, snmpobj, opts):
        self.members = []
        self.count = 0
        self.enabled = False
        self.opts = opts
        self.get_members(snmpobj)

    def __str__(self):
        return f"<enabled={self.enabled},count={self.count},members={self.members}>"

    def __repr__(self):
        return self.__str__()

    def get_members(self, snmpobj):
        if self.opts == None:
            return
        stack_snmp = snmpobj.get_bulk(OID.STACK)
        if stack_snmp == None:
            return None
        if self.opts.get_stack_details:
            self.count = 0
            for row in stack_snmp:
                for n, v in row:
                    n = str(n)
                    if n.startswith(OID.STACK_NUM + '.'):
                        self.count += 1
            if self.count == 1:
                self.count = 0
            return
        if self.opts.get_serial:
            serial_vbtbl = snmpobj.get_bulk(OID.ENTPHYENTRY_SERIAL)
        if self.opts.get_plat:
            platf_vbtbl = snmpobj.get_bulk(OID.ENTPHYENTRY_PLAT)
        for row in stack_snmp:
            for n, v in row:
                n = str(n)
                if n.startswith(OID.STACK_NUM + '.'):
                    # Get info on this stack member and add to the list
                    m = StackMember()
                    t = n.split('.')
                    idx = t[14]
                    m.num = v
                    m.role = snmpobj.table_lookup(stack_snmp, OID.STACK_ROLE + '.' + idx)
                    m.pri = snmpobj.table_lookup(stack_snmp, OID.STACK_PRI + '.' + idx)
                    m.mac = snmpobj.table_lookup(stack_snmp, OID.STACK_MAC + '.' + idx)
                    m.img = snmpobj.table_lookup(stack_snmp, OID.STACK_IMG + '.' + idx)
                    if self.opts.get_serial:
                        m.serial = snmpobj.table_lookup(serial_vbtbl, OID.ENTPHYENTRY_SERIAL + '.' + idx)
                    if self.opts.get_plat:
                        m.plat = snmpobj.table_lookup(platf_vbtbl, OID.ENTPHYENTRY_PLAT + '.' + idx)
                    for k, v in self.roles:
                        if m.role == k:
                            m.role = v
                    mac_seg = [m.mac[x:x+4] for x in range(2, len(m.mac), 4)]
                    m.mac = '.'.join(mac_seg)
                    self.members.append(m)
        self.count = len(self.members)
        if self.count == 1:
            self.count = 0
        if self.count > 0:
            self.enabled = 1

