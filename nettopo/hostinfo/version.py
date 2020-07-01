# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              mappings.py
Description:        mappings.py
Author:             Ricky Laney
Version:            0.1.1
'''
from nettopo.vendors.alcatel.versions import AlcatelVersion
from nettopo.vendors.arista.versions import AristaVersion
from nettopo.vendors.cisco.versions import CiscoVersion
from nettopo.vendors.ericsson.versions import EricssonVersion
from nettopo.vendors.extreme.versions import ExtremeVersion
from nettopo.vendors.hpe.versions import HpeVersion
from nettopo.vendors.huawei.versions import HuaweiVersion
from nettopo.vendors.juniper.versions import JuniperVersion
from nettopo.vendors.metamako.versions import MetamakoVersion

__all__ = [ 'version_map', 'DeviceVersion' ]


version_map = {
    'alcatel': AlcatelVersion,
    'arista': AristaVersion,
    'cisco': CiscoVersion,
    'ericsson': EricssonVersion,
    'extreme': ExtremeVersion,
    'hpe': HpeVersion,
    'huawei': HuaweiVersion,
    'juniper': JuniperVersion,
    'metamako': MetamakoVersion,
}


class DeviceVersion:
    def __init__(self, **kwargs):
        self._sysobjectid = None
        self._description = None
        self._descriptions = []
        self.device_class = None
        self.os = None
        self.version = None
        self.vendor = None

        for key in kwargs:
            if key == 'sysobjectid':
                self._sysobjectid = kwargs[key]
            elif key == 'description':
                self._description = kwargs[key]
                self._descriptions = kwargs[key].split('\r\n')
            elif key == 'snmp':
                self._snmp = kwargs[key]
            elif key == 'vendor':
                self.vendor = kwargs[key]

        self._get_version()
        self._clean()

    def _get_version(self):
        pass

    def _clean(self):
        if self.os is None:
            self.os = 'UNKNOWN'
        if self.version is None:
            self.version = 'UNKNOWN'

