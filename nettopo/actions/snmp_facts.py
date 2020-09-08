# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              snmp_facts.py
Description:        SNMP Facts Gathering
Author:             Ricky Laney
'''
# from nettopo.sysdescrparser import sysdescrparser
from collections import defaultdict
from pysnmp.entity.rfc3413.oneliner import cmdgen

class DefineOid(object):
    """ Define Oids with or without dot prefix
    """
    def __init__(self, dotprefix=False):
        if dotprefix:
            dp = "."
        else:
            dp = ""

        # From SNMPv2-MIB
        self.sysDescr    = dp + "1.3.6.1.2.1.1.1.0"
        self.sysObjectId = dp + "1.3.6.1.2.1.1.2.0"
        self.sysUpTime   = dp + "1.3.6.1.2.1.1.3.0"
        self.sysContact  = dp + "1.3.6.1.2.1.1.4.0"
        self.sysName     = dp + "1.3.6.1.2.1.1.5.0"
        self.sysLocation = dp + "1.3.6.1.2.1.1.6.0"

        # From IF-MIB
        self.ifIndex       = dp + "1.3.6.1.2.1.2.2.1.1"
        self.ifDescr       = dp + "1.3.6.1.2.1.2.2.1.2"
        self.ifMtu         = dp + "1.3.6.1.2.1.2.2.1.4"
        self.ifSpeed       = dp + "1.3.6.1.2.1.2.2.1.5"
        self.ifPhysAddress = dp + "1.3.6.1.2.1.2.2.1.6"
        self.ifAdminStatus = dp + "1.3.6.1.2.1.2.2.1.7"
        self.ifOperStatus  = dp + "1.3.6.1.2.1.2.2.1.8"
        self.ifAlias       = dp + "1.3.6.1.2.1.31.1.1.1.18"

        # From IP-MIB
        self.ipAdEntAddr    = dp + "1.3.6.1.2.1.4.20.1.1"
        self.ipAdEntIfIndex = dp + "1.3.6.1.2.1.4.20.1.2"
        self.ipAdEntNetMask = dp + "1.3.6.1.2.1.4.20.1.3"


def decode_hex(hexstring):
    if len(hexstring) < 3:
        return hexstring
    if hexstring[:2] == "0x":
        return hexstring[2:].decode("hex")
    else:
        return hexstring

def decode_mac(hexstring):
    if len(hexstring) != 14:
        return hexstring
    if hexstring[:2] == "0x":
        return hexstring[2:]
    else:
        return hexstring

def lookup_adminstatus(int_adminstatus):
    adminstatus_options = {
                            1: 'up',
                            2: 'down',
                            3: 'testing'
                          }
    if int_adminstatus in adminstatus_options.keys():
        return adminstatus_options[int_adminstatus]
    else:
        return ""

def lookup_operstatus(int_operstatus):
    operstatus_options = {
                           1: 'up',
                           2: 'down',
                           3: 'testing',
                           4: 'unknown',
                           5: 'dormant',
                           6: 'notPresent',
                           7: 'lowerLayerDown'
                         }
    if int_operstatus in operstatus_options.keys():
        return operstatus_options[int_operstatus]
    else:
        return ""

class SnmpFacts:
    def __init__(self, host: str, community: str='public', version: str='v2c', **kwargs):
        self.host = host
        self.trans = cmdgen.UdpTransportTarget((self.host, 161))
        if version not in ['v2', 'v2c', 'v3']:
            raise Exception(f"Wrong version supplied: {version}")
        self.version = version
        self.community = community
        if self.version == 'v3':
            if not kwargs:
                raise Exception(f"No kwargs with v3 specified")
            self._parse_kwargs(kwargs)
        else:
            self.auth = cmdgen.CommunityData(self.community)
        self.facts = None

    def _parse_kwargs(self, **kwargs):
        if any(['username', 'level', 'integrity', 'authkey']) not in kwargs.keys():
            raise Exception(f"Not all the required kwargs were passed")
        if kwargs['integrity'] == "sha":
            integrity_proto = cmdgen.usmHMACSHAAuthProtocol
        elif kwargs['integrity'] == "md5":
            integrity_proto = cmdgen.usmHMACMD5AuthProtocol
        else:
            raise Exception(f"Integrity: {kwargs['integrity']} is not a valid option")
        if kwargs['level'] == "authNoPriv":
            # Use SNMP Version 3 with authNoPriv
            self.auth =  cmdgen.UsmUserData(kwargs['username'],
                                      authKey=kwargs['authkey'],
                                      authProtocol=integrity_proto)
        elif kwargs['level'] == "authPriv":
            if any(['privacy','privkey']) not in kwargs.keys():
                raise Exception(f"Not all the required kwargs were passed")
            if kwargs['privacy'] == "aes":
                privacy_proto = cmdgen.usmAesCfb128Protocol
            elif kwargs['privacy'] == "des":
                privacy_proto = cmdgen.usmDESPrivProtocol
            # Use SNMP Version 3 with authPriv
            self.auth =  cmdgen.UsmUserData(m_args['username'],
                                      authKey=m_args['authkey'],
                                      privKey=m_args['privkey'],
                                      authProtocol=integrity_proto,
                                      privProtocol=privacy_proto)
        else:
            raise Exception(f"Level: {kwargs['level']} is no valid")

    def get_facts(self):
        if self.facts:
            raise Exception(f"Appears get_facts has already been ran")
        cmdGen = cmdgen.CommandGenerator()
        # Use p to prefix OIDs with a dot for polling
        p = DefineOid(dotprefix=True)
        # Use v without a prefix to use with return values
        v = DefineOid(dotprefix=False)
        # Tree = lambda: defaultdict(Tree)
        results = {}
        # General SNMP data collection
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.auth,
            self.trans,
            cmdgen.MibVariable(p.sysDescr,),
            cmdgen.MibVariable(p.sysObjectId,),
            cmdgen.MibVariable(p.sysUpTime,),
            cmdgen.MibVariable(p.sysContact,),
            cmdgen.MibVariable(p.sysName,),
            cmdgen.MibVariable(p.sysLocation,),
        )

        if errorIndication:
            raise Exception(str(errorIndication))

        for oid, val in varBinds:
            print(f"{oid}: {val.prettyPrint()}")
            current_oid = oid
            current_val = val.prettyPrint()
            if current_oid == v.sysDescr:
                results['sysdescr'] = decode_hex(current_val)
                print(f"sysDescr: {decode_hex(current_val)}")
            elif current_oid == v.sysObjectId:
                results['sysobjectid'] = current_val
                print(f"sysObjectId: {current_val}")
            elif current_oid == v.sysUpTime:
                results['sysuptime'] = current_val
                print(f"sysUpTime: {current_val}")
            elif current_oid == v.sysContact:
                results['syscontact'] = current_val
                print(f"sysContact: {current_val}")
            elif current_oid == v.sysName:
                results['sysname'] = current_val
                print(f"sysName: {current_val}")
            elif current_oid == v.sysLocation:
                results['syslocation'] = current_val
                print(f"sysLocation: {current_val}")

        # Interface SNMP data collection
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
            self.auth,
            self.trans,
            cmdgen.MibVariable(p.ifIndex,),
            cmdgen.MibVariable(p.ifDescr,),
            cmdgen.MibVariable(p.ifMtu,),
            cmdgen.MibVariable(p.ifSpeed,),
            cmdgen.MibVariable(p.ifPhysAddress,),
            cmdgen.MibVariable(p.ifAdminStatus,),
            cmdgen.MibVariable(p.ifOperStatus,),
            cmdgen.MibVariable(p.ipAdEntAddr,),
            cmdgen.MibVariable(p.ipAdEntIfIndex,),
            cmdgen.MibVariable(p.ipAdEntNetMask,),
            cmdgen.MibVariable(p.ifAlias,),
        )

        if errorIndication:
            raise Exception(str(errorIndication))

        interface_indexes = []
        all_ipv4_addresses = []
        ipv4_networks = {}

        for varBinds in varTable:
            for oid, val in varBinds:
                print(f"{oid}: {val.prettyPrint()}")
                current_oid = oid
                current_val = val.prettyPrint()
                if v.ifIndex in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['ifindex'] = current_val
                    interface_indexes.append(ifIndex)
                    print(f"ifIndex: {ifIndex} => {current_val}")
                if v.ifDescr in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['name'] = current_val
                    print(f"ifDescr: {ifIndex} => {current_val}")
                if v.ifMtu in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['mtu'] = current_val
                    print(f"ifMtu: {ifIndex} => {current_val}")
                if v.ifPhysAddress in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['mac'] = decode_mac(current_val)
                    print(f"ifPhysAddress: {ifIndex} => {decode_mac(current_val)}")
                if v.ifAdminStatus in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['adminstatus'] = lookup_adminstatus(int(current_val))
                    print(f"ifAdminStatus: {ifIndex} => {lookup_adminstatus(int(current_val))}")
                if v.ifOperStatus in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['operstatus'] = lookup_operstatus(int(current_val))
                    print(f"ifOperStatus: {ifIndex} => {lookup_operstatus(int(current_val))}")
                if v.ipAdEntAddr in current_oid:
                    curIPList = current_oid.rsplit('.', 4)[-4:]
                    curIP = ".".join(curIPList)
                    ipv4_networks[curIP]['address'] = current_val
                    all_ipv4_addresses.append(current_val)
                    print(f"ipAdEntAddr: {curIP} => {current_val}")
                if v.ipAdEntIfIndex in current_oid:
                    curIPList = current_oid.rsplit('.', 4)[-4:]
                    curIP = ".".join(curIPList)
                    ipv4_networks[curIP]['interface'] = current_val
                    print(f"ipAdEntIfIndex: {curIP} => {current_val}")
                if v.ipAdEntNetMask in current_oid:
                    curIPList = current_oid.rsplit('.', 4)[-4:]
                    curIP = ".".join(curIPList)
                    ipv4_networks[curIP]['netmask'] = current_val
                    print(f"ipAdEntNetMask: {curIP} => {current_val}")
                if v.ifAlias in current_oid:
                    ifIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['interfaces'][ifIndex]['description'] = current_val
                    print(f"ifAlias: {ifIndex} => {current_val}")

        interface_to_ipv4 = {}
        for ipv4_network in ipv4_networks:
            current_interface = ipv4_networks[ipv4_network]['interface']
            current_network = {
                                'address': ipv4_networks[ipv4_network]['address'],
                                'netmask': ipv4_networks[ipv4_network]['netmask']
                              }
            if not current_interface in interface_to_ipv4:
                interface_to_ipv4[current_interface] = []
                interface_to_ipv4[current_interface].append(current_network)
            else:
                interface_to_ipv4[current_interface].append(current_network)

        for interface in interface_to_ipv4:
            results['interfaces'][int(interface)]['ipv4'] = interface_to_ipv4[interface]

        results['all_ipv4_addresses'] = all_ipv4_addresses
        self.facts = results

