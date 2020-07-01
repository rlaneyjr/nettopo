#!/usr/bin/env python3

import ipaddress, json, logging, os, requests, socket, sys, urllib3
from functions import *

urllib3.disable_warnings()

token = '787be7592712066f0e595b114e1da832eb5966e9'
region = 'Italy'
site = 'Padova'
files = ['cdp_neighbors.json', 'facts.json', 'get_arp_table.json', 'interfaces.json', 'interfaces_ip.json', 'lldp_neighbors.json', 'mac_address_table.json', 'vlans.json']

url = 'http://192.168.102.130:8000/api/'
headers_get = {
    'Authorization': 'Token ' + token,
    'Accept': 'application/json;'
}
headers_post = headers_get
headers_post['Content-Type'] = 'application/json'


def main():
    # Reading options
    hosts, working_dir = checkOpts()

    logging.debug('Checking reachability and authentication of ' + url)
    try:
        r = requests.get(url, verify = False, headers = headers_get)
        response = r.json()
        response_code = r.status_code
        if response_code != 200:
            logging.error(response['detail'])
    except Exception as err:
        logging.error(err.error)
        sys.exit(1)

    logging.debug('Checking region ' + region)
    r = requests.get(url + 'dcim/regions/?slug=' + region.lower(), verify = False, headers = headers_get)
    response = r.json()
    response_code = r.status_code
    if response['count'] == 1:
        region_id = response['results'][0]['id']
    else:
        logging.info('Adding region ' + region)
        data = {
            'name': region,
            'slug': region.lower()
        }
        r = requests.post(url + 'dcim/regions/', verify = False, headers = headers_post, data = json.dumps(data))
        response = r.json()
        response_code = r.status_code
        if response_code == 201:
            region_id = response['id']
        else:
            logging.error(response)
            sys.exit(1)

    logging.debug('Checking site ' + site)
    r = requests.get(url + 'dcim/sites/?slug=' + site.lower(), verify = False, headers = headers_get)
    response = r.json()
    response_code = r.status_code
    if response['count'] == 1:
        site_id = response['results'][0]['id']
    else:
        logging.info('Adding site ' + site)
        data = {
            'name': site,
            'slug': site.lower(),
            'region': region_id
        }
        r = requests.post(url + 'dcim/sites/', verify = False, headers = headers_post, data = json.dumps(data))
        response = r.json()
        response_code = r.status_code
        if response_code == 201:
            site_id = response['id']
        else:
            logging.error(response)
            sys.exit(1)

    logging.debug('Checking device role TBD')
    r = requests.get(url + 'dcim/device-roles/?slug=tbd', verify = False, headers = headers_get)
    response = r.json()
    response_code = r.status_code
    if response['count'] == 1:
        device_role_id = response['results'][0]['id']
    else:
        logging.info('Adding device role TBD')
        data = {
            'name': 'To Be Defined',
            'slug': 'tbd',
            'color': 'ff0000'
        }
        r = requests.post(url + 'dcim/device-roles/', verify = False, headers = headers_post, data = json.dumps(data))
        response = r.json()
        response_code = r.status_code
        if response_code == 201:
            device_role_id = response['id']
        else:
            logging.error(response)
            sys.exit(1)

    # Reading discovered devices
    for device_name in os.listdir(working_dir):
        management_ip_id = None
        # Reading files
        for file in files:
            var_name = file.split('.')[0]
            try:
                with open('{}/{}/{}'.format(working_dir, device_name, file)) as fd:
                    globals()[var_name] = json.load(fd)
            except:
                logging.warning('cannot read {} for device {}'.format(file, device_name))
                globals()[var_name] = {}
                pass

        # Checking device vendor
        logging.debug('Checking manufacturer')
        r = requests.get(url + 'dcim/manufacturers/?slug=' + facts['vendor'].lower(), verify = False, headers = headers_get)
        response = r.json()
        response_code = r.status_code
        if response['count'] == 1:
            manufacturer_id = response['results'][0]['id']
        else:
            logging.info('Adding manufacturer ' + facts['vendor'])
            data = {
                'name': facts['vendor'],
                'slug': facts['vendor'].lower()
            }
            r = requests.post(url + 'dcim/manufacturers/', verify = False, headers = headers_post, data = json.dumps(data))
            response = r.json()
            response_code = r.status_code
            if response_code == 201:
                manufacturer_id = response['id']
            else:
                logging.error(response)
                sys.exit(1)

        # Checking device type
        logging.debug('Checking device type')
        r = requests.get(url + 'dcim/device-types/?slug=' + facts['model'].lower(), verify = False, headers = headers_get)
        response = r.json()
        response_code = r.status_code
        if response['count'] == 1:
            device_type_id = response['results'][0]['id']
        else:
            logging.info('Adding device type ' + facts['model'])
            data = {
                'model': facts['model'],
                'slug': facts['model'].lower(),
                'manufacturer': manufacturer_id
            }
            r = requests.post(url + 'dcim/device-types/', verify = False, headers = headers_post, data = json.dumps(data))
            response = r.json()
            response_code = r.status_code
            if response_code == 201:
                device_type_id = response['id']
            else:
                logging.error(response)
                sys.exit(1)

        # Checking device
        logging.debug('Checking device')
        r = requests.get(url + 'dcim/devices/?name=' + facts['hostname'].lower(), verify = False, headers = headers_get)
        response = r.json()
        response_code = r.status_code
        if response['count'] == 1:
            device_id = response['results'][0]['id']
        else:
            logging.info('Adding device ' + facts['hostname'].lower())
            data = {
                'device_role': device_role_id,
                'device_type': device_type_id,
                'name': facts['hostname'].lower(),
                'serial': facts['serial_number'],
                'site': site_id
            }
            r = requests.post(url + 'dcim/devices/', verify = False, headers = headers_post, data = json.dumps(data))
            response = r.json()
            response_code = r.status_code
            if response_code == 201:
                device_id = response['id']
            else:
                logging.error(response)
                sys.exit(1)

        # Checking interfaces
        logging.debug('Checking interfaces')
        r = requests.get(url + 'dcim/interfaces/?device_id=' + str(device_id), verify = False, headers = headers_get)
        response = r.json()
        response_code = r.status_code
        nb_interfaces = []
        if response['count'] > 0:
            # Checking if each interface is in NetBox
            for interface_name, interface in interfaces.items():
                for nb_interface in response['results']:
                    if interface_name == nb_interface['name']:
                        # Interface found
                        nb_interfaces.append(interface_name)
                        break

        # Adding missing interfaces
        for interface_name, interface in interfaces.items():
            if interface_name not in nb_interfaces:
                logging.info('Adding interface ' + interface_name + ' to device ' + facts['hostname'].lower())
                data = {
                    'description': interface['description'],
                    'device': device_id,
                    'is_connected': interface['is_up'],
                    'mac_address': interface['mac_address'],
                    'name': interface_name
                }
                r = requests.post(url + 'dcim/interfaces/', verify = False, headers = headers_post, data = json.dumps(data))
                response = r.json()
                response_code = r.status_code
                if response_code != 201:
                    logging.error(response)
                    sys.exit(1)
            else:
                logging.debug('Skipping interface ' + interface_name + ' to device ' + facts['hostname'].lower())

        # Checking IP addresses and prefixes
        ip_address_table = {}
        logging.debug('Checking IP addresses')
        for interfaces_ip_name, interface_ip in interfaces_ip.items():
            for ip_version, ip_items in interface_ip.items():
                for ip_item in ip_items:
                    ip_address_table[interfaces_ip_name] = ip_item + '/' + str(interface_ip[ip_version][ip_item]['prefix_length'])
        for interface_name, ip_address in ip_address_table.items():
            # Checking IP prefix
            ip_prefix = None
            try:
                ip_interface = ipaddress.IPv4Network(ip_address, strict = False)
                ip_prefix = str(ip_interface)
            except:
                ip_prefix = None
                pass
            if not ip_prefix:
                try:
                    ip_interface = ipaddress.IPv6Network(ip_address, strict = False)
                    ip_prefix = str(ip_interface)
                except:
                    logging.error('Cannot decode IP prefix for IP address ' + ip_address)
            r = requests.get(url + 'ipam/prefixes/?q=' + ip_prefix.split('/')[0], verify = False, headers = headers_get)
            response = r.json()
            response_code = r.status_code
            if response['count'] == 0:
                logging.info('Adding IP prefix ' + ip_prefix)
                data = {
                    'prefix': ip_prefix
                }
                r = requests.post(url + 'ipam/prefixes/', verify = False, headers = headers_post, data = json.dumps(data))
                response = r.json()
                response_code = r.status_code
                if response_code != 201:
                    logging.error(response)
                    sys.exit(1)
            # Getting interface ID
            logging.debug('Getting device ID for interface ' + interface_name)
            r = requests.get(url + 'dcim/interfaces/?device_id=' + str(device_id) + '&name=' + interface_name, verify = False, headers = headers_get)
            response = r.json()
            response_code = r.status_code
            if response['count'] == 1:
                interface_id = response['results'][0]['id']
            else:
                logging.error('Cannot get interface ID')
                sys.exit(1)
            # Checking IP address
            r = requests.get(url + 'ipam/ip-addresses/?q=' + ip_address.split('/')[0], verify = False, headers = headers_get)
            response = r.json()
            response_code = r.status_code
            if response['count'] == 0:
                logging.info('Adding IP address ' + ip_address)
                data = {
                    'address': ip_address,
                    'interface': interface_id
                }
                r = requests.post(url + 'ipam/ip-addresses/', verify = False, headers = headers_post, data = json.dumps(data))
                response = r.json()
                response_code = r.status_code

        # Getting managemet IP (Ansible hostname must be equal to )
        for host in hosts:
            if str(host).lower() == device_name:
                ansible_ip = socket.gethostbyname(host.vars['ansible_host'])
                r = requests.get(url + 'ipam/ip-addresses/?q=' + ansible_ip, verify = False, headers = headers_get)
                response = r.json()
                response_code = r.status_code
                if response['count'] == 1:
                    management_ip_id = response['results'][0]['id']
                else:
                    break
        # Setting managemet IP
        if management_ip_id:
            data = {
                'primary_ip4': management_ip_id
            }
            r = requests.patch(url + 'dcim/devices/' + str(device_id) + '/', verify = False, headers = headers_post, data = json.dumps(data))
            response = r.json()
            response_code = r.status_code
            if response_code != 200:
                logging.error('Failed to update management IP address')
if __name__ == "__main__":
    main()
    sys.exit(0)


    #print(response_code)
    #print(json.dumps(response, indent = 4, separators = (',', ':'), sort_keys = True))
    #sys.exit(0)
