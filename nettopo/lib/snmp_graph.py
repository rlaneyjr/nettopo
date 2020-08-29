#!/usr/bin/env python

from snmp_helper import snmp_get_oid,snmp_extract
import time
import pygal

COMMUNITY_STRING = 'galileo'
SNMP_PORT = 161
IP = '184.105.247.70'
OID = '1.3.6.1.2.1.1.5.0'
a_device = (IP, COMMUNITY_STRING, SNMP_PORT)

snmp_data = snmp_get_oid(a_device, oid=OID)
output = snmp_extract(snmp_data)
print output

snmp_oids = (
    ('sysName', '1.3.6.1.2.1.1.5.0', None),
    ('sysUptime', '1.3.6.1.2.1.1.3.0', None),
    ('ifDescr_fa4', '1.3.6.1.2.1.2.2.1.2.5', None),
    ('ifInOctets_fa4','1.3.6.1.2.1.2.2.1.10.5', True),
    ('ifInUcastPkts_fa4','1.3.6.1.2.1.2.2.1.11.5', True),
    ('ifOutOctets_fa4','1.3.6.1.2.1.2.2.1.16.5', True),
    ('ifOutUcastPkts_fa4','1.3.6.1.2.1.2.2.1.17.5', True),
)

logfile = open('snmp_data.log','w')
i = 0
for i in range(0, 5):
    for desc,an_oid,is_count in snmp_oids:
        snmp_data = snmp_get_oid(a_device, oid=an_oid)
        output = snmp_extract(snmp_data)
        print "%s %s" % (desc,output)
        logfile.write(desc + output + "\n")
    i += 1
    time.sleep(5)


fa4_in_octets = [ 3,4,5,2]
fa4_out_octets = [ 4,5,2,2]
fa4_in_packets = [ 4,2,4,5]
fa4_out_packets = [4,2,5,4]

line_chart = pygal.Line()

line_chart.title = 'Input/Output Packets and Bytes'
line_chart.x_labels = ['5','10','15','20']
line_chart.add('InPackets',fa4_in_packets)
line_chart.add('OutPackets',fa4_out_packets)
line_chart.add('InBytes',fa4_out_octets)
line_chart.add('OutBytes',fa4_in_octets)

line_chart.render_to_file('test.svg')
