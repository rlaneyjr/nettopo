# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
constants.py
'''
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
import os


NETTOPO_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
NETTOPO_ICON_DIR = os.path.join(NETTOPO_ROOT_DIR, 'icons', 'cisco')

NOTHING = (None, '0.0.0.0', 'UNKNOWN', '')
VALID_VERSIONS = ('2', '2c', '3')
VALID_V3_LEVELS = ('authNoPriv', 'authPriv')
VALID_INTEGRITY_ALGO = ('md5', 'sha')
VALID_PRIVACY_ALGO = ('des', '3des', 'aes', 'aes192', 'aes256')
RESERVED_VLANS = [1002, 1003, 1004, 1005]

SNMP_TYPES = {
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


class RETCODE:
    # return codes
    OK: int = 1
    ERR: int = 2
    SYNTAXERR: int = 3

class NODE:
    KNOWN: int = 1
    NEW: int = 2
    NEWIP: int = 3

class DCODE:
    ROOT: int = 0x01
    ERR_SNMP: int = 0x02
    DISCOVERED: int = 0x04
    STEP_INTO: int = 0x08
    CDP: int = 0x10
    LLDP: int = 0x20
    INCLUDE: int = 0x40
    LEAF: int = 0x80
    ROOT_STR: str = '[root]'
    ERR_SNMP_STR: str = '!'
    DISCOVERED_STR: str = '+'
    STEP_INTO_STR: str = '>'
    CDP_STR: str = '[cdp]'
    LLDP_STR: str = '[lldp]'
    INCLUDE_STR: str = 'i'
    LEAF_STR: str = 'L'


port_conversion_map = {
    'TenGigabitEthernet': 'Te',
    'GigabitEthernet': 'Gi',
    'FastEthernet': 'Fa',
    'Port-channel': 'Po',
    'Loopback': 'Lo',
    'Vlan': 'Vl',
}

# return codes
retcode_type_map = {
    1: 'ok',
    2: 'error',
    3: 'syntaxerror',
}

node_type_map = {
    1: 'known',
    2: 'new',
    3: 'newip',
}

arp_type_map = {
    0: 'unknown',
    1: 'other',
    2: 'invalid',
    3: 'dynamic',
    4: 'static',
}

# '1.3.6.1.2.1.17.4.3.1.3'
bridge_status_map = {
    1: 'other',
    2: 'invalid',
    3: 'learned',
    4: 'self',
    5: 'mgmt'
}

stp_state_map = {
    1: 'disabled',
    2: 'blocking',
    3: 'listening',
    4: 'learning',
    5: 'forwarding',
    6: 'broken'
}

entphyclass_type_map = {
    1: 'other',
    2: 'unknown',
    3: 'chassis',
    4: 'backplane',
    5: 'container',
    6: 'powersupply',
    7: 'fan',
    8: 'sensor',
    9: 'module',
    10: 'port',
    11: 'stack',
    12: 'pdu',
}

# http://www.net-snmp.org/docs/mibs/interfaces.html#PhysAddress
int_admin_status_map = {
    1: 'up',
    2: 'down',
    3: 'testing',
}

int_type_map = {
    1: 'other',
    2: 'regular1822',
    3: 'hdh1822',
    4: 'ddnX25',
    5: 'rfc877x25',
    6: 'ethernetCsmacd',
    7: 'iso88023Csmacd',
    8: 'iso88024TokenBus',
    9: 'iso88025TokenRing',
    10: 'iso88026Man',
    11: 'starLan',
    12: 'proteon10Mbit',
    13: 'proteon80Mbit',
    14: 'hyperchannel',
    15: 'fddi',
    16: 'lapb',
    17: 'sdlc',
    18: 'ds1',
    19: 'e1',
    20: 'basicISDN',
    21: 'primaryISDN',
    22: 'propPointToPointSerial',
    23: 'ppp',
    24: 'softwareLoopback',
    25: 'eon',
    26: 'ethernet3Mbit',
    27: 'nsip',
    28: 'slip',
    29: 'ultra',
    30: 'ds3',
    31: 'sip',
    32: 'frameRelay',
    33: 'rs232',
    34: 'para',
    35: 'arcnet',
    36: 'arcnetPlus',
    37: 'atm',
    38: 'miox25',
    39: 'sonet',
    40: 'x25ple',
    41: 'iso88022llc',
    42: 'localTalk',
    43: 'smdsDxi',
    44: 'frameRelayService',
    45: 'v35',
    46: 'hssi',
    47: 'hippi',
    48: 'modem',
    49: 'aal5',
    50: 'sonetPath',
    51: 'sonetVT',
    52: 'smdsIcip',
    53: 'propVirtual',
    54: 'propMultiplexor',
    55: 'ieee80212',
    56: 'fibreChannel',
    57: 'hippiInterface',
    58: 'frameRelayInterconnect',
    59: 'aflane8023',
    60: 'aflane8025',
    61: 'cctEmul',
    62: 'fastEther',
    63: 'isdn',
    64: 'v11',
    65: 'v36',
    66: 'g703at64k',
    67: 'g703at2mb',
    68: 'qllc',
    69: 'fastEtherFX',
    70: 'channel',
    71: 'ieee80211',
    72: 'ibm370parChan',
    73: 'escon',
    74: 'dlsw',
    75: 'isdns',
    76: 'isdnu',
    77: 'lapd',
    78: 'ipSwitch',
    79: 'rsrb',
    80: 'atmLogical',
    81: 'ds0',
    82: 'ds0Bundle',
    83: 'bsc',
    84: 'async',
    85: 'cnr',
    86: 'iso88025Dtr',
    87: 'eplrs',
    88: 'arap',
    89: 'propCnls',
    90: 'hostPad',
    91: 'termPad',
    92: 'frameRelayMPI',
    93: 'x213',
    94: 'adsl',
    95: 'radsl',
    96: 'sdsl',
    97: 'vdsl',
    98: 'iso88025CRFPInt',
    99: 'myrinet',
    100: 'voiceEM',
    101: 'voiceFXO',
    102: 'voiceFXS',
    103: 'voiceEncap',
    104: 'voiceOverIp',
    105: 'atmDxi',
    106: 'atmFuni',
    107: 'atmIma',
    108: 'pppMultilinkBundle',
    109: 'ipOverCdlc',
    110: 'ipOverClaw',
    111: 'stackToStack',
    112: 'virtualIpAddress',
    113: 'mpc',
    114: 'ipOverAtm',
    115: 'iso88025Fiber',
    116: 'tdlc',
    117: 'gigabitEthernet',
    118: 'hdlc',
    119: 'lapf',
    120: 'v37',
    121: 'x25mlp',
    122: 'x25huntGroup',
    123: 'transpHdlc',
    124: 'interleave',
    125: 'fast',
    126: 'ip',
    127: 'docsCableMaclayer',
    128: 'docsCableDownstream',
    129: 'docsCableUpstream',
    130: 'a12MppSwitch',
    131: 'tunnel',
    132: 'coffee',
    133: 'ces',
    134: 'atmSubInterface',
    135: 'l2vlan',
    136: 'l3ipvlan',
    137: 'l3ipxvlan',
    138: 'digitalPowerline',
    139: 'mediaMailOverIp',
    140: 'dtm',
    141: 'dcn',
    142: 'ipForward',
    143: 'msdsl',
    144: 'ieee1394',
    145: 'if-gsn',
    146: 'dvbRccMacLayer',
    147: 'dvbRccDownstream',
    148: 'dvbRccUpstream',
    149: 'atmVirtual',
    150: 'mplsTunnel',
    151: 'srp',
    152: 'voiceOverAtm',
    153: 'voiceOverFrameRelay',
    154: 'idsl',
    155: 'compositeLink',
    156: 'ss7SigLink',
    157: 'propWirelessP2P',
    158: 'frForward',
    159: 'rfc1483',
    160: 'usb',
    161: 'ieee8023adLag',
    162: 'bgppolicyaccounting',
    163: 'frf16MfrBundle',
    164: 'h323Gatekeeper',
    165: 'h323Proxy',
    166: 'mpls',
    167: 'mfSigLink',
    168: 'hdsl2',
    169: 'shdsl',
    170: 'ds1FDL',
    171: 'pos',
    172: 'dvbAsiIn',
    173: 'dvbAsiOut',
    174: 'plc',
    175: 'nfas',
    176: 'tr008',
    177: 'gr303RDT',
    178: 'gr303IDT',
    179: 'isup',
    180: 'propDocsWirelessMaclayer',
    181: 'propDocsWirelessDownstream',
    182: 'propDocsWirelessUpstream',
    183: 'hiperlan2',
    184: 'propBWAp2Mp',
    185: 'sonetOverheadChannel',
    186: 'digitalWrapperOverheadChannel',
    187: 'aal2',
    188: 'radioMAC',
    189: 'atmRadio',
    190: 'imt',
    191: 'mvl',
    192: 'reachDSL',
    193: 'frDlciEndPt',
    194: 'atmVciEndPt',
    195: 'opticalChannel',
    196: 'opticalTransport',
    197: 'propAtm',
    198: 'voiceOverCable',
    199: 'infiniband',
    200: 'teLink',
    201: 'q2931',
    202: 'virtualTg',
    203: 'sipTg',
    204: 'sipSig',
    205: 'docsCableUpstreamChannel',
    206: 'econet',
    207: 'pon155',
    208: 'pon622',
    209: 'bridge',
    210: 'linegroup',
    211: 'voiceEMFGD',
    212: 'voiceFGDEANA',
    213: 'voiceDID',
    214: 'mpegTransport',
    215: 'sixToFour',
    216: 'gtp',
    217: 'pdnEtherLoop1',
    218: 'pdnEtherLoop2',
    219: 'opticalChannelGroup',
    220: 'homepna',
    221: 'gfp',
    222: 'ciscoISLvlan',
    223: 'actelisMetaLOOP',
    224: 'fcipLink',
    225: 'rpr',
    226: 'qam',
    227: 'lmp',
    228: 'cblVectaStar',
    229: 'docsCableMCmtsDownstream',
    230: 'adsl2',
    231: 'macSecControlledIF',
    232: 'macSecUncontrolledIF',
    233: 'aviciOpticalEther',
    234: 'atmbond',
    235: 'voiceFGDOS',
    236: 'mocaVersion1',
    237: 'ieee80216WMAN',
    238: 'adsl2plus',
    239: 'dvbRcsMacLayer',
    240: 'dvbTdm',
    241: 'dvbRcsTdma',
    242: 'x86Laps',
    243: 'wwanPP',
    244: 'wwanPP2',
    245: 'voiceEBS',
    246: 'ifPwType',
    247: 'ilan',
    248: 'pip',
    249: 'aluELP',
    250: 'gpon',
    251: 'vdsl2',
    252: 'capwapDot11Profile',
    253: 'capwapDot11Bss',
    254: 'capwapWtpVirtualRadio',
    255: 'bits',
    256: 'docsCableUpstreamRfPort',
    257: 'cableDownstreamRfPort',
    258: 'vmwareVirtualNic',
    259: 'ieee802154',
    260: 'otnOdu',
    261: 'otnOtu',
    262: 'ifVfiType',
    263: 'g9981',
    264: 'g9982',
    265: 'g9983',
    266: 'aluEpon',
    267: 'aluEponOnu',
    268: 'aluEponPhysicalUni',
    269: 'aluEponLogicalLink',
    270: 'aluGponOnu',
    271: 'aluGponPhysicalUni',
    272: 'vmwareNicTeam',
}

int_oper_status_map = {
    1: 'up',
    2: 'down',
    3: 'testing',
    4: 'unknown',
    5: 'dormant',
    6: 'notPresent',
    7: 'lowerLayerDown',
}

cisco_icon_colors = [
    'aqua',
    'blue',
    'brown',
    'cyan',
    'green',
    'grey',
    'orange1',
    'orange2',
    'red',
    'yellow',
]


cisco_icon_mapper = {
    'cloud': 'generic-cloud',
    'host': 'generic-host',
    'printer': 'generic-printer',
    'router': 'router',
    'firewall': 'security-firewall',
    'switch': 'switch',
    'layer3': 'switch-layer3',
    'multilayer': 'switch-multilayer',
    'n1k': 'switch-nexus1000',
    'n2k': 'switch-nexus2000',
    'n5k': 'switch-nexus5000',
    'n7k': 'switch-nexus7000',
    'stack': 'switch-stack',
    'virtual': 'switch-virtuallayer',
    'vss': 'switch-VSS',
}

cisco_icon_list = [
    'generic-CA',
    'generic-cablemodem',
    'generic-cloud',
    'generic-database',
    'generic-directoryserver',
    'generic-dslam',
    'generic-fileserver',
    'generic-handheld',
    'generic-host',
    'generic-key',
    'generic-keys',
    'generic-laptop-mm',
    'generic-laptop',
    'generic-lock',
    'generic-mac-woman',
    'generic-macintosh',
    'generic-mainframe',
    'generic-man-running',
    'generic-man-woman',
    'generic-modem',
    'generic-oa',
    'generic-page',
    'generic-pc-man',
    'generic-pc',
    'generic-person',
    'generic-printer',
    'generic-radio-tower',
    'generic-server-mini',
    'generic-setopbox',
    'generic-settopbox2',
    'generic-stp',
    'generic-supercomputer',
    'generic-terminal',
    'generic-tv',
    'generic-video-camera',
    'generic-woman',
    'generic-workstation',
    'generic-workstation2',
    'hub-fast',
    'hub-small',
    'router-7513',
    'router-ASR1000',
    'router-ASR9000',
    'router-AXP',
    'router-broadband',
    'router-CME',
    'router-content',
    'router-CRS',
    'router-firewall',
    'router-itp',
    'router-mpls-p',
    'router-mpls-pe',
    'router-mpls',
    'router-netflow',
    'router-opticall',
    'router-services',
    'router-voice',
    'router-wavelength',
    'router-wireless',
    'router',
    'security-asa5500',
    'security-firewall-pix',
    'security-firewall',
    'security-fwsm',
    'security-nac-appliance',
    'switch-atm-fast',
    'switch-atm-tsr',
    'switch-atm',
    'switch-content-module',
    'switch-content',
    'switch-layer3',
    'switch-multifabric',
    'switch-multilayer',
    'switch-nexus1000',
    'switch-nexus2000',
    'switch-nexus5000',
    'switch-nexus7000',
    'switch-pccard',
    'switch-remote-multilayer',
    'switch-remote',
    'switch-server',
    'switch-service-control',
    'switch-slb',
    'switch-sm',
    'switch-stack',
    'switch-virtuallayer',
    'switch-voice',
    'switch-VSS',
    'switch',
    'voice-accessserver',
    'voice-ata',
    'voice-bts10200',
    'voice-callmanager',
    'voice-CUBE',
    'voice-fax',
    'voice-gateway',
    'voice-ipphone',
    'voice-mcu',
    'voice-octel',
    'voice-pbx',
    'voice-pgw2200',
    'voice-phone',
    'voice-phone_fax',
    'voice-server-moh',
    'voice-server-sip',
    'voice-softswitch',
    'voice-switch-atm',
    'voice-switch',
    'voice-tp500',
    'voice-tp1000',
    'voice-tp3000',
    'voice-tp3200',
    'voice-universalgateway',
    'wireless-ap-dualmode',
    'wireless-ap-lw',
    'wireless-ap-mesh',
    'wireless-ap',
    'wireless-bridge',
    'wireless-controller',
    'wireless-wism',
]
