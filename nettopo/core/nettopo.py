# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        nettopo.py
'''
import os
from glob import glob
import re
import sys

from .config import Config
from .exceptions import NettopoError
from .network import Network
from .node import Node
from .mac import MAC
from .diagram import Diagram
from .catalog import Catalog


class Nettopo:
    """ Core Nettopo class provides entrance to all Nettopo actions
    """
    def __init__(self, conf=None, conf_file=None):
        self.config = Config()
        if conf:
            self.config.load(config=conf)
        elif conf_file and os.path.isfile(conf_file):
            self.config.load(filename=conf_file)
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


    def set_verbose(self, verbose=True):
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


    def get_switch_macs(self, switch_ip=None, node=None, vlan=None, mac=None, port=None, verbose=True):
        ''' Get the CAM table from a switch.
        Args:
            switch_ip           IP address of the device
            node                natlas_node from new_node()
            vlan                Filter results by VLAN
            mac                 Filter results by MAC address (regex)
            port                Filter results by port (regex)
            verbose             Display progress to stdout
            switch_ip or node is required
        Return:
            Array of MAC objects
        '''
        if not switch_ip:
            if not node:
                return None
            switch_ip = node.get_ipaddr()
        M = MAC(self.config)
        if vlan:
            # get MACs for single VLAN
            macs = M.get_macs_for_vlan(switch_ip, vlan, verbose)
        else:
            # get all MACs
            macs = M.get_macs(switch_ip, verbose)
        if not all([mac, port]):
            return macs if macs else []
        # filter results
        ret = []
        for m in macs:
            if mac:
                if not re.match(mac, m.mac):
                    continue
            if port:
                if not re.match(port, m.port):
                    continue
            ret.append(m)
        return ret


    def get_nodes(self):
        return self.network.nodes


    def get_discovered_nodes(self):
        return [node for node in self.network.nodes if node.queried]


    def get_node_ip(self, node):
        return node.get_ipaddr()


    def get_switch_arp(self, switch_ip, ip=None, mac=None, interf=None, arp_type=None):
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
        interf = str(interf) if vlan else None
        # filter the result table
        ret = []
        for a in arp:
            if ip and not re.match(ip, a.ip):
                continue
            if mac and not re.match(mac, a.mac):
                continue
            if interf and not re.match(interf, str(a.interf)):
                continue
            if arp_type and not re.match(arp_type, a.arp_type):
                continue
            ret.append(a)
        return ret


    def get_neighbors(self, node):
        neighbors = []
        if self.has_snmp(node):
            neighbors.extend(node.get_cdp_neighbors())
            neighbors.extend(node.get_lldp_neighbors())
        return neighbors
