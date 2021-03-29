# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              data.py
Description:        data.py
Author:             Ricky Laney
Version:            0.1.1
'''
from typing import Any, List, NamedTuple

__all__ = [
    'BaseData',
    'RandomData',
    'DataTable',
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
    # _ignores = ['_', 'get', 'add', 'actions', 'cache', 'que', 'snmp', 'show']
    # if not any([key.startswith(x) for x in self._ignores]):
    def _as_dict(self, keys: list=None) -> dict:
        if keys:
            _dict = {}
            for key, val in self.__dict__.items():
                if key in keys:
                    _dict.update({key: val})
            return _dict
        else:
            return self.__dict__

    @property
    def show(self) -> dict:
        if hasattr(self, 'show_items'):
            return self._as_dict(self.show_items)
        else:
            return self._as_dict()

    def __str__(self) -> str:
        items = [f"{key} = {val}" for key, val in self.show.items()]
        return "\n".join(items)

    def __repr__(self):
        items = [f"{key}={val}" for key, val in self.show.items()]
        items = ",".join(items)
        return f"{self.__class__.__name__}<{items}>"


class RandomData(BaseData):
    def __init__(self, name: str, data: dict):
        self._name = name
        self._data = data
        self.make_nt()

    def make_nt(self) -> None:
        _nt_temp = {}
        for key in self._data.keys():
            _nt_temp.update({key: type(key)})
        self.NT = NamedTuple(self._name, **_nt_temp)
        self.nt = self.NT(self._data)

    def __getattr__(self, attr):
        return getattr(self.nt, attr)


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


class DataTable:
    def __init__(self, data: List[object]) -> None:
        self._data = data
        self._name = self._data[0].__class__.__name__

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return f"[DataTable]{self._name} - {len(self)} items"

    def __len__(self) -> int:
        return len(self._data)

    def columns(self, name) -> list:
        _columns = []
        for item in self._data:
            if hasattr(item, name):
                value = getattr(item, name)
                if value:
                    _columns.append(value)
        return _columns

    def rows(self, key, value) -> list:
        _rows = []
        for row in self._data:
            if hasattr(row, key):
                if getattr(row, key) == value:
                    _rows.append(row)
            else:
                raise AttributeError(f"{self._name} missing attribute {key}")
        return _rows

    def __getattr__(self, attr) -> list:
        # Only called for missing attributes
        return self.columns(attr)

    def row(self, key, value) -> object:
        return self.rows(key, value)[0]


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

    def is_same_link(self, link: LinkData) -> bool:
        # Make sure different protocols were used
        if (self.discovered_proto != link.discovered_proto) \
                and (self.local_port == link.local_port) \
                and ((self.remote_name == link.remote_name) \
                     or (self.remote_port == link.remote_port)):
            return True
        return False

    def injest_link(self, link: LinkData) -> None:
        # No need to check since it's expensive we only do once.
        #if self.is_same_link(link):
        self.discovered_proto = 'both'
        for key, val in link.__dict__.items():
            # Replace items we do not have
            if val and not getattr(self, key):
                setattr(self, key, val)


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
