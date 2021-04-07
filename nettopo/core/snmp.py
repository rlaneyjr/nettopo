# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
        snmp.py
'''
from about_time import about_time
from netaddr import IPAddress
from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.smi.rfc1902 import ObjectIdentity
from queue import Queue
from threading import Thread
from typing import Union, Dict, List, Any, Iterable
import json
import re

from nettopo.core.config import NettopoConfig
from nettopo.core.constants import (
    NOTHING,
    VALID_VERSIONS,
    VALID_V3_LEVELS,
    VALID_INTEGRITY_ALGO,
    VALID_PRIVACY_ALGO,
    INTEGRITY_ALGO,
    PRIVACY_ALGO,
)
from nettopo.core.exceptions import (
    NettopoSNMPError,
    NettopoSNMPTableError,
    NettopoSNMPValueError,
)
from nettopo.core.util import oid_endswith
from nettopo.snmp.utils import (
    return_pretty_val,
    return_snmptype_val,
)

# Typing shortcuts
_IP = Union[str, IPAddress]
_UIS = Union[int, str]
_UISO = Union[int, str, ObjectIdentity]
_UDL = Union[dict, list]
_UDLS = Union[dict, list, str]
_ULN = Union[list, None]
_ULS = Union[list, str]

DEFAULT_COMMS = ['public', 'private', 'letmeSNMP']
DEFAULT_VARBINDS = (ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))


class SNMPValue:
    def __init__(self, oid: object, data: _ULS,
                 time_taken: object, is_error=False) -> None:
        self.oid = oid
        self.duration = time_taken.duration
        self.name = str(oid)
        self.value = None
        if is_error:
            raise NettopoSNMPValueError(
                f"[SNMPValue] ERROR: {data}"
            )
        else:
            self._process_data(data)

    def __str__(self) -> str:
        return self.value or self.name

    def __repr__(self) -> str:
        return f"[SNMPValue] <{self.value}>"

    def _process_data(self, data) -> None:
        if self.value:
            raise NettopoSNMPValueError(
                f"Value exists for {self.name}"
            )
        self.raw_data = data
        # Single entry indicates single oid
        if len(data) == 1:
            self.value = data[0][1].prettyPrint()
        elif len(data) > 1:
            raise NettopoSNMPValueError(
                f"SNMPValue {len(data)} items, use SNMPTable for multiple items"
            )


class SNMPTable:
    def __init__(self, oid: Any, data: _ULS,
                 time_taken, is_error=False) -> None:
        self.oid = oid
        self.duration = time_taken.duration
        self.name = str(oid)
        self.value = None
        self.table = {}
        if is_error:
            raise NettopoSNMPTableError(data)
        else:
            self._process_data(data)

    def __str__(self) -> str:
        return self.value or self.name

    def __repr__(self) -> str:
        return f"[SNMPTable] <{self.name}>"

    def __len__(self) -> int:
        return len(self.table)

    def _process_data(self, data) -> None:
        if self.table:
            raise NettopoSNMPTableError(
                f"Table exists for {self.name}"
            )
        self.raw_data = data
        for row in data:
            for oid, val in row:
                oid = str(oid)
                if oid.startswith(self.name):
                    self.table.update({oid: val.prettyPrint()})

    def index_table(self, index: _UIS) -> dict:
        results = {}
        for oid, val in self.table.items():
            if oid_endswith(oid, index):
                results.update({oid: val})
        return results

    def search(self, item: _UISO, item_type: str='oid',
                        return_type: str=None) -> _UDL:
        """ Returns a dict unless 'return_type' specified which returns a list.
        User must handle single item lists.
        """
        results = {}
        for oid, val in self.table.items():
            if item_type == 'oid':
                # Oid matching is string based
                # Use regex to ensure we do not match ending digit
                # like '1' to '10', '100', etc.
                item_re = re.compile(str(item) + r'(?!\d)')
                # Match re with oid
                if item_re.match(oid):
                    results.update({oid: val})
            elif item_type == 'val':
                # Everything in SNMPTable is strings
                if str(item) == val:
                    results.update({oid: val})
            else:
                raise NettopoSNMPTableError(
                    f"Unknown item_type {item_type}"
                )
        if return_type:
            if return_type == 'oid':
                return [o for o in results.keys()]
            elif return_type == 'val':
                return [v for v in results.values()]
            else:
                raise NettopoSNMPTableError(
                    f"Unknown return_type {return_type}"
                )
        return results


class SNMP:
    def __init__(self, ip: _IP, port: int=161, **kwargs) -> None:
        self.ip = str(ip) if isinstance(ip, IPAddress) else ip
        self.port = port
        self.success = False
        self.community = None
        self.vulnerable = False
        self.config = NettopoConfig()
        if kwargs and 'community' in kwargs.keys():
            self.check_creds(kwargs.get('community'))
        else:
            self.check_creds(self.config.snmp_creds)
        if not self.success:
            if self.check_creds(DEFAULT_COMMS):
                self.vulnerable = True
            else:
                raise NettopoSNMPError(
                    f"Failed all SNMP creds - {self.ip}"
                )

    def check_community(self, community: str) -> bool:
        cmdGen = cmdgen.CommandGenerator()
        errIndication, errStatus, errIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData(community),
            cmdgen.UdpTransportTarget((self.ip, self.port)),
            '1.3.6.1.2.1.1.5.0')
        if errIndication:
            self.success = False
        else:
            self.success = True
            self.community = community
        return self.success

    def check_creds(self, snmp_creds: _UDLS) -> bool:
        if isinstance(snmp_creds, list):
            for cred in snmp_creds:
                if self.check_community(cred):
                    return True
        elif isinstance(snmp_creds, dict):
            for key, val in snmp_creds.items():
                if key == 'community':
                    if self.check_community(val):
                        return True
        else:
            if self.check_community(snmp_creds):
                return True
        return False

    def get_val(self, oid) -> SNMPValue:
        with about_time() as t_total:
            cmdGen = cmdgen.CommandGenerator()
            errIndication, errStatus, errIndex, varBinds = cmdGen.getCmd(
                cmdgen.CommunityData(self.community),
                cmdgen.UdpTransportTarget((self.ip, self.port), retries=2),
                oid,
            )
        if errIndication:
            error = f"SNMP({self.ip}): {errIndication}\n{errStatus}"
            return SNMPValue(oid, error, t_total, is_error=True)
        else:
            return SNMPValue(oid, varBinds, t_total)

    def get_bulk(self, oid) -> SNMPTable:
        with about_time() as t_total:
            cmdGen = cmdgen.CommandGenerator()
            errIndication, errStatus, errIndex, varBindTable = cmdGen.bulkCmd(
                cmdgen.CommunityData(self.community),
                cmdgen.UdpTransportTarget(
                    (self.ip, self.port),
                    timeout=30,
                    retries=2,
                ),
                0, 50, oid,
            )
        if errIndication:
            error = f"SNMP({self.ip}): {errIndication}\n{errStatus}"
            return SNMPTable(oid, error, t_total, is_error=True)
        else:
            return SNMPTable(oid, varBindTable, t_total)
