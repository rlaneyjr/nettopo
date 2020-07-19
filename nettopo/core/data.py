# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              data.py
Description:        data.py
Author:             Ricky Laney
Version:            0.1.1
'''
from typing import Any, List
from .util import is_valid_attr

__all__ = [
    'BaseData',
    'NodeActions',
    'LinkData',
    'StackData',
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
        _dict = {}
        for attr in self.__dir__():
            if is_valid_attr(attr):
                val = self.__getattribute__(attr)
                _dict.update({attr: val})
        return _dict

    @property
    def show(self):
        return self.show

    @show.setter
    def show(self) -> str:
        attrs = [f"{key}={val}" for key, val in self._as_dict().items()]
        attrs = ",".join(attrs)
        self.show = f"<{attrs}>"

    def __str__(self) -> str:
        attrs = self.show.lstrip('<').rstrip('>').replace('=', ' = ')
        return attrs.replace(',', '\n')

    def __repr__(self):
        return self.show


class NodeActions(BaseData):
    def __init__(self, init: bool=True):
        self.get_name = init
        self.get_ip = init
        self.get_plat = init
        self.get_ios = init
        self.get_router = init
        self.get_ospf_id = init
        self.get_bgp_las = init
        self.get_hsrp_pri = init
        self.get_hsrp_vip = init
        self.get_serial = init
        self.get_stack = init
        self.get_stack_details = init
        self.get_vss = init
        self.get_vss_details = init
        self.get_svi = init
        self.get_lo = init
        self.get_bootf = init
        self.get_chassis_info = init
        self.get_vpc = init


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


class VSSData(BaseData):
    def __init__(self):
        self.ios = None
        self.serial = None
        self.plat = None


class StackData(BaseData):
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
        self.ip = []


class LoopBackData(BaseData):
    def __init__(self, name, ips):
        self.name = name
        self.ips = ips


class VLANData(BaseData):
    def __init__(self, vid, name):
        self.vid = int(vid)
        self.name = name


class ARPData(BaseData):
    def __init__(self, ip, mac, interf, arp_type):
        self.ip = ip
        self.mac = mac
        self.interf = interf
        self.arp_type = arp_type


class MACData(BaseData):
    def __init__(self, host, ip, vlan, mac, port):
        self.host = host
        self.ip = ip
        self.vlan = int(vlan)
        self.mac = mac
        self.port = port
