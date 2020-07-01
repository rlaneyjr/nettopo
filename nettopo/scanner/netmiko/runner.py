#!/Users/rlaney/.virtualenvs/netmiko/bin/python

from __future__ import absolute_import, division, print_function

#from datetime import datetime as dt
#from functools import wraps
from paramiko import ssh_exception
from netmiko import Netmiko, ssh_exception
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
from netmiko.snmp_autodetect import SNMPDetect
from pymongo import MongoClient
from pprint import pprint
import json
import logging
#from common import *
import os
import re
import sys
#from trigger.netdevices import NetDevices

NETMIKO_EXCEPTIONS = (ssh_exception.NetMikoTimeoutException,
                      ssh_exception.NetMikoAuthenticationException,
                      ssh_exception.SSHException, ValueError,
                      KeyError, IOError)

log_file = 'runner_' + now + '.log'
logging.basicConfig(filename=log_file, level=LEVEL2, format=FORMAT2)
#logged = logformat(log_file, FORMAT2, LEVEL2)

uri1 = 'mongodb://opUserRW:op42flow42@dc4-mongo/?authSource=admin'
con1 = MongoClient(uri1)
db1 = con1.nmis

uri2 = 'mongodb://opUserRW:op42flow42@sc9-mongo/?authSource=admin'
con2 = MongoClient(uri2)
db2 = con2.nmis
get_fields = {
              "_id": 0, "name": 1, "host": 1, "os_info.os": 1,
              "customer": 1, "group": 1, "deviceType": 1
              }

SKIPPED_TYPES = ['CiscoVPN3000', 'D-Link', 'HP-Switch', 'Linux', 'LinuxARM', 'RiOS',
                 'NetScreen', 'Checkpoint', 'Sofaware', 'UNKNOWN', 'Universal']

#netscaler_pw = 'ralrox22'
#username, password = mytools.get_creds()

ios_cmd = ['username etnoc priv 15 secret 0 B4ngHeadH3r3!', 'wr mem']
nxos_cmd = ['username etnoc password 0 B4ngHeadH3r3!', 'copy run start']
asa_cmd = ['username etnoc password B4ngHeadH3r3!', 'wr mem']
wlc_cmd = ['config mgmtuser password etnoc B4ngHeadH3r3!', 'save config']
avaya_cmd = ['username etnoc password B4ngHeadH3r3! access-type admin',
             'copy running-config startup-config']
chkpt_cmd = ['add user etnoc', 'set user etnoc password', 'B4ngHeadH3r3!', 'save config']
netscaler_cmd = ['set system user etnoc -password B4ngHeadH3r3!', 'save config']
palo_cmd = ['set mgt-config users etnoc password B4ngHeadH3r3!',
            'set mgt-config users etnoc permissions role-based superuser', 'commit']
rios_cmd = ['username etnoc password B4ngHeadH3r3!', 'write memory']
success = []
fail = []


def clean_devices(devices):
    crap = re.compile(r'\s\d\s')
    for dev in devices:
        crap_finder = re.search(crap, dev['name'])
        if crap_finder:
            logging.info("Found CRAP! Removing {} from the list!".format(dev['name']))
            devices.remove(dev)
    return devices


def set_default_type(devices):
    for device in devices:
        try:
            device.setdefault('os_info.os'['autodetect'])
        except KeyError:
            device.update({'os_info': {'os': 'autodetect'}})
    return devices


def get_devices():
    all_devices = list()
    for doc in db1.nodes.find(projection=get_fields):
        if doc not in all_devices:
            all_devices.append(doc)
    for doc in db2.nodes.find(projection=get_fields):
        if doc not in all_devices:
            all_devices.append(doc)
    #devices = clean_devices(all_devices)
    return all_devices


def map_device_type_to_values(device_type):
    username = 'rlaney'
    password = 'FunckyColdMadina22$'
    if device_type in ["ios", "cisco_ios"]:
        return { 'device_type': "cisco_ios",
                 'cmd': ios_cmd,
                 'username': username,
                 'password': password }
    elif device_type in ["ios-xe", "cisco_xe"]:
        return { 'device_type': "cisco_xe",
                 'cmd': ios_cmd,
                 'username': username,
                 'password': password }
    elif device_type in ["nxos", "cisco_nxos"]:
        return { 'device_type': "cisco_nxos",
                 'cmd': nxos_cmd,
                 'username': username,
                 'password': password }
    elif device_type in ["pix", "cisco_asa"]:
        return { 'device_type': "cisco_asa",
                 'cmd': asa_cmd,
                 'username': username,
                 'password': password }
    elif device_type in ["ciscowlc", "cisco_wlc"]:
        return { 'device_type': "cisco_wlc",
                 'cmd': wlc_cmd,
                 'username': username,
                 'password': password }
    elif device_type == "netscaler":
        return { 'device_type': "netscaler",
                 'cmd': netscaler_cmd,
                 'username': 'rlaney',
                 'password': 'ralrox22' }
    elif device_type in ["avaya", "avaya_ers"]:
        return { 'device_type': "avaya_ers",
                 'cmd': avaya_cmd,
                 'username': username,
                 'password': password }
    elif device_type in ["checkpoint", "checkpoint_gaia"]:
        return { 'device_type': "checkpoint_gaia",
                 'cmd': chkpt_cmd,
                 'username': 'admin',
                 'password': 'B!gB4ngTh30ry' }
    elif device_type in ["paloalto", "paloalto_panos"]:
        return { 'device_type': "paloalto_panos",
                 'cmd': palo_cmd,
                 'username': 'admin',
                 'password': 'B!gB4ngTh30ry' }
    elif device_type == "rios":
        return { 'device_type': "cisco_ios",
                 'cmd': rios_cmd,
                 'username': 'etnoc',
                 'password': 'circlebackaround' }
    else:
        logging.debug("Unsupported device type {}".format(device_type))
        raise KeyError


