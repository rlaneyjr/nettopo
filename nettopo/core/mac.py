# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    mac.py
'''
from .cache import MACCache
from .config import Config
from .constants import OID
from .data import BaseData, MACData
from .snmp import SNMP
from .util import normalize_host, mac_format_ascii, lookup_table, oid_last_token


class MAC(BaseData):
    def __init__(self, conf, snmp_object=None):
        self.cache = None
        self.config = conf
        self.snmp = snmp_object

    def __str__(self):
        return (f"<macs={len(self.macs)}>")

    def __repr__(self):
        return self.__str__()

    @property
    def count(self):
        if self.macs:
            return len(self.macs)
        else:
            return None

    def get_macs(self, ip):
        ''' MAC addresses from single node
        '''
        if ip == '0.0.0.0':
            return None
        if not self.snmp:
            self.snmp = SNMP(ip)
        if not self.snmp.get_creds(self.config.snmp_creds):
            return None
        self.cache = self.cache or MACCache(self.snmp)
        sysname = self.cache.sysname
        self.system_name = normalize_host(sysname, self.config.host_domains)
        # cache some common MIB trees
        vlan_cache = self.cache.vlan
        ret_macs = []
        for vlan_row in vlan_cache:
            for vlan_n, vlan_v in vlan_row:
                vlan = oid_last_token(vlan_n)
                if vlan >= 1002:
                    continue
                vmacs = self.get_macs_for_vlan(ip, vlan, self.snmp, self.system_name)
                if vmacs:
                    ret_macs.extend(vmacs)
        return ret_macs

    def get_macs_for_vlan(self, ip, vlan, snmpobj=None, system_name=None):
        ''' MAC addresses for a single VLAN
        '''
        ret_macs = []
        if not snmpobj:
            if not self.snmp or self.snmp.ip != ip:
                self.snmp = SNMP(ip)
        else:
            self.snmp = snmpobj
        if not self.snmp.get_creds(self.config.snmp_creds):
            return None
        self.cache = self.cache or MACCache(self.snmp)
        if not self.system_name:
            sysname = self.cache.sysname
            self.system_name = normalize_host(sysname, self.config.host_domains)
        ifname_cache = self.cache.ifname
        # change our SNMP credentials
        old_cred = self.cache.snmp.community
        self.cache.snmp.community = f"{old_cred}@{str(vlan)}"
        # get CAM table for this VLAN
        cam_cache = self.cache.cam
        if not cam_cache:
            # error getting CAM for VLAN
            return None
        portnum_cache = self.cache.portnum
        ifindex_cache = self.cache.ifindex
        for cam_row in cam_cache:
            for cam_n, cam_v in cam_row:
                cam_entry = mac_format_ascii(cam_v, 0)
                # find the interface index
                p = cam_n.getOid()
                idx = f"{p[11]}.{p[12]}.{p[13]}.{p[14]}.{p[15]}.{p[16]}"
                portnum_oid = f"{OID.BRIDGE_PORTNUMS}.{idx}"
                bridge_portnum = lookup_table(portnum_cache, portnum_oid)
                # get the interface index and description
                try:
                    ifidx = lookup_table(ifindex_cache,
                                         f"{OID.IFINDEX}.{bridge_portnum}")
                    port = lookup_table(ifname_cache, f"{OID.IFNAME}.{ifidx}")
                except TypeError:
                    port = 'None'
                mac_addr = mac_format_ascii(cam_v, 1)
                entry = MACData(system_name, ip, vlan, mac_addr, port)
                ret_macs.append(entry)
        # restore SNMP credentials
        self.cache.snmp.community = old_cred
        return ret_macs
