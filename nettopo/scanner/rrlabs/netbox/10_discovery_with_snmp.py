#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

from nornir.core import InitNornir
from nornir.plugins.functions.text import print_result
from pysnmp.hlapi import *
from functions import *
import logging, pysnmp, re, sys

# Default variables
sysName = '.1.3.6.1.2.1.1.5.0'
cdpCacheDeviceId = '.1.3.6.1.4.1.9.9.23.1.2.1.1.6'
cdpCacheDevicePort = '.1.3.6.1.4.1.9.9.23.1.2.1.1.7'
cdpCachePlatform = '.1.3.6.1.4.1.9.9.23.1.2.1.1.8'
ifDescr = '.1.3.6.1.2.1.2.2.1.2'
vtpVlanName = '.1.3.6.1.4.1.9.9.46.1.3.1.1.4.1'

def basic_configuration(task):
    r = task.run(task = getSNMPAuth, name = 'Setting SNMP authentication', severity_level = logging.WARNING)
    task.host['snmp_auth'] = r.result
    task.run(task = getFacts, name = 'Getting facts', severity_level = logging.WARNING)
    r = task.run(task = getInterfaces, name = 'Getting interfaces', severity_level = logging.WARNING)
    task.host['local_interfaces'] = r.result
    task.run(task = getCDPNeighbors, name = 'Getting CDP neighbors', severity_level = logging.WARNING)
    task.run(task = getVLANs, name = 'Getting VLANs', severity_level = logging.WARNING)

def getCDPNeighbors(task):
    neighbors = {}
    local_port = {}
    try:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            task.host['snmp_auth'],
            UdpTransportTarget((task.host['nornir_host'], 161)),
            ContextData(),
            ObjectType(ObjectIdentity(cdpCacheDeviceId)),
            ObjectType(ObjectIdentity(cdpCacheDevicePort)),
            ObjectType(ObjectIdentity(cdpCachePlatform)),
            lookupMib = False,
            lexicographicMode = False
        ):
            if errorIndication or errorStatus or errorIndex:
                logger.error('error on  host "{}" while quering CDP data (SNMP error)'.format(task.host.name))
                return False
            neighbor_id = int(str(varBinds[0][0]).split('.')[-2])
            neighbors.setdefault(task.host['local_interfaces'][neighbor_id], [])
            neighbors[task.host['local_interfaces'][neighbor_id]].append({
                'remote_system_name': re.findall(r'([^(\n]+).*', str(varBinds[0][1]))[0],
                'remote_port': str(varBinds[1][1]),
                'remote_port_description': str(varBinds[1][1]),
                'remote_system_description': str(varBinds[2][1])
            })
    except Exception as err:
        logger.error('error on host "{}" while quering SNMP CDP data (exception)'.format(task.host.name), extra = err)
        return False

    return neighbors

def getFacts(task):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                task.host['snmp_auth'],
                UdpTransportTarget((task.host['nornir_host'], 161)),
                ContextData(),
                ObjectType(ObjectIdentity(sysName)),
                lookupMib = False,
                lexicographicMode = False
            )
        )
        if errorIndication or errorStatus or errorIndex:
            logger.error('error on  host "{}" while quering SNMP sysName (SNMP error)'.format(task.host.name))
            return False
    except Exception as err:
        logger.error('error on host "{}" while quering SNMP sysName (exception)'.format(task.host.name), extra = err)
        return False

    output =  {
        'uptime': None,
        'vendor': None,
        'os_version': None,
        'serial_number': None,
        'model': None,
        'hostname': str(varBinds[0][1]).split('.')[0],
        'fqdn': str(varBinds[0][1]),
        'interface_list': []
    }
    return output

def getInterfaces(task):
    interfaces = {}
    try:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            task.host['snmp_auth'],
            UdpTransportTarget((task.host['nornir_host'], 161)),
            ContextData(),
            ObjectType(ObjectIdentity(ifDescr)),
            lookupMib = False,
            lexicographicMode = False
        ):
            if errorIndication or errorStatus or errorIndex:
                logger.error('error on  host "{}" while quering SNMP ifDescr (SNMP error)'.format(task.host.name))
                return False
            interfaces[int(str(varBinds[0][0]).split('.')[-1])] = str(varBinds[0][1])
    except Exception as err:
        logger.error('error on host "{}" while quering SNMP ifDescr (exception)'.format(task.host.name), extra = err)
        return False

    return interfaces

