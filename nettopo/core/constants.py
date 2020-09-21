# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
constants.py
'''
from enum import Enum, auto
from pysnmp.entity.rfc3413.oneliner import cmdgen
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


__all__ = [
    'NOTHING',
    'VALID_VERSIONS',
    'VALID_V3_LEVELS',
    'VALID_INTEGRITY_ALGO',
    'VALID_PRIVACY_ALGO',
    'TYPES',
    'INTEGRITY_ALGO',
    'PRIVACY_ALGO',
    'RETCODE',
    'ENTPHYCLASS',
    'ARP',
    'DCODE',
    'NODE',
]

NOTHING = [None, '0.0.0.0', 'UNKNOWN', '']
VALID_VERSIONS = ('2', '2c', '3')
VALID_V3_LEVELS = ('authNoPriv', 'authPriv')
VALID_INTEGRITY_ALGO = ('md5', 'sha')
VALID_PRIVACY_ALGO = ('des', '3des', 'aes', 'aes192', 'aes256')

TYPES = {
    'Counter32': Counter32,
    'Counter64': Counter64,
    'Gauge32': Gauge32,
    'Integer': Integer,
    'Integer32': Integer32,
    'IpAddress': IpAddress,
    'OctetString': OctetString,
    'TimeTicks': TimeTicks,
    'Unsigned32': Unsigned32,
}

INTEGRITY_ALGO = {
    'md5': cmdgen.usmHMACMD5AuthProtocol,
    'sha': cmdgen.usmHMACSHAAuthProtocol
}

PRIVACY_ALGO = {
    'aes': cmdgen.usmAesCfb128Protocol,
    'aes192': cmdgen.usmAesCfb192Protocol,
    'aes256': cmdgen.usmAesCfb256Protocol,
    'des': cmdgen.usmDESPrivProtocol,
    '3des': cmdgen.usm3DESEDEPrivProtocol
}


class RETCODE:
    # return codes
    OK: int = 1
    ERR: int = 2
    SYNTAXERR: int = 3


class NODE:
    KNOWN: int = 1
    NEW: int = 2
    NEWIP: int = 3


class ARP:
    # ARP TYPES
    OTHER: int = 1
    INVALID: int = 2
    DYNAMIC: int = 3
    STATIC: int = 4


class ENTPHYCLASS:
    # OID_ENTPHYENTRY_CLASS values
    OTHER: int = 1
    UNKNOWN: int = 2
    CHASSIS: int = 3
    BACKPLANE: int = 4
    CONTAINER: int = 5
    POWERSUPPLY: int = 6
    FAN: int = 7
    SENSOR: int = 8
    MODULE: int = 9
    PORT: int = 10
    STACK: int = 11
    PDU: int = 12


class DCODE:
    ROOT: int = 0x01
    ERR_SNMP: int = 0x02
    DISCOVERED: int = 0x04
    STEP_INTO: int = 0x08
    CDP: int = 0x10
    LLDP: int = 0x20
    INCLUDE: int = 0x40
    LEAF: int = 0x80
    ROOT_STR: str = '[root]'
    ERR_SNMP_STR: str = '!'
    DISCOVERED_STR: str = '+'
    STEP_INTO_STR: str = '>'
    CDP_STR: str = '[cdp]'
    LLDP_STR: str = '[lldp]'
    INCLUDE_STR: str = 'i'
    LEAF_STR: str = 'L'
