#!/usr/bin/env python
#

import json
import netsnmp
import argparse
import sys

comms = ['immedion', 'bonitz']

def get_hosts(results_file):
    hosts = []
    with open(results_file) as fd:
        data = json.load(fd)
        for d in data:
            net = d['net']
            try:
                for h in d['hosts']:
                    ip = h['ip']
                    hosts.append(ip)
            except:
                print(f'{net} had no hosts')
    return hosts


def snmp_walk(host):
    svars = netsnmp.VarList(netsnmp.Varbind('entityMIB'))
    with open('snmp_walk.csv', 'w+') as sfile:
        try:
            netsnmp.snmpwalk(svars, Version='2', DestHost=host,
                             Community='bonitz')
            sfile.writeline(f'{host} success with bonitz')
            print(f'{host} success with bonitz')
        except:
            netsnmp.snmpwalk(svars, Version='2', DestHost=host,
                             Community='immedion')
            sfile.writeline(f'{host} success with immedion')
            print(f'{host} success with immedion')
        for var in svars:
            sfile.writeline(f'{host}, {svars.tag}, {svars.iid}, {svars.val}')
            print(f'{host}, {svars.tag}, {svars.iid}, {svars.val}')



if __name__ == '__main__':
    res_file = 'scanned.json'
    for host in get_hosts(res_file):
        snmp_walk(host)
        print(f'{host} completed')

