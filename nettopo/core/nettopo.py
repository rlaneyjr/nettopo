# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
        nettopo.py
"""
import os
from glob import glob
import re
import sys
from typing import Union, Optional
from netaddr import IPNetwork, IPAddress

from nettopo.core.config import NettopoConfig
from nettopo.core.exceptions import NettopoError, NettopoSNMPError
from nettopo.core.network import NettopoNetwork
from nettopo.core.node import Node
from nettopo.core.diagram import Diagram
from nettopo.core.catalog import Catalog

# Typing shortcuts
_USA = Union[str, IPAddress]
_USNA = Union[str, IPNetwork, IPAddress]
_USIN = Union[str, IPAddress, Node]


class Nettopo:
    """ Core Nettopo class provides entrance to all Nettopo actions
    """
    def __init__(self, network: _USNA=None, config=None, config_file=None):
        self.config = NettopoConfig(config=config, filename=config_file)
        self.network = NettopoNetwork(network, self.config)
        self.diagram = None
        self.catalog = None

    def has_snmp(self, node: Node):
        if node.snmp.success:
            return True
        raise NettopoSNMPError(f"No valid SNMP credentials for {node.ip}")

    def add_snmp_credential(self, community: str):
        self.config.snmp_creds.append(community)

    def set_maxdepth(self, depth: int):
        self.network.max_depth = depth

    def set_verbose(self, verbose: bool):
        self.network.verbose = verbose

    def discover_network(self, ip: _USA=None):
        self.network.discover(ip=ip)
        self.diagram = Diagram(self.network)
        self.catalog = Catalog(self.network)

    def new_node(self, ip: _USIN) -> Optional[Node]:
        if isinstance(ip, Node):
            node = ip
        else:
            node = self.network.create_node(ip)
        if not node:
            raise NettopoError("Unable to create Node")
        return node

    def query_node(self, node: Node):
        if self.has_snmp(node) and not node.queried:
            node.query_node(self.network.verbose)

    def write_diagram(self, output_file, diagram_title: str="Nettopo Diagram"):
        if not self.diagram:
            raise NettopoError("You must discover_network to write_diagram")
        self.diagram.generate(output_file, diagram_title)

    def write_catalog(self, output_file):
        if not self.catalog:
            raise NettopoError("You must discover_network to write_catalog")
        self.catalog.generate(output_file)

    def get_node_vlans(self, ip):
        node = self.new_node(ip)
        if node:
            node.get_vlans()
            return node.vlans

    def get_node_macs(
        self,
        ip_or_node: _USA,
        *,
        vlan: int=None,
        mac: str=None,
        port: str=None,
    ):
        """ Get the CAM table from a switch.
        Args:
            *switch_ip* or *node* is required
        :param: ip_or_node       IP address of the device
        :param: node            Node() class object
        :param: vlan            Filter results by VLAN
        :param: mac             Filter results by MAC address (regex)
        :param: port            Filter results by port (regex)
        :return:                Array of MAC objects
        """
        node = self.new_node(ip_or_node)
        if vlan:
            # get MACs for single VLAN
            macs = node.get_macs_for_vlan(vlan)
        else:
            # get all MACs
            node.get_cam()
            macs = node.mac_table
        if not all([mac, port]):
            return macs or []
        # filter results
        ret = []
        for m in macs:
            if mac and re.match(mac, m.mac):
                ret.append(m)
            if port and re.match(port, m.port):
                ret.append(m)
        return ret

    def get_nodes(self):
        return self.network.nodes

    def get_discovered_nodes(self):
        return [node for node in self.network.nodes if node.queried]

    def get_node_ip(self, node: Node):
        return node.ip

    def get_node_arp(self, switch_ip, *, ip=None, mac=None, interf=None, arp_type=None):
        """
        Get the ARP table from a switch.
        Args:
            switch_ip           IP address of the device
            ip                  Filter results by IP (regex)
            mac                 Filter results by MAC (regex)
            interf              Filter results by INTERFACE (regex)
            arp_type            Filter results by ARP Type
        Return:
            Array of arp objects
        """
        node = self.new_node(switch_ip)
        if not node.arp_table:
            node.get_arp()
        arps = node.arp_table
        if not all([ip, mac, interf, arp_type]):
            # no filtering
            return arps
        # filter the result table
        ret = []
        for a in arps:
            if ip and not re.match(ip, a.ip):
                continue
            if mac and not re.match(mac, a.mac):
                continue
            if interf and not re.match(str(interf), str(a.interf)):
                continue
            if arp_type and not re.match(arp_type, a.arp_type):
                continue
            ret.append(a)
        return ret

    def get_neighbors(self, node: Node) -> list:
        if not node.links:
            node.create_links()
        return node.links
