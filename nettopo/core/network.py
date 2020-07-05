# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        network.py
'''
from timeit import default_timer as timer
from .config import Config
from .exceptions import NettopoNetworkError
from .util import in_acl, str_matches_pattern
from .node import Node
from .constants import NODE, DCODE


class Network:
    def __init__(self, conf: Config):
        self.root_node = None
        self.nodes = []
        self.max_depth = 0
        self.config = conf
        self.verbose = True

    def _print(self, stuff: str) -> None:
        if self.verbose:
            print(stuff)

    def show(self):
        return f"<root_node={self.root_node.name}, num_nodes={len(self.nodes)}>"

    def set_max_depth(self, depth):
        self.max_depth = depth

    def reset_discovered(self):
        for n in self.nodes:
            n.discovered = False

    def set_verbose(self, level):
        self.verbose = level

    def discover(self, ip):
        '''
        Discover the network starting at the defined root node IP.
        Recursively enumerate the network tree up to self.depth.
        Populates self.nodes[] as a list of discovered nodes in the
        network with self.root_node being the root.
        '''
        self._print(f"""Discovery codes:
                    . depth
                    {DCODE.ERR_SNMP_STR} connection error
                    {DCODE.DISCOVERED_STR} discovering node
                    {DCODE.STEP_INTO_STR} numerating adjacencies
                    {DCODE.INCLUDE_STR} include node
                    {DCODE.LEAF_STR} leaf node""")
        print('Discovering network...')
        # Start the process of querying this node and recursing adjacencies.
        node, new_node = self.query_ip(ip, 'UNKNOWN')
        self.root_node = node
        if node:
            self.nodes.append(node)
            self.print_step(node.ip[0], node.name, False, DCODE.ROOT + DCODE.DISCOVERED)
            self.discover_node(node, False)
        else:
            return
        # we may have missed chassis info
        for n in self.nodes:
            if not any([n.serial, n.plat, n.ios]):
                n.opts.get_chassis_info = True
                if not n.serial:
                    n.opts.get_serial = True
                if not n.ios:
                    n.opts.get_ios = True
                if not n.plat:
                    n.opts.get_plat = True
                n.query_node()

    def discover_details(self):
        '''
        Enumerate the discovered nodes from discover() and update the
        nodes in the array with additional info.
        '''
        if not self.root_node:
            return
        self._print('\nCollecting node details...')
        ni = 0
        for n in self.nodes:
            ni += 1
            indicator = '+'
            if not n.snmpobj.success:
                indicator = '!'
            self._print(f"[{ni}/{len(self.nodes)}]{indicator} {n.name} ({n.snmpobj.ip})")
            # # set what details to discover for this node
            # n.opts.get_router = True
            # n.opts.get_ospf_id = True
            # n.opts.get_bgp_las = True
            # n.opts.get_hsrp_pri = True
            # n.opts.get_hsrp_vip = True
            # n.opts.get_serial = True
            # n.opts.get_stack = True
            # n.opts.get_stack_details = self.config.diagram.get_stack_members
            # n.opts.get_vss = True
            # n.opts.get_vss_details = self.config.diagram.get_vss_members
            # n.opts.get_svi = True
            # n.opts.get_lo = True
            # n.opts.get_vpc = True
            # n.opts.get_ios = True
            # n.opts.get_plat = True
            start = timer()
            n.query_node()
            end = timer()
            self._print(f"Node query took: {end - start:.2f} secs")
        # There is some back fill information we can populate now that
        # we know all there is to know.
        self._print("\nBack filling node details...")
        for n in self.nodes:
            # Find and link VPC nodes together for easy reference later
            if n.vpc_domain and not n.vpc_peerlink_node:
                for link in n.links:
                    if n.vpc_peerlink_if in [link.local_port, link.local_lag]:
                        n.vpc_peerlink_node = link.node
                        link.node.vpc_peerlink_node = n
                        break

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
        name = normalize_host(name, self.config.host_domains)
        self._print(f"{name} ({ip})")

    def query_ip(self, ip, host):
        '''
        Query this IP.
        Return node details and if we already knew about it or if this is a new node.
        Don't save the node to the known list, just return info about it.
        Args:
            ip:                 IP Address of the node.
            host:               Hostname of this known (if known from CDP/LLDP)
        Returns:
            Node:        Node of this object
            int:                NODE.NEW = Newly discovered node
                                NODE.NEWIP = Already knew about this node but not by this IP
                                NODE.KNOWN = Already knew about this node
        '''
        host = normalize_host(host, self.config.host_domains)
        node, node_updated = self.get_known_node(ip, host)
        if not node:
            node = Node()
            node.name = host
            node.ip = [ip]
            state = NODE.NEW
        else:
            # existing node
            if node.snmpobj.success:
                # we already queried this node successfully - return it
                return node, NODE.KNOWN
            state = NODE.NEWIP if node_updated else NODE.KNOWN
            node.name = host
        if ip == 'UNKNOWN':
            return node, state
        # vmware ESX reports the IP as 0.0.0.0
        # LLDP can return an empty string for IPs.
        if ip in ['0.0.0.0', '']:
            return node, state
        # find valid credentials for this node
        if not node.try_snmp_creds(self.config.snmp_creds):
            return node, state
        node.name = node.get_system_name(self.config.host_domains)
        if node.name != host:
            # the hostname changed (cdp/lldp vs snmp)!
            # double check we don't already know about this node
            if state == NODE.NEW:
                node2, node_updated2 = self.get_known_node(ip, host)
                if node2 and not node_updated2:
                    return node, NODE.KNOWN
                elif node_updated2:
                    state = NODE.NEWIP
        # Finally, if we still don't have a name, use the IP.
        # e.g. Maybe CDP/LLDP was empty and we dont have good credentials
        # for this device.  A blank name can break Dot.
        if node.name in [None, '', 'UNKNOWN']:
            node.name = node.get_ipaddr()
        node.opts.get_serial = True     # CDP/LLDP does not report, need for extended ACL
        node.query_node()
        return node, state

    def get_known_node(self, ip, host):
        '''
        Look for known nodes by IP and HOST.
        If found by HOST, add the IP if not already known.
        Return:
            node:       Node, if found. Otherwise None.
            updated:    True=updated, False=not updated
        '''
        for ex in self.nodes:
            for exip in ex.ip:
                if exip == '0.0.0.0':
                    continue
                if exip == ip:
                    return ex, False
            if ex.name == host:
                node = ex
        if node:
            if ip not in node.ip:
                node.ip.append(ip)
                return node, True
            return node, False
        else:
            return None, False

    def discover_node(self, node, depth):
        '''
        Given a node, recursively enumerate its adjacencies
        until we reach the specified depth (>0).
        Args:
            node:   Node object to enumerate.
            depth:  The depth left that we can go further away from the root.
        '''
        if depth >= self.max_depth or node.discovered:
            return
        node.discovered = True
        # vmware ESX can report IP as 0.0.0.0
        # If we are allowing 0.0.0.0/32 in the config,
        # then we added it as a leaf, but don't discover it
        if node.ip[0] == '0.0.0.0' or not node.snmpobj.success:
            return
        # print some info to stdout
        dcodes = list(DCODE.STEP_INTO)
        if depth == 0:
            dcodes.append(DCODE.ROOT)
        self.print_step(node.ip[0], node.name, dcodes)
        # get the cached snmp credentials
        snmpobj = node.snmpobj
        # list of valid neighbors to discover next
        valid_neighbors = []
        # get list of neighbors
        neighbors = []
        neighbors.extend(node.get_cdp_neighbors())
        neighbors.extend(node.get_lldp_neighbors())
        if not neighbors:
            return
        for n in neighbors:
            # some neighbors may not advertise IP addresses - default them to 0.0.0.0
            if not n.remote_ip:
                n.remote_ip = '0.0.0.0'
            # check the ACL
            acl_action = self.check_node_acl(n.remote_ip, n.remote_name)
            if acl_action == 'deny':
                continue
            dcodes.append(DCODE.DISCOVERED)
            child = None
            if acl_action == 'include':
                # include this node but do not discover it
                child = Node()
                child.ip = [n.remote_ip]
                dcodes.append(DCODE.INCLUDE)
            else:
                # discover this node
                child, query_result = self.query_ip(n.remote_ip, n.remote_name)
            # if we couldn't pull info from SNMP fill in what we know
            if not child.snmpobj.success:
                child.name = normalize_host(n.remote_name, self.config.host_domains)
                dcodes.append(DCODE.ERR_SNMP)
            # need to check the ACL again for extended ops (we have more info)
            acl_action = self.check_node_acl(n.remote_ip, n.remote_name, n.remote_plat, n.remote_ios, child.serial)
            if acl_action == 'deny':
                continue
            if query_result == NODE.NEW:
                self.nodes.append(child)
                if acl_action == 'leaf':
                    dcodes.append(DCODE.LEAF)
                if n.discovered_proto == 'cdp':
                    dcodes.append(DCODE.CDP)
                if n.discovered_proto == 'lldp':
                    dcodes.append(DCODE.LLDP)
                self.print_step(n.remote_ip, n.remote_name, dcodes, depth+1)
            # CDP/LLDP advertises the platform
            child.plat = n.remote_plat
            child.ios = n.remote_ios
            # add the discovered node to the link object and link to the parent
            n.node = child
            self.add_update_link(node, n)
            # if we need to discover this node then add it to the list
            if query_result == NODE.NEW and acl_action != 'leaf' and acl_action != 'include':
                valid_neighbors.append(child)
        # discover the valid neighbors
        for n in valid_neighbors:
            self.discover_node(n, depth+1)

    def check_node_acl(self, ip, host, platform=None, software=None, serial=None):
        for acl in self.config.discover_acl:
            if acl.type == 'ip' and in_acl(ip, acl.str):
                return acl.action
            elif acl.type == 'host' and in_acl(host, acl.str):
                return acl.action
            elif platform and acl.type == 'platform' and in_acl(platform, acl.str):
                return acl.action
            elif software and acl.type == 'software' and in_acl(software, acl.str):
                return acl.action
            elif serial and acl.type == 'serial' and in_acl(serial, acl.str):
                return acl.action
            else:
                return 'allow'

    def add_update_link(self, node, link):
        ''' Add or update a link.
        True - Added as a new link
        False - Found an existing link and updated it
        '''
        if link.node.discovered:
            # both nodes have been discovered,
            # so try to update existing reverse link info
            # instead of adding a new link
            for n in self.nodes:
                # find the child, which was the original parent
                if n.name == link.node.name:
                    # find the existing link
                    for ex_link in n.links:
                        if ex_link.node.name == node.name and ex_link.local_port == link.remote_port:
                            if not link.local_if_ip == 'UNKNOWN' and not ex_link.remote_if_ip:
                                ex_link.remote_if_ip = link.local_if_ip
                            if not link.local_lag == 'UNKNOWN' and not ex_link.remote_lag:
                                ex_link.remote_lag = link.local_lag
                            if not len(link.local_lag_ips) and len(ex_link.remote_lag_ips):
                                ex_link.remote_lag_ips = link.local_lag_ips
                            if link.local_native_vlan and not ex_link.remote_native_vlan:
                                ex_link.remote_native_vlan = link.local_native_vlan
                            if link.local_allowed_vlans and not ex_link.remote_allowed_vlans:
                                ex_link.remote_allowed_vlans = link.local_allowed_vlans
                            return False
        else:
            for ex_link in node.links:
                if ex_link.node.name == link.node.name and ex_link.local_port == link.local_port:
                    self._print(f"Discovered duplicate links for node: {ex_link.node.name} port: {ex_link.local_port}")
                    # haven't discovered yet but somehow we have this link twice.
                    # maybe from different discovery processes?
                    return False
        node.add_link(link)
        self._print(f"Added new link: {link} for node: {node}")
        return True
