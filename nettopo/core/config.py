# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    config.py
'''
import json
import sys


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
        "expand_stackwise": False,
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

    def load(self, filename=None):
        # Load defaults then override with custom
        json_config = default_config
        if filename:
            json_data = self.load_json(filename)
            json_config.update(**json_data)
        self.host_domains = json_config['domains']
        self.snmp_creds = json_config['snmp']
        json_diagram = json_config.get('diagram')
        self.diagram.node_text_size = json_diagram.get('node_text_size')
        self.diagram.link_text_size = json_diagram.get('link_text_size')
        self.diagram.title_text_size = json_diagram.get('title_text_size')
        self.diagram.get_stack_members = json_diagram.get('get_stack_members')
        self.diagram.get_vss_members = json_diagram.get('get_vss_members')
        self.diagram.expand_stackwise = json_diagram.get('expand_stackwise')
        self.diagram.expand_vss = json_diagram.get('expand_vss')
        self.diagram.expand_lag = json_diagram.get('expand_lag')
        self.diagram.group_vpc = json_diagram.get('group_vpc')
        self.diagram.node_text = json_diagram.get('node_text', self.diagram.node_text)
        return True

    def load_json(self, json_file):
        with open(json_file) as jf:
            json_data = json.load(json_data)
        return json_data

    def generate_new(self):
        return default_config

    def validate_config(self):
        if not self.snmp_creds:
            return False
        else:
            return True
