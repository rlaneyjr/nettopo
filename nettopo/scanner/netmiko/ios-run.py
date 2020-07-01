#!/Users/rlaney/.virtualenvs/NetEngineerONE/bin/python

from __future__ import absolute_import, division, print_function

import netmiko
import paramiko
import json
import mytools
import os
import sys
import signal
#from trigger.netdevices import NetDevices

signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError: Broken pipe
signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C


#if len(sys.argv) < 3:
#    print('Usage: cmdrunner.py commands.txt devices.json')
#    exit()

netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException,
                      paramiko.ssh_exception.SSHException, ValueError,
                      KeyError, IOError)

with open('more_ip.txt') as device_file:
    devices = device_file.read().splitlines()


#''' Get all the IOS devices seperated and duplicates removed '''
#ios_devices = []
#try:
#    ios_devices = [d for d in mydevices if d['os'] == 'IOS']
#except KeyError:
#    print('Device {} is missing os key'.format(d['name']))
#
#ios_list = set()
#for dev in ios_devices:
#    device_type = dev['deviceType']
#    node = (dev['name']), (dev['host']), (device_type)
#    ios_list.add(node)


with open('op_user_cmds.txt') as ios_file:
    ios_commands = ios_file.read().splitlines()


username = 'etnoc'
password = 'circlebackaround'
#username, password = mytools.get_creds()


log_file = open('log_file.txt', 'w')
error_log_file = open('error_log.txt', 'w')
#nlog_file = open('error_log_NXOS.txt', 'w')

#log_file.write('Total IOS devices unsanitized: {} \n'.format(len(ios_devices)))
#log_file.write('Total sanitized IOS devices: {} \n'.format(len(ios_list)))
#log_file.write('~'*79 + '\n\n')


for device in devices:
    try:
        print('Connecting to IOS IP {} \n'.format(device))
        log_file.write('Connecting to IOS IP {} \n'.format(device))
        connection = netmiko.ConnectHandler(device_type='cisco_ios',
                                            ip=device,
                                            username=username,
                                            password=password,
                                            global_delay_factor=2)
        print('IOS Device: ' + connection.base_prompt + '\n')
        log_file.write('IOS Device: ' + connection.base_prompt + '\n')
        log_file.write(connection.send_config_set(ios_commands))
        log_file.write(connection.send_command('write memory'))
        connection.disconnect()
        log_file.write('~'*79 + '\n\n')
        print('~'*79 + '\n\n')
    except netmiko_exceptions as e:
        error_log_file.write('Failed on IP: {} \n'.format(device))
        error_log_file.write('Error: {} \n'.format(e))
        error_log_file.write('~' * 79 + '\n\n')

        print('Failed on IP: {} \n'.format(device))
        print('Error: {} \n'.format(e))
        print('~'*79 + '\n')

log_file.close()
error_log_file.close()
