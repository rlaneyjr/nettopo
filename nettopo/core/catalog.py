# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    catalog.py
'''
from .exceptions import NettopoCatalogError
from .network import Network
from .data import NodeActions


class Catalog:
    def __init__(self, network: Network):
        if isinstance(network, Network):
            self.network = network
        else:
            try:
                self.network = Network(network)
            except:
                raise NettopoCatalogError(f"{network} not a valid Nettopo Network")

    def generate(self, filename):
        with open(filename, 'w+') as f:
            for node in self.network.nodes:
                if not node.opts:
                    node.opts = NodeActions()
                node.query_node()
                # StackWise
                if node.stack.count:
                    for mem in node.stack.members:
                        serial = mem.serial or 'NotPolled'
                        plat = mem.plat or 'NotPolled'
                        f.write(f"{node.name},{node.ip[0]},{plat},{node.ios}, \
                                            {serial},STACK,{node.bootfile}\n")
                # VSS
                elif node.vss.enabled:
                    for i in range(0, 2):
                        serial = node.vss.members[i].serial
                        plat = node.vss.members[i].plat
                        ios = node.vss.members[i].ios
                        f.write(f"{node.name},{node.ip[0]},{plat},{ios}, \
\                                           {serial},VSS,{node.bootfile}\n")
                # Stand Alone
                else:
                    f.write(f"{node.name},{node.ip[0]},{node.plat}, \
                            {node.ios},{node.serial},SINGLE,{node.bootfile}\n")
