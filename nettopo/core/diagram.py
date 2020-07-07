# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    diagram.py
'''
import pydot
import datetime
from jinja2 import Template, Environment
import os

from .config import DiagramDefaults
from .data import DotNode
from .network import Network
from .templates import node_template, credits_template, link_template
from .util import get_path, get_port_module


class Diagram:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.config = network.config.diagram or DiagramDefaults()

    def generate(self, dot_file, title):
        self.network.reset_discovered()
        title_text_size = self.config.title_text_size
        date_text_size = title_text_size - 2
        today = datetime.datetime.now()
        today = today.strftime('%Y-%m-%d %H:%M')
        credits = Template(credits_template)
        credits = credits.render(title_text_size=title_text_size,
                                 date_text_size=date_text_size,
                                 title=title,
                                 today=today)
        node_text_size = self.config.node_text_size
        link_text_size = self.config.link_text_size
        diagram = pydot.Dot(graph_type='graph',
                            labelloc='b',
                            labeljust='r',
                            fontsize=node_text_size,
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

    def build(self, diagram, node):
        # if not node:
        #     return 0, 0
        # if node.discovered:
        #     return 0, 0
        # node.discovered = 1
        dot_node = self.create_node(node)
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
                                    fontsize=self.config.node_text_size,
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
                                    fontsize=self.config.node_text_size,
                                    label=f"<<br /><b>VPC {node.vpc_domain}</b>>")
            cluster.add_node(pydot.Node(
                             name=node.name,
                             label=f"<{dot_node.label}>",
                             style=dot_node.style,
                             shape=dot_node.shape,
                             peripheries=dot_node.peripheries))
            if node.vpc_peerlink_node:
                node2 = node.vpc_peerlink_node
                # node2.discovered = 1
                dot_node2 = self.create_node(node2)
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
                                    fontsize=self.config.node_text_size,
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
            if any([self.config.expand_lag,
                    link.local_lag == 'UNKNOWN',
                    self.lag_in_links(link.local_lag, node.links)]):
                # a LAG could span different devices, eg Nexus.
                # in this case we should always break it out, otherwise we could
                # get an unlinked node in the diagram.
                edge = self.create_link(node, link, True)
            else:
                if link.local_lag not in lags:
                    lags.append(link.local_lag)
                    edge = self.create_link(node, link, False)
        diagram.add_edge(edge)

    def create_node(self, node):
        dot_node = DotNode()
        # get the node text
        # env = Environment()
        # temp = env.from_string(node_template)
        temp = Template(node_template)
        dot_node.label = temp.render(node=node, config=self.config)
        # set the node properties
        if node.vss.enabled:
            if self.config.expand_vss:
                dot_node.ntype = 'vss'
            else:
                # group VSS into one diagram node
                dot_node.peripheries = 2
        if node.stack.enabled:
            if self.config.expand_stackwise:
                dot_node.ntype = 'stackwise'
            else:
                # group Stackwise into one diagram node
                dot_node.peripheries = node.stack.count
        if node.vpc_domain and self.config.group_vpc:
            dot_node.ntype = 'vpc'
        if node.router:
            dot_node.shape = 'diamond'
        return dot_node

    def create_link(self, node, link, is_lag):
        lag_members = len([lnk for lnk in node.links if lnk.local_lag == link.local_lag])
        temp = Template(link_template)
        link_label = temp.render(node=node, link=link, is_lag=is_lag,
                                 lag_members=lag_members)
        if link.link_type == '1':
            # Trunk = Bold/Blue
            link_color = 'blue'
            link_style = 'bold'
        elif not link.link_type:
            # Routed = Bold/Red
            link_color = 'red'
            link_style = 'bold'
        else:
            link_color = 'black'
            link_style = 'solid'
        edge_src = node.name
        edge_dst = link.node.name
        lmod = get_port_module(link.local_port)
        rmod = get_port_module(link.remote_port)
        if self.config.expand_vss:
            if node.vss.enabled:
                edge_src = f"{node.name}[VSS{lmod}]"
            if link.node.vss.enabled:
                edge_dst = f"{link.node.name}[VSS{rmod}]"
        if self.config.expand_stackwise:
            if node.stack.count:
                edge_src = f"{node.name}[SW{lmod}]"
            if link.node.stack.count:
                edge_dst = f"{link.node.name}[SW{rmod}]"
        edge = pydot.Edge(edge_src, edge_dst, dir='forward',
                          label=link_label,
                          color=link_color,
                          style=link_style)
        return edge

    @staticmethod
    def lag_in_links(lag_name, links):
        devs = [link.node.name for link in links if lag_name in link.local_lag]
        return True if devs else False

"""
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
                if self.config.expand_stackwise and self.config.get_stack_members:
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
"""
