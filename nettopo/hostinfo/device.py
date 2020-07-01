#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    device.py
'''

from nettopo.hostinfo.collect import get_device_version
from nettopo.snmp.errors import NettopoSNMPError
from nettopo.oids import GeneralOids
from nettopo.snmp import SnmpHandler
from nettopo.vendors.mappings import vendor_map
o = GeneralOids()

class HostInfo:

    def __init__(self, Snmp, contact=None, description=None, location=None,
            os=None, vendor=None, sysobjectid=None):
        if not isinstance(Snmp, SnmpHandler):
            raise NettopoSNMPError('Must pass a Nettopo SnmpHandler')

        self.contact = contact
        self.location = location
        self.sysobjectid = sysobjectid
        self.description = description
        self.os = os
        self.vendor = vendor
        self.version = None
        self.uptime = None
        self._snmp = Snmp

    def _parse_data(self, data):
        for oid, value in data:
            if o.sysContact in oid:
                self.contact = value
            if o.sysDescr in oid:
                self.description = value
            if o.sysLocation in oid:
                self.location = value
            if o.sysObjectId in oid:
                self.sysobjectid = value
            if o.sysUpTime in oid:
                self.uptime = value

    def get_all(self):
        oids = [
            o.sysContact + '.0',
            o.sysDescr + '.0',
            o.sysLocation + '.0',
            o.sysObjectId + '.0',
            o.sysUpTime + '.0',
        ]
        data = self._snmp.get(*oids)
        self._parse_data(data)
        self.get_vendor()
        self.get_version()

    def get_description(self):
        data = self._snmp.get(o.sysDescr + '.0')
        self._parse_data(data)

    def get_contact(self):
        data = self._snmp.get(o.sysContact + '.0')
        self._parse_data(data)

    def get_location(self):
        data = self._snmp.get(o.sysLocation + '.0')
        self._parse_data(data)

    def get_vendor(self):
        if self.sysobjectid is None:
            self.get_sysobjectid()
        try:
            enterprise_id = self.sysobjectid.split('.')[6]
            self.vendor = vendor_map[enterprise_id]
        except:
            self.vendor = 'UNKNOWN'

    def get_version(self):
        if self.vendor is None:
            self.get_vendor()
        if self.description is None:
            self.get_description()
        version_info = get_device_version(
            sysobjectid=self.sysobjectid,
            description=self.description,
            vendor=self.vendor,
            snmp=self._snmp
        )
        if self.vendor != version_info.vendor:
            self.vendor = version_info.vendor
        self.os = version_info.os
        self.version = version_info.version

    def get_sysobjectid(self):
        data = self._snmp.get(o.sysObjectId + '.0')
        self._parse_data(data)

