#!/bin/bash

PRTGHOST=$1
PRTGPORT=$2
PRTGPROTO=$3
PRTGUSER=$4
PRTGHASH=$5
NSIP=$6
SNMPUSER=$7
SNMPPASS=$8
TEMPLATEID=$9

BASEURL="${PRTGPROTO}://${PRTGHOST}:${PRTGPORT}/api/table.xml?username=${PRTGUSER}&passhash=${PRTGHASH}"

# Check if device exists
curl -s "${BASEURL}&content=devices&columns=objid,device,host&output=csvtable&filter_host=${NSIP}" | grep ${NSIP} > /dev/null 2>&1
if [ $? -ne 0 ]; then
	echo "ERROR: device ${NSIP} does not exist"
	exit 1
fi

# Get NS ID from PRTG
NSID=$(curl -s "${BASEURL}&content=devices&columns=objid&output=csvtable&filter_host=${NSIP}" | tail -n1 | sed 's/^"\([0-9]*\)".*$/\1/g')

# Get all configured services from NS
SVRS=$(snmpwalk -On -mALL -v3 -l authNoPriv -a SHA -A ${SNMPPASS} -u  ${SNMPUSER} ${NSIP} .1.3.6.1.4.1.5951.4.1.3.1.1.1 | sed 's/^.1.3.6.1.4.1.5951.4.1.3.1.1.1//g' | sed 's/^\([0-9.]*\) = STRING: "\([^"]*\)"$/\2,\1/g' | egrep -v "^IN[A-Za-z0-9]{29}|^TEMPLATE")

for SVR in ${SVRS}; do
	SVRNAME=$(echo ${SVR} | cut -d',' -f1)
	SVROID=$(echo ${SVR} | cut -d',' -f2)

	# Check if sensor exists
	curl -s "${BASEURL}&content=sensor&columns=sensor&output=csvtable&id=${NSID}&filter_name=${SVRNAME}" | grep ${SVRNAME} > /dev/null 2>&1
	if [ $? -eq 0 ]; then
		# Sensor is alredy configured
		continue
	fi

	echo -n "Adding ${SVRNAME} to device ID ${NSID}... "

	# Duplicate the template sensor
	SRVID=$(curl -s -I "${PRTGPROTO}://${PRTGHOST}:${PRTGPORT}/api/duplicateobject.htm?username=${PRTGUSER}&passhash=${PRTGHASH}&id=${TEMPLATEID}&name=${SVRNAME}&targetid=${NSID}" | grep Location | sed 's/[^0-9]//g')
	echo ${SRVID} | egrep "^[0-9]+$" > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "ERROR: cannot duplicate sensor ID ${TEMPLATEID} into device ${NSID}"
		exit 1
	fi

	# Change the OID
	curl -s "${PRTGPROTO}://${PRTGHOST}:${PRTGPORT}/api/setobjectproperty.htm?username=${PRTGUSER}&passhash=${PRTGHASH}&id=${SRVID}&name=oid&value=.1.3.6.1.4.1.5951.4.1.3.1.1.45${SVROID}" > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "ERROR: cannot set OID .1.3.6.1.4.1.5951.4.1.3.1.1.45${SVROID} for  sensor ID ${SRVID}"
		exit 1
	fi

	curl -s "${PRTGPROTO}://${PRTGHOST}:${PRTGPORT}/api/pause.htm?username=${PRTGUSER}&passhash=${PRTGHASH}&id=${SRVID}&action=1" > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo "ERROR: cannot start monitoring for sensor OID ${SVROID}"
		exit 1
	fi

	echo "done"
done
