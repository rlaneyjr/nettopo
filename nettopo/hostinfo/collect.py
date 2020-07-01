#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    collect.py
'''
from nettopo.hostinfo.version import DeviceVersion, version_map
from nettopo.vendors.synology.versions import SynologyVersion
from nettopo.vendors.synology.oids import SynologyOids


def get_device_version(**kwargs):
    vendor = None
    for key in kwargs.keys():
        if key == 'vendor':
            vendor = kwargs.get(key)
    if vendor in version_map.keys():
        return version_map.get(vendor)(**kwargs)
    elif vendor == 'net-snmp':
        if 'snmp' in kwargs.keys():
            if get_netsnmp_device_vendor(kwargs.get('snmp')) == 'synology':
                kwargs['vendor'] = 'synology'
                return SynologyVersion(**kwargs)
    return DeviceVersion(**kwargs)

def get_netsnmp_device_vendor(snmp):
    s = SynologyOids()
    vartable = snmp.getnext(s.systemStatus)
    for varbind in vartable:
        for oid, value in varbind:
            if s.systemStatus in oid:
                return 'synology'
    return None

