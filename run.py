# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

# from nettopo.core.node import Node, Nodes
# sw1 = Node('10.0.0.1', community='letmeSNMP')
# sw1.query_node()
# sw2 = Node('10.0.0.2', community='letmeSNMP')
# sw2.query_node()
# nodes = Nodes([sw1, sw2])

from nettopo.core.network import NettopoNetwork
net = NettopoNetwork('10.0.0.0/24')
net.discover('10.0.0.1')
net.nodes.rows()

