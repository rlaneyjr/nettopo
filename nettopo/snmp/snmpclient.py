# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

"""
Completely stolen from Dennis (below) with some minor modifications for my needs.

Wrapper around pysnmp for easy access to snmp-based information
(c)2008-2010 Dennis Kaarsemaker
Latest version can be found on http://github.com/seveas/python-snmpclient
"""
from dataclasses import dataclass
import datetime
from functools import cached_property
from glob import glob
import pysnmp.entity.rfc3413.oneliner.cmdgen as cmdgen
from pysnmp.smi import builder, view
from pysnmp.smi.error import SmiError

from ..sysdescrparser import sysdescrparser

__all__ = ['V1', 'V2', 'V2C', 'add_mib_path', 'load_mibs', 'load_default_mibs',
           'nodeinfo', 'nodename', 'nodeid', 'SnmpClient', 'cmdgen']

# Snmp version constants
V1 = 0
V2 = V2C = 1

SYS_MIBS = (("SNMPv2-MIB", "sysDescr"), ("SNMPv2-MIB", "sysObjectID"), ("SNMPv2-MIB", "sysUpTime"), ("SNMPv2-MIB", "sysContact"), ("SNMPv2-MIB", "sysName"), ("SNMPv2-MIB", "sysLocation"), ("SNMPv2-MIB", "sysServices"), ("SNMPv2-MIB", "sysORLastChange"), ("SNMPv2-MIB", "sysORID"), ("SNMPv2-MIB", "sysORUpTime"), ("SNMPv2-MIB", "sysORDescr"))

# The internal mib builder
__mibBuilder = builder.MibBuilder()
__mibViewController = view.MibViewController(__mibBuilder)

def add_mib_path(*path):
    """Add a directory to the MIB search path"""
    __mibBuilder.setMibPath(*(__mibBuilder.getMibPath() + path))

def load_mibs(*modules):
    """Load one or more mibs"""
    for m in modules:
        try:
            __mibBuilder.loadModules(m)
        except SmiError as e:
            if 'already exported' in str(e):
                continue
            raise

def load_default_mibs():
    # Load basic mibs that come with pysnmp
    load_mibs('SNMPv2-MIB','IF-MIB','IP-MIB','HOST-RESOURCES-MIB','FIBRE-CHANNEL-FE-MIB')
    # Load all mibs that come with net-snmp
    netsnmp_path = '/usr/share/snmp/mibs'
    mib_files = add_mib_path(netsnmp_path)
    mib_files = glob(f"{netsnmp_path}/*")
    for mib_file in mib_files:
        netsnmp_mib = mib_file.split('/')[-1].rstrip('.txt')
        load_mibs(netsnmp_mib)


def nodeinfo(oid):
    """Translate dotted-decimal oid to a tuple with symbolic info"""
    if isinstance(oid, basestring):
        oid = tuple([int(x) for x in oid.split('.') if x])
    return (__mibViewController.getNodeLocation(oid),
            __mibViewController.getNodeName(oid))

def nodename(oid):
    """Translate dotted-decimal oid or oid tuple to symbolic name"""
    oid = __mibViewController.getNodeLocation(oid)
    name = '::'.join(oid[:-1])
    noid = '.'.join([str(x) for x in oid[-1]])
    if noid:
        name += '.' + noid
    return name

def nodeid(oid):
    """Translate named oid to dotted-decimal format"""
    ids = oid.split('.')
    symbols = ids[0].split('::')
    ids = tuple([int(x) for x in ids[1:]])
    mibnode, = __mibBuilder.importSymbols(*symbols)
    oid = mibnode.getName() + ids
    return oid

