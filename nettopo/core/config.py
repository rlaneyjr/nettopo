# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    config.py
'''
import json
import sys
from typing import Union


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

    def load(self, config=None, filename=None):
        # Load defaults then override with custom
        json_config = default_config
        if config:
            json_config.update(**config)
        if filename:
            json_data = self.load_json(filename)
            json_config.update(**json_data)
        for cred in json_config['snmp']:
            if cred['ver'] == 2:
                self.snmp_creds.append(cred['community'])
        for domain in json_config['domains']:
            self.host_domains.append(domain)

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
