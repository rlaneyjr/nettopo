#!/usr/bin/env python


import json
from easysnmp import Session, snmp_get, snmp_walk

comms = ['immedion', 'bonitz']


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


def get_hosts(results):
    hosts = []
    for item in results:
        hosts.append(item['ip'])
    return hosts


if __name__ == "__main__":
    res = build_from_pretty('pretty_results.json')
    hits = get_hosts(res)
    with open('easy_walker.nfo', 'w') as efile:
        for hit in hits:
            try:
                snmp_name = snmp_get('sysName.0', hostname=hit, community='bonitz', version=2)
                snmp_desc = snmp_get('sysDescr.0', hostname=hit, community='bonitz', version=2)
                efile.write(f"{hit},{snmp_name},{snmp_desc}\n")
            except:
                try:
                    snmp_name = snmp_get('sysName.0', hostname=hit, community='immedion', version=2)
                    snmp_desc = snmp_get('sysDescr.0', hostname=hit, community='immedion', version=2)
                    efile.write(f"{hit},{snmp_name},{snmp_desc}\n")
                except:
                    efile.write(f"Error with {hit}\n")

