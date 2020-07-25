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
    def ip(self):
        try:
            return socket.gethostbyname(self.name)
        except:
            raise NettopoNetworkError("Unable to get Hostname and IP")

    @cached_property
    def name(self):
        try:
            return socket.gethostname()
        except:
            raise NettopoNetworkError("Unable to get Hostname")

dns = socket.gethostbyaddr(ip)[0]

from dataclasses import dataclass
@dataclass
class Port:
    port: int
    @cached_property
    def name(self) -> str:
        try:
            return socket.getservbyport(self.port)
        except:
            return "UNKNOWN"

class HostMaybe:
    def __init__(self, ip: str) -> None:
        self.ip = ip

    def arp_scan(self) -> list:
        """ Arp for a single IP and return list of MACs responded
        """
        arp_request = scapy.ARP(pdst=self.ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=1,
                                  verbose=False)[0]
        self.macs = []
        for element in answered_list:
            # client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
            self.macs.append(element[1].hwsrc)
        if len(self.macs) > 0:
        return self.macs


class ArpScan:
    def __init__(self, net: Union[NtNetwork, NtIPAddress]=None) -> None:
        if net:
            if isinstance(net, NtNetwork):
                self.network = net
                self.ip = None
            elif isinstance(net, NtIPAddress):
                self.ip = net
                self.network = None
        else:
            self.network = None
            self.ip = None

    def scan(self) -> Union[list, dict]:
        if self.network:
            for ip in self.network.iter_hosts():
                host = HostMaybe(ip)
                macs = host.arp_scan()


    def print_result(results_list):
        print("IP\t\t\tMAC Address")
        print("----------------------------------------------------")
        for client in results_list:
            print(client["ip"] + "\t\t" + client["mac"])
