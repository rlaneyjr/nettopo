# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              node.py
Description:        Node
Author:             Ricky Laney
'''
from netmiko
from typing import Union, Dict, List

DL = Union[Dict, List]
IP = Union[IPNetwork, IPAddress]
NS = Union[IPNetwork, str]
AS = Union[IPAddress, str]


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
    def __init__(self, ip: AS, mac: str, net_device: NettopoNode=None, port=None) -> None:
    self.ip = ip
    self.mac = mac
    self.net_device = net_device if net_device else self.get_net_device()
    self.port = port if port else self.get_port()

    def get_net_device(self):
        mac_trac = trace_mac(self.mac)
        return mac_trace.net_device

    def get_port(self):
        mac_trac = trace_mac(self.mac)
        return mac_trace.port


class NettopoNode:
    ''' A NettopoNode is an network device that we have at least one of the
    following ports open: 22,23,161

    :param: ip = IPAddress of node (required)
    :param: ports = list of open ports (required)
    :return: None
    '''
    def __init__(self, ip: IP, ports: List[int]) -> None:
        self.mgmt_ip = ip
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

