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
if_des = sw1.ifDescr
for item in if_des.items():
    k = item[0]
    v = item[1]
    if not v.startswith('unrouted'):
        print(f"{k}: {v}")


from nettopo.snmp.snmpclient import SnmpClient
sw1 = SnmpClient('10.0.0.1')
sw1.parse_descr()
sw1.parse_sys()

from nettopo.pyconfig import *
from nettopo import quicksnmp
from pysnmp.hlapi import CommunityData
com = CommunityData('letmeSNMP')
rawInterfacesTable = quicksnmp.get('10.0.0.1', interfaces_table_named_oid, com)
for row in rawInterfacesTable:
    for item in row:
        print(' = '.join([x.prettyPrint() for x in item]))


from nettopo.actions.scan import Scan
net = Scan('10.0.22.0/24')
net.arp_scan()
net.hosts


from nettopo.snmp_facts import SnmpFacts
sw = SnmpFacts('10.0.0.1', community='letmeSNMP')
sw.get_facts()

from nettopo.actions.async_runner import AsyncRunner
cmds = ['sh ip route', 'sh ip int br', 'sh mac address-table', 'sh ip arp']
sw1 = AsyncRunner('10.0.0.1', 'rlaney', 'ralrox22')
sw2 = AsyncRunner('10.0.0.2', 'rlaney', 'ralrox22')
sw1.login()
sw2.login()

print(sw1.device_type)
print(sw2.device_type)

#############################################################
from nettopo.core.snmp import multi_node_bulk_query, SnmpHandler, SNMP
sw1 = SNMP('10.0.0.1')
sw2 = SNMP('10.0.0.2')
sw1.community = 'letmeSNMP'
sw2.community = 'letmeSNMP'
hosts = [sw1,sw2]
multi_node_bulk_query(hosts)

