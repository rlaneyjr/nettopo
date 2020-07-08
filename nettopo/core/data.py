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
    def __repr__(self):
        return self.show

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
    get_name = True
    get_ip = True
    get_plat = True
    get_ios = True
    get_router = True
    get_ospf_id = True
    get_bgp_las = True
    get_hsrp_pri = True
    get_hsrp_vip = True
    get_serial = True
    get_stack = True
    get_stack_details = True
    get_vss = True
    get_vss_details = True
    get_svi = True
    get_lo = True
    get_bootf = True
    get_chassis_info = True
    get_vpc = True


@dataclass
class LinkData(BaseData):
    '''
    Generic link to another node.
    '''
    node = None
    link_type = None
    remote_ip = None
    remote_name = None
    vlan = None
    local_native_vlan = None
    local_allowed_vlans = None
    remote_native_vlan = None
    remote_allowed_vlans = None
    local_port = None
    remote_port = None
    local_lag = None
    remote_lag = None
    local_lag_ips = None
    remote_lag_ips = None
    local_if_ip = None
    remote_if_ip = None
    remote_platform = None
    remote_ios = None
    remote_mac = None
    discovered_proto = None
    items_2_show = ['local_port', 'remote_name', 'remote_port']


@dataclass
class VSSData(BaseData):
    opts = None
    ios = None
    serial = None
    plat = None


@dataclass
class StackData(BaseData):
    opts = None
    num = 0
    role = 0
    pri = 0
    mac = None
    img = None
    serial = None
    plat = None
    items_2_show = ['num', 'role', 'serial']


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
