#!/usr/bin/env python3


import getopt, sys
import re
from pysnmp.entity.rfc3413.oneliner import cmdgen

verbose = False
SNMP_VERSION = 2
SNMP_COMMUNITY = 0
SNMP_HOST = 0
skip=0
return_code=0


def usage(exit_code):
    print("Gathers LLDP SNMP data from Switch")
    print(f"{sys.argv[0]} -C <community> -H <hostname>")
    print("Options")
    print("-C or --community= SNMP Community")
    print("-H or --host=      Host")
    print("-h or --help       Show Help")
    sys.exit(exit_code)

def prep_mibs():
    dataPoints = {
            'ifDescr':         {'mib': '1.3.6.1.2.1.2.2.1.2',      'key': 10, 'port' : {} },
            'ifAlias':         {'mib': '1.3.6.1.2.1.31.1.1.1.18',  'key': 11, 'port' : {} },
            'ifOperStatus':    {'mib': '1.3.6.1.2.1.2.2.1.8',      'key': 10, 'port' : {} }, #TBD write unknown to ports that should be up but aren't
            'ifAdminStatus':   {'mib': '1.3.6.1.2.1.2.2.1.7',      'key': 10, 'port' : {} },
            'lldpRemSysName':  {'mib': '1.0.8802.1.1.2.1.4.1.1.9', 'key': 12, 'port' : {} },
            'lldpRemPortId':   {'mib': '1.0.8802.1.1.2.1.4.1.1.7', 'key': 12, 'port' : {} },
            'lldpRemPortDesc': {'mib': '1.0.8802.1.1.2.1.4.1.1.8', 'key': 12, 'port' : {} },
            }
    mibs=[]
    for item in dataPoints:
        mibs.append(dataPoints[item]['mib'])
    return mibs

def send_query(host, community, mibs):
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.bulkCmd(
        cmdgen.CommunityData(community),
        cmdgen.UdpTransportTarget((host, 161), timeout=2,retries=3),
        0, 32,
        *mibs)
    if errorIndication:
        print(errorIndication)
        exit(1)
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'}")
        exit(2)
    else:
        return varBindTable

def print_vbt(varBindTable):
    for varBindTableRow in varBindTable:
       for name, val in varBindTableRow:
           print(f"{name.prettyPrint()} = {val.prettyPrint()}")

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:],"C:H:h",["community=","host","help",])
    except getopt.GetoptError:
        usage(2)
    for opt, arg in opts:
        if opt in ("-h",   "--help"):
            usage(0)
        elif opt in ("-C", "--community"):
            community = arg
        elif opt in ("-H", "--host"):
            host = arg
    #require parameters
    if not SNMP_COMMUNITY or not SNMP_HOST:
        usage(2)
    else:
        mibs = prep_mibs()
        vbt = send_query(host, community, mibs)
        print_vbt(vbt)


"""
for port in xrange(len(varBindTable)):
    for item in dataPoints:
        #LLDP Table Index has key 12
        portNumber=int(str( varBindTable[ port ][ dataPoints.keys().index(item) ][ 0 ] ).split('.')[ dataPoints[item]['key'] ])
        #print ('portNumber:%s, item:%s, mib:%s, value:%s' % ( portNumber, item, varBindTable[ port ][ dataPoints.keys().index(item) ][ 0 ], varBindTable[port][dataPoints.keys().index(item)][1]))
        #Fix Bug on SNMP returning too much data
        if dataPoints[item]['mib'] in str(varBindTable[ port ][ dataPoints.keys().index(item) ][ 0 ]):
            dataPoints[item]['port'][portNumber]= varBindTable[port][dataPoints.keys().index(item)][1]

#Header
#print('switch,port<=connects-to=>portId,portDesc,device')

for port in dataPoints['lldpRemSysName']['port']:
    #replace hex to mac address string
    if not str(dataPoints['lldpRemPortId']['port'][port]).isalnum():
        dataPoints['lldpRemPortId']['port'][port]=str(dataPoints['lldpRemPortId']['port'][port]).encode('hex')
    #change interface name 'Interface   4 as eth0' to eth0'
    if re.search('^Interface\ +[0-9]+ as [a-z0-9]+',str(dataPoints['lldpRemPortDesc']['port'][port])):
        dataPoints['lldpRemPortDesc']['port'][port]=re.sub('^Interface\ +[0-9]+ as ','',str(dataPoints['lldpRemPortDesc']['port'][port]))

    #Ignore Port Channels and Vlans
    #if re.search('^(Port-Channel|Vlan)[0-9]+$',str(dataPoints['ifDescr']['port'][port])):
        #continue

    #NO LLDP Data Nothing to show
    if dataPoints['ifDescr']['port'][port] == 6:
        continue

    print(f"""
# {SNMP_HOST},
# {dataPoints['ifDescr']['port'][port]}
# <=connects-to=>
# {dataPoints['lldpRemPortId']['port'][port]},
# {dataPoints['lldpRemPortDesc']['port'][port]},
# {dataPoints['lldpRemSysName']['port'][port]}
""")

exit(return_code)

vars = netsnmp.VarList(netsnmp.Varbind('IF-MIB::ifDescr'),
                       netsnmp.Varbind('IF-MIB::ifAlias'),
                       netsnmp.Varbind('IF-MIB::ifAdminStatus'),
                       netsnmp.Varbind('LLDP-MIB::lldpRemSysName'),
                       netsnmp.Varbind('LLDP-MIB::lldpRemPortId'),
                       netsnmp.Varbind('LLDP-MIB::lldpRemPortDesc'))

vals = session.getbulk(0, 16, vars)
print "v2 session.getbulk result: ", vals, "\n"

for var in vars:
 print var.tag, var.iid, "=", var.val, '(',var.type,')'

print "\n"
"""
