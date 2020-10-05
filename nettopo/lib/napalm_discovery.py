#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20171206'

import getopt, json, logging, napalm, os, sys
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

logging.basicConfig(level = logging.INFO)

def main():
    # Set default
    inventory_file = None
    ansible_loader = DataLoader()
    discovered_devices = {}
    output_file = 'discovery_output.json'
    links = []

    # Reading options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'di:')
    except getopt.GetoptError as err:
        logger.error(err)
        sys.exit(255)

    for opt, arg in opts:
        if opt == '-d':
            logging.basicConfig(level = logging.DEBUG)
        elif opt == '-i':
            inventory_file = arg
        else:
            logging.error('unhandled option ({})'.format(opt))
            sys.exit(255)

    # Checking options and environment
    if not inventory_file:
        logging.error('inventory file not given (use -i)')
        sys.exit(255)
    if not os.path.isfile(inventory_file):
        logging.error('inventory file does not exist ({})'.format(inventory_file))
        sys.exit(255)
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except:
            logging.error('output file cannot be deleted ({})'.format(output_file))
            sys.exit(255)

    # Reading the inventory file
    try:
        ansible_inventory = InventoryManager(loader = ansible_loader, sources = inventory_file)
    except:
        logging.error('cannot read inventory file ({})'.format(inventory_file))
        sys.exit(255)
    variable_manager = VariableManager(loader = ansible_loader, inventory = ansible_inventory)

    # Discover each host
    for host in ansible_inventory.get_hosts():
        driver = napalm.get_network_driver(host.vars['napalm_driver'])
        device = driver(hostname = host.vars['ansible_host'], username = host.vars['ansible_username'], password = host.vars['ansible_password'], optional_args = {'port': 22})
        device.open()
        facts = device.get_facts()
        neighbors = device.get_cdp_neighbors_detail()
        device.close()

        # Saving data
        discovered_devices.setdefault(facts['fqdn'], {})
        discovered_devices[facts['fqdn']] = {
            'facts': facts,
            'neighbors': neighbors
        }

    # For each device
    for device_name, device in discovered_devices.items():
        if device['neighbors']:
            # For each interface where a neighbor exists
            for device_if_name, neighbors in device['neighbors'].items():
                # For each neighbor
                for neighbor in neighbors:
                    remote_device_name = neighbor['remote_system_name']
                    remote_if_name = neighbor['remote_port']
                    if device_name > remote_device_name:
                        source = remote_device_name
                        source_if = remote_if_name
                        destination = device_name
                        destination_if = device_if_name
                    else:
                        source = device_name
                        source_if = device_if_name
                        destination = remote_device_name
                        destination_if = remote_if_name
                    link = {
                        'source': source,
                        'source_if': source_if,
                        'destination': destination,
                        'destination_if': destination_if
                    }

                    if not link in links:
                        links.append(link)

    try:
        discovery_output = open(output_file, 'w+')
        discovery_output.write(json.dumps(links))
        discovery_output.close()
    except:
        logging.error('output file is not writable ({})'.format(output_file))
        sys.exit(255)

if __name__ == "__main__":
    main()
    sys.exit(0)

