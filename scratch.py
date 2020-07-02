# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              scratch.py
'''
from nettopo.snmp import *
from nettopo.oids import *
from nettopo.hostinfo.device import HostInfo
from nettopo.core.snmp import NettopoSNMP

sw = NettopoSNMP(ip='10.0.0.1')
sw.community = 'letmeSNMP'
snmp = SnmpHandler(host=sw.ip, community=sw.community)

from nettopo.cdp import CdpNeighbors

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

