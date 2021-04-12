# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        nettopo.py
'''
import os
from glob import glob
import re
import sys

from nettopo.core.config import NettopoConfig
from nettopo.core.exceptions import NettopoError
from nettopo.core.network import Network
from nettopo.core.node import Node
from nettopo.core.diagram import Diagram
from nettopo.core.catalog import Catalog


class Nettopo:
    """ Core Nettopo class provides entrance to all Nettopo actions
    """
    def __init__(self, config=None, config_file=None):
        self.config = NettopoConfig()
        if config:
            self.config.load(config=config)
        elif config_file and os.path.isfile(config_file):
            self.config.load(filename=config_file)
        self.network = Network(self.config)
        self.diagram = None
        self.catalog = None


    def has_snmp(self, node):
        if node.snmp.success:
            return True
        if node.get_snmp_creds(self.config.snmp_creds):
            return True
        raise NettopoError(f"No valid SNMP credentials for {node.ip}")


    def add_snmp_credential(self, snmp_community, snmp_ver=2):
        if snmp_ver != 2:
            raise NettopoError('snmp_ver is not valid')
            return
        self.config.add_creds(snmp_community)


    def set_discover_maxdepth(self, depth: int=0):
        self.network.max_depth = depth


    def set_verbose(self, verbose: bool=True):
        self.network.verbose = verbose


    def discover_network(self, root_ip, details):
        self.network.discover(root_ip)
        if details:
            self.network.discover_details()
        self.diagram = Diagram(self.network)
        self.catalog = Catalog(self.network)


    def new_node(self, ip):
        node = Node(ip)
        return node if self.has_snmp(node) else False


    def query_node(self, node, **get_values):
        # see node.actions in node.py for what get_values are available
        if self.has_snmp(node):
            for getv in get_values:
                setattr(node.actions, getv, get_values[getv])
        return node.query_node()


    def write_diagram(self, output_file, diagram_title: str="Nettopo Diagram"):
        if not self.diagram:
            raise NettopoError("You must discover_network to write_diagram")
        self.diagram.generate(output_file, diagram_title)


    def write_catalog(self, output_file):
        if not self.catalog:
            raise NettopoError("You must discover_network to write_catalog")
        self.catalog.generate(output_file)


    def get_switch_vlans(self, ip):
        node = ip if isinstance(ip, Node) else Node(ip)
        if not node.get_snmp_creds(self.config.snmp_creds):
            return []
        return node.get_vlans()


    def get_switch_macs(self, switch_ip_or_node, *, vlan=None, mac=None, port=None):
        ''' Get the CAM table from a switch.
        Args:
            *switch_ip* or *node* is required
        :param: switch_ip       IP address of the device
        :param: node            Node() class object
        :param: vlan            Filter results by VLAN
        :param: mac             Filter results by MAC address (regex)
        :param: port            Filter results by port (regex)
        :param: verbose         Display progress to stdout
        :return:                Array of MAC objects
        '''
        if not isinstance(switch_ip_or_node, Node):
            node = Node(switch_ip_or_node)
        else:
            node = switch_ip_or_node
        # if not node.queried:
        #     node.query_node()
        if vlan:
            # get MACs for single VLAN
            macs = node.get_macs_for_vlan(vlan)
        else:
            # get all MACs
            macs = node.get_cam()
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


    def get_switch_arp(self, switch_ip, *, ip=None, mac=None, interf=None, arp_type=None):
        '''
        Get the ARP table from a switch.
        Args:
            switch_ip           IP address of the device
            ip                  Filter results by IP (regex)
            mac                 Filter results by MAC (regex)
            interf              Filter results by INTERFACE (regex)
            arp_type            Filter results by ARP Type
        Return:
            Array of arp objects
        '''
        node = Node(switch_ip)
        if not node.get_snmp_creds(self.config.snmp_creds):
            return []
        arp = node.get_arp()
        if not arp:
            return []
        if not all([ip, mac, interf, arp_type]):
            # no filtering
            return arp
        # filter the result table
        ret = []
        for a in arp:
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
        neighbors = []
        if self.has_snmp(node):
            neighbors.extend(node.get_cdp_neighbors())
            neighbors.extend(node.get_lldp_neighbors())
        return neighbors
