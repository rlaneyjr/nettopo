# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        snmp.py
'''

import json
from queue import Queue
from threading import Thread
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from typing import Union, Dict, List, Any
try:
    from netaddr import IPAddress
except:
    from ipaddress import ip_address as IPAddress

from nettopo.core.constants import *
from nettopo.oids import Oids
o = Oids()

DEFAULT_COMMS = ['public', 'private', 'letmeSNMP']
DEFAULT_VARBINDS = (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

# Typing shortcuts
DLS = Union[dict, list, str]
IP = Union[str, IPAddress]


class SNMP:
    def __init__(self, ip: IP='0.0.0.0', port: int=161, **kwargs) -> None:
        self.ip = str(ip) if isinstance(ip, IPAddress) else ip
        self.port = port
        self.success = False
        self.community = None
        self.default_comms = DEFAULT_COMMS
        self.vulnerable = False
        if kwargs:
            for key,val in kwargs.items():
                if key == 'community':
                    self.default_comms.append(val)
        self.get_creds(self.default_comms)
        if self.success:
            self.vulnerable = True


    def check_community(self, community: str) -> bool:
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


    def get_creds(self, snmp_creds: DLS) -> bool:
        if isinstance(snmp_creds, str):
            if self.check_community(snmp_creds):
                return True
        else:
            for cred in snmp_creds:
                if isinstance(snmp_creds, dict):
                    if self.check_community(cred['community']):
                        return True
                else:
                    if self.check_community(cred):
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
            if r is any((o.ERR, o.ERR_INST)):
                return None
            return r


    def get_bulk(self, oid) -> Union[list, None]:
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


class SnmpHandler:

    def __init__(self, host, **kwargs):
        if hasattr(host, 'ip'):
            self.host = host.ip
        else:
            self.host = host
        self.port = 161
        self.timeout = 2
        self.retries = 3
        self.version = '2c'
        self.community = 'public'
        self.username = False
        self.level = False
        self.integrity = False
        self.privacy = False
        self.authkey = False
        self.privkey = False
        self._parse_args(**kwargs)


    def _parse_args(self, **kwargs):
        for key in kwargs.keys():
            if key == 'version':
                self.version = kwargs[key]
            if key == 'community':
                self.community = kwargs[key]
            if key == 'host':
                self.host = kwargs[key]
            if key == 'port':
                try:
                    port = int(kwargs[key])
                except:
                    raise ArgumentError('Port must be an integer')
                if 1 <= port <= 65535:
                    self.port = port
                else:
                    raise ArgumentError('Port must be between 1 and 65535')
            if key == 'timeout':
                self.timeout = kwargs[key]
            if key == 'retries':
                self.retries = kwargs[key]
            if key == 'username':
                self.username = kwargs[key]
            if key == 'level':
                if kwargs[key] in VALID_V3_LEVELS:
                    self.level = kwargs[key]
                else:
                    raise ArgumentError('Security level invalid')
            if key == 'integrity':
                if kwargs[key] in VALID_INTEGRITY_ALGO:
                    self.integrity = kwargs[key]
                else:
                    raise ArgumentError('Integrity algorithm not valid')
            if key == 'privacy':
                if kwargs[key] in VALID_PRIVACY_ALGO:
                    self.privacy = kwargs[key]
                else:
                    raise ArgumentError('Privacy algorithm not valid')
            if key == 'authkey':
                self.authkey = kwargs[key]
            if key == 'privkey':
                self.privkey = kwargs[key]
        if not self.host:
            raise ArgumentError('Host not defined')
        if self.version not in VALID_VERSIONS:
            raise ArgumentError('No valid SNMP version defined')
        if self.version.startswith("2"):
            self.snmp_auth = cmdgen.CommunityData(self.community)
        elif self.version == "3":
            if not self.username:
                raise ArgumentError('No username specified')
            if not self.level:
                raise ArgumentError('No security level specified')
            if not self.integrity:
                raise ArgumentError('No integrity protocol specified')
            if not self.authkey:
                raise ArgumentError('No authkey specified')
            if self.level == 'authNoPriv':
                self.snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity])
            elif self.level == 'authPriv':
                if not self.privacy:
                    raise ArgumentError('No privacy protocol specified')
                if not self.privkey:
                    raise ArgumentError('No privacy key specified')
                self.snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity],
                    privKey=self.privkey,
                    privProtocol=PRIVACY_ALGO[self.privacy])


    def get(self, *oidlist):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port),
                                      timeout=self.timeout,
                                      retries=self.retries),
            *oidlist,
            lookupMib=False,
        )
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)
        pretty_varbinds = []
        for oid, value in varBinds:
            pretty_varbinds.append([oid.prettyPrint(),
                                    return_pretty_val(value)])
        return pretty_varbinds


    def get_value(self, *oidlist):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *oidlist,
            lookupMib=False
        )
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)
        values = []
        for oid, value in varBinds:
            values.append(return_pretty_val(value))
        if len(values) == 1:
            return values


    def getnext(self, *oidlist):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *oidlist,
            lookupMib=False
        )
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)
        pretty_vartable = []
        for varbinds in varTable:
            pretty_varbinds = []
            for oid, value in varbinds:
                pretty_varbinds.append([oid.prettyPrint(),
                                        return_pretty_val(value)])
            pretty_vartable.append(pretty_varbinds)
        return pretty_vartable


    def set(self, oid=None, value=None, value_type=None, multi=None):
        if multi is None:
            data = return_snmp_data(value, value_type)
            snmp_sets = (oid, data)
        else:
            snmp_sets = []
            for snmp_set in multi:
                if len(snmp_set) == 2:
                    oid = snmp_set[0]
                    value = snmp_set[1]
                    value_type = None
                    data = return_snmp_data(value, value_type)
                elif len(snmp_set) == 3:
                    oid = snmp_set[0]
                    value = snmp_set[1]
                    value_type = snmp_set[2]
                    data = return_snmp_data(value, value_type)
                snmp_sets.append((oid, data))
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.setCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *snmp_sets,
            lookupMib=False
        )
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)


class Worker(Thread):
    def __init__(self, requests, responses):
        Thread.__init__(self)
        self.snmpEngine = SnmpEngine()
        self.requests = requests
        self.responses = responses
        self.setDaemon(True)
        self.start()


    def run(self):
        while True:
            authData, transportTarget, varBinds = self.requests.get()
            self.responses.append(
                next(
                    getCmd(
                        self.snmpEngine,
                        authData, transportTarget, ContextData(), *varBinds
                    )
                )
            )
            if hasattr(self.requests, 'task_done'):  # 2.5+
                self.requests.task_done()


class ThreadPool:
    def __init__(self, num_threads):
        self.requests = Queue(num_threads)
        self.responses = []
        for _ in range(num_threads):
            Worker(self.requests, self.responses)


    def addRequest(self, authData, transportTarget, varBinds):
        self.requests.put((authData, transportTarget, varBinds))


    def getResponses(self): return self.responses


    def waitCompletion(self):
        if hasattr(self.requests, 'join'):
            self.requests.join()  # 2.5+
        else:
            from time import sleep
            # this is a lame substitute for missing .join()
            # adding an explicit synchronization might be a better solution
            while not self.requests.empty():
                sleep(1)


def multi_node_bulk_query(hosts: List[Any], varBinds=DEFAULT_VARBINDS):
    pool = ThreadPool(4)
    for host in hosts:
        if not isinstance(host, (SNMP, SnmpHandler)):
            raise Exception(f"Must pass in a object of type SNMP or SnmpHandler")
        trans = UdpTransportTarget((host.ip, 161))
        # SNMPv2c over IPv4/UDP
        authv2 = CommunityData(host.community)
        pool.addRequest(authv2, trans, varBinds)
        # SNMPv1 over IPv4/UDP
        authv1 = CommunityData(host.community, mpModel=0)
        pool.addRequest(authv1, trans, varBinds)
    # Wait for responses or errors
    pool.waitCompletion()
    # Walk through responses
    for errorIndication, errorStatus, errorIndex, varBinds in pool.getResponses():
        if errorIndication or errorStatus:
            print(f"ERROR: {host.ip} using {host.community}\n")
        else:
            print(f"SUCCESS: {host.ip} using {host.community}\n")
            for varBind in varBinds:
                print(' = '.join([ x.prettyPrint() for x in varBind ]))
                print('-'*100)

