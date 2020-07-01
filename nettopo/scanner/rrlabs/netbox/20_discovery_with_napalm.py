#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

import napalm
from functions import *

def main():
    # Reading options
    hosts, working_dir = checkOpts()

    # Discover each host
    for host in hosts:
        device_info = {}
        try:
            ansible_host = host.vars['ansible_host']
            ansible_username = host.vars['ansible_username']
            ansible_password = host.vars['ansible_password']
            napalm_driver = host.vars['napalm_driver']
        except Exception as err:
            logger.warning('skipping host "{}" because ansible_host, ansible_username, ansible_password and/or napalm_driver are not set in inventory file'.format(host.vars['ansible_host']))
            continue

        logger.debug('connecting to "{}"'.format(host.vars['ansible_host']))
        driver = napalm.get_network_driver(napalm_driver)
        device = driver(hostname = ansible_host, username = ansible_username, password = ansible_password, optional_args = {'port': 22})
        device.open()
        device_info['facts'] = device.get_facts()
        device_info['interfaces'] = device.get_interfaces()
        device_info['interfaces_ip'] = device.get_interfaces_ip()
        device_info['get_arp_table'] = device.get_arp_table()
        device_info['mac_address_table'] = device.get_mac_address_table()
        device_info['lldp_neighbors'] = device.get_lldp_neighbors_detail()
        device.close()

        writeDeviceInfo(device_info, '{}/{}'.format(working_dir, device_info['facts']['hostname'].lower()))

if __name__ == "__main__":
    main()
    sys.exit(0)
