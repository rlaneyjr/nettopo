# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    catalog.py
'''
import os
from nettopo.core.exceptions import NettopoCatalogError
from nettopo.core.network import Network


class Catalog:
    def __init__(self, network: Network):
        if isinstance(network, Network):
            self.network = network
        else:
            try:
                self.network = Network(network)
            except:
                raise NettopoCatalogError(f"{network} not a valid Nettopo \
                                                                    Network")


    def generate(self, filename=None):
        lines = []
        for node in self.network.nodes:
            if not node.queried:
                node.query_node()
            # StackWise
            if node.stack.enabled:
                for mem in node.stack.members:
                    serial = mem.serial or 'Unknown'
                    plat = mem.plat or 'Unknown'
                    lines.append(f"{node.name},{node.ip[0]},{plat},{node.ios}, \
                                        {serial},STACK,{node.bootfile}\n")
            # VSS
            elif node.vss.enabled:
                for i in range(0, 2):
                    serial = node.vss.members[i].serial
                    plat = node.vss.members[i].plat
                    ios = node.vss.members[i].ios
                    lines.append(f"{node.name},{node.ip[0]},{plat},{ios}, \
                                       {serial},VSS,{node.bootfile}\n")
            # Stand Alone
            else:
                lines.append(f"{node.name},{node.ip[0]},{node.plat}, \
                        {node.ios},{node.serial},SINGLE,{node.bootfile}\n")
        if filename and os.path.isfile(filename):
            with open(filename, 'w+') as f:
                for line in lines:
                    f.write(line)
        else:
            for line in lines:
                print(line)
