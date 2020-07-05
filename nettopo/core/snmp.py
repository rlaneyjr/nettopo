# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        snmp.py
'''

from nelsnmp.snmp import cmdgen
try:
    from netaddr import IPAddress
except:
    from ipaddress import ip_address as IPAddress

from .constants import OID


class SNMP:
    def __init__(self, ip='0.0.0.0', port=161):
        self.success = False
        self.community = None
        self.ip = str(ip) if isinstance(ip, IPAddress) else ip
        self.port = port

    def check_community(self, community):
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((self.ip, self.port)),
            '1.3.6.1.2.1.1.5.0')
        if errIndication:
            self.success = False
        else:
            self.success = True
            self.community = community
        return self.success

    def get_creds(self, snmp_creds):
        if isinstance(snmp_creds, dict):
            for cred in snmp_creds:
                if self.check_community(cred['community']):
                    return True
        elif isinstance(snmp_creds, list):
            for cred in snmp_creds:
                if self.check_community(cred):
                    return True
        elif isinstance(snmp_creds, str):
            if self.check_community(snmp_creds):
                return True
        return False

    def get_val(self, oid):
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBinds = cmdGen.getCmd(
                        cmdgen.CommunityData(self.community),
                        cmdgen.UdpTransportTarget((self.ip, self.port), retries=2),
                        oid)
        if errIndication:
            print(f"[E] get_snmp_val({self.community}): {errIndication}\n{errStatus}")
            return None
        else:
            r = varBinds[0][1].prettyPrint()
            if r is any((OID.ERR, OID.ERR_INST)):
                return None
            return r

    def get_bulk(self, oid):
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBindTable = cmdGen.bulkCmd(
                        cmdgen.CommunityData(self.community),
                        cmdgen.UdpTransportTarget((self.ip, self.port), timeout=30, retries=2),
                        0, 50, oid)
        if errIndication:
            print(f"[E] get_snmp_bulk({self.community}): {errIndication}\n{errStatus}")
            return None
        else:
            ret = []
            for r in varBindTable:
                for n, v in r:
                    if str(n).startswith(oid):
                        ret.append(r)
            return ret

    @staticmethod
    def table_lookup(table, name):
        for row in table:
            for n, v in row:
                if name in str(n):
                    return v.prettyPrint()
        return None

    @staticmethod
    def get_last_oid_token(objectId):
        oid = objectId.getOid()
        idx = len(oid) - 1
        return oid[idx]
