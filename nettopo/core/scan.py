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

class Scan:
    """ Factory class for all scanning operations on a single network
    """
    def __init__(self, net: N, prefix: int=24) -> None:
        self.me = NettopoLocalNetwork()
        self.hosts = []
        self.num_hosts = 0

        if isinstance(net, IPAddress):
            # Prevent scanning large networks with *default_prefix*
            self.network = IPNetwork(f"{self.net}/{self.prefix}")
        elif isinstance(net, str):
            self.network = IPNetwork(self.net)
        else:
            self.network = net

        if self.network.prefixlen > prefix:
            self.prefix = self.network.prefixlen
        else:
            self.prefix = prefix

    def is_local(self, net: str=None) -> bool:
        if not net:
            return self.me.network == self.network
        else:
            return IPNetwork(net) == self.network

    def arp_scan(self) -> None:
        arp = ArpScan(self)
        arp.do_scan()


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
    def __init__(self, cls: Scan) -> None:
        self.scan = cls

    def do_scan(self) -> None:
        if self.scan.hosts:
            return print(f"Scan has already been ran for \
                         {str(self.scan.network)}")
        for host in self.scan.network.iter_hosts():
            ip = host.format()
            if ip not in self.scan.me.ips:
                try:
                    host_dict = self.do_arp_scan(ip)
                    if host_dict:
                        self.scan.num_hosts += 1
                        self.scan.hosts.append(host_dict)
                except:
                    continue
        return self.print_result()

    def do_arp_scan(self, ip) -> dict:
        """ Arp for a single IP and return a dict of IP and MAC
        """
        # send ARP requests to gather MAC address
        responses, unanswered = scapy.arping(ip, timeout=0.05)
        # use the MAC address from the first response
        for _, macaddr in responses:
            dst_ip = macaddr[scapy.Ether].psrc
            dst_mac = macaddr[scapy.Ether].hwsrc
            return {"ip": dst_ip, "mac": dst_mac}

    def print_result(self):
        print("IP\t\t\tMAC Address")
        print("-" * 52)
        for host in self.scan.hosts:
            print(f"{host['ip']}\t\t{host['mac']}")
        return print(f"Found {self.scan.num_hosts} for {str(self.scan.network)}")
