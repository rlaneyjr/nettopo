from nelsnmp.errors import ArgumentError, SnmpError
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
from pyasn1.type.univ import ObjectIdentifier
from datetime import timedelta

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


def is_ipv4_address(value):
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
            raise ValueError("'{}' is not one of the supported types: {}".format(
                value_type,
                ", ".join(TYPES.keys())
            ))

        data = TYPES[value_type](value)
    return data


class SnmpHandler(object):

    def __init__(self, **kwargs):

        self.port = 161
        self.timeout = 1
        self.retries = 5
        self.version = False
        self.community = False
        self.host = False
        self.username = False
        self.level = False
        self.integrity = False
        self.privacy = False
        self.authkey = False
        self.privkey = False

        self._parse_args(**kwargs)

    def _parse_args(self, **kwargs):
        for key in kwargs:
            if key == 'version':
                self.version = kwargs[key]
            if key == 'community':
                self.community = kwargs[key]
            if key == 'host':
                self.host = kwargs[key]
            if key == 'port':
                try:
                    port = int(kwargs[key])
                except:
                    self._raise_error(ArgumentError,
                                      'Port must be an integer between 1 and 65535')

                if 1 <= port <= 65535:
                    self.port = port
                else:
                    self._raise_error(ArgumentError,
                                      'Port must be between 1 and 65535')
            if key == 'timeout':
                self.timeout = kwargs[key]
            if key == 'retries':
                self.retries = kwargs[key]
            if key == 'username':
                self.username = kwargs[key]
            if key == 'level':
                if kwargs[key] in VALID_V3_LEVELS:
                    self.level = kwargs[key]
                else:
                    self._raise_error(ArgumentError, 'Security level invalid')
            if key == 'integrity':
                if kwargs[key] in VALID_INTEGRITY_ALGO:
                    self.integrity = kwargs[key]
                else:
                    self._raise_error(ArgumentError,
                                      'Integrity algorithm not valid')
            if key == 'privacy':
                if kwargs[key] in VALID_PRIVACY_ALGO:
                    self.privacy = kwargs[key]
                else:
                    self._raise_error(ArgumentError,
                                      'Privacy algorithm not valid')
            if key == 'authkey':
                self.authkey = kwargs[key]
            if key == 'privkey':
                self.privkey = kwargs[key]

        if self.host is False:
            self._raise_error(ArgumentError, 'Host not defined')

        if self.version not in VALID_VERSIONS:
            self._raise_error(ArgumentError, 'No valid SNMP version defined')

        if self.version == "2c":
            self.snmp_auth = cmdgen.CommunityData(self.community)

        if self.version == "3":
            if self.username is False:
                self._raise_error(ArgumentError, 'No username specified')
            if self.level is False:
                self._raise_error(ArgumentError, 'No security level specified')
            if self.integrity is False:
                self._raise_error(ArgumentError,
                                  'No integrity protocol specified')
            if self.authkey is False:
                self._raise_error(ArgumentError, 'No authkey specified')

            if self.level == 'authNoPriv':
                self.snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity])
            elif self.level == 'authPriv':
                if self.privacy is False:
                    self._raise_error(ArgumentError,
                                      'No privacy protocol specified')
                if self.privkey is False:
                    self._raise_error(ArgumentError,
                                      'No privacy key specified')
                self.snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authkey,
                    authProtocol=INTEGRITY_ALGO[self.integrity],
                    privKey=self.privkey,
                    privProtocol=PRIVACY_ALGO[self.privacy])

    def _raise_error(self, ErrorType, error_data):
        raise ErrorType(error_data)

    def get(self, *oidlist):

        snmp_query = []
        for oid in oidlist:
            snmp_query.append(oid,)

        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port),
                                      timeout=self.timeout,
                                      retries=self.retries),
            *snmp_query,
            lookupMib=False
        )

        if errorIndication or errorStatus:
            current_error = errorIndication._ErrorIndication__descr
            self._raise_error(SnmpError, current_error)

        pretty_varbinds = []
        for oid, value in varBinds:
            pretty_varbinds.append([oid.prettyPrint(),
                                   return_pretty_val(value)])

        return pretty_varbinds

    def get_value(self, *oidlist):

        snmp_query = []
        for oid in oidlist:
            snmp_query.append(oid,)

        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *snmp_query,
            lookupMib=False
        )

        if errorIndication or errorStatus:
            current_error = errorIndication._ErrorIndication__descr
            self._raise_error(SnmpError, current_error)

        values = []
        for oid, value in varBinds:
            values.append(return_pretty_val(value))

        if len(values) == 1:
            values = values[0]

        return values

    def getnext(self, *oidlist):

        snmp_query = []
        for oid in oidlist:
            snmp_query.append(oid,)

        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *snmp_query,
            lookupMib=False
        )

        if errorIndication or errorStatus:
            current_error = errorIndication._ErrorIndication__descr
            self._raise_error(SnmpError, current_error)

        pretty_vartable = []

        for varbinds in varTable:
            pretty_varbinds = []
            for oid, value in varbinds:
                pretty_varbinds.append([oid.prettyPrint(),
                                       return_pretty_val(value)])
            pretty_vartable.append(pretty_varbinds)

        return pretty_vartable

    def set(self, oid=None, value=None, value_type=None, multi=None):

        if multi is None:
            data = return_snmp_data(value, value_type)
            snmp_sets = (oid, data),
        else:
            snmp_sets = []
            for snmp_set in multi:
                if len(snmp_set) == 2:
                    oid = snmp_set[0]
                    value = snmp_set[1]
                    value_type = None
                    data = return_snmp_data(value, value_type)
                elif len(snmp_set) == 3:
                    oid = snmp_set[0]
                    value = snmp_set[1]
                    value_type = snmp_set[2]
                    data = return_snmp_data(value, value_type)
                snmp_sets.append((oid, data),)

        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varTable = cmdGen.setCmd(
            self.snmp_auth,
            cmdgen.UdpTransportTarget((self.host, self.port)),
            *snmp_sets,
            lookupMib=False
        )

        if errorIndication or errorStatus:
            current_error = errorIndication._ErrorIndication__descr
            self._raise_error(SnmpError, current_error)
