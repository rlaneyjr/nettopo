import sys
from collections import defaultdict
from pysnmp.entity.rfc3413.oneliner import cmdgen


class PortStatusError(Exception):
    pass


class PortStatus:
    def __init__(self, ip, community):
        self.ip = ip
        self.community = community
        self.mibs = [('1.3.6.1.2.1.2.2.1.8', 'ifOperStatus'),
                     ('1.3.6.1.2.1.2.2.1.3', 'ifType'),
                     ('1.3.6.1.2.1.2.2.1.5', 'ifSpeed'),
                     ('1.3.6.1.2.1.31.1.1.1.1', 'ifName'),
                     ('1.3.6.1.2.1.31.1.1.1.18', 'ifAlias')]
        self.ports = defaultdict(dict)


    def datafrommib(self, mib):
        value = tuple([int(i) for i in mib.split('.')])
        generator = cmdgen.CommandGenerator()
        comm_data = cmdgen.CommunityData('server', self.community, 1)
        transport = cmdgen.UdpTransportTarget((self.ip, 161))
        real_fun = getattr(generator, 'nextCmd')
        errorIndication, errorStatus, errorIndex, varBindTable = \
            real_fun(comm_data, transport, value)
        if errorIndication or errorStatus is True:
            raise PortStatusError(f"{errorIndication}, {errorStatus}, {errorIndex}\n \
                                    {varBindTable}")
        else:
            for varBindTableRow in varBindTable:
                data = varBindTableRow[0]
                port = data[0]._value[len(value):]
                octets = data[1]
                yield {'port': port[0], 'octets': octets}


    def get_status(self):
        for mib in self.mibs:
            for row in self.datafrommib(mib[0]):
                if row:
                    self.ports[row['port']][mib[1]] = row['octets']
        return self.ports
