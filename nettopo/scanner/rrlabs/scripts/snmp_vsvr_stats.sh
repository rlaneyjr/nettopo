#!/bin/bash

NSIP=$1
SNMPUSER=$2
SNMPPASS=$3

echo "Name,Address,Port,Type,State,Request Rate,RX Bytes Rate,TX Bytes Rate"
SVRS=$(snmpwalk -mALL -v3 -l authNoPriv -a SHA -A ${SNMPPASS} -u ${SNMPUSER} ${NSIP} -On .1.3.6.1.4.1.5951.4.1.3.1.1.1 | sed 's/^.1.3.6.1.4.1.5951.4.1.3.1.1.1//g' | cut -d' ' -f1)
for SVR in ${SVRS}; do
	snmpgetnext -mALL -v3 -l authNoPriv -a SHA -A ${SNMPPASS} -u ${SNMPUSER} ${NSIP} -Ov NS-ROOT-MIB::vsvrName${SVR} NS-ROOT-MIB::vsvrIpAddress${SVR} NS-ROOT-MIB::vsvrPort${SVR} NS-ROOT-MIB::vsvrType${SVR} NS-ROOT-MIB::vsvrState${SVR} NS-ROOT-MIB::vsvrRequestRate${SVR} NS-ROOT-MIB::vsvrRxBytesRate${SVR} NS-ROOT-MIB::vsvrTxBytesRate${SVR} | sed -e 's/^[^"]*"\([^"]*\)"$/\1/g' -e 's/^[^:]*: \([^()]*\).*$/\1/g' | sed ':a;N;$!ba;s/\n/,/g'
done
