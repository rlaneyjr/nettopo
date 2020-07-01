# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              utils.py
Description:        SNMP Utils
Author:             Ricky Laney
Version:            0.1.1
'''
from datetime import timedelta
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

from nettopo.snmp.constants import TYPES

__all__ = [
    'is_ipv4_address',
    'return_pretty_val',
    'return_snmp_data',
]

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
    if isinstance(value, Counter32):
        return int(value.prettyPrint())
    if isinstance(value, Counter64):
        return int(value.prettyPrint())
    if isinstance(value, Gauge32):
        return int(value.prettyPrint())
    if isinstance(value, Integer):
        return int(value.prettyPrint())
    if isinstance(value, Integer32):
        return int(value.prettyPrint())
    if isinstance(value, Unsigned32):
        return int(value.prettyPrint())
    if isinstance(value, IpAddress):
        return str(value.prettyPrint())
    if isinstance(value, ObjectIdentifier):
        return str(value.prettyPrint())
    if isinstance(value, OctetString):
        try:
            return value.asOctets().decode(value.encoding)
        except UnicodeDecodeError:
            return value.asOctets()
    if isinstance(value, TimeTicks):
        return timedelta(seconds=int(value.prettyPrint()) / 100.0)
    return value


def return_snmp_data(value, value_type):
    if value_type is None:
        if isinstance(value, int):
            data = Integer(value)
        elif isinstance(value, float):
            data = Integer(value)
        elif isinstance(value, str):
            if is_ipv4_address(value):
                data = IpAddress(value)
            else:
                data = OctetString(value)
        else:
            raise TypeError(
                "Unable to autodetect type. Please pass one of "
                "these strings as the value_type keyword arg: "
                ", ".join(TYPES.keys())
            )
    else:
        if value_type not in TYPES:
            raise ValueError(f"{value_type} is not one of the supported types: \
                             {', '.join(TYPES.keys())}")

        data = TYPES[value_type](value)
    return data

