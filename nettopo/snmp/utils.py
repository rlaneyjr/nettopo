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
    return value


def return_snmp_data(value, value_type=None):
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
        data = return_pretty_val(value)
        # raise TypeError(
        #     f"Unable to process type for {value} type: {value_type} \
        #     Please use one of: {', '.join(TYPES.keys())}"
        # )
    return data

