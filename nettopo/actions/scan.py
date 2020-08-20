# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              scanner.py
Description:        Network ARP Scanner
Author:             Ricky Laney
'''
from netaddr import IPNetwork, IPAddress
from dataclasses import dataclass
from functools import cached_property
import netifaces
import scapy.all as scapy
import socket
from typing import Union, Dict, List

from nettopo.core.exceptions import NettopoNetworkError

N = Union[str, IPNetwork, IPAddress]

class My:
    """ Use this class to store local network details and ensure we don't
    include in other operations

    >>> socket.gethostbyaddr('10.0.22.22')
    ... ('flymon.icloudmon.local', ['22.22.0.10.in-addr.arpa'], ['10.0.22.22'])
    """
    @cached_property
    def name(self):
        try:
            return socket.gethostname()
        except:
            raise NettopoNetworkError("Unable to get My Hostname")

    @cached_property
    def ip(self):
        try:
            return socket.gethostbyname(self.name)
        except:
            raise NettopoNetworkError("Unable to get My IP")

    @cached_property
    def fqdn(self):
        try:
            return socket.getfqdn()
        except:
            raise NettopoNetworkError("Unable to get My FQDN")

    @cached_property
    def netmask(self):
        addrs = netifaces.ifaddresses(self.default_interface)
        return addrs[netifaces.AF_INET][0]['netmask']

    @cached_property
    def network(self):
        return IPNetwork(f"{self.ip}/{self.netmask}")

    @cached_property
    def gws(self):
        return netifaces.gateways()

    @cached_property
    def default_gateway(self):
        return self.gws['default'][netifaces.AF_INET][0]

    @cached_property
    def default_interface(self):
        return self.gws['default'][netifaces.AF_INET][1]


@dataclass
class Nslookup:
    ip: str
    @cached_property
    def dns(self) -> str:
        try:
            return socket.gethostbyaddr(self.ip)[0]
        except:
            return "UNKNOWN"


@dataclass
class Port:
    port: int
    @cached_property
    def name(self) -> str:
        try:
            return socket.getservbyport(self.port)
        except:
            return "UNKNOWN"


class ArpScan:
    """ Arp scan an entire network building objects from results.

    # Create a network with the IPNetwork object:
    >>> net = IPNetwork('10.0.22.0/24')

    # Create an ArpScan object with the IPNetwork above:
    (IPAddress, or string with '/' cidr can be used as well)
    >>> arp = ArpScan(net)

    # Now tell it to scan:
    >>> arp.scan()
    >>> for host in arp.hosts:
    ...     print(host)

    """
    def __init__(self, net: N, prefix: int=24) -> None:
        self.net = net
        self.prefix = prefix
        self.me = My()
        if isinstance(net, IPAddress):
            # Prevent scanning large networks with *default_prefix*
            net = IPNetwork(f"{self.net}/{self.prefix}")
        elif isinstance(net, str):
            net = IPNetwork(self.net)
        if net._prefixlen < self.prefix:
            net._prefixlen = self.prefix
        self.network = net
        self.hosts = None

    def is_local(self, net: str=None) -> bool:
        if not net:
            return self.me.network == self.network
        else:
            return IPNetwork(net) == self.network

    def scan(self) -> None:
        if self.hosts:
            return print(f"Scan has been ran already for {self.network}")
        self.hosts = []
        self.num_hosts = 0
        for ip in self.network.iter_hosts():
            if not ip == self._me.ip:
                try:
                    # send ARP requests to gather MAC address
                    responses, unanswered = scapy.arping(ip)
                    # use the MAC address from the first response
                    for iface, macaddr in responses:
                        if iface == self._me.default_interface:
                            mac = macaddr[scapy.Ether].src
                            self.num_hosts += 1
                            host_dict = {"ip": ip, "mac": mac}
                            self.hosts.append(host_dict)
                except:
                    continue

    # def do_arp_scan(self, ip) -> list:
    #     """ Arp for a single IP and return list potential hosts
    #     """
    #     arp_request = scapy.ARP(pdst=ip)
    #     broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    #     arp_request_broadcast = broadcast/arp_request
    #     return scapy.srp(arp_request_broadcast, timeout=1,
    #                      verbose=False)[0]

    def print_result(self):
        print("IP\t\t\tMAC Address")
        print("-" * 52)
        for client in self.hosts:
            print(f"{client['ip']}\t\t{client['mac']}")
