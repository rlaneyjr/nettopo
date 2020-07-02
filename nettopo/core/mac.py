# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        mac.py
'''
from .config import Config
from .constants import OID
from .data import BaseData
from .snmp import SNMP
from .util import normalize_host, mac_format_ascii


class HostMAC(BaseData):
    def __init__(self, host, ip, vlan, mac, port):
        self.host = host
        self.ip = ip
        self.vlan = int(vlan)
        self.mac = mac
        self.port = port


class MAC:
    def __init__(self, conf):
        self.config = conf

    def __str__(self):
        return (f"<macs={len(self.macs)}>")

    def __repr__(self):
        return self.__str__()

    def get_macs(self, ip):
        '''
        Return array of MAC addresses from single node at IP
        '''
        if ip == '0.0.0.0':
            return None
        ret_macs = []
        snmpobj = SNMP(ip)
        if not snmpobj.get_creds(self.config.snmp_creds):
            return None
        system_name = normalize_host(snmpobj.get_val(OID.SYSNAME), self.config.host_domains)
        # cache some common MIB trees
        vlan_vbtbl = snmpobj.get_bulk(OID.VLANS)
        ifname_vbtbl = snmpobj.get_bulk(OID.IFNAME)
        for vlan_row in vlan_vbtbl:
            for vlan_n, vlan_v in vlan_row:
                vlan = SNMP.get_last_oid_token(vlan_n)
                if vlan >= 1002:
                    continue
                vmacs = self.get_macs_for_vlan(ip, vlan, snmpobj, system_name, ifname_vbtbl)
                if vmacs:
                    ret_macs.extend(vmacs)
        return ret_macs

    def get_macs_for_vlan(self, ip, vlan, snmpobj=None, system_name=None, ifname_vbtbl=None):
        '''
        Return array of MAC addresses for a single VLAN from a single node at an IP
        '''
        ret_macs = []
        if not snmpobj:
            snmpobj = SNMP(ip)
            if not snmpobj.get_creds(self.config.snmp_creds):
                return None
        if not ifname_vbtbl:
            ifname_vbtbl = snmpobj.get_bulk(OID.IFNAME)
        if not system_name:
            system_name = normalize_host(snmpobj.get_val(OID.SYSNAME), self.config.host_domains)
        # change our SNMP credentials
        old_cred = snmpobj.community
        snmpobj.community = old_cred + '@' + str(vlan)
        # get CAM table for this VLAN
        cam_vbtbl = snmpobj.get_bulk(OID.VLAN_CAM)
        portnum_vbtbl = snmpobj.get_bulk(OID.BRIDGE_PORTNUMS)
        ifindex_vbtbl = snmpobj.get_bulk(OID.IFINDEX)
        if not cam_vbtbl:
            # error getting CAM for VLAN
            return None
        for cam_row in cam_vbtbl:
            for cam_n, cam_v in cam_row:
                cam_entry = mac_format_ascii(cam_v, 0)
                # find the interface index
                p = cam_n.getOid()
                portnum_oid = f"{OID.BRIDGE_PORTNUMS}.{p[11]}.{p[12]}.{p[13]}.{p[14]}.{p[15]}.{p[16]}"
                bridge_portnum = snmpobj.table_lookup(portnum_vbtbl, portnum_oid)
                # get the interface index and description
                try:
                    ifidx = snmpobj.table_lookup(ifindex_vbtbl, OID.IFINDEX + '.' + bridge_portnum)
                    port = snmpobj.table_lookup(ifname_vbtbl, OID.IFNAME + '.' + ifidx)
                except TypeError:
                    port = 'None'
                mac_addr = mac_format_ascii(cam_v, 1)
                entry = HostMAC(system_name, ip, vlan, mac_addr, port)
                ret_macs.append(entry)
        # restore SNMP credentials
        snmpobj.community = old_cred
        return ret_macs
