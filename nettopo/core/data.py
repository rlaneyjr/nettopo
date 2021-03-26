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
    'InterfaceData',
]


class BaseData:
    """ Base Data class that all other classes inherit from
    Provides:
    :property:  show - Show the show_items
    """
    _ignores = ['_', 'get', 'add', 'actions', 'cache', 'que', 'snmp', 'show']
    def _as_dict(self) -> dict:
        _dict = {}
        for item in dir(self):
            if not any([item.startswith(x) for x in self._ignores]):
                val = getattr(self, item)
                _dict.update({item: val})
        return _dict

    @property
    def show(self) -> dict:
        _dict = {}
        if hasattr(self, 'show_items'):
            show_items = self.show_items
        else:
            show_items = self._as_dict().keys()
        for item in show_items:
            if hasattr(self, item):
                val = getattr(self, item)
            else:
                show_items.remove(item)
            _dict.update({item: val})
        return _dict

    def __str__(self) -> str:
        items = [f"{key} = {val}" for key, val in self.show.items()]
        return  "\n".join(items)

    def __repr__(self):
        items = [f"{key}={val}" for key, val in self.show.items()]
        items = ",".join(items)
        return f"<{items}>"


class InterfaceData(BaseData):
    show_items = ['name', 'cidrs', 'mac', 'oper_status']
    def __init__(self):
        self.idx = None
        self.name = None
        self.media = None
        self.mac = None
        self.cidrs = None
        self.admin_status = None
        self.oper_status = None

    @property
    def ip(self) -> str:
        if self.cidrs:
            ips = self.cidrs
            if len(ips) > 1:
                ips.sort()
            ip = ips[0]
            if '/' in ip:
                return ip.split('/')[0]
            else:
                return ip

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.idx


class LinkData(BaseData):
    show_items = ['local_port', 'remote_name', 'remote_port']
    def __init__(self) -> None:
        self.node = None
        self.discovered_proto = None
        self.link_type = None
        self.vlan = None
        self.local_interface = None
        self.local_port = None
        self.local_if_ip = None
        self.local_native_vlan = None
        self.local_allowed_vlans = None
        self.local_lag = None
        self.local_lag_ips = None
        self.remote_ip = None
        self.remote_name = None
        self.remote_port = None
        self.remote_port_desc = None
        self.remote_interface = None
        self.remote_native_vlan = None
        self.remote_allowed_vlans = None
        self.remote_lag = None
        self.remote_lag_ips = None
        self.remote_if_ip = None
        self.remote_desc = None
        self.remote_os = None
        self.remote_model = None
        self.remote_vendor = None
        self.remote_version = None
        self.remote_platform = None
        self.remote_ios = None
        self.remote_mac = None

    def add_local_interface(self, interface: InterfaceData) -> None:
        if self.local_interface:
            raise NettopoDataError(f"Local interface exists for {self}")
        self.local_interface = interface
        self.local_port = interface.name
        self.local_if_ip = interface.ip

    def add_remote_interface(self, interface: InterfaceData) -> None:
        if self.remote_interface:
            raise NettopoDataError(f"Remote interface exists for {self}")
        self.remote_interface = interface
        self.remote_port = interface.name
        self.remote_if_ip = interface.ip


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
    show_items = ['num', 'role', 'serial']
    def __init__(self):
        self.num = 0
        self.role = None
        self.pri = None
        self.mac = None
        self.img = None
        self.serial = None
        self.plat = None
        self.ios = None


class EntData(BaseData):
    def __init__(self, serial, plat, ios):
        self.serial = serial
        self.plat = plat
        self.ios = ios


class VPCData(BaseData):
    def __init__(self):
        self.domain = None
        self.ifname = None


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
    def __init__(self, vlan, mac, port):
        self.vlan = int(vlan)
        self.mac = mac
        self.port = port