def getSNMPAuth(task):
    SNMPAuth = None
    snmp_version = task.host['snmp_version'] if 'snmp_version' in dict(task.host) else None
    snmp_community = task.host['snmp_community'] if 'snmp_community' in dict(task.host) else None
    snmp_auth = task.host['snmp_auth'] if 'snmp_auth' in task.host else None
    snmp_username = task.host['snmp_username'] if 'snmp_username' in dict(task.host) else None
    snmp_password = task.host['snmp_password'] if 'snmp_password' in dict(task.host) else None
    snmp_priv = task.host['snmp_priv'] if 'snmp_priv' in dict(task.host) else None
    snmp_privpassword = task.host['snmp_privpassword'] if 'snmp_privpassword' in dict(task.host) else None

    if not snmp_version:
        logger.error('error on host "{}" because snmp_version is set'.format(task.host.name))

    if snmp_version == '2c':
        if snmp_community:
            SNMPAuth = CommunityData(snmp_community)
        else:
            llogger.error('error on host "{}" because snmp_community is not set/snot valid'.format(task.host.name))
            return False
    elif str(snmp_version) == '3':
        if not snmp_auth:
            auth_protocol = usmNoAuthProtocol
        elif snmp_auth == 'sha' and snmp_username and snmp_password:
            auth_protocol = usmHMACSHAAuthProtocol
        elif snmp_auth == 'md5' and snmp_username and snmp_password:
            auth_protocol = usmHMACMD5AuthProtocol
        else:
            logger.error('error on host "{}" because snmp_auth, snmp_username or snmp_password are not set/not valid'.format(task.host.name))
            return False
        if not snmp_priv:
            priv_protocol = usmNoPrivProtocol
        elif snmp_priv == 'des' and snmp_privpassword:
            priv_protocol = usmDESPrivProtocol
        elif snmp_priv == '3des' and snmp_privpassword:
            priv_protocol = usm3DESEDEPrivProtocol
        elif snmp_priv == 'aes128' and snmp_privpassword:
            priv_protocol = usmAesCfb128Protocol
        elif snmp_priv == 'aes192' and snmp_privpassword:
            priv_protocol = usmAesCfb192Protocol
        elif snmp_priv == 'aes256' and snmp_privpassword:
            priv_protocol = usmAesCfb256Protocol
        else:
            logger.error('skipping host "{}" because snmp_priv or snmp_privpassword are not set/not valid'.format(task.host.name))
            return False

        if snmp_auth and snmp_priv:
            SNMPAuth = UsmUserData(snmp_username, snmp_password, authProtocol = auth_protocol, privProtocol = priv_protocol)
        elif snmp_auth:
            SNMPAuth = UsmUserData(snmp_username, snmp_password, authProtocol = auth_protocol)
        else:
            logger.error('skipping host "{}" because snmp_priv requires snmp_auth'.format(task.host.name))
            return False
    else:
        logger.error('skipping host "{}" because snmp_version "{}" is not supported'.format(task.host.name, snmp_version))
        return False
    return SNMPAuth

def getVLANs(task):
    vlans = {}
    try:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            task.host['snmp_auth'],
            UdpTransportTarget((task.host['nornir_host'], 161)),
            ContextData(),
            ObjectType(ObjectIdentity(vtpVlanName)),
            lookupMib = False,
            lexicographicMode = False
        ):
            if errorIndication or errorStatus or errorIndex:
                logger.error('error on  host "{}" while quering SNMP vtpVlanName (SNMP error)'.format(task.host.name))
                return False
            vlans[int(str(varBinds[0][0]).split('.')[-1])] = str(varBinds[0][1])
    except Exception as err:
        logger.error('error on host "{}" while quering SNMP vtpVlanName (exception)'.format(task.host.name), extra = err)
        return False

    return vlans

def main():
    device_info = {}

    # Reading options
    host_file, group_file, working_dir = checkOpts()

    # Executing requests
    nr = InitNornir(num_workers = 20, host_file = 'hosts.yaml', group_file = 'groups.yaml')
    nrf = nr.filter(filter_func = lambda h: h['snmp_version'] in ['2c', '3'])
    result = nrf.run(task = basic_configuration)

    for device_name, device_multioutput in result.items():
        if device_multioutput.failed:
            logger.error('error while running on device {}'.format(device_name))
            continue
        device_info['facts'] = device_multioutput[2].result
        for interface_id, interface_name in device_multioutput[3].result.items():
            if interface_name not in ignore_interfaces:
                device_info['facts']['interface_list'].append(interface_name)
        device_info['cdp_neighbors'] = device_multioutput[4].result
        device_info['vlans'] = device_multioutput[5].result
        writeDeviceInfo(device_info, '{}/{}'.format(working_dir, device_info['facts']['hostname']))

    print_result(result, severity_level = logging.ERROR)

if __name__ == "__main__":
    main()
    sys.exit(0)
