# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        snmp.py
'''

import json
from queue import Queue
import re
from threading import Thread
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from typing import Union, Dict, List, Any
try:
    from netaddr import IPAddress
except:
    from ipaddress import ip_address as IPAddress

from nettopo.core.constants import (
    NOTHING,
    VALID_VERSIONS,
    VALID_V3_LEVELS,
    VALID_INTEGRITY_ALGO,
    VALID_PRIVACY_ALGO,
    TYPES,
    INTEGRITY_ALGO,
    PRIVACY_ALGO,
    RETCODE,
    ENTPHYCLASS,
    ARP,
    DCODE,
    NODE,
)
from nettopo.core.exceptions import NettopoSNMPError
from nettopo.snmp.utils import (
    return_pretty_val,
    return_snmptype_val,
)
from nettopo.core.util import oid_last_token
from nettopo.oids import Oids
o = Oids()

DEFAULT_COMMS = ['public', 'private', 'letmeSNMP']
DEFAULT_VARBINDS = (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

# Typing shortcuts
DLS = Union[dict, list, str]
DLSN = Union[dict, list, str, None]
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

    def __init__(self, ip: IP, **kwargs) -> None:
        self.ip = ip
        self.port = 161
        self.timeout = 10
        self.retries = 2
        self.version = '2c'
        self.community = None
        self.default_comms = DEFAULT_COMMS
        self.username = False
        self.level = False
        self.integrity = False
        self.privacy = False
        self.authkey = False
        self.privkey = False
        self.success = False
        self._parse_args(**kwargs)
        if not self.ip:
            raise ArgumentError('Host not defined')
        self._build_auth()
        if not self.success:
            raise NettopoSNMPError(f"Invalid SNMP creds for {self.ip}")
        self.transport = cmdgen.UdpTransportTarget(
            (self.ip, self.port),
            timeout=self.timeout,
            retries=self.retries
        )


    def _parse_args(self, **kwargs):
        for key in kwargs.keys():
            if key == 'version':
                self.version = kwargs[key]
            if key == 'community':
                self.community = kwargs[key]
            if key == 'host':
                self.ip = kwargs[key]
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


    def _build_auth(self) -> None:
        if self.version not in VALID_VERSIONS:
            raise ArgumentError('No valid SNMP version defined')
        if "2" in self.version:
            if self.community:
                self.find_v2_creds(self.community)
            else:
                self.find_v2_creds(self.default_comms)
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
                snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity])
            elif self.level == 'authPriv':
                if not self.privacy:
                    raise ArgumentError('No privacy protocol specified')
                if not self.privkey:
                    raise ArgumentError('No privacy key specified')
                snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity],
                    privKey=self.privkey,
                    privProtocol=PRIVACY_ALGO[self.privacy])
            self.check_auth(snmp_auth)


    def check_auth(self, snmp_auth) -> bool:
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBinds = cmdGen.getCmd(
            snmp_auth,
            cmdgen.UdpTransportTarget((self.ip, self.port),
                                      timeout=self.timeout,
                                      retries=self.retries),
            '1.3.6.1.2.1.1.5.0',
            lookupMib=False,
        )
        if errIndication:
            self.success = False
        else:
            self.success = True
            self.snmp_auth = snmp_auth
        return self.success


    def find_v2_creds(self, snmp_creds: DLS) -> bool:
        if isinstance(snmp_creds, str):
            snmp_auth = cmdgen.CommunityData(snmp_creds)
            if self.check_auth(snmp_auth):
                return True
        else:
            for cred in snmp_creds:
                if isinstance(cred, dict):
                    snmp_auth = cmdgen.CommunityData(cred['community'])
                    if self.check_auth(snmp_auth):
                        return True
                else:
                    snmp_auth = cmdgen.CommunityData(cred)
                    if self.check_auth(snmp_auth):
                        return True
        return False


    def get(self, *oidlist):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            self.transport,
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


    def get_val(self, oid):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            self.transport,
            oid,
            lookupMib=False
        )
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)
        value = return_pretty_val(varBinds[0][1])
        if value is any((o.ERR, o.ERR_INST)):
            return None
        return value


    def get_bulk(self, oid) -> Union[list, None]:
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBindTable = cmdGen.bulkCmd(
            self.snmp_auth,
            self.transport,
            0, 50, oid)
        if errorIndication or errorStatus:
            raise SnmpError(errorIndication._ErrorIndication__descr)
        else:
            pretty_table = []
            for row in varBindTable:
                for name, value in row:
                    if str(name).startswith(oid):
                        pretty_table.append([name.prettyPrint(),
                                             return_pretty_val(value)])
            return pretty_table


    def getnext(self, *oidlist):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.ip, self.port)),
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
            cmdgen.UdpTransportTarget((self.ip, self.port)),
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


class TableBuilder:
    def __init__(self, name: str, data: list) -> None:
        self.name = name
        self.raw_data = data
        self.table = []
        self._build_table(self.raw_data)

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return f"[TableBuilder] <{self.name}>"

    def __len__(self) -> int:
        return len(self.table)

    def _add_to_table(self, thing: Union[tuple, list]) -> None:
        if isinstance(thing, list):
            for item in thing:
                if item not in self.table:
                    self.table.append(item)
        else:
            if thing not in self.table:
                self.table.append(thing)

    def _build_table(self, data) -> None:
        if len(self.table):
            raise NettopoSNMPError(f"{self.name} has been built")
        for row in data:
            for oid, val in row:
                value = return_pretty_val(val)
                entry = (oid, value)
                self._add_to_table(entry)

    def index_table(self, index: Union[int, str], strip_oids: bool=True) -> List[tuple]:
        results = []
        for oid, val in self.table:
            if oid_last_token(oid) == index:
                if strip_oids:
                    oid_no_idx = '.'.join(str(oid).split('.')[:-1])
                    results.append((oid_no_idx, val))
                else:
                    results.append((oid, val))
        return results

    def search(
        self,
        item: Union[int, str, ObjectIdentity],
        item_type: str='oid',
        return_type: str=None,
    ) -> list:
        """ Always returns a list. User must handle single item lists.
        """
        results = []
        for oid, val in self.table:
            if item_type == 'oid':
                # Oid matching is string based
                item = str(item)
                # Use regex to ensure we do not match ending digit
                # like '1' to '10', '100', etc.
                item_re = re.compile(item + r'(?!\d)')
                # Match re with oid
                if item_re.match(str(oid)):
                    results.append((oid, val))
            elif item_type == 'val':
                if item == val:
                    results.append((oid, val))
            else:
                raise NettopoSNMPError(f"Wrong item_type {item_type}")
        if return_type:
            if return_type == 'oid':
                results = [oid for oid, _ in results]
            elif return_type == 'val':
                results = [val for _, val in results]
            else:
                raise NettopoSNMPError(f"Wrong return_type {return_type}")
        return results

