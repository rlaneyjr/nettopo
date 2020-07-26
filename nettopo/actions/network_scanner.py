# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              scanner.py
Description:        Network ARP Scanner
Author:             Ricky Laney
'''
from nettopo.net import NtNetwork, NtIPAddress
from nettopo.core.exceptions import NettopoNetworkError
from dataclasses import dataclass
from functools import cached_property
import scapy.all as scapy
import socket
from typing import Union, Dict, List


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
    """
    def __init__(self, net: Union[NtNetwork, NtIPAddress],
                 prefix_min: int=24) -> None:
        # Store original values for debugging
        self._net = net
        self._prefix_min = prefix_min
        # Store my own IP details
        self._me = My()
        if isinstance(net, NtIPAddress):
            # Prevent scanning large networks with *prefix_min*
            net = NtNetwork(f"{net}/{prefix_min}")
        if net._prefixlen < prefix_min:
            net._prefixlen = prefix_min
        self.network = net
        self.hosts = None

    def scan(self) -> Union[list, dict]:
        if self.hosts:
            return print(f"Scan has been ran already for {self.network}")
        self.hosts = []
        self.num_hosts = 0
        for ip in self.network.iter_hosts():
            if not ip == self._me.ip:
                results = self.do_arp_scan(ip)
                for element in results:
                    self.num_hosts += 1
                    host_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
                    self.hosts.append(host_dict)

    def do_arp_scan(self, ip) -> list:
        """ Arp for a single IP and return list potential hosts
        """
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        return scapy.srp(arp_request_broadcast, timeout=1,
                         verbose=False)[0]

    def print_result(self):
        print("IP\t\t\tMAC Address")
        print("-" * 52)
        for client in self.hosts:
            print(f"{client['ip']}\t\t{client['mac']}")
