# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    diagram.py
'''
import pydot
import datetime
from jinja2 import Template, Environment
import os

from nettopo.core.exceptions import NettopoDiagramError
from nettopo.core.config import DiagramDefaults
from nettopo.core.network import Network
from nettopo.core.templates import (
    node_template,
    credits_template,
    link_template,
)
from nettopo.core.util import get_path, get_port_module

"""
from N2G import yed_diagram

diagram = yed_diagram()
sample_list_graph = [
    {'source': {'id': 'SW1', 'top_label': 'CORE', 'bottom_label': '1,1,1,1'}, 'src_label': 'Gig0/0', 'target': 'R1', 'trgt_label': 'Gig0/1'},
    {'source': {'id': 'R2', 'top_label': 'DC-PE'}, 'src_label': 'Gig0/0', 'target': 'SW1', 'trgt_label': 'Gig0/2'},
    {'source': {'id':'R3', 'bottom_label': '1.1.1.3'}, 'src_label': 'Gig0/0', 'target': 'SW1', 'trgt_label': 'Gig0/3'},
    {'source': 'SW1', 'src_label': 'Gig0/4', 'target': 'R4', 'trgt_label': 'Gig0/1'},
    {'source': 'SW1', 'src_label': 'Gig0/5', 'target': 'R5', 'trgt_label': 'Gig0/7'},
    {'source': 'SW1', 'src_label': 'Gig0/6', 'target': 'R6', 'trgt_label': 'Gig0/11'}
]
diagram.from_list(sample_list_graph)
diagram.dump_file(filename="Sample_graph.graphml", folder="./")


from_dict:
Method to build graph from dictionary.
**Parameters**
* ``data`` (dict) dictionary with nodes and link/edges details.
Example ``data`` dictionary::
sample_graph = {
    'nodes': [
        {
            'id': 'a',
            'pic': 'router',
            'label': 'R1'
        },
        {
            'id': 'b',
            'label': 'somelabel',
            'bottom_label':'botlabel',
            'top_label':'toplabel',
            'description': 'some node description'
        },
        {
            'id': 'e',
            'label': 'E'
        }
    ],
    'edges': [
        {
            'source': 'a',
            'src_label': 'Gig0/0',
            'label': 'DF',
            'target': 'b',
            'trgt_label': 'Gig0/1',
            'description': 'vlans_trunked: 1,2,3'
        }
    ],
    'links': [
        {
            'source': 'a',
            'target': 'e'
        }
    ]
}
"""

class DotNode:
    ''' Represents a network node for a DOT diagram
    '''
    def __init__(self, node, config):
        self.node = node
        self.config = config
        self.ntype = 'single'
        self.shape = 'diamond' if self.node.router else 'ellipse'
        self.style = 'solid'
        self.peripheries = 1
        # set the node properties
        if self.node.vss.enabled:
            if self.config.expand_vss:
                self.ntype = 'vss'
            else:
                # group VSS into one diagram node
                self.peripheries = 2
        if self.node.stack.enabled:
            if self.config.expand_stackwise:
                self.ntype = 'stackwise'
            else:
                # group Stackwise into one diagram node
                self.peripheries = self.node.stack.count
        if self.node.vpc_domain and self.config.group_vpc:
            self.ntype = 'vpc'

    @property
    def label(self):
        return self.label

    @label.setter
    def label(self):
        template = Template(node_template)
        # env = Environment()
        # temp = env.from_string(node_template)
        return template.render(node=self.node, config=self.config)


class Diagram:
    def __init__(self, network: Network) -> None:
        self.network = network
        self.config = self.network.config.diagram or DiagramDefaults()


    def generate(self, dot_file, title):
        self.network.reset_discovered()
        title_text_size = self.config.title_text_size
        date_text_size = title_text_size - 2
        today = datetime.datetime.now()
        today = today.strftime('%Y-%m-%d %H:%M')
        credit_temp = Template(credits_template)
        credits = credit_temp.render(title_text_size=title_text_size,
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
            func_name = f"write_{file_ext.lstrip('.')}"
            # write_'format'(path, prog='program')
            if func_name in diagram.__dir__():
                output_func = getattr(diagram, func_name)
                output_func(f)
                print(f"Created diagram: {f}")
            else:
                raise NettopoDiagramError(f"Error: Output type {file_ext} \
                                                            does not exist.")


    @staticmethod
    def lag_in_links(lag_name, links):
        devs = [link.node.name for link in links if lag_name in link.local_lag]
        return True if devs else False


    def build(self, diagram, node):
        dot_node = DotNode(node, self.config)
        if dot_node.ntype == 'single':
            diagram.add_node(pydot.Node(name=node.name,
                                        label=f"<{dot_node.label}>",
                                        style=dot_node.style,
                                        shape=dot_node.shape,
                                        peripheries=dot_node.peripheries))
        elif dot_node.ntype == 'vss':
            vss_label = f"<<br /><b>VSS {node.vss.domain}</b>>"
            cluster = pydot.Cluster(graph_name=node.name,
                                    suppress_disconnected=False,
                                    labelloc='t', labeljust='c',
                                    fontsize=self.config.node_text_size,
                                    label=vss_label)
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
            vpc_label = f"<<br /><b>VPC {node.vpc_domain}</b>>"
            cluster = pydot.Cluster(graph_name=node.name,
                                    suppress_disconnected=False,
                                    labelloc='t',
                                    labeljust='c',
                                    fontsize=self.config.node_text_size,
                                    label=vpc_label)
            cluster.add_node(pydot.Node(
                             name=node.name,
                             label=f"<{dot_node.label}>",
                             style=dot_node.style,
                             shape=dot_node.shape,
                             peripheries=dot_node.peripheries))
            if node.vpc_peerlink_node:
                node2 = node.vpc_peerlink_node
                # node2.queried = 1
                dot_node2 = DotNode(node2)
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
        for link in node.links:
            self.build(diagram, link.node)
            # determine if this link should be broken out or not
            if any([self.config.expand_lag,
                    link.local_lag == 'Unknown',
                    self.lag_in_links(link.local_lag, node.links)]):
                # a LAG could span different devices, eg Nexus.
                # in this case we always break it out, otherwise we could
                # get an unlinked node in the diagram.
                edge = self.create_link(node, link, True)
            else:
                edge = self.create_link(node, link, False)
            diagram.add_edge(edge)


    def create_link(self, node, link, is_lag):
        lag_members = len([lnk for lnk in node.links
                           if lnk.local_lag == link.local_lag])
        template = Template(link_template)
        link_label = template.render(node=node, link=link, is_lag=is_lag,
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
            if node.vss:
                edge_src = f"{node.name}[VSS{lmod}]"
            if link.node.vss:
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
