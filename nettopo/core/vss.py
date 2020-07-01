# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        node_vss.py
'''
from .constants import OID


class VSSMember:
    def __init__(self):
        self.opts   = None
        self.ios    = None
        self.serial = None
        self.plat   = None

    def __str__(self):
        return f"<serial={self.serial},plat={self.plat}>"

    def __repr__(self):
        return self.__str__()


class VSS:
    def __init__(self, snmpobj = None, opts = None):
        self.members = []
        self.enabled = False
        self.domain = None
        self.opts = opts
        if snmpobj != None:
            self.get_members(snmpobj)

    def __str__(self):
        return f"<enabled={self.enabled},domain={self.domain},members={self.members}>"

    def __repr__(self):
        return self.__str__()

    def get_members(self, snmpobj):
        if not self.opts.get_vss_details:
            return False
        # check if VSS is enabled
        if snmpobj.get_val(OID.VSS_MODE) == '2':
            self.enabled = True
        else:
            return False
        self.domain = snmpobj.get_val(OID.VSS_DOMAIN)
        # pull some VSS-related info
        module_vbtbl = snmpobj.get_bulk(OID.VSS_MODULES)
        if self.opts.get_ios:
            ios_vbtbls = snmpobj.get_bulk(OID.ENTPHYENTRY_SOFTWARE)
        if self.opts.get_serial:
            serial_vbtbls = snmpobj.get_bulk(OID.ENTPHYENTRY_SERIAL)
        if self.opts.get_plat:
            plat_vbtbl = snmpobj.get_bulk(OID.ENTPHYENTRY_PLAT)
        # enumerate VSS modules and find chassis info
        chassis = 0
        for row in module_vbtbl:
            for n,v in row:
                if v == 1:
                    modidx = str(n).split('.')[14]
                    # we want only chassis - line card module have no software
                    ios = snmpobj.table_lookup(ios_vbtbl, OID.ENTPHYENTRY_SOFTWARE + '.' + modidx)
                    if ios != '':
                        if self.opts.get_ios:
                            self.members[chassis].ios = ios
                        if self.opts.get_plat:
                            self.members[chassis].plat = snmpobj.table_lookup(plat_vbtbl, OID.ENTPHYENTRY_PLAT + '.' + modidx)
                        if self.opts.get_serial:
                            self.members[chassis].serial = snmpobj.table_lookup(serial_vbtbl, OID.ENTPHYENTRY_SERIAL + '.' + modidx)
                        chassis += 1
                if chassis > 1:
                    return

