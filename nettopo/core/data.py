# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              data.py
Description:        data.py
Author:             Ricky Laney
Version:            0.1.1
'''
from dataclasses import dataclass
from typing import Any, List

__all__ = [
    'BaseData',
    'NodeActions',
    'LinkData',
    'StackData',
    'SVIData',
    'LoopBackData',
    'VLANData',
    'ARPData',
]


class BaseData:
    def _as_dict(self):
        IGN_DEFS = ['show']
        _dict = {}
        for item in self.__dir__():
            if not item.startswith('_') and item not in IGN_DEFS:
                val = self.__getattribute__(item)
                _dict.update({item: val})
        return _dict

    def __str__(self):
        attrs = [f"{key.capitalize()} = {val}" for key, val in \
                                        self._as_dict().items()]
        return "\n".join(attrs)

    @property
    def show(self) -> str:
        try:
            attrs = [f"{key}={val}" for key, val in self._as_dict().items() \
                                                if key in self.items_2_show]
        except AttributeError:
            attrs = [f"{key}={val}" for key, val in self._as_dict().items()]
        attrs = ",".join(attrs)
        return f"<{attrs}>"


@dataclass
class NodeActions(BaseData):
    get_name: bool = True
    get_ip: bool = True
    get_plat: bool = True
    get_ios: bool = True
    get_router: bool = True
    get_ospf_id: bool = True
    get_bgp_las: bool = True
    get_hsrp_pri: bool = True
    get_hsrp_vip: bool = True
    get_serial: bool = True
    get_stack: bool = True
    get_stack_details: bool = True
    get_vss: bool = True
    get_vss_details: bool = True
    get_svi: bool = True
    get_lo: bool = True
    get_bootf: bool = True
    get_chassis_info: bool = True
    get_vpc: bool = True


@dataclass
class LinkData(BaseData):
    '''
    Generic link to another node.
    '''
    node: Any = None
    link_type: Any = None
    remote_ip: Any = None
    remote_name: Any = None
    vlan: Any = None
    local_native_vlan: Any = None
    local_allowed_vlans: Any = None
    remote_native_vlan: Any = None
    remote_allowed_vlans: Any = None
    local_port: Any = None
    remote_port: Any = None
    local_lag: Any = None
    remote_lag: Any = None
    local_lag_ips: Any = None
    remote_lag_ips: Any = None
    local_if_ip: Any = None
    remote_if_ip: Any = None
    remote_platform: Any = None
    remote_ios: Any = None
    remote_mac: Any = None
    discovered_proto: Any = None
    items_2_show: List = ['local_port', 'remote_name', 'remote_port']


@dataclass
class VSSData(BaseData):
    opts: Any = None
    ios: Any = None
    serial: Any = None
    plat: Any = None


@dataclass
class StackData(BaseData):
    opts: Any = None
    num: int = 0
    role: int = 0
    pri: int = 0
    mac: Any = None
    img: Any = None
    serial: Any = None
    plat: Any = None
    items_2_show: List = ['num', 'role', 'serial']


class SVIData(BaseData):
    def __init__(self, vlan):
        self.vlan = vlan
        self.ip = []


class LoopBackData(BaseData):
    def __init__(self, name, ips):
        self.name = name.replace('Loopback', 'lo')
        self.ips = ips


class VLANData(BaseData):
    def __init__(self, vid, name):
        self.vid = vid
        self.name = name


class ARPData(BaseData):
    def __init__(self, ip, mac, interf, arp_type):
        self.ip = ip
        self.mac = mac
        self.interf = interf
        self.arp_type = arp_type
