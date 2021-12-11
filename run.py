# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

# from nettopo.core.node import Node, Nodes
# sw1 = Node('10.0.0.1', community='letmeSNMP')
# sw1.query_node()
# sw2 = Node('10.0.0.2', community='letmeSNMP')
# sw2.query_node()
# nodes = Nodes([sw1, sw2])

from nettopo.core.nettopo import Nettopo
net = Nettopo('192.168.255.0/24')
net.discover_network('192.168.255.1')

# from pprint import pprint
# from nettopo.core.node import Node
# from nettopo.core.data import DataTable
# sw1 = Node('10.0.0.1', community='letmeSNMP')
# sw1.query_node(bar=True)
# sw1.links.rows()
# cdp = DataTable(sw1.get_cdp())
# lldp = DataTable(sw1.get_lldp())
# pprint("CDP rows")
# cdp.rows()
# pprint("LLDP rows")
# lldp.rows()
# pprint("LLDP rows")
# pprint(" ")
# pprint("CDP as DICT")
# for l in cdp:
#     pprint(l._as_dict())
# pprint("LLDP as DICT")
# for l in lldp:
#     pprint(l._as_dict())
