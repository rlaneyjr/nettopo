# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
Title:              snmp.py
Description:        SNMP
Author:             Ricky Laney
Version:            0.1.1
"""
import json
from queue import Queue
from threading import Thread
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen

from nettopo.snmp.constants import (
    VALID_VERSIONS,
    VALID_V3_LEVELS,
    VALID_INTEGRITY_ALGO,
    VALID_PRIVACY_ALGO,
    TYPES,
    INTEGRITY_ALGO,
    PRIVACY_ALGO,
)
from nettopo.snmp.errors import ArgumentError, SnmpError
from nettopo.snmp.utils import (
    return_pretty_val,
    return_snmp_data,
)

comms = ['public', 'private', 'letmeSNMP']


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


class SnmpHandler:

    def __init__(self, **kwargs):
        self.port = 161
        self.timeout = 2
        self.retries = 3
        self.version = '2c'
        self.community = 'public'
        self.host = False
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
