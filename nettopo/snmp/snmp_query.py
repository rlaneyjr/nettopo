#!/usr/bin/env python

"""
Query Agents from multiple threads
++++++++++++++++++++++++++++++++++

"""
import json
from queue import Queue
from threading import Thread
from pysnmp.hlapi import *

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


def build_from_pretty(pretty_file):
    results = []
    with open(pretty_file) as pf:
        for item in json.load(pf):
           if len(item['scan'].values()) > 0:
               for key,value in item['scan'].items():
                   ip = key
                   oports = []
                   for k,v in value['tcp'].items():
                       if v['state'] == 'open':
                           port = k
                           pname = v['name']
                           pprod = v['product']
                           pextra = v['extrainfo']
                           oports.append({'port': port, 'port_name': pname, 'port_desc': f"{pprod} {pextra}"})
                   results.append({ 'ip': ip, 'ports': oports })
        return results


def build_hosts(results):
    hosts = []
    for item in results:
        hosts.append(item['ip'])
    return hosts


def v1_bonitz(host):
    # 1-st community (SNMPv1 over IPv4/UDP)
    return ( CommunityData('bonitz', mpModel=0),
             UdpTransportTarget((host, 161)))


def v1_immedion(host):
    # 2-nd community (SNMPv1 over IPv4/UDP)
    return ( CommunityData('immedion', mpModel=0),
             UdpTransportTarget((host, 161)))


def v2_bonitz(host):
    # 1-st community (SNMPv2c over IPv4/UDP)
    return ( CommunityData('bonitz'),
             UdpTransportTarget((host, 161)))


def v2_immedion(host):
    # 2-nd community (SNMPv2c over IPv4/UDP)
    return ( CommunityData('immedion'),
             UdpTransportTarget((host, 161)))


def add_host_to_pool(host, pool):
    varBinds = ( ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
    trans = UdpTransportTarget((host, 161))
    for com in comms:
        # SNMPv2c over IPv4/UDP
        authv2 = CommunityData(com)
        pool.addRequest(authv2, trans, varBinds)
        # SNMPv1 over IPv4/UDP
        authv1 = CommunityData(com, mpModel=0)
        pool.addRequest(authv1, trans, varBinds)


if __name__ == "__main__":
    hits = build_from_pretty('pretty_results.json')
    with open('pretty_ports.csv', 'w+') as cfile:
        for hit in hits:
            cfile.write(f"{hit['ip']}, {', '.join([port['port_desc'] for port in hit['ports']])}\n")
    print("Built CSV file")

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

