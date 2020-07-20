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

from nettopo.core.node import Node
sw1 = Node('10.0.0.1')
sw2 = Node('10.0.0.2')
sw1.get_snmp_creds('letmeSNMP')
sw2.get_snmp_creds('letmeSNMP')
sw1.query_node()
sw2.query_node()

from nettopo.core.nettopo import Nettopo
net = Nettopo()
net.add_snmp_credential('letmeSNMP')
net.set_discover_maxdepth(100)
net.discover_network('10.0.0.1', True)


import ipdb
from nettopo.core.constants import *
from nettopo.core.util import *
def get_cdp_neighbors(switch):
    """ Get a list of CDP neighbors.
    Returns a list of LinkData's.
    Will always return an array.
    """
    # get list of CDP neighbors
    neighbors = []
    switch.cache.cdp = switch.snmp.get_bulk(OID.CDP)
    ipdb.set_trace()
    if not switch.cache.cdp:
        print('No CDP Neighbors Found.')
        return []
    for row in switch.cache.cdp:
        for oid, val in row:
            oid = str(oid)
            # process only if this row is a CDP_DEVID
            if oid.startswith(OID.CDP_DEVID):
                continue
            t = oid.split('.')
            ifidx = t[14]
            ifidx2 = t[15]
            idx = f".{ifidx}.{ifidx2}"
            # get remote IP
            rip = lookup_table(switch.cache.cdp, f"{OID.CDP_IPADDR}{idx}")
            rip = ip_2_str(rip)
            # get local port
            lport = switch.get_ifname(ifidx)
            # get remote port
            rport = lookup_table(switch.cache.cdp, f"{OID.CDP_DEVPORT}{idx}")
            rport = normalize_port(rport)
            # get remote platform
            rplat = lookup_table(switch.cache.cdp, f"{OID.CDP_DEVPLAT}{idx}")
            # get IOS version
            rios = lookup_table(switch.cache.cdp, f"{OID.CDP_IOS}{idx}")
            if rios:
                try:
                    rios = binascii.unhexlify(rios[2:])
                except:
                    pass
                rios = format_ios_ver(rios)
                link = switch.get_link(ifidx)
                link.remote_name = val.prettyPrint()
                link.remote_ip = rip
                link.discovered_proto = 'cdp'
                link.local_port = lport
                link.remote_port = rport
                link.remote_plat = rplat
                link.remote_ios = rios
                neighbors.append(link)
        return neighbors
