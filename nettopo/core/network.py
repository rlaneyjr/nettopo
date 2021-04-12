# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
        network.py
"""
import netifaces
import scapy.all as scapy
import socket
from dataclasses import dataclass
from functools import cached_property
from netaddr import IPNetwork, IPAddress
from nmap import PortScanner
from timeit import default_timer as timer
from typing import Union, Dict, List

from nettopo.core.exceptions import NettopoNetworkError
from nettopo.core.util import normalize_host
from nettopo.core.node import Node, Nodes
from nettopo.core.config import NettopoConfig
from nettopo.core.constants import NOTHING, NODE, DCODE
from nettopo.core.data import BaseData

_USNA = Union[str, IPNetwork, IPAddress]
_USN = Union[str, IPNetwork]
_USA = Union[str, IPAddress]
_UNN = Union[IPNetwork, None]


class NettopoLocalNetwork:
    """ Use this class to store local network details to ensure we don't
    include in other operations
    """
    @cached_property
    def name(self):
        try:
            myname = socket.gethostname()
        except:
            myname = 'localhost'
        return myname

    @cached_property
    def dns_ip(self):
        try:
            myip = socket.gethostbyname(self.name)
        except:
            myip = '127.0.0.1'
        return myip

    @cached_property
    def if_addrs(self):
        return netifaces.ifaddresses(self.default_interface)

    @cached_property
    def ip(self):
        return self.if_addrs[netifaces.AF_INET][0]['addr']

    @cached_property
    def ips(self):
        return [self.ip, self.dns_ip]

    @cached_property
    def fqdn(self):
        try:
            myfqdn = socket.getfqdn()
        except:
            myfqdn = 'localhost.local'
        return myfqdn

    @cached_property
    def netmask(self):
        return self.if_addrs[netifaces.AF_INET][0]['netmask']

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


class NettopoNetwork(BaseData):
    show_items = ['root_node', 'num_nodes']
    def __init__(self, network: _USNA=None):
        self.local_net = NettopoLocalNetwork()
        self.config = NettopoConfig()
        self.root_node = None
        self.nodes = None
        self.snmp_nodes = None
        self.is_local = False
        self.network =  None
        self.max_depth = self.config.general['max_depth']
        self.verbose = self.config.general['verbose']
        self.create_network(network)

    def __len__(self) -> int:
        if self.nodes:
            return len(self.nodes)

    def _print(self, stuff: str) -> None:
        if self.verbose:
            print(stuff)

    def create_network(self, network: _USNA=None) -> None:
        if not network:
            network = self.local_net.network
            self.is_local = True
        if not isinstance(network, IPNetwork):
            network = IPNetwork(network)
        if self.config.passes_acl(network):
            self.network = network
        else:
            self.network = False
            self.is_local = None
            self._print(f"{network} is not allowed to be discovered")

    def snmp_scan(self, hosts: str) -> None:
        self._print(f"Scanning network = {hosts}")
        port_scanner = PortScanner()
        port_scanner.scan(hosts=hosts, ports='161')
        self.snmp_nodes = port_scanner.all_hosts()

    def discover(self, root_ip: _USA=None):
        hosts = None
        if not root_ip:
            if not self.is_local:
                raise NettopoNetworkError(
                    f"Must provide root ip for non-local network {self.network}"
                )
            else:
                # Try the default gateway as starting point
                root_ip = self.local_net.default_gateway
        if self.network and root_ip in self.network:
            hosts = str(self.network)
        else:
            # Try creating network with root_ip
            self.create_network(f"{root_ip}/24")
            if self.network:
                hosts = str(self.network)
        if hosts:
            self.snmp_scan(hosts)
        else:
            raise NettopoNetworkError(f"{root_ip}/24 did not pass ACL")
        if root_ip not in self.snmp_nodes:
            raise NettopoNetworkError(f"{root_ip} does not have SNMP enabled")
        self._print(f"""Discovery codes:
                    . depth indicator
                    {DCODE.ERR_SNMP_STR} connection error
                    {DCODE.DISCOVERED_STR} discovering node
                    {DCODE.STEP_INTO_STR} numerating adjacencies
                    {DCODE.INCLUDE_STR} include node
                    {DCODE.LEAF_STR} leaf node""")
        print('Discovering network...')
        # Start the process of querying this node and recursing adjacencies.
        root_node = Node(root_ip, immediate_query=True)
        if root_node.snmp.success:
            self._print(f"Discovery of {root_ip} successful")
            self.root_node = root_node
            self.print_step(self.root_node.ip, self.root_node.name,
                            [DCODE.ROOT, DCODE.DISCOVERED])
            self.discover_node(self.root_node)
        else:
            print(f"Discovery of {root_ip} failed")
            return
