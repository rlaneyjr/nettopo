#!/usr/bin/env python3
import logging, natsort, re, sys, textfsm

# for i in 1 2 3 4 5; do ./procurve2catalyst.py switch${i}.cfg ${i} ${i}0 > switch${i}_cisco.cfg; done

config_file = sys.argv[1]
switch_id = int(sys.argv[2])
po_offset = int(sys.argv[3])

interface_prefix = f'GigabitEthernet{switch_id}/0/'
interfaces = {}
vlans = {'1': 'default'}

def rangeToList(x):
    result = []
    for part in x.split(','):
        if '-' in part:
            a, b = part.split('-')
            prefix_a = ''.join(re.findall(r'^\D+', a))
            prefix_b = ''.join(re.findall(r'^\D+', b))
            if prefix_a != prefix_b:
                logging.error('cannot parse a range with different prefixes')
                return []
            a = int(re.findall(r'\d+$', a)[0])
            b = int(re.findall(r'\d+$', b)[0])
            if a >= b:
                logging.error('cannot parse a range with unordered integers')
            a, b = int(a), int(b)
            for v in range(a, b + 1):
                result.append(f'{prefix_a}{v}')
        else:
            result.append(part)
    return result

def configureInterface(x, config = None):
    if not x in interfaces:
        interfaces[x] = []
    if config:
        interfaces[x].append(config)

def configureVlan(x, name = None):
    if not x in vlans:
        vlans[x] = None
    if name:
        vlans[x] = name

def trk2Po(x):
    id = int(''.join(re.findall(r'\d+$', x)))
    return f'Port-channel{id + po_offset}'

# Configure logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Reading configuration
with open(config_file, 'r') as f:
    running_config = f.read()

# Reading interface description
desc_template = open('interface.template')
re_table = textfsm.TextFSM(desc_template)
for k in re_table.ParseText(running_config):
    if k[1]:
        configureInterface(f'{interface_prefix}{k[0]}', f'description {k[1]}')
    if k[2]:
        configureInterface(f'{interface_prefix}{k[0]}', f'shutdown')
    else:
        configureInterface(f'{interface_prefix}{k[0]}', f'no shutdown')

# Reading trunks (port-channels)
trunk_template = open('trunk.template')
re_table = textfsm.TextFSM(trunk_template)
for trunk in re_table.ParseText(running_config):
    configureInterface(f'Port-channel{int(trunk[1]) + po_offset}')
    for port_id in rangeToList(trunk[0]):
        configureInterface(f'{interface_prefix}{port_id}', f'channel-group {int(trunk[1]) + po_offset} mode active')

# Reading vlans
trunk_interfaces = {}
vlan_template = open('vlan.template')
re_table = textfsm.TextFSM(vlan_template)
for vlan in re_table.ParseText(running_config):
    # Adding VLAN
    configureVlan(vlan[0], vlan[1])
    # Adding SVI
    if vlan[2] and vlan[3]:
        configureInterface(f'Vlan{vlan[0]}', f'ip address {vlan[2]} {vlan[3]}')
    # Getting interfaces where VLAN is untagged
    if vlan[4]:
        for port_id in rangeToList(vlan[4]):
            if 'Trk' in port_id:
                port = trk2Po(port_id)
            else:
                port = f'{interface_prefix}{port_id}'
            trunk_interfaces[port] = {
                'native': vlan[0],
                'trunked': []
            }
    if vlan[5]:
        for port_id in rangeToList(vlan[5]):
            if 'Trk' in port_id:
                port = trk2Po(port_id)
            else:
                port = f'{interface_prefix}{port_id}'
            if port not in trunk_interfaces:
                trunk_interfaces[port] = {
                    'native': None,
                    'trunked': []
                }
            trunk_interfaces[port]['trunked'].append(vlan[0])

# Reading SNMP
snmp_contact = None
snmp_location = None
snmp_communities = []
snmp_hosts = {}

snmp_contact_template = open('snmp-contact.template')
re_table = textfsm.TextFSM(snmp_contact_template)
for contact in re_table.ParseText(running_config):
    snmp_contact = contact[0]

snmp_location_template = open('snmp-location.template')
re_table = textfsm.TextFSM(snmp_location_template)
for location in re_table.ParseText(running_config):
    snmp_location = location[0]

snmp_community_template = open('snmp-community.template')
re_table = textfsm.TextFSM(snmp_community_template)
for community in re_table.ParseText(running_config):
    snmp_communities.extend(community)

snmp_hosts_template = open('snmp-hosts.template')
re_table = textfsm.TextFSM(snmp_hosts_template)
for host in re_table.ParseText(running_config):
    snmp_hosts[host[0]] = host[1]

# Reading SNTP
sntp_hosts = []
sntp_template = open('sntp.template')
re_table = textfsm.TextFSM(sntp_template)
for host in re_table.ParseText(running_config):
    sntp_hosts.append(host[0])

# Reading default gateway
default_gateway = None
default_gateway_template = open('default-gateway.template')
re_table = textfsm.TextFSM(default_gateway_template)
for gateway in re_table.ParseText(running_config):
    default_gateway = gateway[0]

# Reading STP
stp_template = open('stp.template')
re_table = textfsm.TextFSM(stp_template)
for interface in re_table.ParseText(running_config):
    if 'Trk' in interface[0]:
        port = trk2Po(interface[0])
    else:
        port = f'{interface_prefix}{interface[0]}'
    if interface[1]:
        # BPDU protection
        configureInterface(port, 'spanning-tree bpduguard enable')
    elif interface[2]:
        # BPDU filter
        configureInterface(port, 'spanning-tree bpdufilter enable')
    elif interface[3]:
        # Admin Edge
        if port in interfaces and 'switchport mode trunk' in interfaces[port]:
            configureInterface(port, 'spanning-tree portfast trunk')
        else:
            configureInterface(port, 'spanning-tree portfast')

# Printing configuration
for vlan, name in vlans.items():
    print(f'vlan {vlan}')
    if name and int(vlan) != 1:
        print(f' name {name}')
    print('!')

for interface_name, interface_configs in natsort.natsorted(interfaces.items()):
    print(f'interface {interface_name}')
    for interface_config in interface_configs:
        print(f' {interface_config}')
    if interface_name in trunk_interfaces:
        if trunk_interfaces[interface_name]['trunked']:
            print(' switchport mode trunk')
            print(' switchport trunk allowed vlan {}'.format(','.join(trunk_interfaces[interface_name]['trunked'])))
            if trunk_interfaces[interface_name]['native']:
                print(f' switchport trunk native vlan {trunk_interfaces[interface_name]["native"]}')
        elif trunk_interfaces[interface_name]['native']:
            print(' switchport mode access')
            print(f' switchport access vlan {trunk_interfaces[interface_name]["native"]}')
    print('!')

if default_gateway:
    print('ip routing')
    print(f'ip route 0.0.0.0 0.0.0.0 {default_gateway}')

if snmp_contact:
    print(f'snmp-server contact {snmp_contact}')
if snmp_location:
    print(f'snmp-server location {snmp_location}')
for snmp_community in snmp_communities:
    print(f'snmp-server community {snmp_community} ro')
for snmp_host, snmp_community in snmp_hosts.items():
    print(f'snmp-server host {snmp_host} {snmp_community}')
print('!')

for sntp_host in sntp_hosts:
    print(f'ntp server {sntp_host}')
print('!')

print('end')
