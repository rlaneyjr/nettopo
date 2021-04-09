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
    """ Use this class to store local network details and ensure we don't
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
    def __init__(self, network: _USNA=None, conf: NettopoConfig=None):
        self.local_net = NettopoLocalNetwork()
        self.config = conf or NettopoConfig()
        self.max_depth = 100
        self.root_node = None
        self.nodes = None
        self.possible_nodes = None
        self.verbose = True
        self.is_local = False
        self.network = self.create_network(network)

    def __len__(self) -> int:
        if self.nodes:
            return len(self.nodes)

    def create_network(self, network: _USNA=None) -> _UNN:
        if not network:
            network = self.local_net.network
            self.is_local = True
        if self.config.passes_acl(network):
            if not isinstance(network, IPNetwork):
                return IPNetwork(network)
            else:
                return network
        else:
            self._print(f"{network} is not allowed to be discovered")

    def _print(self, stuff: str) -> None:
        if self.verbose:
            print(stuff)

    def snmp_scan(self, hosts=None) -> None:
        if not hosts:
            hosts = self.network
        self._print(f"Scanning network = {hosts}")
        port_scanner = PortScanner()
        port_scanner.scan(hosts=str(hosts), ports='161')
        self.possible_nodes = port_scanner.all_hosts()

    def discover(self, root_ip: _USA=None, network: _USN=None):
        """ Discover the network starting at the defined root node IP.
        Recursively enumerate the network tree up to self.depth.
        Populates self.nodes[] as a list of discovered nodes in the
        network with self.root_node being the root.
        """
        if not root_ip:
            # Use the default gateway as starting point
            root_ip = self.local_net.default_gateway
        if not network:
            network = f"{root_ip}/24"
        self.snmp_scan(network)
        if root_ip not in self.possible_nodes:
            raise NettopoNetworkError(
                f"{root_ip} appears to not have SNMP enabled"
            )
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
        if root_node.queried:
            self._print(f"Discovery of {root_ip} successful")
            self.root_node = root_node
            self.print_step(self.root_node.ip, self.root_node.name,
                            [DCODE.ROOT, DCODE.DISCOVERED])
            self.discover_node(self.root_node, self.max_depth)
        else:
            print(f"Discovery of {root_ip} failed")
            return

    def discover_node(self, node: Node, depth: int=0):
        """ Given a node, recursively enumerate its adjacencies
        until we reach the specified depth (>0).
        Args:
        node:   Node object to enumerate.
        depth:  The depth left that we can go further away from the root.
        """
        if depth > self.max_depth:
            return
        # vmware ESX can report IP as 0.0.0.0
        # If we are allowing 0.0.0.0/32 in the config,
        # then we added it, but don't discover it
        if node.ip == '0.0.0.0' or not node.snmp.success:
            return
        # print some info to stdout
        dcodes = list(DCODE.STEP_INTO)
        if depth == 0:
            dcodes.append(DCODE.ROOT)
        self.print_step(node.ip, node.name, dcodes)
        # get list of neighbors
        neighbors = node.links
        for n in neighbors:
            # some neighbors may not advertise IP addresses - default them to 0.0.0.0
            if not n.remote_ip:
                n.remote_ip = '0.0.0.0'
            dcodes.append(DCODE.DISCOVERED)
            # discover this node
            child, query_result = self.query_ip(n.remote_ip, n.remote_name)
            # if we couldn't pull info from SNMP fill in what we know
            if not child.snmp.success:
                child.name = normalize_host(n.remote_name)
                child.ip = n.remote_ip
                dcodes.append(DCODE.ERR_SNMP)
            if query_result == NODE.NEW:
                self.nodes.append(child)
                if n.discovered_proto == 'cdp':
                    dcodes.append(DCODE.CDP)
                if n.discovered_proto == 'lldp':
                    dcodes.append(DCODE.LLDP)
                self.print_step(n.remote_ip, n.remote_name, dcodes, depth+1)
            # CDP/LLDP advertises the platform
            child.plat = n.remote_plat
            child.ios = n.remote_ios
            # add discovered node to the link object and link to the parent
            n.node = child
            self.add_update_link(node, n)
            # if we need to discover this node then add it to the list
            if query_result == NODE.NEW:
                self.discover_node(child, depth+1)

    def discover_details(self):
        """ Enumerate the discovered nodes from discover() and update the
        nodes in the array with additional info.
        """
        if not self.root_node:
            return
        self._print('\nCollecting node details...')
        ni = 0
        for node in self.nodes:
            ni += 1
            indicator = '+'
            if not node.snmp.success:
                indicator = '!'
            self._print(f"[{ni}/{len(self.nodes)}]{indicator} {node.name} ({node.snmp.ip})")
            # # set what details to discover for this node
            # node.actions.get_router = True
            # node.actions.get_ospf_id = True
            # node.actions.get_bgp_las = True
            # node.actions.get_hsrp_pri = True
            # node.actions.get_hsrp_vip = True
            # node.actions.get_serial = True
            # node.actions.get_stack = True
            # node.actions.get_stack_details = self.config.diagram.get_stack_members
            # node.actions.get_vss = True
            # node.actions.get_vss_details = self.config.diagram.get_vss_members
            # node.actions.get_svi = True
            # node.actions.get_lo = True
            # node.actions.get_vpc = True
            # node.actions.get_ios = True
            # node.actions.get_plat = True
            start = timer()
            node.query_node()
            end = timer()
            self._print(f"Node query took: {end - start:.2f} secs")
            # There is some back fill information we can populate now that
            # we know all there is to know.
            self._print("Back filling node details...")
            # Find and link VPC nodes together for easy reference later
            if node.vpc_domain and not node.vpc_peerlink_node:
                for link in node.links:
                    if node.vpc_peerlink_if in [link.local_port, link.local_lag]:
                        node.vpc_peerlink_node = link.node
                        link.node.vpc_peerlink_node = node
                        break

    def get_node(self, ip, hostname: str):
        """ Look for known nodes by IP and HOSTNAME.
        If found by HOSTNAME, add the IP if not already known.
        Return:
        node:       Node, if found. Otherwise False.
        updated:    True=updated, False=not updated
        """
        current_node = None
        for node in self.nodes:
            if (ip == node.ip) or (hostname == node.name):
                current_node = node
        if current_node:
            if ip not in current_node.ips:
                current_node.ips.append(ip)
                return current_node, True
            else:
                return current_node, False
        else:
            return False, False

    def query_ip(self, ip, hostname: str=None):
        """ Query this IP.
        Return node details and if we already knew about it or if this is a new node.
        Don't save the node to the known list, just return info about it.
        Args:
        ip:                 IP Address of the node.
        host:               Hostname of this node (if known from CDP/LLDP)
        Returns:
        Node:        Node of this object
        int:                NODE.NEW = Newly queried node
        NODE.NEWIP = Already knew about this node but not by this IP
        NODE.KNOWN = Already knew about this node
        """
        if hostname:
            host = normalize_host(hostname, self.config.host_domains)
        else:
            host = 'unknown'
        node, was_updated = self.get_node(ip, host)
        if node:
            state = NODE.NEWIP if was_updated else NODE.KNOWN
            if node.queried:
                return node, state
        else:
            node = Node(ip)
            state = NODE.NEW
        # vmware ESX reports the IP as 0.0.0.0
        # LLDP can return an empty string for IPs.
        if node.ip in NOTHING or not node.snmp.success:
            return node, state
        node.query_node()
        if (node.name != host) and (state != NODE.NEW):
            # the hostname changed (cdp/lldp vs snmp)!
            # double check we don't already know about this node
            if state == NODE.NEW:
                node2, node2_updated = self.get_node(ip, host)
                if node2 and not node2_updated:
                    return node, NODE.KNOWN
                elif node2_updated:
                    state = NODE.NEWIP
        return node, state

    def print_step(self, ip, name, dcodes, depth=0):
        dcodes = dcodes if isinstance(dcodes, list) else list(dcodes)
        if DCODE.DISCOVERED in dcodes:
            self._print(f"{len(self.nodes):-3}")
        else:
            self._print("")
        if DCODE.INCLUDE in dcodes:
            # Remove SNMP error on 'include' nodes b/c we don't attempt
            if DCODE.ERR_SNMP in dcodes:
                dcode.remove(DCODE.ERR_SNMP)
            self._print(DCODE.ROOT_STR)
        elif DCODE.CDP in dcodes:
            self._print(DCODE.CDP_STR)
        elif DCODE.LLDP in dcodes:
            self._print(DCODE.LLDP_STR)
        else:
            self._print("")
        status = ""
        if DCODE.ERR_SNMP in dcodes:
            status += DCODE.ERR_SNMP_STR
        if DCODE.LEAF in dcodes:
            status += DCODE.LEAF_STR
        elif DCODE.INCLUDE in dcodes:
            status += DCODE.INCLUDE_STR
        if DCODE.DISCOVERED in dcodes:
            status += DCODE.DISCOVERED_STR
        elif DCODE.STEP_INTO in dcodes:
            status += DCODE.STEP_INTO_STR
        self._print(f"{status:3s}")
        for i in range(0, depth):
            self._print(".")
        name = normalize_host(name)
        self._print(f"{name} ({ip})")

    def add_update_link(self, node, link):
        """ Add or update a link.
        True - Added as a new link
        False - Found an existing link and updated it
        """
        if link.node.queried:
            # both nodes have been queried,
            # so try to update existing reverse link info
            # instead of adding a new link
            for cur_node in self.nodes:
                # find the child, which was the original parent
                if cur_node.name == link.node.name:
                    # find the existing link
                    for cur_link in cur_node.links:
                        if cur_link.node.name == node.name and \
                                cur_link.local_port == link.remote_port:
                            if not link.local_if_ip == 'UNKNOWN' and \
                                            not cur_link.remote_if_ip:
                                cur_link.remote_if_ip = link.local_if_ip
                            if not link.local_lag == 'UNKNOWN' and \
                                            not cur_link.remote_lag:
                                cur_link.remote_lag = link.local_lag
                            if not len(link.local_lag_ips) and \
                                            len(cur_link.remote_lag_ips):
                                cur_link.remote_lag_ips = link.local_lag_ips
                            if link.local_native_vlan and \
                                            not cur_link.remote_native_vlan:
                                cur_link.remote_native_vlan \
                                    = link.local_native_vlan
                            if link.local_allowed_vlans and \
                                            not cur_link.remote_allowed_vlans:
                                cur_link.remote_allowed_vlans \
                                    = link.local_allowed_vlans
                            return False
        else:
            for node_link in node.links:
                if node_link.node.name == link.node.name and \
                    node_link.local_port == link.local_port:
                    self._print(f"Discovered duplicate links for:\n \
                                Node: {link.node.name} Port: {link.local_port}")
                    # haven't queried yet but we have this link twice.
                    # maybe from different discovery processes?
                    return False
        node.add_link(link)
        self._print(f"Added new link: {link} for node: {node}")
        return True
