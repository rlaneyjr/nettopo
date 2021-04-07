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

def pp_table(table):
    for row in table:
        for n,v in row:
            print(f"{n}: {v.prettyPrint()}")

from nettopo.core.node import Node
sw1 = Node('10.0.0.1')
sw1.query_node()
sw2 = Node('10.0.0.2')
sw2.query_node()

from nettopo.core.util import *
from nettopo.oids import Oids
o = Oids()
rip = sw1.get_cached_item('cdp', f"{o.CDP_IPADDR}")

sw2.get_snmp_creds('letmeSNMP')

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


from nettopo.core.snmp import SNMP
from nettopo.oids import Oids
o = Oids()
sw1 = SNMP('10.0.0.1')
sw2 = SNMP('10.0.0.2')
ifname_cache = sw1.get_bulk(o.IFNAME)
ifname_cache2 = sw2.get_bulk(o.IFNAME)
ifip_cache = sw1.get_bulk(o.IF_IP)
ifip_cache2 = sw2.get_bulk(o.IF_IP)
ethif_cache = sw1.get_bulk(o.ETH_IF)
ethif_cache2 = sw2.get_bulk(o.ETH_IF)
ip_cache = sw1.get_bulk(o.IP)
ip_cache2 = sw2.get_bulk(o.IP)
pp_table(ifname_cache)
pp_table(ifname_cache2)
pp_table(ifip_cache)
pp_table(ifip_cache2)
pp_table(ethif_cache)
pp_table(ethif_cache2)
pp_table(ip_cache)
pp_table(ip_cache2)

def cache_out(name, cache):
    with open(f'./{name}_cache.txt', 'w+') as out:
        out.write(f"SNMP {name} table:\n")
        for row in cache:
            for n,v in row:
                out.write(f"{n} = {v.prettyPrint()}\n")
        out.write("\n")
cache_out('sw1_ifname', ifname_cache)
cache_out('sw2_ifname', ifname_cache2)
cache_out('sw1_ifip', ifip_cache)
cache_out('sw2_ifip', ifip_cache2)
cache_out('sw1_ethif', ethif_cache)
cache_out('sw2_ethif', ethif_cache2)
cache_out('sw1_ip', ip_cache)
cache_out('sw2_ip', ip_cache2)

ifname_table = TableBuilder('ifname', ifname_cache)
ifname_table2 = TableBuilder('ifname2', ifname_cache2)
ifip_table = TableBuilder('ifip', ifip_cache)
ifip_table2 = TableBuilder('ifip2', ifip_cache2)
ethif_table = TableBuilder('ethif', ethif_cache)
ethif_table2 = TableBuilder('ethif2', ethif_cache2)
ip_table = TableBuilder('ip', ip_cache)
ip_table2 = TableBuilder('ip2', ip_cache2)

from nettopo.core.snmp import SNMP
from nettopo.oids import Oids, GeneralOids, CiscoOids
o = Oids()
g = GeneralOids()
c = CiscoOids()
sw1 = SNMP('10.0.0.1', community='letmeSNMP')
sw1_vlans = TableBuilder('sw1_vlans', sw1.get_bulk(o.VLANS))
sw1_vlans
sw1_vlans.table
len(sw1_vlans)
sw1_vlandesc = TableBuilder('sw1_vlandesc', sw1.get_bulk(o.VLAN_DESC))
len(sw1_vlandesc)
sw1_vlandesc.table
o.VLANS
o.VLAN_DESC
g.entPhysicalName
c.cL2L3IfModeAdmin
c.vtpVlanState
c.vtpVlanName
c.vtpVlanIndex
sw1.get_bulk(c.vtpVlanIndex)
sw1.get_bulk(c.vtpVlanName)

In [24]: c.vtpVlanIndex
Out[24]: '1.3.6.1.4.1.9.9.46.1.3.1.1.1'
In [25]: c.vtpVlanName
Out[25]: '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
In [26]: c_vlans = sw1.get_bulk('1.3.6.1.4.1.9.9.46.1.3.1.1')

from nettopo.core.node import Node
sw1 = Node('10.0.0.1', community='letmeSNMP')
sw1.query_node()
sw2 = Node('10.0.0.2', community='letmeSNMP')
sw2.query_node()

del sw1
from nettopo.core.snmp import SNMP
from nettopo.oids import Oids, GeneralOids, CiscoOids
o = Oids()
g = GeneralOids()
c = CiscoOids()
sw1 = SNMP('10.0.0.1', community='letmeSNMP')

_arp_table = '1.3.6.1.2.1.4.22'
_arp_entry = '1.3.6.1.2.1.4.22.1'
_arp_vlan = '1.3.6.1.2.1.4.22.1.1'
_arp_mac = '1.3.6.1.2.1.4.22.1.2'
_arp_ip = '1.3.6.1.2.1.4.22.1.3'
_arp_type = '1.3.6.1.2.1.4.22.1.4'
_arp_oid = '1.3.6.1.2.1.3.1.1.2'
