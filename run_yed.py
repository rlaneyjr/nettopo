# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

from N2G import yed_diagram

diagram = yed_diagram()
sample_graph={
'nodes': [
    {'id': 'r1', 'pic': 'router.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'R1' },
    {'id': 'sw1', 'pic': 'router.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'SW1', 'description': 'role: dist' },
    {'id': 'sw2', 'pic': 'switch.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'SW2', 'description': 'role: access' },
    {'id': 'fw1', 'pic': 'security-firewall.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'FW1', 'description': 'location: US'},
    {'id': 'r4', 'pic': 'router.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'R4' },
    {'id': 'host', 'pic': 'generic-host.svg', 'pic_path': './nettopo/icons/cisco/blue/', 'label': 'HOST' }
],
'links': [
    {'source': 'r1', 'src_label': 'Gig0/0\nUP', 'label': 'INET', 'target': 'sw1', 'trgt_label': 'Gig0/1', 'description': 'role: INET' },
    {'source': 'r4', 'src_label': 'Gig0/0', 'label': 'MPLS', 'target': 'sw1', 'trgt_label': 'Gig0/2', 'description': 'role: MPLS'},
    {'source': 'sw1', 'src_label': 'Gig0/0', 'label': 'Outside', 'target': 'fw1', 'trgt_label': 'Gig0/1'},
    {'source': 'fw1', 'src_label': 'Gig0/2', 'label': 'Inside', 'target': 'sw2', 'trgt_label': 'Gig0/0'},
    {'source': 'sw2', 'src_label': 'Gig0/11', 'target': 'host', 'trgt_label': 'Port 1'}
]}
diagram.from_dict(sample_graph)
diagram.layout(algo="kk")
diagram.dump_file(filename="Sample_graph.graphml", folder="./")

