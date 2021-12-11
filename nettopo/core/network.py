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

    def create_network(self, network: _USNA=None, check_acl: bool=True) -> None:
        if network == None:
            # If no network use local and don't check ACL.
            network = self.local_net.network
            check_acl = False
            # Use the default gateway as root on local network
            self.root_ip = self.local_net.default_gateway
            self._print(f"Root IP: {self.root_ip}")
        if not isinstance(network, IPNetwork):
            network = IPNetwork(network)
        if check_acl == False or self.config.passes_acl(network):
            self._print(f"Using network: {self.network}")
            self.network = network
        else:
            raise NettopoACLDenied(f"{network} is not premitted discovery")

    def discover_ip(self, ip) -> Optional[Node]:
        if ip not in self.network:
            self.create_network(ip)
        try:
            node = Node(ip)
            node.query_node(self.verbose)
            self._print(f"Discovery of {ip} success")
        except NettopoSNMPError:
            self._print(f"Discovery of {ip} failed")
            node = None
        finally:
            if node:
                # If we don't have root_node make first node root
                if not self.root_node:
                    self.root_ip = ip
                    self.root_node = node
                    self._print(f"Found root: {self.root_ip}")
                return node

    def snmp_scan_network(self, network: _USNA=None) -> Optional[Node]:
        if network != None:
            self.create_network(network)
        snmp_nodes = Nodes()
        hosts = str(self.network)
        self._print(f"Scanning network = {hosts}")
        port_scanner = PortScanner()
        port_scanner.scan(hosts=hosts, ports='161')
        snmp_ips = port_scanner.all_hosts()
        for ip in snmp_ips:
            node = self.discover_ip(ip)
            snmp_nodes.append(node)
        return snmp_nodes

    def _auto_discover(self, network: _USNA=None) -> None:
        snmp_nodes = self.snmp_scan_network(network)
        if snmp_nodes:
            self._print(f"Discovered {len(snmp_nodes)} SNMP nodes")
            self._discover_nodes(snmp_nodes)
        else:
            raise NettopoNetworkError(
                f"No SNMP nodes discovered on {self.network}"
            )

    def _discover_nodes(self, nodes: Nodes) -> None:
        # First level 0 "root level"
        self.depth = 0
        self.nodes = nodes
        root_level = Level(self.depth, self.nodes)
        self.levels.append(root_level)
        # Now start the recursive discovery
        self._discover_level(self.nodes)

    def _discover_level(self, nodes: Nodes):
        # Increase our depth
        self.depth += 1
        # Now check max depth
        if self.depth <= self.max_depth:
            # Discover neighbors
            new_nodes = self.get_nodes_neighbors(nodes)
            if new_nodes:
                # Add our new nodes to global list
                self.nodes.extend(new_nodes)
                # Now create the next level
                new_level = Level(self.depth, new_nodes)
                self.levels.append(new_level)
                # And try again
                self._discover_level(new_nodes)
            else:
                self._print("No more neighbors found. Stopping discovery")
        else:
            self._print("Reached max depth. Stopping discovery")

    def get_link_remote_node(self, link: LinkData) -> Optional[Node]:
        if link.remote_name in self.nodes.column('name'):
            return self.nodes.get_node(link.remote_name, 'name')
        elif is_ipv4_address(link.remote_ip) and link.remote_ip != '0.0.0.0':
            # Discover remote node
            return self.discover_ip(link.remote_ip)

    def get_nodes_neighbors(self, nodes: Nodes):
        # Store our new nodes here
        neighbors = Nodes()
        for node in nodes:
            if not node.queried:
                node.query_node(self.verbose)
            for link in node.links:
                # We have not processed this link yet
                if not link.remote_node:
                    neighbor = self.get_link_remote_node(link)
                    if neighbor:
                        # Add IP to list if not there
                        if link.remote_ip not in neighbor.ips:
                            neighbor.ips.append(link.remote_ip)
                        link.remote_node = neighbor._id
                        neighbors.append(neighbor)
                    else:
                        link.remote_node = 'host'
        return neighbors

    def discover(self, ip: _OUSA=None):
        """ Main function to perform discovery on this network.
        """
        if ip:
            self.discover_ip(ip=ip)
        if self.root_node:
            self._print(f"Discovery of {self.root_node.name} successful")
            nodes = Nodes([self.root_node])
            self._discover_nodes(nodes)
        else:
            print(f"Auto discovery of {self.network} started")
            self._auto_discover()
