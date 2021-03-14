# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    config.py
'''
from netaddr import IPNetwork
import json
import sys
from typing import Union

from nettopo.core.exceptions import NettopoConfigError
from nettopo.core.util import SingletonDecorator


DEFAULT_CONFIG = {
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


@SingletonDecorator
class Config:
    def __init__(self, config=None, filename=None):
        # Load defaults then override with custom
        self.config = DEFAULT_CONFIG
        self.host_domains = []
        self.snmp_creds = []
        self.diagram = DiagramDefaults()
        self.acl = {'permit': [], 'deny': []}
        self.load(config=config, filename=filename)

    def add_acl_line(self, line: str) -> None:
        if line.startswith('#'):
            return
        elif line.startswith('permit'):
            net = IPNetwork(line.split(' ip ')[1])
            if net not in self.acl['permit']:
                self.acl['permit'].append(net)
        elif line.startswith('deny'):
            net = IPNetwork(line.split(' ip ')[1])
            if net not in self.acl['deny']:
                self.acl['deny'].append(net)
        else:
            raise NettopoConfigError(f"ACl line has no permit or deny {line}")

    def sync_config(self) -> None:
        for cred in self.config['snmp']:
            if cred['community'] not in self.snmp_creds:
                self.snmp_creds.append(cred['community'])
        for domain in self.config['domains']:
            if domain not in self.host_domains:
                self.host_domains.append(domain)
        for line in self.config['discover']:
            self.add_acl_line(line)

    def load_json(self, json_file):
        with open(json_file) as jf:
            json_data = json.load(jf)
        return json_data

    def load(self, config=None, filename=None):
        if config:
            self.config.update(**config)
        if filename:
            json_data = self.load_json(filename)
            self.config.update(**json_data)
        self.sync_config()

    def ip_passes_acl(self, ip: str) -> bool:
        """ Check to see if this IP is allowed to be discovered
        """
        # Check allow first
        for allow_net in self.acl['permit']:
            if ip in allow_net:
                return True
        for deny_net in self.acl['deny']:
            if ip in deny_net:
                return False
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
