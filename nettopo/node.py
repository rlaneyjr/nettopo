# -*- coding: utf-8 -*-

# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              node.py
Description:        Node
Author:             Ricky Laney
'''
from netaddr import IPNetwork, IPAddress
from netmiko import ConnectHandler
from typing import Any, Union, Dict, List
# My Stuff
from nettopo.utils import build_uuid

DL = Union[Dict, List]
IP = Union[IPNetwork, IPAddress]
NS = Union[IPNetwork, str]
AS = Union[IPAddress, str]


class NettopoLink:
    """ Represents a connection between two entities.
    """
    def __init__(self, local_device, local_port: str,
                 remote_device, remote_port: str) -> None:
        self.myid = build_uuid()
        self.local = local_device
        self.local_port = local_port
        self.local_ip = self.local.ip
        self.remote = remote_device
        self.remote_port = remote_port
        self.remote_ip = self.remote.ip

    @property
    def local_mac(self):
        if isinstance(self.local, NettopoHost):
            return self.local.mac
        elif isinstance(self.local, NettopoNode):
            return self.local.get_port_mac(self.local_port)


class NettopoHost:
    ''' A NettopoHost is an IPAddress and associated
    MAC address that replys to ping. End-user stations, laptops, printers, etc.
    Basically, anything NOT a network device.

    :param: ip = IPAddress of node (required)
    :param: mac = MAC address of node (required)
    :param: net_device = The NettopoNode this host is connected to
    :paraqm: port = The port on the NettopoNode this host is connected to
    :return: None
    '''
    def __init__(self, ip: AS, mac: str, net_devices=None, links=None) -> None:
        self.ip = ip
        self.mac = mac
        self.net_devices = net_devices if net_devices else self.get_net_device()
        self.links = links if links else self.get_links()

    def get_net_device(self):
        mac_trac = trace_mac(self.mac)
        return mac_trace.net_device

    def get_port(self):
        mac_trac = trace_mac(self.mac)
        return mac_trace.port


class NettopoNode:
    ''' A NettopoNode is a network device

    :param: ip = IPAddress of node (required)
    :return: None
    '''
    def __init__(self, ip: IP, ports: List[int]=None) -> None:
        self.ip = ip
        self.ports = ports
        self.name = name if name else str(ip)
        self.neighbors = []
        self.upstream = []
        self.downstream = []
        self.is_edge = False
        self.links = []
        self.ips = [ip]
        self.device_type = None
        self.model = None
        self.man = None
        self.serial = None
        self.version = None
        self.os = None
        self.has_snmp = True if 161 in ports else False
        self.has_ssh = True if 22 in ports else False
        self.has_telnet = True if 23 in ports else False
        self.has_http = True if 80 in ports else False
        self.has_https = True if 443 in ports else False
        self.default_route = None
        self.int_table = []
        self.vlan_table = []
        self.mac_table = []
        self.arp_table = []
        self.fib_table = []
        self.rib_table = []

    def get_neighbors(self):
        if not self.neighbors:
            self.neighbors.extend(self.get_cdp_neighbors())
            self.neighbors.extend(self.get_lldp_neighbors())
        return self.neighbors

