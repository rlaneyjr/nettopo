# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        util.py
'''

import re
import binascii
from functools import wraps
from timeit import default_timer as timer
from typing import Union
from nettopo.core.exceptions import NettopoError


__all__ = [
    'timethis',
    'bits_from_mask',
    'in_cidr',
    'normalize_host',
    'normalize_port',
    'ip_2_str',
    'get_port_module',
    'ip_from_cidr',
    'get_path',
    'format_ios_ver',
    'mac_ascii_to_hex',
    'mac_format_ascii',
    'mac_hex_to_ascii',
    'mac_format_cisco',
    'parse_allowed_vlans',
    'in_acl',
    'str_matches_pattern',
    'lookup_table',
    'oid_last_token',
]


def timethis(func):
    @wraps(func)
    def run_func(*args, **kwargs):
        start = timer()
        run = func(*args, **kwargs)
        end = timer() - start
        h=int(end/3600)
        m=int((end-(h*3600))/60)
        s=end-(int(end/3600)*3600)-(m*60)
        print(f"Completed in {h}:{m}:{s:.2f}")
        return run
    return run_func

def bits_from_mask(netm):
    cidr = 0
    mt = netm.split('.')
    for b in range(0, 4):
        v = int(mt[b])
        while (v > 0):
            if (v & 0x01):
                cidr += 1
            v = v >> 1
    return cidr

def in_cidr(ip, cidr):
    t = cidr.split('/')
    cidr_ip = t[0]
    cidr_m  = t[1]
    o = cidr_ip.split('.')
    cidr_ip = ((int(o[0])<<24) + (int(o[1]) << 16) + (int(o[2]) << 8) + (int(o[3])))
    cidr_mb = 0
    zeros = 32 - int(cidr_m)
    for b in range(0, zeros):
        cidr_mb = (cidr_mb << 1) | 0x01
    cidr_mb = 0xFFFFFFFF & ~cidr_mb
    o = ip.split('.')
    ip = ((int(o[0])<<24) + (int(o[1]) << 16) + (int(o[2]) << 8) + (int(o[3])))
    return ((cidr_ip & cidr_mb) == (ip & cidr_mb))

def normalize_host(host: Union[str, list], domains: list=None):
    # some devices (eg Motorola) report as hex strings
    if host.startswith('0x'):
        try:
            host = binascii.unhexlify(host[2:]).decode('utf-8')
        except:
            # this can fail if the node gives us bad data - revert to original
            # ex, lldp can advertise MAC as hostname, and it might not convert
            # to ascii
            host = host
    # Nexus appends (SERIAL) to hosts
    host = re.sub('\([^\(]*\)$', '', host)
    if domains:
        if isinstance(domains, list):
            for domain in domains:
                domain = domain if domain.startswith('.') else f".{domain}"
                host = host.replace(domain, '')
        elif isinstance(domains, str):
            domain = domains if domains.startswith('.') else f".{domains}"
            host = host.replace(domain, '')
        else:
            raise NettopoError(f"normalize_host {type(domains)} unsupported")
    # fix some stuff that can break Dot
    host = re.sub('-', '_', host)
    host = host.rstrip(' \r\n\0')
    return host

def normalize_port(port: str=None):
    if not port:
        return 'UNKNOWN'
    else:
        port = port.replace('TenGigabitEthernet', 'te')
        port = port.replace('GigabitEthernet', 'gi')
        port = port.replace('FastEthernet', 'fa')
        port = port.replace('port-channel', 'po')
        port = port.replace('Loopback', 'lo')
        port = port.replace('Te', 'te')
        port = port.replace('Gi', 'gi')
        port = port.replace('Fa', 'fa')
        port = port.replace('Po', 'po')
    return port

def ip_2_str(_ip):
    ip = int(_ip, 0)
    ip = '%i.%i.%i.%i' % (((ip >> 24) & 0xFF), ((ip >> 16) & 0xFF), ((ip >> 8) & 0xFF), (ip & 0xFF))
    return ip

def get_port_module(port):
    try:
        s = re.search('[^\d]*(\d*)/\d*/\d*', port)
        if s:
            return s.group(1)
    except:
        pass
    return False

def ip_from_cidr(cidr):
    try:
        s = re.search('^(.*)/[0-9]{1,2}$', cidr)
        if s:
            return s.group(1)
    except:
        pass
    return cidr

def get_path(pattern):
    try:
        match = re.search('{([^\}]*)}', pattern)
        tokens = match[1].split('|')
    except:
        return [pattern]
    return [pattern.replace(match[0], token) for token in tokens]

def format_ios_ver(img):
    x = img.decode("utf-8") if isinstance(img, bytes) else img
    try:
        img_s = re.search('(Version:? |CCM:)([^ ,$]*)', x)
    except:
        return img
    if img_s:
        if img_s.group1 == 'CCM:':
            return f"CCM {img_s.group(2)}"
        return img_s.group(2)
    return img

def mac_ascii_to_hex(mac_str):
    mac_str = re.sub('[\.:]', '', mac_str)
    if not len(mac_str) == 12:
        return None
    mac_hex = ''
    for i in range(0, len(mac_str), 2):
        mac_hex += chr(int(mac_str[i:i+2], 16))
        return mac_hex

def mac_hex_to_ascii(mac_hex, inc_dots):
    ''' Format a hex MAC string to ASCII
    Args:
        mac_hex:    Value from SNMP
        inc_dots:   1 to format as aabb.ccdd.eeff, 0 to format aabbccddeeff
    Returns:
        String representation of the mac_hex
    '''
    v = mac_hex[2:]
    ret = ''
    for i in range(0, len(v), 4):
        ret += v[i:i+4]
        if inc_dots and (i+4) < len(v):
            ret += '.'
    return ret

def mac_format_ascii(mac_hex, inc_dots):
    v = mac_hex.prettyPrint()
    return mac_hex_to_ascii(v, inc_dots)

def mac_format_cisco(devid):
    mac_seg = [devid[x:x+4] for x in xrange(2, len(devid), 4)]
    return '.'.join(mac_seg)

def parse_allowed_vlans(allowed_vlans):
    if not allowed_vlans.startswith('0x'):
        return 'All'
    ret = ''
    group = 0
    op = 0
    for i in range(2, len(allowed_vlans)):
        v = int(allowed_vlans[i], 16)
        for b in range(0, 4):
            a = v & (0x1 << (3 - b))
            vlan = ((i-2)*4)+b
            if a:
                if op:
                    group += 1
                else:
                    if ret:
                        if group > 1:
                            ret += '-'
                            ret += str(vlan - 1) if vlan else '1'
                        else:
                            ret += f",{int(vlan)}"
                    else:
                        ret += str(vlan)
                    group = 0
                    op = 1
            else:
                if op:
                    if ret and group:
                        ret += f"-{int(vlan - 1)}"
                    op = 0
                group = 0
    if op:
        if ret == '1':
            return 'All'
        if group:
            ret += '-1001'
        else:
            ret += ',1001'
    return ret if ret else 'All'

def in_acl(item, acl):
        if acl == 'any':
            return True
        if not re.match('^([0-2]?[0-9]?[0-9]\.){3}[0-2]?[0-9]?[0-9]$', ip):
            return False
        try:
            if ip in IPNetwork(cidr):
                return True
        except:
            if in_cidr(ip, cidr):
                return True
        return False

def str_matches_pattern(string, pattern):
    return True if string == '*' or re.search(pattern, string) else False

def lookup_table(table, name):
    if table:
        for row in table:
            for n, v in row:
                if name in str(n):
                    return v.prettyPrint()
    else:
        return None

def oid_last_token(objectId):
    oid = objectId.getOid()
    idx = len(oid) - 1
    return oid[idx]
