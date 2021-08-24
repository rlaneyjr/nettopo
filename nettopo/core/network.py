# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
        network.py
"""
from dataclasses import dataclass
from functools import cached_property
from netaddr import IPNetwork, IPAddress
import netifaces
from nmap import PortScanner
import scapy.all as scapy
import socket
from typing import Union, Dict, List, Optional

from nettopo.core.exceptions import (
    NettopoSNMPError,
    NettopoNetworkError,
    NettopoACLDenied,
)
from nettopo.core.util import normalize_host, is_ipv4_address
from nettopo.core.node import Node, Nodes
from nettopo.core.config import NettopoConfig
from nettopo.core.constants import NOTHING, NODE, DCODE
from nettopo.core.data import BaseData, LinkData, DataTable

_USNA = Union[str, IPNetwork, IPAddress]
_USN = Union[str, IPNetwork]
_USA = Union[str, IPAddress]
_ON = Optional[IPNetwork]
_LO = List[object]
_OLO = Optional[List[object]]
_OUSA = Optional[Union[str, IPAddress]]
_USNA = Optional[Union[str, IPNetwork, IPAddress]]


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


class Level:
    """ A level is the results from the discovery of a single level.
    It contains the node(s), link(s), and host(s) if any. A level must
    contain a numerical value and at least one node.

    :params:depth:int - Integer representation of the depth. (required)
    :params:nodes:list - Nodes discovered in this level. (required)
    """
    def __init__(self, depth: int, nodes: Union[Nodes, Node]):
        self.depth = depth
        if isinstance(nodes, Node):
            nodes = Nodes([nodes])
        self.nodes = nodes


class NettopoNetwork(BaseData):
    show_items = ['root_node', 'num_nodes']
    def __init__(self, network: _USNA=None, config: NettopoConfig=None):
        self.local_net = NettopoLocalNetwork()
        self.config =  config if config else NettopoConfig()
        self.root_ip = None
        self.root_node = None
        self.nodes = Nodes()
        self.is_local = False
        self.network = None
        self.levels = []
        self.depth = None
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
            self._print(f"{network} is allowed to be discovered")
            self.network = network
            if self.is_local:
                # Use the default gateway as root on local network
                self.root_ip = self.local_net.default_gateway
            elif self.network.prefixlen == 32:
                self.root_ip = self.network.ip
        else:
            self._print(f"{network} is not allowed to be discovered")
            raise NettopoACLDenied(f"{network} not premitted discovery")

    def create_node(self, ip, query: bool=False):
        try:
            node = Node(ip)
            self._print(f"SNMP access to {ip} success")
            if query:
                node.query_node(self.verbose)
            return node
        except NettopoSNMPError:
            self._print(f"SNMP access to {ip} failed")

    def snmp_discover_nodes(self, network: _USNA=None, query: bool=False) -> Optional[Node]:
        snmp_nodes = Nodes()
        if network:
            self.create_network(network)
        hosts = str(self.network)
        self._print(f"Scanning network = {hosts}")
        port_scanner = PortScanner()
        port_scanner.scan(hosts=hosts, ports='161')
        snmp_ips = port_scanner.all_hosts()
        for ip in snmp_ips:
            self._print(f"Discovered {ip} has port 161 checking SNMP access")
            node = self.create_node(ip, query)
            if node:
                snmp_nodes.append(node)
        return snmp_nodes

    def auto_discover(self, network: _USNA=None) -> None:
        snmp_nodes = self.snmp_discover_nodes(network, True)
        if snmp_nodes:
            self._print(f"Discovered {len(snmp_nodes)} SNMP nodes")
            self._start_discovery(snmp_nodes)
        else:
            raise NettopoNetworkError(
                f"No SNMP nodes discovered on {self.network}"
            )

    def discover(self, ip: _OUSA=None):
        if ip:
            if not self.network or (ip not in self.network):
                self.create_network(ip)
            if (ip in self.network) and not self.root_ip:
                self.root_ip = ip
        if self.root_ip:
            print('Discovering root {self.root_ip}')
            # Create the root node
            self.root_node = self.create_node(self.root_ip)
            if self.root_node:
                self.root_node.query_node(self.verbose)
                self._print(f"Discovery of {self.root_node.name} successful")
                self._start_discovery()
            else:
                print(f"Discovery of {self.root_ip} failed")
        else:
            print(f"Auto discovery of {self.network} started")
            self.auto_discover()

    def _start_discovery(self, nodes: Optional[Nodes]=None):
        if nodes:
            self.nodes = nodes
        elif self.root_node:
            self.nodes = Nodes([self.root_node])
        else:
            raise NettopoNetworkError(
                f"No nodes provided or root node discovered on {self.network}"
            )
        # First level 0 "root level"
        self.depth = 0
        root_level = Level(self.depth, self.nodes)
        self.levels.append(root_level)
        # Now start the recursive discovery
        self.discover_level(self.nodes)

    def discover_level(self, nodes: Nodes):
        # Increase our depth
        self.depth += 1
        # Now check max depth
        if self.depth <= self.max_depth:
            # Discover neighbors
            new_nodes = self.discover_neighbors(nodes)
            if new_nodes:
                # Add our new nodes to global list
                self.nodes.extend(new_nodes)
                # Now create the next level
                new_level = Level(self.depth, new_nodes)
                self.levels.append(new_level)
                # And try again
                self.discover_level(new_nodes)
            else:
                self._print("No more neighbors found. Stopping discovery")
        else:
            self._print("Reached max depth. Stopping discovery")

    def discover_neighbors(self, nodes: Nodes):
        # Store our new nodes here
        new_nodes = Nodes()
        for node in nodes:
            if not node.queried:
                node.query_node(self.verbose)
            for link in node.links:
                new_node = self.process_link(link)
                if new_node:
                    new_nodes.append(new_node)
        return new_nodes

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
                    return None
                else:
                    # Create and process as remote node but don't query
                    new_node = self.create_node(link.remote_ip)
                    if new_node:
                        link.remote_node = new_node._id
                        return new_node
                    else:
                        link.remote_node = 'host'
                        return None
            else:
                # No valid IP so add it as a host
                link.remote_node = 'host'
                return None
