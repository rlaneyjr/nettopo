# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    node.py
'''
from functools import cached_property
from typing import Union
from .cache import Cache
from .data import LinkData, StackData
from .snmp import SNMP
from .util import (timethis,
                   bits_from_mask,
                   normalize_host,
                   normalize_port,
                   ip_2_str,
                   ip_from_cidr,
                   format_ios_ver,
                   mac_hex_to_ascii,
                   mac_format_cisco,
                   parse_allowed_vlans,
                   lookup_table,
                   oid_last_token)
from .data import (NodeActions,
                   BaseData,
                   LinkData,
                   SVIData,
                   LoopBackData,
                   VLANData,
                   ARPData)
from .stack import Stack
from .vss import VSS
from .constants import OID, ARP, DCODE, NODE


class Node(BaseData):
    def __init__(self, ip: Union[str, list]) -> None:
        self.ip = ip if isinstance(ip, list) else [ip]
        self.snmpobj = None
        self.cache = None
        self.actions = NodeActions()
        self.links = []
        self.svis = []
        self.loopbacks = []
        self.discovered = False
        self.stack = None
        self.vss = None
        self.name = None
        self.name_raw = None
        self.plat = None
        self.ios = None
        self.router = None
        self.ospf_id = None
        self.bgp_las = None
        self.hsrp_pri = None
        self.hsrp_vip = None
        self.serial = None
        self.bootfile = None
        self.vpc_peerlink_if = None
        self.vpc_peerlink_node = None
        self.vpc_domain = None
        self.items_2_show = ['name', 'ip', 'plat', 'ios',
                             'serial', 'router', 'vss', 'stack']

    def add_link(self, link):
        self.links.append(link)

    def get_snmp_creds(self, snmp_creds):
        """ find valid credentials for this node.
        try each known IP until one works
        """
        if not self.snmpobj.success:
            for ipaddr in self.ip:
                if ipaddr in ['0.0.0.0', 'UNKNOWN', '']:
                    continue
                self.snmpobj.ip = ipaddr
                if self.snmpobj.get_creds(snmp_creds):
                    return True
        return False

    def query_node(self):
        """ Query this node.
        Set .actions and .snmp_creds before calling.
        """
        if not self.snmpobj:
            self.snmpobj = SNMP(self.ip[0])
            if not snmpobj.success:
                # failed to find good creds
                return False
        if not self.cache:
            self.cache = Cache(self.snmpobj)

        if self.actions.get_name:
            self.name_raw = self.cache.name
            self.name = normalize_host(self.name_raw)
        # router
        if self.actions.get_router:
            self.router = self.cache.router
            if self.router:
                # OSPF
                if self.actions.get_ospf_id:
                    self.ospf_id = self.cache.ospf_id
                # BGP
                if self.actions.get_bgp_las:
                    self.bgp_las = self.cache.bgp
                # HSRP
                if self.actions.get_hsrp_pri:
                    self.hsrp_pri = self.cache.hsrp
                    self.hsrp_vip = self.cache.hsrp_vip
        # stack
        if self.actions.get_stack:
            self.stack = self.cache.stack
        # vss
        if self.actions.get_vss:
            self.vss = self.cache.vss
        # serial
        if self.actions.get_serial and not all([self.stack.count,
                                                self.vss.enabled]):
            self.serial = self.cache.serial
        # SVI
        if self.actions.get_svi:
            self.cache.svi
            for row in self.cache.svi:
                for n, v in row:
                    n = str(n)
                    vlan = n.split('.')[14]
                    svi = SVIData(vlan)
                    svi_ips = self.get_cidrs_ifidx(v)
                    svi.ip.extend(svi_ips)
                    self.svis.append(svi)
        # loopback
        if self.actions.get_lo:
            self.cache.ethif
            self.cache.ifip
            for row in self.cache.ethif:
                for n, v in row:
                    n = str(n)
                    if n.startswith(OID.ETH_IF_TYPE) and v == 24:
                        ifidx = n.split('.')[10]
                        lo_name = lookup_table(self.cache.ethif,
                                               f"{OID.ETH_IF_DESC}.{ifidx}")
                        lo_ips = self.get_cidrs_ifidx(ifidx)
                        lo = LoopBackData(lo_name, lo_ips)
                        self.loopbacks.append(lo)
        # bootfile
        if self.actions.get_bootf:
            self.bootfile = self.cache.bootfile
        # chassis info (serial, IOS, platform)
        if self.actions.get_chassis_info:
            self.get_chassis()
        # VPC peerlink
        if self.actions.get_vpc:
            self.vpc_domain, self.vpc_peerlink_if = self.get_vpc(self.cache.ethif)
        return True

    def get_cidrs_ifidx(self, ifidx):
        ips = []
        for ifrow in self.cache.ifip:
            for ifn, ifv in ifrow:
                ifn = str(ifn)
                if ifn.startswith(OID.IF_IP_ADDR):
                    if str(ifv) == str(ifidx):
                        t = ifn.split('.')
                        ip = ".".join(t[10:])
                        mask = lookup_table(self.cache.ifip,
                                            f"{OID.IF_IP_NETM}{ip}")
                        nbits = bits_from_mask(mask)
                        cidr = f"{ip}/{nbits}"
                        ips.append(cidr)
        return ips


    def get_cdp_neighbors(self):
        ''' Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        '''
        # get list of CDP neighbors
        neighbors = []
        self.cache.cdp = self.snmpobj.get_bulk(OID.CDP)
        if not self.cache.cdp:
            print('No CDP Neighbors Found.')
            return []
        for row in self.cache.cdp:
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
                rip = lookup_table(self.cache.cdp, f"{OID.CDP_IPADDR}{idx}")
                rip = ip_2_str(rip)
                # get local port
                lport = self.get_ifname(ifidx)
                # get remote port
                rport = lookup_table(self.cache.cdp, f"{OID.CDP_DEVPORT}{idx}")
                rport = normalize_port(rport)
                # get remote platform
                rplat = lookup_table(self.cache.cdp, f"{OID.CDP_DEVPLAT}{idx}")
                # get IOS version
                rios = lookup_table(self.cache.cdp, f"{OID.CDP_IOS}{idx}")
                if rios:
                    try:
                        rios = binascii.unhexlify(rios[2:])
                    except:
                        pass
                    rios = format_ios_ver(rios)
                link = self.get_link(ifidx)
                link.remote_name = val.prettyPrint()
                link.remote_ip = rip
                link.discovered_proto = 'cdp'
                link.local_port = lport
                link.remote_port = rport
                link.remote_plat = rplat
                link.remote_ios = rios
                neighbors.append(link)
        return neighbors


    def get_lldp_neighbors(self):
        """ Get a list of LLDP neighbors.
        Returns a list of LinkData's
        Will always return an array.
        """
        neighbors = []
        if not self.cache.lldp:
            print('No LLDP Neighbors Found.')
            return []
        for row in self.cache.lldp:
            for oid, val in row:
                oid = str(oid)
                if not oid.startswith(OID.LLDP_TYPE):
                    continue
                t = oid.split('.')
                ifidx = t[12]
                ifidx2 = t[13]
                if oid.startswith(f"{OID.LLDP_DEVADDR}.{ifidx}.{ifidx2}"):
                    rip = '.'.join(t[16:])
                else:
                    rip = ''
                lport = self.get_ifname(ifidx)
                rport = lookup_table(self.cache.lldp,
                                     f"{OID.LLDP_DEVPORT}.{ifidx}.{ifidx2}")
                rport = normalize_port(rport)
                devid = lookup_table(self.cache.lldp,
                                     f"{OID.LLDP_DEVID}.{ifidx}.{ifidx2}")
                try:
                    devid = mac_format_cisco(devid)
                except:
                    pass
                rimg = lookup_table(self.cache.lldp,
                                    f"{OID.LLDP_DEVDESC}.{ifidx}.{ifidx2}")
                if rimg:
                    try:
                        rimg = binascii.unhexlify(rimg[2:])
                    except:
                        pass
                    rimg = format_ios_ver(rimg)
                name = lookup_table(self.cache.lldp,
                                    f"{OID.LLDP_DEVNAME}.{ifidx}.{ifidx2}")
                if name in [None, '']:
                    name = devid
                link = self.get_link(ifidx)
                link.remote_ip = rip
                link.remote_name = name
                link.discovered_proto = 'lldp'
                link.local_port = lport
                link.remote_port = rport
                link.remote_plat = None
                link.remote_ios = rimg
                link.remote_mac = devid
                neighbors.append(link)
        return neighbors


    def get_link(self, ifidx):
        link = LinkData()
        # trunk
        link.link_type = lookup_table(self.cache.link_type,
                                      f"{OID.TRUNK_VTP}.{ifidx}")
        if link.link_type == '1':
            native_vlan = lookup_table(self.cache.trunk_native,
                                       f"{OID.TRUNK_NATIVE}.{ifidx}")
            allowed_vlans = lookup_table(self.cache.trunk_allowed,
                                         f"{OID.TRUNK_ALLOW}.{ifidx}")
            allowed_vlans = parse_allowed_vlans(allowed_vlans)
        else:
            native_vlan = None
            allowed_vlans = 'All'
        link.local_native_vlan = native_vlan
        link.local_allowed_vlans = allowed_vlans
        # LAG membership
        lag = lookup_table(self.cache.lag, f"{OID.LAG_LACP}.{ifidx}")
        link.local_lag = self.get_ifname(lag)
        link.local_lag_ips = self.get_cidrs_ifidx(lag)
        # VLAN info
        link.vlan = lookup_table(self.cache.vlan, f"{OID.IF_VLAN}.{ifidx}")
        # IP address
        lifips = self.get_cidrs_ifidx(ifidx)
        link.local_if_ip = lifips[0] if lifips else None
        link.remote_lag_ips = []
        return link


    def get_chassis(self) -> None:
        # Get:
        #    Serial number
        #    Platform
        #    IOS
        # Slow but reliable method by using SNMP directly.
        # Usually we will get this via CDP.
        if not any([self.stack.count, self.vss.enabled]):
            # Use actions.get_stack_details
            # or  actions.get_vss_details
            # for this.
            ent_cache = self.cache.ent_class
            if ent_cache:
                for row in ent_cache:
                    for n, v in row:
                        n = str(n)
                        if v != 'ENTPHYCLASS_CHASSIS':
                            continue
                        t = n.split('.')
                        idx = t[12]
                        self.serial = lookup_table(self.cache.ent_serial,
                                            f"{OID.ENTPHYENTRY_SERIAL}.{idx}")
                        self.plat = lookup_table(self.cache.ent_plat,
                                            f"{OID.ENTPHYENTRY_PLAT}.{idx}")
                        self.ios = lookup_table(self.cache.ent_ios,
                                            f"{OID.ENTPHYENTRY_SOFTWARE}.{idx}")
                if self.actions.get_ios:
                    # modular switches may have IOS on module than chassis
                    if not self.ios:
                        for row in ent_cache:
                            for n, v in row:
                                n = str(n)
                                if v != 'ENTPHYCLASS_MODULE':
                                    continue
                                t = n.split('.')
                                idx = t[12]
                                self.ios = lookup_table(self.cache.ent_ios,
                                            f"{OID.ENTPHYENTRY_SOFTWARE}.{idx}")
                                if self.ios:
                                    break
                    self.ios = format_ios_ver(self.ios)


    def get_ifname(self, ifidx=None):
        if not ifidx or ifidx == OID.ERR:
            return 'UNKNOWN'
        res = lookup_table(self.cache.ifname, f"{OID.IFNAME}.{ifidx}")
        return normalize_port(res) or 'UNKNOWN'


    def get_system_name(self, domains):
        return normalize_host(self.cache.name, domains) if domains \
                                                else self.cache.name


    def get_ipaddr(self):
        ''' Returns the first matching IP:
            - Lowest Loopback interface
            - Lowest SVI address/known IP
        '''
        # Loopbacks
        if self.loopbacks:
            ips = self.loopbacks[0].ips
            if ips:
                ips.sort()
                return ip_from_cidr(ips[0])
        # SVIs
        ips = []
        for svi in self.svis:
            ips.extend(svi.ip)
        ips.extend(self.ip)
        if ips:
            ips.sort()
            return ip_from_cidr(ips[0])
        return self.ip[0]


    def get_vpc(self, ifarr):
        ''' If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        '''
        if not self.cache.vpc:
            return None, None
        domain = oid_last_token(self.cache.vpc[0][0][0])
        ifidx = str(self.cache.vpc[0][0][1])
        ifname = lookup_table(ifarr, f"{OID.ETH_IF_DESC}.{ifidx}")
        ifname = normalize_port(ifname)
        return domain, ifname


    def get_vlans(self):
        arr = []
        i = 0
        for vlan_row in self.cache.vlan:
            for vlan_n, vlan_v in vlan_row:
                # get VLAN ID from OID
                vlan = oid_last_token(vlan_n)
                if vlan >= 1002:
                    continue
                arr.append(VLANData(vlan, str(self.cache.vlandesc[i][0][1])))
                i += 1
        return arr if arr else []


    def get_arp(self):
        arr = []
        for r in self.cache.arp:
            for n, v in r:
                n = str(n)
                if n.startswith(OID.ARP_VLAN):
                    tok = n.split('.')
                    ip = '.'.join(tok[11:])
                    interf = self.get_ifname(str(v))
                    mach = lookup_table(self.cache.arp, f"{OID.ARP_MAC}.{str(v)}.{ip}")
                    mac = mac_hex_to_ascii(mach, 1)
                    atype = lookup_table(self.cache.arp, f"{OID.ARP_TYPE}.{str(v)}.{ip}")
                    atype = int(atype)
                    type_str = 'unknown'
                    if atype == ARP.TYPE_OTHER:
                        type_str = 'other'
                    elif atype == ARP.TYPE_INVALID:
                        type_str = 'invalid'
                    elif atype == ARP.TYPE_DYNAMIC:
                        type_str = 'dynamic'
                    elif atype == ARP.TYPE_STATIC:
                        type_str = 'static'
                    arr.append(ARPData(ip, mac, interf, type_str))
        return arr if arr else []
