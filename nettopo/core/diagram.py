# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    diagram.py
'''
import pydot
import datetime
from jinja2 import Template
import os

from .config import Config
from .data import DotNode
from .network import Network
from .templates import node_template, credits_template
from .util import get_path, get_port_module


class Diagram:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.config = network.config or Config().generate_new()

    def generate(self, dot_file, title):
        self.network.reset_discovered()
        title_text_size = self.config.diagram.title_text_size
        date_text_size = title_text_size - 2
        today = datetime.datetime.now()
        today = today.strftime('%Y-%m-%d %H:%M')
        credits = Template(credits_template)
        credits = credits.render(title_text_size, date_text_size, title, today)
        node_text_size = self.config.diagram.node_text_size
        link_text_size = self.config.diagram.link_text_size
        diagram = pydot.Dot(graph_type='graph', labelloc='b',
                            labeljust='r', fontsize=node_text_size,
                            label=f"<{credits}>")
        diagram.set_node_defaults(fontsize=link_text_size)
        diagram.set_edge_defaults(fontsize=link_text_size, labeljust='l')
        # add all of the nodes and links
        self.build(diagram, self.network.root_node)
        # expand output string
        files = get_path(dot_file)
        for f in files:
            # get file extension
            _, file_ext = os.path.splitext(f)
            output_func = getattr(diagram, 'write_' + file_ext.lstrip('.'))
            if not output_func:
                print(f"Error: Output type {file_ext} does not exist.")
            else:
                output_func(f)
                print(f"Created diagram: {f}")

    def build(self, diagram, node=None):
        if not node:
            return 0, 0
        if node.discovered:
            return 0, 0
        node.discovered = 1
        dot_node = self.get_node(diagram, node)
        if dot_node.ntype == 'single':
            diagram.add_node(pydot.Node(name=node.name,
                                        label=f"<{dot_node.label}>",
                                        style=dot_node.style,
                                        shape=dot_node.shape,
                                        peripheries=dot_node.peripheries))
        elif dot_node.ntype == 'vss':
            cluster = pydot.Cluster(graph_name=node.name,
                                    suppress_disconnected=False,
                                    labelloc='t', labeljust='c',
                                    fontsize=self.config.diagram.node_text_size,
                                    label=f"<<br /><b>VSS {node.vss.domain}</b>>")
            for i in range(0, 2):
                # {vss.} vars
                nlabel = dot_node.label.format(vss=node.vss.members[i])
                cluster.add_node(
                                pydot.Node(name=f"{node.name}[VSS{i+1}]",
                                           label=f"<{nlabel}>",
                                           style=dot_node.style,
                                           shape=dot_node.shape,
                                           peripheries=dot_node.peripheries))
            diagram.add_subgraph(cluster)
        elif dot_node.ntype == 'vpc':
            cluster = pydot.Cluster(graph_name=node.name,
                                    suppress_disconnected=False,
                                    labelloc='t',
                                    labeljust='c',
                                    fontsize=self.config.diagram.node_text_size,
                                    label=f"<<br /><b>VPC {node.vpc_domain}</b>>")
            cluster.add_node(pydot.Node(
                             name=node.name,
                             label=f"<{dot_node.label}>",
                             style=dot_node.style,
                             shape=dot_node.shape,
                             peripheries=dot_node.peripheries))
            if node.vpc_peerlink_node:
                node2 = node.vpc_peerlink_node
                node2.discovered = 1
                dot_node2 = self.get_node(diagram, node2)
                cluster.add_node(pydot.Node(
                                 name=node2.name,
                                 label=f"<{dot_node2.label}>",
                                 style=dot_node2.style,
                                 shape=dot_node2.shape,
                                 peripheries=dot_node2.peripheries))
            diagram.add_subgraph(cluster)
        elif dot_node.ntype == 'stackwise':
            cluster = pydot.Cluster(graph_name=node.name,
                                    suppress_disconnected=False,
                                    labelloc='t',
                                    labeljust='c',
                                    fontsize=self.config.diagram.node_text_size,
                                    label='<<br /><b>Stackwise</b>>')
            for i in range(0, node.stack.count):
                # {stack.} vars
                if len(node.stack.members):
                    nlabel = dot_node.label
                else:
                    nlabel = dot_node.label.format(stack=node.stack.members[i])
                cluster.add_node(pydot.Node(name=f"{node.name}[SW{i+1}]",
                                            label=f"<{nlabel}>",
                                            style=dot_node.style,
                                            shape=dot_node.shape,
                                            peripheries=dot_node.peripheries))
            diagram.add_subgraph(cluster)

        lags = []
        for link in node.links:
            self.build(diagram, link.node)
            # determine if this link should be broken out or not
            if self.config.diagram.expand_lag \
                or link.local_lag == 'UNKNOWN' \
                or self.devs_in_lag(link.local_lag, node.links) > 1:
                # a LAG could span different devices, eg Nexus.
                # in this case we should always break it out, otherwise we could
                # get an unlinked node in the diagram.
                self.create_link(diagram, node, link, True)
            else:
                found = [lag for lag in lags if link.local_lag == lag]
                if not found:
                    lags.append(link.local_lag)
                    self.create_link(diagram, node, link, False)

    def get_node(self, diagram, node):
        dot_node = DotNode()
        # get the node text
        dot_node.label = self.format_node_text(diagram, node, self.config.diagram.node_text)
        # set the node properties
        if node.vss.enabled:
            if self.config.diagram.expand_vss:
                dot_node.ntype = 'vss'
            else:
                # group VSS into one diagram node
                dot_node.peripheries = 2
        if node.stack.count:
            if self.config.diagram.expand_stackwise:
                dot_node.ntype = 'stackwise'
            else:
                # group Stackwise into one diagram node
                dot_node.peripheries = node.stack.count
        if node.vpc_domain and self.config.diagram.group_vpc:
            dot_node.ntype = 'vpc'
        if node.router:
            dot_node.shape = 'diamond'
        return dot_node

    def create_link(self, diagram, node, link, draw_as_lag):
        link_color = 'black'
        link_style = 'solid'
        link_label = ''
        if node.vpc_peerlink_if in [link.local_port, link.local_lag]:
            link_label += 'VPC'
        if draw_as_lag:
            link_label += 'LAG'
            members = 0
            for lnk in node.links:
                if lnk.local_lag == link.local_lag:
                    members += 1
            link_label += f"\n{str(members)} Members"
        else:
            link_label += f"Local:{link.local_port}\nRemote:{link.remote_port}"
        is_lag = True if link.local_lag != 'UNKNOWN' else False
        if draw_as_lag:
            # LAG as member
            if is_lag:
                local_lag_ip = ''
                remote_lag_ip = ''
                if len(link.local_lag_ips):
                    local_lag_ip = f" - {link.local_lag_ips[0]}"
                if len(link.remote_lag_ips):
                    remote_lag_ip = f" - {link.remote_lag_ips[0]}"
                link_label += '\nLAG Member'
                if not all([local_lag_ip, remote_lag_ip]):
                    link_label += f"\nLocal:{link.local_lag} | Remote:{link.remote_lag}"
                else:
                    link_label += f"\nLocal:{link.local_lag}{local_lag_ip}"
                    link_label += f"\nRemote:{link.remote_lag}{remote_lag_ip}"
            # IP Addresses
            if link.local_if_ip and link.local_if_ip != 'UNKNOWN':
                link_label += f"\nLocal:{link.local_if_ip}"
            if link.remote_if_ip and link.remote_if_ip != 'UNKNOWN':
                link_label += f"\nRemote:{link.remote_if_ip}"
        # LAG as group
        else:
            for lnk in node.links:
                if lnk.local_lag == link.local_lag:
                    link_label += f"\nLocal:{l.local_port} | Remote:{l.remote_port}"
            local_lag_ip = ''
            remote_lag_ip = ''
            if len(link.local_lag_ips):
                local_lag_ip = f" - {link.local_lag_ips[0]}"
            if len(link.remote_lag_ips):
                remote_lag_ip = f" - {link.remote_lag_ips[0]}"
            if not all([local_lag_ip, remote_lag_ip]):
                link_label += f"\nLocal:{link.local_lag} | Remote:{link.remote_lag}"
            else:
                link_label += f"\nLocal:{link.local_lag}{local_lag_ip}"
                link_label += f"\nRemote:{link.remote_lag}{remote_lag_ip}"
        if link.link_type == '1':
            # Trunk = Bold/Blue
            link_color = 'blue'
            link_style = 'bold'
            if link.local_native_vlan == link.remote_native_vlan:
                link_label += f"\nNative Match:{link.local_native_vlan}"
            elif not link.remote_native_vlan:
                link_label += f"\nNative Local:{link.local_native_vlan} Remote:None"
            else:
                link_label += f"\nNative Local:{link.local_native_vlan} Remote:{link.remote_native_vlan}"
            if link.local_allowed_vlans == link.remote_allowed_vlans:
                link_label += f"\nAllowed Match:{link.local_allowed_vlans}"
            else:
                link_label += f"\nAllowed Local:{link.local_allowed_vlans}"
                if link.remote_allowed_vlans:
                    link_label += f"\nAllowed Remote:{link.remote_allowed_vlans}"
        elif not link.link_type:
            # Routed = Bold/Red
            link_color = 'red'
            link_style = 'bold'
        else:
            # Switched access, include VLAN ID in label
            if link.vlan:
                link_label += f"\nVLAN {link.vlan}"
        edge_src = node.name
        edge_dst = link.node.name
        lmod = get_port_module(link.local_port)
        rmod = get_port_module(link.remote_port)
        if self.config.diagram.expand_vss:
            if node.vss.enabled:
                edge_src = f"{node.name}[VSS{lmod}]"
            if link.node.vss.enabled:
                edge_dst = f"{link.node.name}[VSS{rmod}]"
        if self.config.diagram.expand_stackwise:
            if node.stack.count:
                edge_src = f"{node.name}[SW{lmod}]"
            if link.node.stack.count:
                edge_dst = f"{link.node.name}[SW{rmod}]"
        edge = pydot.Edge(edge_src, edge_dst, dir='forward',
                          label=link_label,
                          color=link_color,
                          style=link_style)
        diagram.add_edge(edge)

    @staticmethod
    def devs_in_lag(lag_name, links):
        devs = []
        for link in links:
            if link.local_lag == lag_name:
                devs.append(link.node.name)
        return len(set(devs))

    def eval_if_block(self, if_cond, node):
        # evaluate condition
        if_cond_eval = if_cond.format(node=node, config=self.config).strip()
        try:
            if eval(if_cond_eval):
                return True
        except:
            if if_cond_eval not in ['0', 'None', '']:
                return True
            else:
                return False
        return False

    def format_node_text(self, node):
        '''
        Generate the node text given the format string 'fmt'
        '''
        temp = Template(node_template)
        return temp.render(node, self.config)
        while True:
            if_block = re.search('<%if ([^%]*): ([^%]*)%>', fmt)
            if not if_block:
                break
            if_cond = if_block[1]
            if_val = if_block[2]
            if not self.eval_if_block(if_cond, node):
                if_val = ''
            fmt = fmt[:if_block.span()[0]] + if_val + fmt[if_block.span()[1]:]
        ip = node.get_ipaddr()
        fmt = fmt.replace(node.ip, ip)
        # stackwise
        stack_block = re.search('<%stack ([^%]*)%>', fmt)
        if stack_block:
            if not node.stack.count:
                fmt = fmt[:stack_block.span()[0]] + fmt[stack_block.span()[1]:]
            else:
                val = ''
                if self.config.diagram.expand_stackwise and self.config.diagram.get_stack_members:
                    for smem in node.stack.members:
                        nval = stack_block[1]
                        nval = nval.replace(stack.num,    smem.num)
                        nval = nval.replace(stack.plat,   smem.plat)
                        nval = nval.replace(stack.serial, smem.serial)
                        nval = nval.replace(stack.role,   smem.role)
                        val += nval
                fmt = fmt[:stack_block.span()[0]] + val + fmt[stack_block.span()[1]:]
        # loopbacks
        loop_block = re.search('<%loopback ([^%]*)%>', fmt)
        if loop_block:
            val = ''
            for lo in node.loopbacks:
                for lo_ip in lo.ips:
                    nval = loop_block[1]
                    nval = nval.replace(lo.name, lo.name)
                    nval = nval.replace(lo.ip, lo_ip)
                    val += nval
            fmt = fmt[:loop_block.span()[0]] + val + fmt[loop_block.span()[1]:]
        # SVIs
        svi_block = re.search('<%svi ([^%]*)%>', fmt)
        if svi_block:
            val = ''
            for svi in node.svis:
                for svi_ip in svi.ip:
                    nval = svi_block[1]
                    nval = nval.replace(svi.vlan, svi.vlan)
                    nval = nval.replace(svi.ip, svi_ip)
                    val += nval
            fmt = fmt[:svi_block.span()[0]] + val + fmt[svi_block.span()[1]:]
        # replace {stack.} with magic
        fmt = re.sub('{stack\.(([a-zA-Z])*)}', '$stack2354$\g<1>$stack2354$', fmt)
        fmt = re.sub('{vss\.(([a-zA-Z])*)}', '$vss2354$\g<1>$vss2354$', fmt)
        # {node.} variables
        fmt = fmt.format(node=node)
        # replace magics
        fmt = re.sub('\$stack2354\$(([a-zA-Z])*)\$stack2354\$', '{stack.\g<1>}', fmt)
        fmt = re.sub('\$vss2354\$(([a-zA-Z])*)\$vss2354\$', '{vss.\g<1>}', fmt)
        return fmt
