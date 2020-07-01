#!/usr/bin/env python3

import os
import sys
import nmap

IP_FILE = 'small_nets.nfo'


def get_nets(IP_FILE):
    nets = []
    with open(IP_FILE) as net_file:
        for line in net_file.readlines():
            nets.append(line)
    return nets


def port_scan_nets(nets):
    results = []
    pscan = nmap.PortScanner()
    for net in nets:
        #res = pscan.scan(net, '21-22,80,443,161,53')
        results.append(pscan.scan(net, '21-22,161'))
    return results

if __name__ == '__main__':
    print(port_scan_nets(get_nets(IP_FILE)))
