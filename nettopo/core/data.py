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
    'LinkData',
    'SVIData',
    'LoopBackData',
    'VLANData',
    'ARPData',
]


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

class BaseData:
    def _as_dict(self):
        IGN_DEFS = ['show']
        _dict = {}
        for item in self.__dir__():
            if not item.startswith('_') or item not in IGN_DEFS:
                val = self.__getattribute__(item)
                _dict.update({item: val})
        return _dict

    def __str__(self):
        d = self._as_dict()
        d = str(d).replace(':', ' =')
        d = d.lstrip('{').strip('}')
        d = d.replace(',', '\n')
        return d


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

    def show(self):
        return f"<local_port={self.local_port},remote_name={self.remote_name},remote_port={self.remote_port}>"


class SVIData(BaseData):
    def __init__(self, vlan):
        self.vlan = vlan
        self.ip = []

    def show(self):
        return f"<vlan={self.vlan},ip={self.ip}>"


class LoopBackData(BaseData):
    def __init__(self, name, ips):
        self.name = name.replace('Loopback', 'lo')
        self.ips = ips

    def show(self):
        return f"<name={self.name},ips={self.ips}>"


class VLANData(BaseData):
    def __init__(self, vid, name):
        self.id = vid
        self.name = name

    def show(self):
        return f"<vlan_id={self.id},vlan_name={self.name}>"


class ARPData(BaseData):
    def __init__(self, ip, mac, interf, arp_type):
        self.ip = ip
        self.mac = mac
        self.interf = interf
        self.arp_type = arp_type

    def show(self):
        return f"<arp_ip={self.ip},arp_mac={self.mac},arp_interf={self.interf},arp_type={self.arp_type}>"

