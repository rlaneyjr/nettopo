# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    config.py
'''
from netaddr import IPNetwork
import json
import sys
from typing import Union

from .exceptions import NettopoConfigError


default_config = {
    "snmp": [
        {"community": "private", "ver": 2},
        {"community": "public", "ver": 2}
    ],
    "domains": [
        ".company.net",
        ".company.com"
    ],
    "discover": [
        "permit ip 10.0.0.0/8",
        "permit ip 172.16.0.0/12",
        "permit ip 192.168.0.0/16",
        "permit ip 0.0.0.0/32"
    ],
    "diagram": {
        "node_text_size": 10,
        "link_text_size": 8,
        "title_text_size": 15,
        "get_stack_members": True,
        "get_vss_members": True,
        "expand_stackwise": True,
        "expand_vss": True,
        "expand_lag": True,
        "group_vpc": True
    }
}


class DiagramDefaults:
    node_text_size = 10
    link_text_size = 8
    title_text_size = 15
    get_stack_members = True
    get_vss_members = True
    expand_stackwise = True
    expand_vss = True
    expand_lag = True
    group_vpc = True


class Config:
    def __init__(self):
        self.host_domains = []
        self.snmp_creds = []
        self.diagram = DiagramDefaults()
        self.acl = {'permit': [], 'deny': []}

    def load(self, config=None, filename=None):
        # Load defaults then override with custom
        json_config = default_config
        if config:
            json_config.update(**config)
        if filename:
            json_data = self.load_json(filename)
            json_config.update(**json_data)
        creds = [cred['community'] for cred in json_config['snmp']]
        self.snmp_creds.extend(creds)
        domains = [domain for domain in json_config['domains']]
        self.host_domains.extend(domains)
        for line in json_config['discover']:
            if line.startswith('permit'):
                net = IPNetwork(line.split(' ip ')[1])
                self.acl['permit'].append(net)
            elif line.startswith('deny'):
                net = IPNetwork(line.split(' ip ')[1])
                self.acl['deny'].append(net)
            elif line.startswith('#'):
                continue
            else:
                raise NettopoConfigError(
                    f"Line in discover ACL has no permit or deny: {line}")

    def load_json(self, json_file):
        with open(json_file) as jf:
            json_data = json.load(jf)
        return json_data

    def add_creds(self, creds: Union[str, list]=None) -> None:
        if isinstance(creds, list):
            for cred in creds:
                self.snmp_creds.append(cred)
        else:
            self.snmp_creds.append(creds)

    def ip_passes_acl(self, ip: str) -> bool:
        """ Check to see if this IP is allowed to be discovered
        """
        # Check deny first
        for denies in self.acl['deny']:
            if ip in denies:
                return False
        for allows in self.acl['permit']:
            if ip in allows:
                return True
        else:
            return False

    def net_passes_acl(self, net: Union[str, IPNetwork]) -> bool:
        """ Check to see if this IP is allowed to be discovered
        """
        if '/' not in net:
            return self.ip_passes_acl(net)
        if not isinstance(net, IPNetwork):
            net = IPNetwork(net)
        if net.prefixlen == 32:
            host_wild = IPNetwork("0.0.0.0/32")
            if host_wild in self.acl['deny']:
                return False
            elif host_wild in self.acl['permit']:
                return True
            else:
                ip = str(net).split('/')[0]
                return self.ip_passes_acl(ip)
        if net in self.acl['deny']:
            return False
        elif net in self.acl['permit']:
            return True
        else:
            return self.ip_passes_acl(net)
