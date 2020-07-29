# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
constants.py
'''
from enum import Enum, auto

try:
    from nettopo.oids import Oids as OID
except:
    print("Unable to import nettopo.oids")
    OID = None
    pass

__all__ = [
    'NOTHING',
    'RETCODE',
    'OID',
    'ENTPHYCLASS',
    'ARP',
    'DCODE',
    'NODE',
]

NOTHING = [None, '0.0.0.0', 'UNKNOWN', '']


class RETCODE(Enum):
    # return codes
    OK = auto()
    ERR = auto()
    SYNTAXERR = auto()


class NODE(Enum):
    KNOWN = auto()
    NEW = auto()
    NEWIP = auto()


class ARP(Enum):
    # ARP TYPES
    OTHER: int = 1
    INVALID: int = 2
    DYNAMIC: int = 3
    STATIC: int = 4


class ENTPHYCLASS(Enum):
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


class DCODE(Enum):
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
