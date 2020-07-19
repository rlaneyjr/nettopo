import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen


class FDBError(Exception):
    pass


class FDB:
    def __init__(self, ip, community):
        self.mib = '1.3.6.1.2.1.17.7.1.2.2.1.2'
        self.ip = ip
        self.community = community

    def genFdb(self):
        value = tuple([int(i) for i in self.mib.split('.')])
        generator = cmdgen.CommandGenerator()
        comm_data = cmdgen.CommunityData('server', self.community, 1)
        transport = cmdgen.UdpTransportTarget((self.ip, 161))
        real_fun = getattr(generator, 'nextCmd')
        errorIndication, errorStatus, errorIndex, varBindTable = real_fun(comm_data,
                                                                          transport,
                                                                          value)
        if errorIndication or errorStatus is True:
            raise FDBError(f"{errorIndication}, {errorStatus}, {errorIndex}\n \
                             {varBindTable}")
        else:
            for varBindTableRow in varBindTable:
                data = varBindTableRow[0][0]._value[len(value):]
                vlan = data[0]
                #mac = '%s' % ':'.join([hex(int(i))[2:] for i in data[-6:]])
                mac = '%02x:%02x:%02x:%02x:%02x:%02x' % tuple(map(int, data[-6:]))
                port = varBindTableRow[0][1]
                yield {'vlan': vlan, 'mac': mac, 'port': port}
