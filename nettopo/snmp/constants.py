# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              constants.py
Description:        SNMP Constants
Author:             Ricky Laney
Version:            0.1.1
'''
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
    'VALID_VERSIONS',
    'VALID_V3_LEVELS',
    'VALID_INTEGRITY_ALGO',
    'VALID_PRIVACY_ALGO',
    'TYPES',
    'INTEGRITY_ALGO',
    'PRIVACY_ALGO',
]


VALID_VERSIONS = ('2c', '3')
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

