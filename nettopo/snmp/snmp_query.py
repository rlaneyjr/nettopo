#!/usr/bin/env python

"""
Query Agents from multiple threads
++++++++++++++++++++++++++++++++++

"""
import json
from multiprocessing import cpu_count
from queue import Queue
from threading import Thread
from pysnmp.hlapi import *

comms = ['public', 'private', 'letmeSNMP']


class Worker(Thread):
    def __init__(self, requests, responses):
        Thread.__init__(self)
        self.snmp_engine = SnmpEngine()
        self.requests = requests
        self.responses = responses
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            auth_data, transport_target, var_binds = self.requests.get()
            self.responses.append(
                next(
                    getCmd(
                        self.snmp_engine,
                        auth_data,
                        transport_target,
                        ContextData(),
                        *var_binds
                    )
                )
            )
            if hasattr(self.requests, 'task_done'):
                self.requests.task_done()


class ThreadPool:
    def __init__(self, num_threads: int=None):
        num_threads = num_threads or cpu_count()
        self.requests = Queue(num_threads)
        self.responses = []
        for _ in range(num_threads):
            Worker(self.requests, self.responses)

    def addRequest(self, authData, transportTarget, varBinds=None):
        default_varbinds = ( ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                             ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        self.requests.put((authData, transportTarget, varBinds))

    def getResponses(self): return self.responses

    def waitCompletion(self):
        if hasattr(self.requests, 'join'):
            self.requests.join()
        else:
            from time import sleep
            # this is a lame substitute for missing .join()
            # adding an explicit synchronization might be a better solution
            while not self.requests.empty():
                sleep(1)


def run_pool(host, pool):
    trans = UdpTransportTarget((host, 161))
    for com in comms:
        # SNMPv2c over IPv4/UDP
        authv2 = CommunityData(com)
        pool.addRequest(authv2, trans, varBinds)
        # SNMPv1 over IPv4/UDP
        authv1 = CommunityData(com, mpModel=0)
        pool.addRequest(authv1, trans, varBinds)


if __name__ == "__main__":
    with open('snmp_results.nfo', 'w+') as sfile:
        pool = ThreadPool(4)
        for host in build_hosts(hits):
            authData, transportTarget = v1_bonitz(host)
            pool.addRequest(authData, transportTarget, varBinds)
            authData, transportTarget = v1_immedion(host)
            pool.addRequest(authData, transportTarget, varBinds)
            authData, transportTarget = v2_bonitz(host)
            pool.addRequest(authData, transportTarget, varBinds)
            authData, transportTarget = v2_immedion(host)
            pool.addRequest(authData, transportTarget, varBinds)
        # Wait for responses or errors
        pool.waitCompletion()
        # Walk through responses
        for errorIndication, errorStatus, errorIndex, varBinds in pool.getResponses():
            if errorIndication or errorStatus:
                print(f"ERROR: {host}, {transportTarget}\n")
                sfile.write(f"ERROR: {host}, {transportTarget}\n")
            else:
                print(f'SUCCESS: {host}, {transportTarget}\n')
                sfile.write(f'SUCCESS: {host}, {transportTarget}\n')
                for varBind in varBinds:
                    sfile.write(' = '.join([ x.prettyPrint() for x in varBind ]))
                    sfile.write('-'*100)

