#!/usr/bin/env python

#title:             parsenmap.py
#description:       Parse's Nmap results
#author:            Ricky Laney
#date:              20190411
#version:           0.0.1
#usage:             python parsenmap.py or ./parsenmap.py
#notes:
#python_version:    3.7.0
#==============================================================================

import ast
from collections import OrderedDict
import datetime as dt
import json
import nmap
from pprint import pprint as pp

tday = dt.date.today().strftime('%m-%d-%Y')
my_file = f'results_{tday}.json'
da_file = 'pretty_results.json'


def parse_file(da_file):
    res_scan = []
    with open(da_file) as f:
        scans = ast.literal_eval(f.read())
        for s in scans:
            net = s['nmap']['command_line'].split()[-1]
            hosts = s['scan']
            if not hosts:
                res = {"net": net}
            else:
                host_list = []
                for key in hosts.keys():
                    ip = key
                    host = hosts[ip]
                    if len(host['hostnames']) > 1:
                        host_names = []
                        for h in host['hostnames']:
                            for hk,hv in h.items():
                                if hk == 'name' and hv:
                                    host_names.append(hv)
                    else:
                        host_names = host['hostnames'][0]['name']
                    ports = []
                    for ky in host['tcp'].keys():
                        port_name = str(ky)
                        ky = host['tcp'][ky]
                        if ky['state'] == 'open':
                            open_port = {'port': port_name}
                            for k,v in ky.items():
                                if k == 'product' and v != '':
                                    open_port.update({'prod': v})
                                if k == 'extrainfo' and v != '':
                                    open_port.update({'extra ': v})
                                if k == 'cpe' and v != '':
                                    open_port.update({'cpe ': v})
                            ports.append(open_port)
                    host_list.append(OrderedDict({"ip": ip,
                                                  "names": host_names,
                                                  "ports": ports}))
                    res = OrderedDict({"net": net, "hosts": host_list})
            res_scan.append(res)
        return res_scan


def write_results(my_file):
    with open(my_file, 'w+') as m:
        data = parse_file(da_file)
        json.dump(data, m, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    write_results(my_file)
