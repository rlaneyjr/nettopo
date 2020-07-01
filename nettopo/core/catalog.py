# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    catalog.py
'''

from .config import Config
from .exceptions import NettopoCatalogError
from .network import Network
from .constants import NodeActions


class Catalog:
    def __init__(self, network: Network):
        if isinstance(network, Network):
            self.network = network
        else:
            try:
                self.network = Network(network)
            except:
                raise NettopoCatalogError(f"{network} not a valid Nettopo Network")
        self.config = self.network.config

    def generate(self, filename):
        with open(filename, 'w+') as f:
            for n in self.network.nodes:
                if not n.opts:
                    n.opts = NodeActions()
                n.query_node()
                # StackWise
                if n.stack.count:
                    for mem in n.stack.members:
                        serial = mem.serial or 'NOT CONFIGURED TO POLL'
                        plat = mem.plat or 'NOT CONFIGURED TO POLL'
                        f.write(f"{n.name},{n.ip[0]},{plat},{n.ios},{serial},STACK,{n.bootfile}\n")
                # VSS
                elif n.vss.enabled:
                    for i in range(0, 2):
                        serial = n.vss.members[i].serial
                        plat = n.vss.members[i].plat
                        ios = n.vss.members[i].ios
                        f.write(f"{n.name},{n.ip[0]},{plat},{ios},{serial},VSS,{n.bootfile}\n")
                # Stand Alone
                else:
                    f.write(f"{n.name},{n.ip[0]},{n.plat},{n.ios},{n.serial},SINGLE,{n.bootfile}\n")