class SnmpClient:
    """ Easy access to an snmp deamon on a host
    """
    DEFAULT_AUTHS = ['public', 'private', 'letmeSNMP', 'snmp', 'cisco']

    def __init__(self, host: str, authorizations: list=None, *, port: int=161):
        """Set up the client and detect the community to use"""
        self.host = host
        self.port = port
        self.target = (self.host, self.port)
        self.alive = False
        if not authorizations:
            self._try_auths(self.DEFAULT_AUTHS)
        else:
            self._try_auths(authorizations)
            if not self.alive:
                last_try = authorizations.extend(self.DEFAULT_AUTHS)
                self._try_auths(set(last_try))

        if not self.alive:
            raise RuntimeError("No authentications succeeded!")

    def _try_auths(self, auths: list) -> None:
        noid = nodeid('SNMPv2-MIB::sysName.0')
        nodescr = nodeid('SNMPv2-MIB::sysDescr.0')
        for auth in auths:
            _auth = cmdgen.CommunityData(auth)
            (errorIndication, errorStatus, errorIndex, varBinds) = \
                cmdgen.CommandGenerator().getCmd(_auth,
                cmdgen.UdpTransportTarget(self.target), noid)
            if errorIndication or errorStatus:
                continue
            else:
                self.alive = True
                self.auth = _auth
                break

    @cached_property
    def name(self) -> str:
        return self.get('SNMPv2-MIB::sysName.0').prettyPrint()

    @cached_property
    def descr(self) -> str:
        return self.get('SNMPv2-MIB::sysDescr.0').prettyPrint()

    def parse_descr(self) -> None:
        sys = sysdescrparser(self.descr)
        self.vendor = sys.vendor
        self.model = sys.model
        self.os = sys.os
        self.version = sys.version

    def parse_sys(self):
        self.sys = SystemSNMP(self)
        # for item in SYS_MIBS:
        #     mib, prop = item
        #     sys_prop = f"{mib}::{prop}.0"
        #     attr = prop.lower()
        #     value = self.get(sys_prop).prettyPrint()
        #     if attr == 'sysuptime':
        #         secs = int(value)/100
        #         value = str(datetime.timedelta(seconds=secs))
        #     self.__setattr__(attr, value)

    def get(self, oid):
        """Get a specific node in the tree"""
        noid = nodeid(oid)
        (errorIndication, errorStatus, errorIndex, varBinds) = \
            cmdgen.CommandGenerator().getCmd(self.auth, cmdgen.UdpTransportTarget(self.target), noid)
        if errorIndication:
            raise RuntimeError("SNMPget of %s on %s failed" % (oid, self.host))
        return varBinds[0][1]

    def gettable(self, oid):
        """Get a complete subtable"""
        noid = nodeid(oid)
        (errorIndication, errorStatus, errorIndex, varBinds) = \
            cmdgen.CommandGenerator().nextCmd(self.auth, cmdgen.UdpTransportTarget(self.target), noid)
        if errorIndication:
            raise RuntimeError("SNMPget of %s on %s failed" % (oid, self.host))
        return [x[0] for x in varBinds]

    def matchtables(self, index, tables):
        """Match a list of tables using either a specific index table or the
           common tail of the OIDs in the tables"""
        oid_to_index = {}
        result = {}
        indexlen = 1
        if index:
            #  Use the index if available
            for oid, index in self.gettable(index):
                oid_to_index[oid[-indexlen:]] = index
                result[index] = []
        else:
            # Generate an index from the first table
            baselen = len(nodeid(tables[0]))
            for oid, value in self.gettable(tables[0]):
                indexlen = len(oid) - baselen
                oid_to_index[oid[-indexlen:]] = oid[-indexlen:]
                result[oid[-indexlen:]] = [value]
            tables = tables[1:]
        # Fetch the tables and match indices
        for table in tables:
            for oid, value in self.gettable(table):
                index = oid_to_index[oid[-indexlen:]]
                result[index].append(value)
        return result


class SystemSNMP:
    def __init__(self, snmp_client: SnmpClient):
        self.snmp = snmp_client
        self.mibs = SYS_MIBS
        for item in self.mibs:
            mib, prop = item
            sys_prop = f"{mib}::{prop}.0"
            value = self.snmp.get(sys_prop).prettyPrint()
            attr = prop.lstrip('sys').lower()
            if attr == 'uptime':
                secs = int(value)/100
                value = str(datetime.timedelta(seconds=secs))
            self.__setattr__(attr, value)