def auto_detect(device):
    ''' Attemp SNMP OID device type discovery first. If that fails we try
    a more 'manual' type of discovery.

    Parameters
    ----------
    hostname: str
        The name or IP address of the hostname we want to guess the type
    snmp_version : str, optional ('v1', 'v2c' or 'v3')
        The SNMP version that is running on the device (default: 'v3')
    snmp_port : int, optional
        The UDP port on which SNMP is listening (default: 161)
    community : str, optional
        The SNMP read community when using SNMPv2 (default: None)
    user : str, optional
        The SNMPv3 user for authentication (default: '')
    auth_key : str, optional
        The SNMPv3 authentication key (default: '')
    encrypt_key : str, optional
        The SNMPv3 encryption key (default: '')
    auth_proto : str, optional ('des', '3des', 'aes128', 'aes192', 'aes256')
        The SNMPv3 authentication protocol (default: 'aes128')
    encrypt_proto : str, optional ('sha', 'md5')
        The SNMPv3 encryption protocol (default: 'sha')
    '''
    try:
        my_snmp = SNMPDetect(hostname=device['host'], snmp_version='v2c',
                             community='0d71d56ae6')
        device_type = my_snmp.autodetect()
        logging.info("Autodetected {} for {}".format(device_type,
                                                     device['name']))
        print("Autodetected {} for {}".format(device_type, device['name']))
    except NETMIKO_EXCEPTIONS as e:
        remote_device = {'device_type': 'autodetect',
                         'host': device['host'],
                         'username': 'rlaney',
                         'password': 'FunckyColdMadina22$'}
        guesser = SSHDetect(**remote_device)
        device_type = guesser.autodetect()
        logging.info("Our best guess for {} was {}".format(device['name'],
                                                           device_type))
        logging.info("Our potential matches: {}".format(guesser.potential_matches))
        print("Our best guess for {} was {}".format(device['name'], device_type))
        print("Our potential matches: {}".format(guesser.potential_matches))
    finally:
        if device_type:
            return device_type
        else:
            raise KeyError


def get_type(device):
    if device['os_info']['os'] in SKIPPED_TYPES:
        logging.info("Skipping {} with {}".format(device['name'], device['os_info']['os']))
        print("Skipping {} with {}".format(device['name'], device['os_info']['os']))
        device['device_type'] = "skip"
    elif not device['os_info']['os']:
        logging.info("{} had no 'os_info', autodetecting".format(device['name']))
        try:
            dev_type = auto_detect(device)
            new_values = map_device_type_to_values(dev_type)
            device.update(new_values)
        except KeyError:
            logging.info("Unable to autodetect device type for {}".format(device['name']))
            print("Unable to autodetect device type for {}".format(device['name']))
            device['device_type'] = "unknown"
    else:
        dev_type = device['os_info']['os'].lower()
        new_values = map_device_type_to_values(dev_type)
        device.update(new_values)
    return device


def run_cmds(device):
    try:
        logging.debug('Connecting to {} with IP {}'.format(device['name'],
                                                          device['host']))
        cmd = device['cmd']
        connection = Netmiko(device_type=device['device_type'],
                             ip=device['host'],
                             username=device['username'],
                             password=device['password'],
                             global_delay_factor=2)
        logging.debug('Device prompt: ' + connection.base_prompt + '\n')
        connection.enable()
        if len(cmd) == 2:
            results = connection.send_config_set(cmd[0])
            connection.send_command_expect(cmd[1])
        elif len(cmd) == 3:
            save = cmd.pop([3])
            results = connection.send_config_set(cmd)
            connection.send_command_expect(save)
        elif len(cmd) == 4:
            save = cmd.pop([4])
            results = connection.send_config_set(cmd)
            connection.send_command_expect(save)
        else:
            logging.debug('Invalid command length {}'.format(len(cmd)))
            raise ValueError
        connection.disconnect()
        logging.debug(results)
        logging.debug('Successfully changed password for {}'.format(device['name']))
        logging.debug('~'*79 + '\n')
        success.append((device['name'], device['host']))
    except NETMIKO_EXCEPTIONS as e:
        if e is ssh_exception.NetMikoAuthenticationException:
            logging.debug('Device {} with IP {} would not allow login with OLD \
                          password.\n'.format(device['name'], device['host']))
            logging.info('Device {} password has already been changed?'.format( \
                         device['name']))
            success.append((device['name'], device['host']))
        else:
            logging.debug('Failed on {} with IP {}\n'.format(device['name'],
                                                            device['host']))
            logging.debug('Error: {}\n'.format(e))
            logging.debug('~'*79 + '\n')
            fail.append((device['name'], device['host']))


