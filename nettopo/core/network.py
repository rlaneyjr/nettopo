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

from nettopo.core.exceptions import NettopoSNMPError, NettopoNetworkError
from nettopo.core.util import normalize_host, is_ipv4_address
from nettopo.core.node import Node, Nodes
from nettopo.core.config import NettopoConfig
from nettopo.core.constants import NOTHING, NODE, DCODE
from nettopo.core.data import BaseData, LinkData

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
        self.hosts = None
        self.snmp_nodes = None
        self.is_local = False
        self.network =  None
        self.level = None
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

    def create_node(self, ip, query=True):
        try:
            node = Node(ip)
            if query:
                node.query_node()
            return node
        except NettopoSNMPError:
            self._print(f"SNMP failed for SNMP discovered node {ip}")

    def snmp_scan(self, hosts: str) -> None:
        self._print(f"Scanning network = {hosts}")
        port_scanner = PortScanner()
        port_scanner.scan(hosts=hosts, ports='161')
        snmp_ips = port_scanner.all_hosts()
        while snmp_ips:
            ip = snmp_ips.pop(0)
            node = self.create_node(ip, False)
            if node:
                if not self.snmp_nodes:
                    self.snmp_nodes = Nodes([node])
                else:
                    self.snmp_nodes.append(node)

    def discover(self, root_ip: _USA=None):
        if not root_ip and not self.network:
            raise NettopoNetworkError("Error must provide root IP or network")
        elif not root_ip and self.is_local:
            # Try the default gateway on local network
            root_ip = self.local_net.default_gateway
        if (root_ip and not self.network) or (root_ip not in self.network):
            # Try creating network with root_ip
            self.create_network(f"{root_ip}/24")
            if not self.network:
                raise NettopoNetworkError(f"{root_ip}/24 did not pass ACL")
        if not root_ip and self.network:
            # Still no root but we have network we can scan for SNMP nodes
            self.snmp_scan(str(self.network))
        # Create the root node
        if root_ip:
            self.root_node = self.create_node(root_ip, False)
        elif self.snmp_nodes:
            self.root_node = self.snmp_nodes.pop(0)
        else:
            raise NettopoNetworkError(
                f"No SNMP nodes discovered on {self.network}"
            )
        self._print(f"""Discovery codes:
                    . depth indicator
                    {DCODE.ERR_SNMP_STR} connection error
                    {DCODE.DISCOVERED_STR} discovering node
                    {DCODE.STEP_INTO_STR} numerating adjacencies
                    {DCODE.INCLUDE_STR} include node
                    {DCODE.LEAF_STR} leaf node""")
        print('Discovering network...')
        # Start the process of querying snmp nodes and recursing adjacencies.
        if self.root_node:
            self.root_node.query_node()
            self._print(f"Discovery of {root_ip} successful")
            self._print(f"""Checking adjacencies:
                {self.root_node.name}, {self.root_node.ip}
                {DCODE.ROOT}, {DCODE.DISCOVERED}""")
            self.nodes = Nodes([self.root_node])
            self.hosts = []
            self.level = 0
            if self.snmp_nodes:
                self.discover_level(self.snmp_nodes)
            else:
                self.discover_level()
        else:
            print(f"Discovery of {root_ip} failed")
            return

    def discover_level(self, nodes=None):
        if self.level == 0:
            # First level "root level"
            if not nodes:
                self.discover_neighbors(self.root_node)
        # Increase our level
        self.level += 1
        # Check max depth
        if self.level <= self.max_depth:
            for node in nodes:
                self.discover_neighbors(node)

    def discover_neighbors(self, node: Node):
        # Store our new nodes here
        new_nodes = []
        for link in node.links:
            link, new_node = self.process_link(link)
            if new_node:
                new_nodes.append(new_node)
            elif link:
                self.hosts.append(link)
            else:
                self._print("Already knew about this node")
        # Got our new neighbors now discover them
        if new_nodes:
            self.nodes.extend(new_nodes)
            self.discover_level(new_nodes)

    def process_link(self, link: LinkData):
        # We have not processed this link yet
        if not link.remote_node:
            if is_ipv4_address(link.remote_ip) and link.remote_ip != '0.0.0.0':
                if link.remote_name in self.nodes.column('name'):
                    known_node = self.nodes.get_node(link.remote_name, 'name')
                    link.remote_node = known_node._id
                    # Add IP to list if not there
                    if link.remote_ip not in known_node.ips:
                        known_node.ips.append(link.remote_ip)
                    return False, False
                else:
                    try:
                        # Create and process as remote node
                        new_node = Node(link.remote_ip)
                        link.remote_node = new_node._id
                        new_node.query_node()
                        return link, new_node
                    except NettopoSNMPError:
                        self._print(f"SNMP failed for {link.remote_ip}")
                        link.remote_node = 'host'
                        return link, False
            else:
                # No valid IP so add it as a host
                link.remote_node = 'host'
                return link, False
