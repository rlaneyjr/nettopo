# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    node.py
'''
from functools import cached_property
from .snmp import SNMP
from .util import (timethis,
                   bits_from_mask,
                   normalize_host,
                   normalize_port,
                   ip_2_str,
                   get_cidr,
                   mac_hex_to_ascii,
                   mac_format_cisco,
                   parse_allowed_vlans)
from .data import (CacheData,
                   NodeActions,
                   BaseData,
                   LinkData,
                   SVIData,
                   LoopBackData,
                   VLANData,
                   ARPData)
from .stack import Stack, StackMember
from .vss import VSS, VSSMember
from .constants import OID, ARP, DCODE, NODE


class Node(BaseData):
    def __init__(self, ip):
        self.actions = NodeActions()
        self.snmpobj = SNMP()
        self.links = []
        self.discovered = False
        self.name = None
        self.ip = ip
        self.plat = None
        self.ios = None
        self.router = None
        self.ospf_id = None
        self.bgp_las = None
        self.hsrp_pri = None
        self.hsrp_vip = None
        self.serial = None
        self.bootfile = None
        self.svis = []
        self.loopbacks = []
        self.vpc_peerlink_if = None
        self.vpc_peerlink_node = None
        self.vpc_domain = None
        self.stack = Stack()
        self.vss = VSS()
        self.cache = CacheData()

    def show(self):
        return f"<name={self.name}, ip={self.ip}, plat={self.plat}, \
                ios={self.ios}, serial={self.serial}, router={self.router}, \
                vss={self.vss}, stack={self.stack}>"

    @cached_property
    def link_type_cache(self):
        return self.snmpobj.get_bulk(OID.TRUNK_VTP)

    @cached_property
    def lag_cache(self):
        return self.snmpobj.get_bulk(OID.LAG_LACP)

    @cached_property
    def vlan_cache(self):
        return self.snmpobj.get_bulk(OID.IF_VLAN)

    @cached_property
    def ifname_cache(self):
        return self.snmpobj.get_bulk(OID.IFNAME)

    @cached_property
    def trunk_allowed_cache(self):
        return self.snmpobj.get_bulk(OID.TRUNK_ALLOW)

    @cached_property
    def trunk_native_cache(self):
        return self.snmpobj.get_bulk(OID.TRUNK_NATIVE)

    @cached_property
    def ifip_cache(self):
        return self.snmpobj.get_bulk(OID.IF_IP)

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
                if self.snmpobj.get_cred(snmp_creds):
                    return True
        return False

    def query_node(self):
        """ Query this node.
        Set .actions and .snmp_creds before calling.
        """
        if not self.snmpobj.ver:
            # call get_snmp_creds() first or it failed to find good creds
            return False
        if self.actions.get_name:
            self.name = self.get_system_name([])
        # router
        if self.actions.get_router:
            if not self.router:
                self.router = True if self.snmpobj.get_val(OID.IP_ROUTING) == '1' else False
            if self.router:
                # OSPF
                if self.actions.get_ospf_id:
                    self.ospf_id = self.snmpobj.get_val(OID.OSPF)
                    if self.ospf_id:
                        self.ospf_id = self.snmpobj.get_val(OID.OSPF_ID)
                # BGP
                if self.actions.get_bgp_las:
                    self.bgp_las = self.snmpobj.get_val(OID.BGP_LAS)
                    if self.bgp_las == '0':       # 4500x is reporting 0 with disabled
                        self.bgp_las = None
                # HSRP
                if self.actions.get_hsrp_pri:
                    self.hsrp_pri = self.snmpobj.get_val(OID.HSRP_PRI)
                    if self.hsrp_pri:
                        self.hsrp_vip = self.snmpobj.get_val(OID.HSRP_VIP)
        # stack
        if self.actions.get_stack:
            self.stack = Stack(self.snmpobj, self.actions)
        # vss
        if self.actions.get_vss:
            self.vss = VSS(self.snmpobj, self.actions)
        # serial
        if self.actions.get_serial == 1 and self.stack.count == 0 and self.vss.enabled == 0:
            self.serial = self.snmpobj.get_val(OID.SYS_SERIAL)
        # SVI
        if self.actions.get_svi:
            if not self.svi_cache:
                self.svi_cache = self.snmpobj.get_bulk(OID.SVI_VLANIF)
            if not self.ifip_cache:
                self.ifip_cache = self.snmpobj.get_bulk(OID.IF_IP)
            for row in self.svi_cache:
                for n, v in row:
                    n = str(n)
                    vlan = n.split('.')[14]
                    svi = SVIData(vlan)
                    svi_ips = self.get_cidrs_ifidx(v)
                    svi.ip.extend(svi_ips)
                    self.svis.append(svi)
        # loopback
        if self.actions.get_lo:
            self.ethif_cache = self.snmpobj.get_bulk(OID.ETH_IF)
            if not self.ifip_cache:
                self.ifip_cache = self.snmpobj.get_bulk(OID.IF_IP)
            for row in self.ethif_cache:
                for n, v in row:
                    n = str(n)
                    if n.startswith(OID.ETH_IF_TYPE) and v == 24:
                        ifidx = n.split('.')[10]
                        lo_name = self.snmpobj.table_lookup(self.ethif_cache, OID.ETH_IF_DESC + '.' + ifidx)
                        lo_ips = self.get_cidrs_ifidx(ifidx)
                        lo = LoopBackData(lo_name, lo_ips)
                        self.loopbacks.append(lo)
        # bootfile
        if self.actions.get_bootf:
            self.bootfile = self.snmpobj.get_val(OID.SYS_BOOT)
        # chassis info (serial, IOS, platform)
        if self.actions.get_chassis_info:
            self.get_chassis()
        # VPC peerlink
        if self.actions.get_vpc:
            self.vpc_domain, self.vpc_peerlink_if = self.get_vpc(self.ethif_cache)
        return True

    def get_cidrs_ifidx(self, ifidx):
        ips = []
        for ifrow in self.ifip_cache:
            for ifn, ifv in ifrow:
                ifn = str(ifn)
                if ifn.startswith(OID.IF_IP_ADDR):
                    if str(ifv) == str(ifidx):
                        t = ifn.split('.')
                        ip = ".".join(t[10:])
                        mask = self.snmpobj.table_lookup(self.ifip_cache, OID.IF_IP_NETM + ip)
                        nbits = bits_from_mask(mask)
                        cidr = '%s/%i' % (ip, nbits)
                        ips.append(cidr)
        return ips

    def get_cdp_neighbors(self):
        ''' Get a list of CDP neighbors.
        Returns a list of LinkData's.
        Will always return an array.
        '''
        # get list of CDP neighbors
        neighbors = []
        self.cdp_cache = self.snmpobj.get_bulk(OID.CDP)
        if not self.cdp_cache:
            print('No CDP Neighbors Found.')
            return []
        for row in self.cdp_cache:
            for name, val in row:
                name = str(name)
                # process only if this row is a CDP_DEVID
                if name.startswith(OID.CDP_DEVID):
                    continue
                t = name.split('.')
                ifidx = t[14]
                ifidx2 = t[15]
                idx = f".{ifidx}.{ifidx2}"
                # get remote IP
                rip = self.snmpobj.table_lookup(self.cdp_cache, f"{OID.CDP_IPADDR}{idx}")
                rip = ip_2_str(rip)
                # get local port
                lport = self.get_ifname(ifidx)
                # get remote port
                rport = self.snmpobj.table_lookup(self.cdp_cache, f"{OID.CDP_DEVPORTf}{idx}")
                rport = normalize_port(rport)
                # get remote platform
                rplat = self.snmpobj.table_lookup(self.cdp_cache, f"{OID.CDP_DEVPLAT}{idx}")
                # get IOS version
                rios = self.snmpobj.table_lookup(self.cdp_cache, f"{OID.CDP_IOS}{idx}")
                if rios:
                    try:
                        rios = binascii.unhexlify(rios[2:])
                    except:
                        pass
                    rios = self.format_ios_ver(rios)
                link = self.get_link(ifidx, ifidx2)
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
        self.lldp_cache = self.snmpobj.get_bulk(OID.LLDP)
        if not self.lldp_cache:
            print('No LLDP Neighbors Found.')
            return []
        for row in self.lldp_cache:
            for name, val in row:
                name = str(name)
                if not name.startswith(OID.LLDP_TYPE):
                    continue
                t = name.split('.')
                ifidx = t[12]
                ifidx2 = t[13]
                rip = ''
                for r in self.lldp_cache:
                    for n, v in r:
                        n = str(n)
                        if n.startswith(OID.LLDP_DEVADDR + '.' + ifidx + '.' + ifidx2):
                            t2 = n.split('.')
                            rip = '.'.join(t2[16:])
                lport = self.get_ifname(ifidx)
                rport = self.snmpobj.table_lookup(self.lldp_cache, OID.LLDP_DEVPORT + '.' + ifidx + '.' + ifidx2)
                rport = normalize_port(rport)
                devid = self.snmpobj.table_lookup(self.lldp_cache, OID.LLDP_DEVID + '.' + ifidx + '.' + ifidx2)
                try:
                    devid = mac_format_cisco(devid)
                except:
                    pass
                rimg = self.snmpobj.table_lookup(self.lldp_cache, OID.LLDP_DEVDESC + '.' + ifidx + '.' + ifidx2)
                if rimg:
                    try:
                        rimg = binascii.unhexlify(rimg[2:])
                    except:
                        pass
                    rimg = self.format_ios_ver(rimg)
                name = self.snmpobj.table_lookup(self.lldp_cache, OID.LLDP_DEVNAME + '.' + ifidx + '.' + ifidx2)
                if name in [None, '']:
                    name = devid
                link = self.get_link(ifidx, ifidx2)
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

    def get_link(self, ifidx, ifidx2):
        # trunk
        link_type = self.snmpobj.table_lookup(self.link_type_cache, OID.TRUNK_VTP + '.' + ifidx)
        native_vlan = None
        allowed_vlans = 'All'
        if (link_type == '1'):
            native_vlan = self.snmpobj.table_lookup(self.trunk_native_cache, OID.TRUNK_NATIVE + '.' + ifidx)
            allowed_vlans = self.snmpobj.table_lookup(self.trunk_allowed_cache, OID.TRUNK_ALLOW + '.' + ifidx)
            allowed_vlans = parse_allowed_vlans(allowed_vlans)
        # LAG membership
        lag = self.snmpobj.table_lookup(self.lag_cache, OID.LAG_LACP + '.' + ifidx)
        lag_ifname = self.get_ifname(lag)
        lag_ips = self.get_cidrs_ifidx(lag)
        # VLAN info
        vlan = self.snmpobj.table_lookup(self.vlan_cache, OID.IF_VLAN + '.' + ifidx)
        # IP address
        lifips = self.get_cidrs_ifidx(ifidx)
        link = LinkData()
        link.link_type = link_type
        link.vlan = vlan
        link.local_native_vlan = native_vlan
        link.local_allowed_vlans = allowed_vlans
        link.local_lag = lag_ifname
        link.local_lag_ips = lag_ips
        link.remote_lag_ips = []
        link.local_if_ip = lifips[0] if lifips else None
        return link

    def get_chassis(self):
        # Get:
        #    Serial number
        #    Platform
        #    IOS
        # Slow but reliable method by using SNMP directly.
        # Usually we will get this via CDP.
        if self.stack.count > 0 or self.vss.enabled == 1:
            # Use actions.get_stack_details
            # or  actions.get_vss_details
            # for this.
            return
        class_cache = self.snmpobj.get_bulk(OID.ENTPHYENTRY_CLASS)
        if self.actions.get_serial:
            serial_cache = self.snmpobj.get_bulk(OID.ENTPHYENTRY_SERIAL)
        if self.actions.get_plat:
            platf_cache = self.snmpobj.get_bulk(OID.ENTPHYENTRY_PLAT)
        if self.actions.get_ios:
            ios_cache = self.snmpobj.get_bulk(OID.ENTPHYENTRY_SOFTWARE)
        if not class_cache:
            return
        for row in class_cache:
            for n, v in row:
                n = str(n)
                if v != "ENTPHYCLASS_CHASSIS":
                    continue
                t = n.split('.')
                idx = t[12]
                if self.actions.get_serial:
                    self.serial = self.snmpobj.table_lookup(serial_cache, OID.ENTPHYENTRY_SERIAL + '.' + idx)
                if self.actions.get_plat:
                    self.plat = self.snmpobj.table_lookup(platf_cache, OID.ENTPHYENTRY_PLAT + '.' + idx)
                if self.actions.get_ios:
                    self.ios = self.snmpobj.table_lookup(ios_cache, OID.ENTPHYENTRY_SOFTWARE + '.' + idx)
        if self.actions.get_ios:
            # modular switches might have IOS on a module rather than chassis
            if self.ios == '':
                for row in class_cache:
                    for n, v in row:
                        n = str(n)
                        if v != ENTPHYCLASS_MODULE:
                            continue
                        t = n.split('.')
                        idx = t[12]
                        self.ios = self.snmpobj.table_lookup(ios_cache, OID.ENTPHYENTRY_SOFTWARE + '.' + idx)
                        if self.ios != '':
                            break
                    if self.ios != '':
                        break
            self.ios = self.format_ios_ver(self.ios)
        return

    def get_ifname(self, ifidx):
        if not ifidx or ifidx == OID.ERR:
            return 'UNKNOWN'
        if not self.ifname_cache:
            self.ifname_cache = self.snmpobj.get_bulk(OID.IFNAME)
        s = self.snmpobj.table_lookup(self.ifname_cache, OID.IFNAME + '.' + ifidx)
        return normalize_port(s) or 'UNKNOWN'

    def get_system_name(self, domains):
        return normalize_host(self.snmpobj.get_val(OID.SYSNAME), domains)

    def format_ios_ver(self, img):
        x = img
        if isinstance(img, bytes):
            x = img.decode("utf-8")
        try:
            img_s = re.search('(Version:? |CCM:)([^ ,$]*)', x)
        except:
            return img
        if img_s:
            if img_s.group1 == 'CCM:':
                return 'CCM %s' % img_s.group(2)
            return img_s.group(2)
        return img

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
                return get_cidr(ips[0])
        # SVIs
        ips = []
        for svi in self.svis:
            ips.extend(svi.ip)
        ips.extend(self.ip)
        if ips:
            ips.sort()
            return get_cidr(ips[0])
        return ''

    def get_vpc(self, ifarr):
        ''' If VPC is enabled,
        Return the VPC domain and interface name of the VPC peerlink.
        '''
        if not self.vpc_cache:
            self.vpc_cache = self.snmpobj.get_bulk(OID.VPC_PEERLINK_IF)
        if not self.vpc_cache or not len(self.vpc_cache):
            return None, None
        domain = SNMP.get_last_oid_token(self.vpc_cache[0][0][0])
        ifidx = str(self.vpc_cache[0][0][1])
        ifname = self.snmpobj.table_lookup(ifarr, OID.ETH_IF_DESC + '.' + ifidx)
        ifname = normalize_port(ifname)
        return domain, ifname

    def get_vlans(self):
        if not self.vlan_cache:
            self.vlan_cache = self.snmpobj.get_bulk(OID.VLANS)
        if not self.vlandesc_cache:
            self.vlandesc_cache = self.snmpobj.get_bulk(OID.VLAN_DESC)
        arr = []
        i = 0
        for vlan_row in self.vlan_cache:
            for vlan_n, vlan_v in vlan_row:
                # get VLAN ID from OID
                vlan = self.snmpobj.get_last_oid_token(vlan_n)
                if vlan >= 1002:
                    continue
                arr.append(VLANData(vlan, str(self.vlandesc_cache[i][0][1])))
                i += 1
        return arr

    def get_arp(self):
        if not self.arp_cache:
            self.arp_cache = self.snmpobj.get_bulk(OID.ARP)
        arr = []
        for r in self.arp_cache:
            for n, v in r:
                n = str(n)
                if n.startswith(OID.ARP_VLAN):
                    tok = n.split('.')
                    ip = '.'.join(tok[11:])
                    interf = self.get_ifname(str(v))
                    mach = self.snmpobj.table_lookup(self.arp_cache, OID.ARP_MAC+'.'+str(v)+'.'+ip)
                    mac = mac_hex_to_ascii(mach, 1)
                    atype = self.snmpobj.table_lookup(self.arp_cache, OID.ARP_TYPE+'.'+str(v)+'.'+ip)
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

