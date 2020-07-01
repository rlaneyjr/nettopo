#!/bin/bash

VER="0.1"
URL="http://www.routereflector.com/tag/waas/"
SNMPGETNEXT="/usr/bin/snmpgetnext"

#Checking binaries
if [ ! -f "$SNMPGETNEXT" ]; then
    echo -ne "ERROR: Missing snmpgetnext binary.\n\n"
    exit 3
fi

#Help function
usage() {
    echo $OPTARG
    echo -ne "USAGE: $0 [OPTIONS]\n\n"
    echo -ne "  Version:  $VER\n"
    echo -ne "  Web:      $URL\n\n"
    echo -ne "OPTIONS:\n"
    echo -ne "  -v 1|2c     specifies SNMP version to use\n"
    echo -ne "  -C STRING   set the community string\n"
    echo -ne "  -w INTEGER  set warning (%) threshold on available connections\n"
    echo -ne "  -c INTEGER  set critical (%) threshold on available connections\n"
    exit 3
}

#Parsing Parameters
while getopts ":C:v:H:w:c:" OPT; do
    case "$OPT" in
        "H")
            HOST=$OPTARG
        ;;
        "C")
            COMMUNITY=$OPTARG
        ;;
        "v")
            VERSION=$OPTARG
            if [ "$VERSION" != "1" ] && [ "$VERSION" != "2c" ]; then
                echo -ne "ERROR: Only SNMP version 1 and 2c are supported, $VERSION is not.\n\n"
                usage
            fi
        ;;
        "w")
            WARNING_PERC=$OPTARG
            if [[ ! "$WARNING_PERC" =~ "^[-0-9]+$" ]]; then
                echo -ne "ERROR: -w $WARNING_PERC is not an integer.\n\n"
                usage
            fi
        ;;
        "c")
            CRITICAL_PERC=$OPTARG
            if [[ ! "$CRITICAL_PERC" =~ "^[-0-9]+$" ]]; then
                echo -ne "ERROR: -c $CRITICAL_PERC is not an integer.\n\n"
                usage
            fi
        ;;
        *)
            usage
        ;;
    esac
done

if [ -z "$COMMUNITY" ] || [ -z "$VERSION" ] || [ -z "$HOST" ] || [ -z "$WARNING_PERC" ] || [ -z "$CRITICAL_PERC" ]; then
    echo -ne "ERROR: missing required parameter.\n\n"
    usage
fi

#Alarm
cceAlarmCriticalCount=1.3.6.1.4.1.9.9.178.1.6.2.1
cceAlarmMajorCount=1.3.6.1.4.1.9.9.178.1.6.2.2
cceAlarmMinorCount=1.3.6.1.4.1.9.9.178.1.6.2.3

#Connections
cwoTfoStatsMaxActiveConn=1.3.6.1.4.1.9.9.762.1.2.1.3
cwoTfoStatsActiveOptConn=1.3.6.1.4.1.9.9.762.1.2.1.2
cwoTfoStatsActivePTConn=1.3.6.1.4.1.9.9.762.1.2.1.10

#Checking connections
OUTPUT=$($SNMPGETNEXT -m /dev/null -c $COMMUNITY -v $VERSION $HOST $cwoTfoStatsMaxActiveConn $cwoTfoStatsActiveOptConn $cwoTfoStatsActivePTConn)

MAX=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\1/')
OPT=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\2/')
PT=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\3/')

CURRENT_PERC=$(echo "100*($OPT)/$MAX" | bc)
WARNING=$(echo "$MAX*0.$WARNING_PERC" | bc)
CRITICAL=$(echo "$MAX*0.$CRITICAL_PERC" | bc)

if [ "$CURRENT_PERC" -ge "$CRITICAL_PERC" ]; then
    STATUS="CRITICAL"
    RC=2
elif [ "$CURRENT_PERC" -ge "$WARNING_PERC" ]; then
    STATUS="WARNING"
    RC=1
elif [ "$CURRENT_PERC" -ge 0 ]; then
    STATUS="OK"
    RC=0
else
    STATUS="UNKNOWN"
    RC=3
fi

#Checking alerts
OUTPUT=$($SNMPGETNEXT -m /dev/null -c $COMMUNITY -v $VERSION $HOST $cceAlarmCriticalCount $cceAlarmMajorCount $cceAlarmMinorCount)

MSG_CRITICAL=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\1/')
MSG_MAJOR=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\2/')
MSG_MINOR=$(echo $OUTPUT | sed 's/.*: \([0-9]*\) .*: \([0-9]*\) .*: \([0-9]*\)/\3/')

if [ "$MSG_CRITICAL" -gt 0 ] && [ "$RC" -le 3 ]; then
    STATUS="CRITICAL"
    RC=2
elif [ "$MSG_MAJOR" -gt 0 ] && [ "$RC" -le 2 ]; then
    STATUS="WARNING"
    RC=2
fi

# Nagios Required Output: varname=value;warn;crit;min;max
echo -n "$STATUS (Msg $MSG_CRITICAL/$MSG_MAJOR/$MSG_MINOR) - Connections $OPT/$MAX (PT=$PT) | conn=$OPT;$WARNING;$CRITICAL;0;$MAX"
exit $RC

