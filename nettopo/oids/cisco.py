# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              cisco.py
Description:        Cisco OIDs
Author:             Ricky Laney
Version:            0.1.1

How To Get Dynamic CAM Entries (CAM Table) for Catalyst Switches Using SNMP
From https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/13492-cam-snmp.html
1. Retrieve the VLANs. Use snmpwalk on the vtpVlanState object (.1.3.6.1.4.1.9.9.46.1.3.1.1.2 )
2. For each VLAN, get the MAC address table (using community string indexing) dot1dTpFdbAddress (.1.3.6.1.2.1.17.4.3.1.1)
3. For each VLAN, get the bridge port number, dot1dTpFdbPort (.1.3.6.1.2.1.17.4.3.1.2)
4. Get the bridge port to ifIndex (1.3.6.1.2.1.2.2.1.1) mapping, dot1dBasePortIfIndex (.1.3.6.1.2.1.17.1.4.1.2)
5. Walk the ifName (.1.3.6.1.2.1.31.1.1.1.1) so that the ifIndex value obtained in step 4 can be correllated with a proper port name

Now the port information obtained can be used, for example:
    From Step 2 , there is a MAC address: .1.3.6.1.2.1.17.4.3.1.1.0.208.211.106.71.251 = Hex-STRING: 00 D0 D3 6A 47 FB
    From Step 3: .1.3.6.1.2.1.17.4.3.1.2.0.208.211.106.71.251 = INTEGER: 113
    This tells you that this MAC address (00 D0 D3 6A 47 FB) is from bridge port number 113.
    From Step 4, the bridge port number 113 has an ifIndex number 57 .1.3.6.1.2.1.17.1.4.1.2.113 = INTEGER: 57
    From Step 5, the ifIndex 57 corresponds to port 2/49 .1.3.6.1.2.1.31.1.1.1.1.57 = STRING: 2/49
Compare that with the output from the show cam dynamic command output for CatOS switches, or show mac command output for CatIOS switches. You see a match for 1 00-d0-d3-6a-47-fb 2/49 [ALL].

 Verify
This section provides information you can use to confirm your configuration is working properly.
1. Telnet to your switch.
2. From the command line, issue the appropriate command:
    CatOS devices: show cam dynamic
    CatIOS devices: show mac
3. Compare the output with the results obtained by the procedure specified here.
    nms-2948g> (enable) show cam dynamic
