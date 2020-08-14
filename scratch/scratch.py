# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              scratch.py
'''
from nettopo.snmp import *
from nettopo.oids import *
from nettopo.hostinfo.device import HostInfo
from nettopo.core.snmp import SNMP

sw = NettopoSNMP(ip='10.0.0.1')
sw.community = 'letmeSNMP'

from nettopo.snmp.snmp import SnmpHandler
from nettopo.actions.cdp import CdpNeighbors

snmp = SnmpHandler(host='10.0.0.1', community='letmeSNMP')
cdp = CdpNeighbors(snmp)
ne_dict = cdp.get_cdp_neighbors_dict()
ne_list = cdp.get_cdp_neighbors_list()
print(ne_dict)
print(ne_list)

from nettopo.core.data import VLANData
vlan = VLANData(22, 'flynet')
vlan._as_dict()
vlan.show()
vlan._as_dict().items()

from nettopo.core.node import Node
sw1 = Node('10.0.0.1')
sw1.get_snmp_creds('letmeSNMP')
sw1.query_node()

sw2 = Node('10.0.0.2')
sw2.get_snmp_creds('letmeSNMP')
sw2.query_node()

from nettopo.core.nettopo import Nettopo
net = Nettopo()
net.add_snmp_credential('letmeSNMP')
net.set_discover_maxdepth(100)
net.discover_network('10.0.0.1', True)

from snimpy.manager import Manager, load
from nettopo.sysdescrparser import sysdescrparser
mibs = ['SNMPv2-MIB', 'IF-MIB', 'IP-MIB', 'ENTITY-MIB', 'IP-FORWARD-MIB', 'NHRP-MIB', 'POWER-ETHERNET-MIB', 'TUNNEL-MIB', 'VRRP-MIB', 'ENTITY-MIB', 'INET-ADDRESS-MIB']
for i in mibs:
    try:
        load(i)
    except:
        print(f"Unable to load {i}")

sw1 = Manager('10.0.0.1', 'letmeSNMP', retries=2, timeout=3)
print(sw1.sysDescr)
sw1_sys = sysdescrparser(str(sw1.sysDescr))
print(sw1_sys.vendor)
print(sw1_sys.model)
print(sw1_sys.version)
print(sw1_sys.os)

from nettopo.snmp.snmpclient import SnmpClient
sw1 = SnmpClient('10.0.0.1')
sw1.parse_descr()
sw1.parse_sys()