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
from nettopo.cdp import CdpNeighbors

snmp = SnmpHandler(host='10.0.0.1', community='letmeSNMP')
cdp = CdpNeighbors(snmp)
ne_dict = cdp.get_cdp_neighbors_dict()
ne_list = cdp.get_cdp_neighbors_list()
print(ne_dict)
print(ne_list)

vartable = cdp.getnext(o.cdpCacheEntry)
neighbors = {}
local_cdp_interfaces = []
for varbind in vartable:
    for oid, value in varbind:
        entry = oid.rsplit('.', 2)[-1]
        print(f"{oid}: {entry}")
        interface = oid.rsplit('.', 2)[-2]
        print(f"{oid}: {interface}")
        if entry not in neighbors.keys():
            neighbors[entry] = {}
            if interface not in local_cdp_interfaces:
                local_cdp_interfaces.append(interface)
                if interface not in neighbors[entry].keys():
                    neighbors[entry][interface] = {}
                if o.cdpCacheDeviceId in oid:
                    neighbors[entry][interface]['cdpCacheDeviceId'] = value
                if o.cdpCacheDevicePort in oid:
                    neighbors[entry][interface]['cdpCacheDevicePort'] = value
        print(neighbors)
        print(local_cdp_interfaces)

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


def pptable(table):
    ppt_items = []
    for thing in table:
        for item in thing:
            print(item.prettyPrint())
            ppt_items.append(item.prettyPrint())
    return ppt_items

# import ipdb
# ipdb.set_trace()
import binascii
from nettopo.core.constants import *
from nettopo.core.util import *
def get_cdp_neighbors(switch):
    neighbors = []
    switch.cache.cdp = switch.snmp.get_bulk(OID.CDP)
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


from nettopo.core.data import *
from nettopo.core.constants import *
from nettopo.core.util import *
def get_link(switch, ifidx):
    # ipdb.set_trace()
    link = LinkData()
    # trunk
    link.link_type = lookup_table(switch.cache.link_type,
                                  f"{OID.TRUNK_VTP}.{ifidx}")
    if link.link_type == '1':
        native_vlan = lookup_table(switch.cache.trunk_native,
                                   f"{OID.TRUNK_NATIVE}.{ifidx}")
        allowed_vlans = lookup_table(switch.cache.trunk_allowed,
                                     f"{OID.TRUNK_ALLOW}.{ifidx}")
        allowed_vlans = parse_allowed_vlans(allowed_vlans)
    else:
        native_vlan = None
        allowed_vlans = 'All'
    link.local_native_vlan = native_vlan
    link.local_allowed_vlans = allowed_vlans
    # LAG membership
    lag = lookup_table(switch.cache.lag, f"{OID.LAG_LACP}.{ifidx}")
    link.local_lag = switch.get_ifname(lag)
    link.local_lag_ips = switch.get_cidrs_ifidx(lag)
    # VLAN info
    link.vlan = lookup_table(switch.cache.vlan, f"{OID.IF_VLAN}.{ifidx}")
    # IP address
    lifips = switch.get_cidrs_ifidx(ifidx)
    link.local_if_ip = lifips[0] if lifips else None
    link.remote_lag_ips = []
    return link


from nettopo.core.constants import *
from nettopo.core.util import *
def get_cidrs_ifidx(switch, ifidx):
    ips = []
    for ifrow in switch.cache.ifip:
        for ifn, ifv in ifrow:
            ifn = str(ifn)
            if ifn.startswith(OID.IF_IP_ADDR):
                if str(ifv) == str(ifidx):
                    t = ifn.split('.')
                    ip = ".".join(t[10:])
                    mask = lookup_table(switch.cache.ifip,
                                        f"{OID.IF_IP_NETM}{ip}")
                    nbits = bits_from_mask(mask)
                    cidr = f"{ip}/{nbits}"
                    ips.append(cidr)
        return ips

def snmp_extract(snmp_data):
    '''
    Unwrap the SNMP response data and return in a readable format
    Assumes only a single list element is returned
    '''
    if len(snmp_data) > 1:
        raise ValueError("snmp_extract only allows a single element")
    if len(snmp_data) == 0:
        return None
    else:
        # Unwrap the data which is returned as a tuple wrapped in a list
        return snmp_data[0][1].prettyPrint()


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

from nettopo.snmp.snmpclient import *
load_default_mibs()
sw1 = SnmpClient('10.0.0.1')
sw1.parse_descr()
sw1.parse_sys()