'''
from nettopo.oids.general import GeneralOids


class CiscoOids(GeneralOids):
    """ Statically define Cisco OIDs and inherit general oids
    """
    # From CISCO-ENVMON-MIB
    ciscoEnvMonMIB = '1.3.6.1.4.1.9.9.13'
    ciscoEnvMonObjects = '1.3.6.1.4.1.9.9.13.1'
    ciscoEnvMonPresent = '1.3.6.1.4.1.9.9.13.1.1'
    ciscoEnvMonVoltageStatusTable = '1.3.6.1.4.1.9.9.13.1.2'
    ciscoEnvMonVoltageStatusEntry = '1.3.6.1.4.1.9.9.13.1.2.1'
    ciscoEnvMonVoltageStatusIndex = '1.3.6.1.4.1.9.9.13.1.2.1.1'
    ciscoEnvMonVoltageStatusDescr = '1.3.6.1.4.1.9.9.13.1.2.1.2'
    ciscoEnvMonVoltageStatusValue = '1.3.6.1.4.1.9.9.13.1.2.1.3'
    ciscoEnvMonVoltageThresholdLow = '1.3.6.1.4.1.9.9.13.1.2.1.4'
    ciscoEnvMonVoltageThresholdHigh = '1.3.6.1.4.1.9.9.13.1.2.1.5'
    ciscoEnvMonVoltageLastShutdown = '1.3.6.1.4.1.9.9.13.1.2.1.6'
    ciscoEnvMonVoltageState = '1.3.6.1.4.1.9.9.13.1.2.1.7'
    ciscoEnvMonTemperatureStatusTable = '1.3.6.1.4.1.9.9.13.1.3'
    ciscoEnvMonTemperatureStatusEntry = '1.3.6.1.4.1.9.9.13.1.3.1'
    ciscoEnvMonTemperatureStatusIndex = '1.3.6.1.4.1.9.9.13.1.3.1.1'
    ciscoEnvMonTemperatureStatusDescr = '1.3.6.1.4.1.9.9.13.1.3.1.2'
    ciscoEnvMonTemperatureStatusValue = '1.3.6.1.4.1.9.9.13.1.3.1.3'
    ciscoEnvMonTemperatureThreshold = '1.3.6.1.4.1.9.9.13.1.3.1.4'
    ciscoEnvMonTemperatureLastShutdown = '1.3.6.1.4.1.9.9.13.1.3.1.5'
    ciscoEnvMonTemperatureState = '1.3.6.1.4.1.9.9.13.1.3.1.6'
    ciscoEnvMonFanStatusTable = '1.3.6.1.4.1.9.9.13.1.4'
    ciscoEnvMonFanStatusEntry = '1.3.6.1.4.1.9.9.13.1.4.1'
    ciscoEnvMonFanStatusIndex = '1.3.6.1.4.1.9.9.13.1.4.1.1'
    ciscoEnvMonFanStatusDescr = '1.3.6.1.4.1.9.9.13.1.4.1.2'
    ciscoEnvMonFanState = '1.3.6.1.4.1.9.9.13.1.4.1.3'
    ciscoEnvMonSupplyStatusTable = '1.3.6.1.4.1.9.9.13.1.5'
    ciscoEnvMonSupplyStatusEntry = '1.3.6.1.4.1.9.9.13.1.5.1'
    ciscoEnvMonSupplyStatusIndex = '1.3.6.1.4.1.9.9.13.1.5.1.1'
    ciscoEnvMonSupplyStatusDescr = '1.3.6.1.4.1.9.9.13.1.5.1.2'
    ciscoEnvMonSupplyState = '1.3.6.1.4.1.9.9.13.1.5.1.3'
    ciscoEnvMonSupplySource = '1.3.6.1.4.1.9.9.13.1.5.1.4'
    ciscoEnvMonAlarmContacts = '1.3.6.1.4.1.9.9.13.1.6'
    # From CISCO-CDP-MIB
    cdpInterfaceEntry = '1.3.6.1.4.1.9.9.23.1.1.1.1'
    cdpInterfaceEnable = '1.3.6.1.4.1.9.9.23.1.1.1.1.2'
    cdpCacheEntry = '1.3.6.1.4.1.9.9.23.1.2.1.1'
    cdpCacheDeviceId = '1.3.6.1.4.1.9.9.23.1.2.1.1.6'
    cdpCacheDevicePort = '1.3.6.1.4.1.9.9.23.1.2.1.1.7'
    cdpCacheAddressType = '1.3.6.1.4.1.9.9.23.1.2.1.1.3'
    cdpCacheAddress = '1.3.6.1.4.1.9.9.23.1.2.1.1.4'
    cdpGlobalRun = '1.3.6.1.4.1.9.9.23.1.3.1'
    cdpGlobalMessageInterval = '1.3.6.1.4.1.9.9.23.1.3.2'
    cdpGlobalHoldTime = '1.3.6.1.4.1.9.9.23.1.3.3'
    # From CISCO-RTTMON-MIB
    ciscoRttMonMIB = '1.3.6.1.4.1.9.9.42'
    rttMonCtrlAdminEntry = '1.3.6.1.4.1.9.9.42.1.2.1.1'
    rttMonCtrlAdminIndex = '1.3.6.1.4.1.9.9.42.1.2.1.1.1'
    rttMonCtrlAdminOwner = '1.3.6.1.4.1.9.9.42.1.2.1.1.2'
    rttMonCtrlAdminTag = '1.3.6.1.4.1.9.9.42.1.2.1.1.3'
    rttMonCtrlAdminRttType = '1.3.6.1.4.1.9.9.42.1.2.1.1.4'
    rttMonCtrlAdminThreshold = '1.3.6.1.4.1.9.9.42.1.2.1.1.5'
    rttMonCtrlAdminFrequency = '1.3.6.1.4.1.9.9.42.1.2.1.1.6'
    rttMonCtrlAdminTimeout = '1.3.6.1.4.1.9.9.42.1.2.1.1.7'
    rttMonCtrlAdminVerifyData = '1.3.6.1.4.1.9.9.42.1.2.1.1.8'
    rttMonCtrlAdminStatus = '1.3.6.1.4.1.9.9.42.1.2.1.1.9'
    rttMonCtrlAdminNvgen = '1.3.6.1.4.1.9.9.42.1.2.1.1.10'
    rttMonCtrlAdminGroupName = '1.3.6.1.4.1.9.9.42.1.2.1.1.11'
    rttMonLatestRttOperEntry = '1.3.6.1.4.1.9.9.42.1.2.10.1'
    rttMonLatestRttOperCompletionTime = '1.3.6.1.4.1.9.9.42.1.2.10.1.1'
    rttMonLatestRttOperSense = '1.3.6.1.4.1.9.9.42.1.2.10.1.2'
    rttMonLatestRttOperApplSpecificSense = '1.3.6.1.4.1.9.9.42.1.2.10.1.3'
    rttMonLatestRttOperSenseDescription = '1.3.6.1.4.1.9.9.42.1.2.10.1.4'
    rttMonLatestRttOperTime = '1.3.6.1.4.1.9.9.42.1.2.10.1.5'
    rttMonLatestRttOperAddress = '1.3.6.1.4.1.9.9.42.1.2.10.1.6'
    # From CISCO-VTP-MIB
    vtpVlanIndex = '1.3.6.1.4.1.9.9.46.1.3.1.1.1'
    vtpVlanState = '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
    vtpVlanName = '1.3.6.1.4.1.9.9.46.1.3.1.1.4'
    vtpVlanEditOperation = '1.3.6.1.4.1.9.9.46.1.4.1.1.1'
    vtpVlanEditBufferOwner = '1.3.6.1.4.1.9.9.46.1.4.1.1.3'
    vtpVlanEditTable = '1.3.6.1.4.1.9.9.46.1.4.2'
    vtpVlanApplyStatus = '1.3.6.1.4.1.9.9.46.1.4.1.1.2'
    vtpVlanEditType = '1.3.6.1.4.1.9.9.46.1.4.2.1.3'
    vtpVlanEditName = '1.3.6.1.4.1.9.9.46.1.4.2.1.4'
    vtpVlanEditDot10Said = '1.3.6.1.4.1.9.9.46.1.4.2.1.6'
    vtpVlanEditRowStatus = '1.3.6.1.4.1.9.9.46.1.4.2.1.11'
    vlanTrunkPortEncapsulationType = '1.3.6.1.4.1.9.9.46.1.6.1.1.3'
    vlanTrunkPortVlansEnabled = '1.3.6.1.4.1.9.9.46.1.6.1.1.4'
    vlanTrunkPortNativeVlan = '1.3.6.1.4.1.9.9.46.1.6.1.1.5'
    vlanTrunkPortDynamicState = '1.3.6.1.4.1.9.9.46.1.6.1.1.13'
    vlanTrunkPortDynamicStatus = '1.3.6.1.4.1.9.9.46.1.6.1.1.14'
    vlanTrunkPortEncapsulationOperType = '1.3.6.1.4.1.9.9.46.1.6.1.1.16'
    vlanTrunkPortVlansEnabled2k = '1.3.6.1.4.1.9.9.46.1.6.1.1.17'
    vlanTrunkPortVlansEnabled3k = '1.3.6.1.4.1.9.9.46.1.6.1.1.18'
    vlanTrunkPortVlansEnabled4k = '1.3.6.1.4.1.9.9.46.1.6.1.1.19'
    vlanTrunkPortSetSerialNo = '1.3.6.1.4.1.9.9.46.1.6.2'
    # From CISCO-VLAN-MEMBERSHIP-MIB
    vmVlan = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'
    # From CISCO-STP-EXTENSIONS-MIB
    stpxSpanningTreeType = '1.3.6.1.4.1.9.9.82.1.6.1'
    # From CISCO-ENTITY-SENSOR-MIB
    entitySensorMIBObjects = '1.3.6.1.4.1.9.9.91.1'
    entSensorValues = '1.3.6.1.4.1.9.9.91.1.1'
    entSensorValueTable = '1.3.6.1.4.1.9.9.91.1.1.1'
    entSensorValueEntry = '1.3.6.1.4.1.9.9.91.1.1.1.1'
    entSensorType = '1.3.6.1.4.1.9.9.91.1.1.1.1.1'
    entSensorScale = '1.3.6.1.4.1.9.9.91.1.1.1.1.2'
    entSensorPrecision = '1.3.6.1.4.1.9.9.91.1.1.1.1.3'
    entSensorValue = '1.3.6.1.4.1.9.9.91.1.1.1.1.4'
    entSensorStatus = '1.3.6.1.4.1.9.9.91.1.1.1.1.5'
    entSensorValueTimeStamp = '1.3.6.1.4.1.9.9.91.1.1.1.1.6'
    entSensorValueUpdateRate = '1.3.6.1.4.1.9.9.91.1.1.1.1.7'
    entSensorMeasuredEntity = '1.3.6.1.4.1.9.9.91.1.1.1.1.8'
    # From CISCO-CONFIG-COPY-MIB
    ccCopyProtocol = '1.3.6.1.4.1.9.9.96.1.1.1.1.2'
    ccCopySourceFileType = '1.3.6.1.4.1.9.9.96.1.1.1.1.3'
    ccCopyDestFileType = '1.3.6.1.4.1.9.9.96.1.1.1.1.4'
    ccCopyServerAddress = '1.3.6.1.4.1.9.9.96.1.1.1.1.5'
    ccCopyFileName = '1.3.6.1.4.1.9.9.96.1.1.1.1.6'
    ccCopyUserName = '1.3.6.1.4.1.9.9.96.1.1.1.1.7'
    ccCopyUserPassword = '1.3.6.1.4.1.9.9.96.1.1.1.1.8'
    ccCopyNotificationOnCompletion = '1.3.6.1.4.1.9.9.96.1.1.1.1.9'
    ccCopyState = '1.3.6.1.4.1.9.9.96.1.1.1.1.10'
    ccCopyTimeStarted = '1.3.6.1.4.1.9.9.96.1.1.1.1.11'
    ccCopyTimeCompleted = '1.3.6.1.4.1.9.9.96.1.1.1.1.12'
    ccCopyFailCause = '1.3.6.1.4.1.9.9.96.1.1.1.1.13'
    ccCopyEntryRowStatus = '1.3.6.1.4.1.9.9.96.1.1.1.1.14'
    ccCopyServerAddressType = '1.3.6.1.4.1.9.9.96.1.1.1.1.15'
    ccCopyServerAddressRev1 = '1.3.6.1.4.1.9.9.96.1.1.1.1.16'
    # From CISCO-FIREWALL-MIB
    cfwConnectionStatValue = '1.3.6.1.4.1.9.9.147.1.2.2.2.1.5'
    # From CISCO-L2L3-INTERFACE-CONFIG-MIB
    cL2L3IfModeAdmin = '1.3.6.1.4.1.9.9.151.1.1.1.1.1'
    # From CISCO-PAE-MIB
    cpaePortMode = '1.3.6.1.4.1.9.9.220.1.1.1.2'
    cpaeGuestVlanNumber = '1.3.6.1.4.1.9.9.220.1.1.1.3'
    cpaeShutdownTimeoutEnabled = '1.3.6.1.4.1.9.9.220.1.1.1.5'
    cpaePortAuthFailVlan = '1.3.6.1.4.1.9.9.220.1.1.1.6'
    cpaePortOperVlan = '1.3.6.1.4.1.9.9.220.1.1.1.7'
    cpaePortOperVlanType = '1.3.6.1.4.1.9.9.220.1.1.1.8'
    cpaeAuthFailVlanMaxAttempts = '1.3.6.1.4.1.9.9.220.1.1.1.9'
    cpaePortCapabilitiesEnabled = '1.3.6.1.4.1.9.9.220.1.1.1.10'
    cpaeMacAuthBypassPortEnabled = '1.3.6.1.4.1.9.9.220.1.8.6.1.1'
    # From CISCO-LAG-MIB
    clagAggDistributionProtocol = '1.3.6.1.4.1.9.9.225.1.1.1'
    clagAggDistributionAddressMode = '1.3.6.1.4.1.9.9.225.1.1.2'
    # From CISCO-PORT-SECURITY-MIB
    cpsIfPortSecurityEnable = '1.3.6.1.4.1.9.9.315.1.2.1.1.1'
    cpsIfPortSecurityStatus = '1.3.6.1.4.1.9.9.315.1.2.1.1.2'
    cpsIfMaxSecureMacAddr = '1.3.6.1.4.1.9.9.315.1.2.1.1.3'
    cpsIfCurrentSecureMacAddrCount = '1.3.6.1.4.1.9.9.315.1.2.1.1.4'
    cpsIfSecureMacAddrAgingTime = '1.3.6.1.4.1.9.9.315.1.2.1.1.5'
    cpsIfSecureMacAddrAgingType = '1.3.6.1.4.1.9.9.315.1.2.1.1.6'
    cpsIfStaticMacAddrAgingEnable = '1.3.6.1.4.1.9.9.315.1.2.1.1.7'
    cpsIfViolationAction = '1.3.6.1.4.1.9.9.315.1.2.1.1.8'
    cpsIfViolationCount = '1.3.6.1.4.1.9.9.315.1.2.1.1.9'
    cpsIfSecureLastMacAddress = '1.3.6.1.4.1.9.9.315.1.2.1.1.10'
    cpsIfUnicastFloodingEnable = '1.3.6.1.4.1.9.9.315.1.2.1.1.12'
    cpsIfShutdownTimeout = '1.3.6.1.4.1.9.9.315.1.2.1.1.13'
    cpsIfClearSecureMacAddresses = '1.3.6.1.4.1.9.9.315.1.2.1.1.14'
    cpsIfStickyEnable = '1.3.6.1.4.1.9.9.315.1.2.1.1.15'
    cpsIfInvalidSrcRateLimitEnable = '1.3.6.1.4.1.9.9.315.1.2.1.1.16'
    cpsIfInvalidSrcRateLimitValue = '1.3.6.1.4.1.9.9.315.1.2.1.1.17'
    cpsIfSecureLastMacAddrVlanId = '1.3.6.1.4.1.9.9.315.1.2.1.1.18'
    # How To Get Dynamic CAM Entries
    how2_ifIndex = '1.3.6.1.2.1.2.2.1.1'
    how2_ifName = '1.3.6.1.2.1.31.1.1.1.1'
    how2_vtpVlanState = '1.3.6.1.4.1.9.9.46.1.3.1.1.2'
    how2_dot1dBasePortIfIndex = '1.3.6.1.2.1.17.1.4.1.2'
    how2_dot1dTpFdbTable = '1.3.6.1.2.1.17.4.3'
    how2_dot1dTpFdbAddress = '1.3.6.1.2.1.17.4.3.1.1'
    how2_dot1dTpFdbPort = '1.3.6.1.2.1.17.4.3.1.2'
    how2_dot1dTpFdbStatus = '1.3.6.1.2.1.17.4.3.1.3'

