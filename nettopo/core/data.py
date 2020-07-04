# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              data.py
Description:        data.py
Author:             Ricky Laney
Version:            0.1.1
'''
from dataclasses import dataclass

__all__ = [
    'CacheData',
    'NodeActions',
    'BaseData',
    'DotNode',
    'LinkData',
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
        attrs = [f"{key.capitalize()} = {val}" for key, val in self._as_dict().items()]
        return "\n".join(attrs)

    @property
    def show(self) -> str:
        try:
            attrs = [f"{key}={val}" for key, val in self._as_dict().items() if key in self.items_2_show]
        except AttributeError:
            attrs = [f"{key}={val}" for key, val in self._as_dict().items()]
        attrs = ",".join(attrs)
        return f"<{attrs}>"


@dataclass
class CacheData:
    cdp_cache = None
    ldp_cache = None
    link_type_cache = None
    lag_cache = None
    vlan_cache = None
    ifname_cache = None
    ifip_cache = None
    svi_cache = None
    ethif_cache = None
    trk_allowed_cache = None
    trk_native_cache = None
    vpc_cache = None
    vlandesc_cache = None
    arp_cache = None


@dataclass
class NodeActions:
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
class DotNode(BaseData):
    ntype: str = 'single'
    shape: str = 'ellipse'
    style: str = 'solid'
    peripheries: int = 1
    label: str = ''
    vss_label: str = ''


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
