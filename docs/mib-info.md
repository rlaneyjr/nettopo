## Is there an SNMP MIB to show Address Resolution Protocol (ARP) table information? I need both the IP and MAC addresses in the same table.

### Yes, ipNetToMediaPhysAddress = .1.3.6.1.2.1.4.22.1.2 from the MIB RFC1213-MIB.my.

```
ipNetToMediaPhysAddress OBJECT-TYPE

       -- FROM RFC1213-MIB, IP-MIB
       -- TEXTUAL CONVENTION PhysAddress

    SYNTAX          OCTET STRING
    MAX-ACCESS      read-write
    STATUS          Mandatory
    DESCRIPTION     "The media-dependent `physical' address."
 
::= { iso(1) org(3) dod(6) internet(1) mgmt(2) mib-2(1) ip(4)
      ipNetToMediaTable(22) ipNetToMediaEntry(1) 2 }

