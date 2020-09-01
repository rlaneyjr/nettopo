# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
    node.py
"""
import binascii
from functools import cached_property
from typing import Union
from nettopo.core.cache import Cache
from nettopo.core.constants import NOTHING
from nettopo.core.data import LinkData, StackData
from nettopo.core.exceptions import NettopoSNMPError, NettopoNodeError
from nettopo.core.snmp import SNMP
from nettopo.core.util import (
    timethis,
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
    oid_last_token
)
from nettopo.core.data import (
    NodeActions,
    BaseData,
    LinkData,
    SVIData,
    LoopBackData,
    VLANData,
    ARPData
)
from nettopo.core.stack import Stack
from nettopo.core.vss import VSS
from nettopo.core.constants import ARP, DCODE, NODE
from nettopo.oids import Oids
o = Oids()


class Node(BaseData):
    def __init__(self, ip: str, immediate_query: bool=False) -> None:
        self.ip = ip
        self.snmp = SNMP(self.ip)
        self.cache = Cache(self.snmp)
        self.actions = NodeActions()
        self.queried = False
        self.ips = None
        self.links = None
        self.svis = None
        self.loopbacks = None
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
        if immediate_query:
            self.query_node()


    def add_link(self, link):
        if not isinstance(link, LinkData):
            link = LinkData(link)
        if link not in self.links:
            self.links.append(link)


    def get_snmp_creds(self, snmp_creds):
        """ find valid credentials for this node.
        try each known IP until one works
        """
        orig_snmp_ip = self.snmp.ip
        if self.snmp.success:
            return True
        if self.ip in NOTHING:
            self.snmp.ip = self.get_ips()
        if self.snmp.get_creds(snmp_creds):
            self.ip = self.snmp.ip
            return True
        for ip in self.ips:
            self.snmp.ip = ip
            if self.snmp.get_creds(snmp_creds):
                self.ip = self.snmp.ip
                return True
        if self.snmp.ip != orig_snmp_ip:
            print(f"Reseting SNMP IP {self.snmp.ip} back to {orig_snmp_ip}")
            self.snmp.ip = orig_snmp_ip
        return False


    def query(self) -> None:
        self.queried = True
        if not self.snmp.success:
            raise NettopoNodeError(f"FAILED: SNMP credentials")
        self.cache.name
        self.cache.cdp
        self.cache.lldp
        self.cache.link_type
        self.cache.lag
        self.cache.vlan
        self.cache.vlandesc
        self.cache.ifname
        self.cache.svi
        self.cache.ifip
        self.cache.ethif
        self.cache.trunk_allowed
        self.cache.trunk_native
        self.cache.vpc
        self.cache.arp
        self.cache.serial
        self.cache.bootfile
        self.cache.ent_class
        self.cache.ent_serial
        self.cache.ent_plat
        self.cache.ent_ios
        self.cache.router
        self.cache.ospf
        self.cache.ospf_id
        self.cache.bgp
        self.cache.hsrp
        self.cache.hsrp_vip


    def query_node(self) -> None:
        """ Query this node.
        Builds the cache for this node.
        """
        if not self.queried:
            self.query()
        if self.actions.get_name:
            self.name_raw = self.cache.name
            self.name = self.get_system_name()
        # router
        if self.actions.get_router:
            router = self.cache.router
            self.router = True if router == '1' else False
            if self.router:
                # OSPF
                if self.actions.get_ospf_id:
                    self.ospf_id = self.cache.ospf_id
                # BGP
                if self.actions.get_bgp_las:
                    bgp_las = self.cache.bgp
                    # 4500x reports 0 as disabled
                    self.bgp_las = bgp_las if bgp_las != '0' else None
                # HSRP
                if self.actions.get_hsrp_pri:
                    self.hsrp_pri = self.cache.hsrp
                    self.hsrp_vip = self.cache.hsrp_vip
        # stack
        if self.actions.get_stack:
            stack = Stack(self.snmp, self.actions)
            self.stack = stack if stack.enabled else False
        # vss
        if self.actions.get_vss:
            vss = VSS(self.snmp, self.actions)
            self.vss = vss if vss.enabled else False
        # serial
        if self.actions.get_serial:
            if self.vss:
                self.serial = self.vss.serial
            elif self.stack:
                self.serial = self.stack.serial
            else:
                self.serial = self.cache.serial
        # SVI
        if self.actions.get_svi:
            self.svis = []
            self.cache.svi
            for row in self.cache.svi:
                for k, v in row:
                    k = str(k)
                    vlan = k.split('.')[14]
                    svi = SVIData(vlan)
                    svi.ips = self.get_cidrs_ifidx(v)
                    self.svis.append(svi)
        # loopback
        if self.actions.get_lo:
            self.loopbacks = []
            self.cache.ethif
            self.cache.ifip
            for row in self.cache.ethif:
                for k, v in row:
                    k = str(k)
                    if k.startswith(o.ETH_IF_TYPE) and v == 24:
                        ifidx = k.split('.')[10]
                        lo_name = lookup_table(self.cache.ethif,
                                               f"{o.ETH_IF_DESC}.{ifidx}")
                        lo_ip = self.get_cidrs_ifidx(ifidx)
                        lo = LoopBackData(lo_name, lo_ip)
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


    def get_cidrs_ifidx(self, idx):
        ips = []
        for row in self.cache.ifip:
            for n, v in row:
                n = str(n)
                if n.startswith(o.IF_IP_ADDR):
                    if str(v) == str(idx):
                        t = n.split('.')
                        ip = ".".join(t[10:])
                        mask = lookup_table(self.cache.ifip,
                                            f"{o.IF_IP_NETM}{ip}")
                        mask = bits_from_mask(mask)
                        cidr = f"{ip}/{mask}"
                        ips.append(cidr)
        if ips:
            return ips if len(ips) > 1 else ips[0]
        else:
            return None


    def get_cdp_neighbors(self):
        """ Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        """
        # get list of CDP neighbors
        neighbors = []
        if not self.cache.cdp:
            print('No CDP Neighbors Found.')
            return []
        for row in self.cache.cdp:
            for oid, val in row:
                oid = str(oid)
                # process only if this row is a CDP_DEVID
                if oid.startswith(o.CDP_DEVID):
                    continue
                t = oid.split('.')
                ifidx = t[14]
                ifidx2 = t[15]
                idx = f".{ifidx}.{ifidx2}"
                # get remote IP
                rip = lookup_table(self.cache.cdp, f"{o.CDP_IPADDR}{idx}")
                rip = ip_2_str(rip)
                # get local port
                lport = self.get_ifname(ifidx)
                # get remote port
                rport = lookup_table(self.cache.cdp, f"{o.CDP_DEVPORT}{idx}")
                rport = normalize_port(rport)
                # get remote platform
                rplat = lookup_table(self.cache.cdp, f"{o.CDP_DEVPLAT}{idx}")
                # get IOS version
                rios = lookup_table(self.cache.cdp, f"{o.CDP_IOS}{idx}")
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
                if not oid.startswith(o.LLDP_TYPE):
                    continue
                t = oid.split('.')
                ifidx = t[12]
                ifidx2 = t[13]
                if oid.startswith(f"{o.LLDP_DEVADDR}.{ifidx}.{ifidx2}"):
                    rip = '.'.join(t[16:])
                else:
                    rip = ''
                lport = self.get_ifname(ifidx)
                rport = lookup_table(self.cache.lldp,
                                     f"{o.LLDP_DEVPORT}.{ifidx}.{ifidx2}")
                rport = normalize_port(rport)
                devid = lookup_table(self.cache.lldp,
                                     f"{o.LLDP_DEVID}.{ifidx}.{ifidx2}")
                try:
                    devid = mac_format_cisco(devid)
                except:
                    pass
                rimg = lookup_table(self.cache.lldp,
                                    f"{o.LLDP_DEVDESC}.{ifidx}.{ifidx2}")
                if rimg:
                    try:
                        rimg = binascii.unhexlify(rimg[2:])
                    except:
                        pass
                    rimg = format_ios_ver(rimg)
                name = lookup_table(self.cache.lldp,
                                    f"{o.LLDP_DEVNAME}.{ifidx}.{ifidx2}")
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
                                      f"{o.TRUNK_VTP}.{ifidx}")
        if link.link_type == '1':
            native_vlan = lookup_table(self.cache.trunk_native,
                                       f"{o.TRUNK_NATIVE}.{ifidx}")
            allowed_vlans = lookup_table(self.cache.trunk_allowed,
                                         f"{o.TRUNK_ALLOW}.{ifidx}")
            allowed_vlans = parse_allowed_vlans(allowed_vlans)
        else:
            native_vlan = None
            allowed_vlans = 'All'
        link.local_native_vlan = native_vlan
        link.local_allowed_vlans = allowed_vlans
        # LAG membership
        lag = lookup_table(self.cache.lag, f"{o.LAG_LACP}.{ifidx}")
        link.local_lag = self.get_ifname(lag)
        link.local_lag_ips = self.get_cidrs_ifidx(lag)
        # VLAN info
        link.vlan = lookup_table(self.cache.vlan, f"{o.IF_VLAN}.{ifidx}")
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
        for row in self.cache.ent_class:
            for n, v in row:
                n = str(n)
                if v != 'ENTPHYCLASS_CHASSIS':
                    continue
                t = n.split('.')
                idx = t[12]
                self.serial = lookup_table(self.cache.ent_serial,
                                    f"{o.ENTPHYENTRY_SERIAL}.{idx}")
                self.plat = lookup_table(self.cache.ent_plat,
                                    f"{o.ENTPHYENTRY_PLAT}.{idx}")
                self.ios = lookup_table(self.cache.ent_ios,
                                    f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
        if self.actions.get_ios:
            # modular switches may have IOS on module than chassis
            if not self.ios:
                for row in self.cache.ent_class:
                    for n, v in row:
                        n = str(n)
                        if v != 'ENTPHYCLASS_MODULE':
                            continue
                        t = n.split('.')
                        idx = t[12]
                        self.ios = lookup_table(self.cache.ent_ios,
                                    f"{o.ENTPHYENTRY_SOFTWARE}.{idx}")
                        if self.ios:
                            break
            self.ios = format_ios_ver(self.ios)


    def get_ifname(self, ifidx=None):
        if not ifidx or ifidx == o.ERR:
            return 'UNKNOWN'
        res = lookup_table(self.cache.ifname, f"{o.IFNAME}.{ifidx}")
        return normalize_port(res) or 'UNKNOWN'


    def get_system_name(self, domains=None):
        if not self.queried:
            self.query_node()
        return normalize_host(self.name_raw, domains)


    def get_ips(self):
        """ Collects and stores all the IPs for Node
        Return the lowest numbered IP of all interfaces
        """
        self.ips = list(self.ip)
        if not self.queried:
            self.query_node()
        # Loopbacks
        if self.loopbacks:
            for lb in self.loopbacks:
                if lb.ip:
                    self.ips.append(lb.ip)
        # SVIs
        if self.svis:
            for svi in self.svis:
                if svi.ips:
                    self.ips.extend(svi.ips)
        self.ips.sort()
        return ip_from_cidr(self.ips[0])


    def get_vpc(self, ifarr):
        """ If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        """
        if not self.cache.vpc:
            return None, None
        domain = oid_last_token(self.cache.vpc[0][0][0])
        ifidx = str(self.cache.vpc[0][0][1])
        ifname = lookup_table(ifarr, f"{o.ETH_IF_DESC}.{ifidx}")
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
        return arr


    def get_arp(self):
        arr = []
        for r in self.cache.arp:
            for n, v in r:
                n = str(n)
                if n.startswith(o.ARP_VLAN):
                    tok = n.split('.')
                    ip = '.'.join(tok[11:])
                    interf = self.get_ifname(str(v))
                    mach = lookup_table(self.cache.arp,
                                        f"{o.ARP_MAC}.{str(v)}.{ip}")
                    mac = mac_hex_to_ascii(mach, 1)
                    atype = lookup_table(self.cache.arp,
                                         f"{o.ARP_TYPE}.{str(v)}.{ip}")
                    atype = int(atype)
                    type_str = 'unknown'
                    if atype == ARP.OTHER:
                        type_str = 'other'
                    elif atype == ARP.INVALID:
                        type_str = 'invalid'
                    elif atype == ARP.DYNAMIC:
                        type_str = 'dynamic'
                    elif atype == ARP.STATIC:
                        type_str = 'static'
                    arr.append(ARPData(ip, mac, interf, type_str))
        return arr
