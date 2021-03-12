# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        util.py
'''
import binascii
from datetime import timedelta
from functools import wraps
from pyasn1.type.univ import ObjectIdentifier
from pysnmp.proto.rfc1902 import (
    Counter32,
    Counter64,
    Gauge32,
    Integer,
    Integer32,
    IpAddress,
    OctetString,
    TimeTicks,
    Unsigned32,
)
import re
from timeit import default_timer as timer
from typing import Union
import uuid
# My Stuff
from nettopo.core.constants import TYPES
from nettopo.core.exceptions import NettopoError, NettopoTypeError


__all__ = [
    'build_uuid',
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
    'mac_hex_to_ascii',
    'parse_allowed_vlans',
    'in_acl',
    'str_matches_pattern',
    'lookup_table',
    'oid_last_token',
    'is_ipv4_address',
    'return_pretty_val',
    'return_snmptype_val',
    'bits_2_megabytes',
]


def build_uuid():
    return str(uuid.uuid4())


def timethis(func):
    @wraps(func)
    def run_func(*args, **kwargs):
        start = timer()
        run = func(*args, **kwargs)
        end = timer() - start
        h = int(end / 3600)
        m = int((end - (h * 3600)) / 60)
        s = end - (int(end / 3600) * 3600) - (m * 60)
        print(f"Completed {func.__name__} in {h}:{m:02}:{s:.2f}")
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
    cidr_m = t[1]
    o = cidr_ip.split('.')
    cidr_ip = (
        (int(o[0]) << 24)
        + (int(o[1]) << 16)
        + (int(o[2]) << 8)
        + (int(o[3]))
    )
    cidr_mb = 0
    zeros = 32 - int(cidr_m)
    for b in range(0, zeros):
        cidr_mb = (cidr_mb << 1) | 0x01
    cidr_mb = 0xFFFFFFFF & ~cidr_mb
    o = ip.split('.')
    ip = (
        (int(o[0]) << 24)
        + (int(o[1]) << 16)
        + (int(o[2]) << 8)
        + (int(o[3]))
    )
    return ((cidr_ip & cidr_mb) == (ip & cidr_mb))


def bits_2_megabytes(bits_per_sec) -> int:
    return int(bits_per_sec) / 8000000


def normalize_host(host: Union[str, list], domains: list=None):
    # some devices (eg Motorola) report as hex strings
    if host.startswith('0x'):
        try:
            host = binascii.unhexlify(host[2:]).decode('utf-8')
        except Exception:
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
        return 'Unknown'
    else:
        port = port.replace('TenGigabitEthernet', 'te')
        port = port.replace('GigabitEthernet', 'gi')
        port = port.replace('FastEthernet', 'fa')
        port = port.replace('port-channel', 'po')
        port = port.replace('Loopback', 'lo')
        port = port.replace('Vlan', 'vl')
        port = port.replace('Te', 'te')
        port = port.replace('Gi', 'gi')
        port = port.replace('Fa', 'fa')
        port = port.replace('Lo', 'lo')
        port = port.replace('Po', 'po')
        port = port.replace('Vl', 'vl')
    return port


def ip_2_str(ip_hex: Union[str, int]) -> str:
    ip = None
    try:
        if isinstance(ip_hex, str):
            ip = int(ip_hex, base=0)
        elif isinstance(ip_hex, int):
            ip = ip_hex
        seg1 = ((ip >> 24) & 0xFF)
        seg2 = ((ip >> 16) & 0xFF)
        seg3 = ((ip >> 8) & 0xFF)
        seg4 = (ip & 0xFF)
        ip = f"{seg1}.{seg2}.{seg3}.{seg4}"
    except ValueError as e:
        ip = e
    finally:
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
    x = img.decode("utf-8") if isinstance(img, bytes) else str(img)
    try:
        img_s = re.search('(Version:? |CCM:)([^ ,$]*)', x)
    except:
        return img
    if img_s:
        if img_s.group(1) == 'CCM:':
            return f"CCM {img_s.group(2)}"
        return img_s.group(2)
    return img


def mac_ascii_to_hex(mac_str):
    mac_str = re.sub(r'[\.:]', '', mac_str)
    if not len(mac_str) == 12:
        return None
    mac_hex = ''
    for i in range(0, len(mac_str), 2):
        mac_hex += chr(int(mac_str[i:i+2], 16))
        return mac_hex


def mac_hex_to_ascii(mac_hex, *, separator: str='.') -> str:
    ''' Format a hex MAC string to ASCII

    :param:     mac_hex
        Value from SNMP
    :param:str:     separator
        '.' to format as 'aabb.ccdd.eeff' (default)
    :return:str:
        String representation of the mac_hex
    '''
    if not str(mac_hex).startswith('0x'):
        return mac_hex
    v = mac_hex[2:]
    mac = ''
    if separator == '.':
        mac_segs = [str(v[i:i+4]) for i in range(0, len(v), 4)]
        mac = separator.join(mac_segs)
    elif separator in [':', '-']:
        mac_segs = [str(v[i:i+2]) for i in range(0, len(v), 2)]
        mac = separator.join(mac_segs)
    else:
        mac = str(v)
    return mac


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
            vlan = ((i - 2) * 4) + b
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


def lookup_table(table, item):
    if not table:
        return None
    for row in table:
        for n, v in row:
            if item in str(n):
                return v.prettyPrint()
    return None


def oid_last_token(objectId):
    oid = objectId.getOid()
    idx = len(oid) - 1
    return oid[idx]


def strip_oid_index(oid, idx):
    oid = oid.getOid()
    if oid_last_token(objectId) == idx:
        return oid[:-1]
    return oid


def is_ipv4_address(value):
    try:
        from netaddr import IPAddress
        ip = IPAddress(value)
        if isinstance(ip, IPAddress):
            return True
        else:
            return False
    except:
        try:
            c1, c2, c3, c4 = value.split(".")
            assert 0 <= int(c1) <= 255
            assert 0 <= int(c2) <= 255
            assert 0 <= int(c3) <= 255
            assert 0 <= int(c4) <= 255
            return True
        except:
            return False


def return_pretty_val(value):
    if isinstance(value, (
        Counter32,
        Counter64,
        Gauge32,
        Integer,
        Integer32,
        Unsigned32,
    )):
        return int(value.prettyPrint())
    if isinstance(value, (IpAddress, ObjectIdentifier)):
        return str(value.prettyPrint())
    if isinstance(value, OctetString):
        try:
            return value.asOctets().decode(value.encoding)
        except UnicodeDecodeError:
            return value.asOctets()
    if isinstance(value, TimeTicks):
        return timedelta(seconds=int(value.prettyPrint()) / 100.0)
    if isinstance(value, bytes):
        return value.prettyPrint().decode('utf-8')
    return value


def return_snmptype_val(value, value_type=None):
    if not value_type:
        value_type = type(value)
    if value_type in TYPES:
        data = TYPES[value_type](value)
    elif value_type in [int, float]:
        data = Integer(value)
    elif value_type == str:
        if is_ipv4_address(value):
            data = IpAddress(value)
        else:
            data = OctetString(value)
    else:
        raise NettopoTypeError(
            f"Unable to process type for {value} type: {value_type} \
            Please use one of: {', '.join(TYPES.keys())}"
        )
    return data


def snmp_extract(snmp_data, data_type='val'):
    '''
    Unwrap the SNMP response data and return the requested 'data_type' in a
    readable 'pretty' format. Will only return single item first one in list.
    '''
    if len(snmp_data) > 1:
        raise ValueError("snmp_extract only allows a single element")
    if len(snmp_data) == 0:
        return None
    else:
        # Unwrap the data which is returned as a tuple wrapped in a list
        if data_type == 'val':
            return snmp_data[0][1].prettyPrint()
        elif data_type == 'oid':
            return snmp_data[0][0].getOid()

