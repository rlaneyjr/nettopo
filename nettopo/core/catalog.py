# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    catalog.py
'''
import os
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
                raise NettopoCatalogError(f"{network} not a valid Nettopo \
                                                                    Network")


    def _print(lines, filename=None):
        if filename and os.path.isfile(filename):
            with open(filename, 'w+') as f:
                for line in lines:
                    return f.write(line)
        else:
            for line in lines:
                return print(line)


    def generate(self, filename=None):
        lines = []
        for node in self.network.nodes:
            # node.query_node()
            # StackWise
            if node.stack:
                for mem in node.stack.members:
                    serial = mem.serial or 'NotPolled'
                    plat = mem.plat or 'NotPolled'
                    lines.append(f"{node.name},{node.ip[0]},{plat},{node.ios}, \
                                        {serial},STACK,{node.bootfile}\n")
            # VSS
            elif node.vss:
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
        _print(lines, filename)
