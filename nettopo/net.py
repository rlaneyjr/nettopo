# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              net.py
Description:        Network Utilities
Author:             Ricky Laney
'''
from nettopo.sysdescrparser import sysdescrparser
from netaddr import IPAddress, IPNetwork
from snimpy.manager import Manager, load
from typing import Union, Dict, List

SNIMPY_MIBS = ['SNMPv2-MIB', 'IF-MIB', 'IP-MIB', 'IP-FORWARD-MIB', 'NHRP-MIB', 'POWER-ETHERNET-MIB', 'TUNNEL-MIB', 'VRRP-MIB', 'ENTITY-MIB', 'INET-ADDRESS-MIB']


class NtIPAddress(IPAddress):
    ''' Represents a ip we will discover
    '''


class NtNetwork(IPNetwork):
    ''' Represents a network we will discover
    '''


def load_mibs(mibs: list=SNIMPY_MIBS) -> None:
    for i in mibs:
        try:
            load(i)
        except:
            print(f"Unable to load {i}")


class Discover:
    def __init__(self, network: NtNetwork=None) -> None:
        self.network = network

    def discover(self) -> None:
        massscan_results = MassScanner(self.network)


class IcmpResponder:
    def __init__(self, ip: Union[str, IPAddress]) -> None:
        self.ip = ip

class PossibleNetDevice:
    """ Represents a network device that has at least one of the required ports
    open and accessible.
    """
    def __init__(self, ip: Union[str, IPAddress], ports: list=None) -> None:

sw1 = Manager('10.0.0.1', 'letmeSNMP', retries=2, timeout=3)
print(sw1.sysName)
print(sw1.sysDescr)
sw1_sys = sysdescrparser(str(sw1.sysDescr))
