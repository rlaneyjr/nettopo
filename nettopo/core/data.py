# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              data.py
Description:        data.py
Author:             Ricky Laney
Version:            0.1.1
'''
from typing import Any, List

__all__ = [
    'BaseData',
    'LinkData',
    'VssData',
    'VssMemberData',
    'StackData',
    'StackMemberData',
    'SVIData',
    'LoopBackData',
    'VLANData',
    'ARPData',
    'MACData',
]


class BaseData:
    """ Base Data class that all other classes inherit from
    Provides:
    :property:  show - Show the items_2_show
    """
    def _as_dict(self) -> dict:
        _ignores = ['_', 'get', 'add', 'actions', 'cache',
                    'que', 'snmp', 'show']
        _dict = {}
        for item in dir(self):
            if not any([item.startswith(x) for x in _ignores]):
                val = self.__getattribute__(item)
                _dict.update({item: val})
        return _dict

    @property
    def show(self) -> dict:
        _dict = {}
        if hasattr(self, 'items_2_show'):
            show_items = self.items_2_show
        else:
            show_items = self._as_dict().keys()
        for item in show_items:
            try:
                val = getattr(self, item)
            except ValueError:
                val = 'Unknown'
            finally:
                _dict.update({item: val})
        return _dict

    def __str__(self) -> str:
        items = [f"{key} = {val}" for key, val in self.show.items()]
        return  "\n".join(items)

    def __repr__(self):
        items = [f"{key}={val}" for key, val in self.show.items()]
        items = ",".join(items)
        return f"<{items}>"


class LinkData(BaseData):
    def __init__(self):
        self.node = None
        self.link_type = None
        self.remote_ip = None
        self.remote_name = None
        self.vlan = None
        self.local_native_vlan = None
        self.local_allowed_vlans = None
        self.remote_native_vlan = None
        self.remote_allowed_vlans = None
        self.local_port = None
        self.remote_port = None
        self.local_lag = None
        self.remote_lag = None
        self.local_lag_ips = None
        self.remote_lag_ips = None
        self.local_if_ip = None
        self.remote_if_ip = None
        self.remote_platform = None
        self.remote_ios = None
        self.remote_mac = None
        self.discovered_proto = None
        self.items_2_show = ['local_port', 'remote_name', 'remote_port']


class VssData(BaseData):
    def __init__(self):
        self.enabled = False
        self.members = []
        self.domain = None


class VssMemberData(BaseData):
    def __init__(self):
        self.ios = None
        self.serial = None
        self.plat = None


class StackData(BaseData):
    def __init__(self):
        self.enabled = False
        self.members = []
        self.count = 0


class StackMemberData(BaseData):
    def __init__(self):
        self.num = 0
        self.role = None
        self.pri = None
        self.mac = None
        self.img = None
        self.serial = None
        self.plat = None
        self.items_2_show = ['num', 'role', 'serial']


class SVIData(BaseData):
    def __init__(self, vlan):
        self.vlan = vlan
        self.ips = None


class LoopBackData(BaseData):
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip


class VLANData(BaseData):
    def __init__(self, vid, name):
        self.vid = int(vid)
        self.name = name


class ARPData(BaseData):
    def __init__(self, ip, mac, port, arp_type):
        self.ip = ip
        self.mac = mac
        self.port = port
        self.arp_type = arp_type


class MACData(BaseData):
    def __init__(self, ip, vlan, mac, port):
        self.ip = ip
        self.vlan = int(vlan)
        self.mac = mac
        self.port = port

