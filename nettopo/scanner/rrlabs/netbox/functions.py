#!/usr/bin/env python3
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://www.gnu.org/licenses/gpl.html'
__revision__ = '20170329'

import getopt, json, logging, os, sys
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager

logger = logging.getLogger('nornir')

ignore_interfaces = [
    'Null0',
    'VoIP-Null0'
]

def usage():
    print('Usage: {} [OPTIONS]'.format(sys.argv[0]))
    print('  -h STRING  hosts file')
    print('  -g STRING  groups file')
    print('  -d         enable debug')
    sys.exit(1)

def checkOpts():
    host_file = None
    group_file = None

    # Reading options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'dh:g:')
    except getopt.GetoptError as err:
        logger.error('cannot parse options', exc_info = True)
        usage()

    for opt, arg in opts:
        if opt == '-d':
            logger.setLevel(logging.DEBUG)
        elif opt == '-h':
            host_file = arg
            working_dir = '{}/working/{}/devices'.format(os.path.dirname(os.path.abspath(arg)), os.environ.get('NETDOC_FOLDER', 'default'))
        elif opt == '-g':
            group_file = arg
        else:
            logger.error('unhandled option ({})'.format(opt))
            usage()
            sys.exit(1)

    # Checking options and environment
    if not host_file:
        logger.error('hosts file not specified')
        usage()
    if not os.path.isfile(host_file):
        logger.error('hosts file "{}" does not exist'.format(host_file))
        sys.exit(1)
    if not group_file:
        logger.error('groups file not specified')
        usage()
    if not os.path.isfile(group_file):
        logger.error('groups file "{}" does not exist'.format(group_file))
        sys.exit(1)

    return host_file, group_file, working_dir

def writeDeviceInfo(device_info, path):
    for key, value in device_info.items():
        try:
            os.makedirs(path, exist_ok = True)
        except Exception as err:
            logger.error('cannot create directory "{}"'.format(path), exc_info = True)
        try:
            output = open('{}/{}.json'.format(path, key), 'w+')
            output.write(json.dumps(value, sort_keys=True, indent=4, separators=(',', ': ')))
            output.close()
        except Exception as err:
            logger.error('cannot write "{}/{}.json"'.format(path, key), exc_info = True)
    return True
