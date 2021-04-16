# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    config.py
'''
from collections import UserList
from netaddr import IPNetwork
import json
import sys
from typing import Any, Union
from nettopo.core.data import SecretList, SingletonDecorator
from nettopo.core.exceptions import NettopoConfigError
from nettopo.core.util import is_ipv4_address


DEFAULT_CONFIG = {
    'general': {
        'show_progress': True,
        'verbose': True,
        'max_depth': 100,
    },
    'snmp': [
        {'community': 'letmeSNMP', 'ver': 2},
        {'community': 'private', 'ver': 2},
        {'community': 'public', 'ver': 2}
    ],
    'domains': [
        '.icloudmon.local',
    ],
    'discover': [
        'permit 10.0.0.0/8',
        'permit 172.16.0.0/12',
        'permit 192.168.0.0/16',
    ],
    'diagram': {
        'node_text_size': 10,
        'link_text_size': 8,
        'title_text_size': 16,
        'get_stack_members': True,
        'get_vss_members': True,
        'expand_stackwise': True,
        'expand_vss': True,
        'expand_lag': True,
        'group_vpc': True
    }
}


@SingletonDecorator
class NettopoConfig:
    def __init__(self, config=None, filename=None):
        # Load defaults then override with custom
        self.config = DEFAULT_CONFIG
        self.general = {}
        self.diagram = {}
        self.host_domains = []
        self.snmp_creds = SecretList([])
        self.acl = {'permit': [], 'deny': []}
        self.load(config=config, filename=filename)

    def add_acl_line(self, line: str) -> None:
        if line.startswith('#'):
            return
        elif line.startswith('permit'):
            net = IPNetwork(line.split(' ')[1])
            if net not in self.acl['permit']:
                self.acl['permit'].append(net)
        elif line.startswith('deny'):
            net = IPNetwork(line.split(' ')[1])
            if net not in self.acl['deny']:
                self.acl['deny'].append(net)
        else:
            raise NettopoConfigError(f"ACl line has no permit or deny {line}")

    def sync_config(self) -> None:
        general_cfg = self.config.get('general')
        self.general.update(**general_cfg)
        diagram_cfg = self.config.get('diagram')
        self.diagram.update(**diagram_cfg)
        for cred in self.config.get('snmp'):
            self.snmp_creds.append(cred['community'])
        for domain in self.config.get('domains'):
            if domain not in self.host_domains:
                self.host_domains.append(domain)
        for line in self.config.get('discover'):
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
        """ Is this IPv4 address allowed discovery?
        """
        if not is_ipv4_address(ip):
            raise NettopoConfigError(f"Invalid IPv4 - {ip}")
        # Check for host_wild first
        _host_wild = IPNetwork("0.0.0.0/32")
        if _host_wild in self.acl.get('permit'):
            return True
        elif _host_wild in self.acl.get('deny'):
            return False
        else:
            for allow_net in self.acl.get('permit'):
                if ip in allow_net:
                    return True
            for deny_net in self.acl.get('deny'):
                if ip in deny_net:
                    return False
        # No match is deny
        return False

    def passes_acl(self, net: Union[str, IPNetwork]) -> bool:
        """ Is this IPv4 address or IPv4 network allowed discovery?
        """
        if '/' not in str(net):
            return self.ip_passes_acl(str(net))
        if not isinstance(net, IPNetwork):
            net = IPNetwork(net)
        if net.prefixlen == 32:
            ip = str(net).split('/')[0]
            return self.ip_passes_acl(ip)
        else:
            # Check allow first
            for allow_net in self.acl.get('permit'):
                if (net == allow_net) or (net in allow_net):
                    return True
            for deny_net in self.acl.get('deny'):
                if (net == deny_net) or (net in deny_net):
                    return False
        # No match is deny
        return False