if __name__ == "__main__":
    with open("report_changes.txt", "w+") as report:
        dirty_devices = get_devices()
        logging.debug("{} unique devices pulled from Opmantek".format(len(dirty_devices)))
        report.write("{} unique devices pulled from Opmantek".format(len(dirty_devices)))
        devices = clean_devices(dirty_devices)
        remove_cnt = len(dirty_devices) - len(devices)
        logging.debug("{} clean devices. Removed {} devices with bad names" \
                      .format(clean_cnt, remove_cnt))
        report.write("{} clean devices. Removed {} devices with bad names" \
                      .format(clean_cnt, remove_cnt))
        for dev in devices:
            try:
                get_type(dev)
                logging.debug("Running {} on {} with type {}".format(dev['cmd'],
                                                                   dev['name'],
                                                                   dev['device_type']))
                run_cmds(dev)
            except NETMIKO_EXCEPTIONS as e:
                logging.debug("Not running commands on {}".format(dev))
                logging.debug("Error: {}".format(e))
                fail.append((dev['name'], dev['host']))
        logging.debug("Successfully changed {} devices".format(len(success)))
        logging.debug("Failed changing {} devices".format(len(fail)))

        report.write("Successfully changed {} devices".format(len(success)))
        report.write("=" * 79 + "\n")
        for name, ip in success.items():
            report.write("{} : {}".format(name, ip))
        report.write("\n" + "\n")
        report.write("Failed changing {} devices".format(len(success)))
        report.write("=" * 79 + "\n")
        for name, ip in fail.items():
            report.write("{} : {}".format(name, ip))

'''
Avaya
Checkpoint
CiscoVPN3000
CiscoWLC
D-Link
HP-Switch
IOS
IOS-XE
Linux
LinuxARM
NXOS
NetScreen
Netscaler
PIX
PaloAlto
RiOS
Sofaware
UNKNOWN
Universal

    'a10': A10SSH,
    'accedian': AccedianSSH,
    'alcatel_aos': AlcatelAosSSH,
    'alcatel_sros': AlcatelSrosSSH,
    'arista_eos': AristaSSH,
    'aruba_os': ArubaSSH,
    'avaya_ers': AvayaErsSSH,
    'avaya_vsp': AvayaVspSSH,
    'brocade_fastiron': RuckusFastironSSH,
    'brocade_netiron': BrocadeNetironSSH,
    'brocade_nos': BrocadeNosSSH,
    'brocade_vdx': BrocadeNosSSH,
    'brocade_vyos': VyOSSSH,
    'checkpoint_gaia': CheckPointGaiaSSH,
    'calix_b6': CalixB6SSH,
    'ciena_saos': CienaSaosSSH,
    'cisco_asa': CiscoAsaSSH,
    'cisco_ios': CiscoIosSSH,
    'cisco_nxos': CiscoNxosSSH,
    'cisco_s300': CiscoS300SSH,
    'cisco_tp': CiscoTpTcCeSSH,
    'cisco_wlc': CiscoWlcSSH,
    'cisco_xe': CiscoIosSSH,
    'cisco_xr': CiscoXrSSH,
    'coriant': CoriantSSH,
    'dell_force10': DellForce10SSH,
    'dell_os10': DellOS10SSH,
    'dell_powerconnect': DellPowerConnectSSH,
    'eltex': EltexSSH,
    'enterasys': EnterasysSSH,
    'extreme': ExtremeSSH,
    'extreme_wing': ExtremeWingSSH,
    'f5_ltm': F5LtmSSH,
    'fortinet': FortinetSSH,
    'generic_termserver': TerminalServerSSH,
    'hp_comware': HPComwareSSH,
    'hp_procurve': HPProcurveSSH,
    'huawei': HuaweiSSH,
    'huawei_vrpv8': HuaweiVrpv8SSH,
    'juniper': JuniperSSH,
    'juniper_junos': JuniperSSH,
    'linux': LinuxSSH,
    'mellanox': MellanoxSSH,
    'mrv_optiswitch': MrvOptiswitchSSH,
    'netapp_cdot': NetAppcDotSSH,
    'netscaler': NetscalerSSH,
    'ovs_linux': OvsLinuxSSH,
    'paloalto_panos': PaloAltoPanosSSH,
    'pluribus': PluribusSSH,
    'quanta_mesh': QuantaMeshSSH,
    'ruckus_fastiron': RuckusFastironSSH,
    'ubiquiti_edge': UbiquitiEdgeSSH,
    'ubiquiti_edgeswitch': UbiquitiEdgeSSH,
    'vyatta_vyos': VyOSSSH,
    'vyos': VyOSSSH,
'''
