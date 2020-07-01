Nettopo will 'attempt' to discover your network topology by performing the following steps.

1. Find the 'management' network.  It is recommended to manually configure the management network to avoid the overhead involved with discovering the network.
  - If not defined, Nettopo will use the local machine's IP and attempt discovery of the default gateway.


Discovery
---------
> We have an IP we wish to 'Discover', now what?
1. Ping the IP to verify it is replying. (Sometimes ping is blocked)
2. Run nmap scan on IP for ports 22,23,161,162. If none are open, tag as host and move on.
3. See if we can login via SSH/Telnet. Add to list of avail discovery methods for device.
4. See if we can SNMP query device. Add to list of avail discovery methods for device.
5. Collect and store the following data using available discovery methods.
  - Device information (type, model, vendor, version, serial, inventory, hardware)
  - MAC, ARP, CAM, CEF, and route tables
  - CDP and LLDP neighbors with details
  - Interface information (status, description, type, members, vlans)
  - Local IPs and their respective interface (VLAN, eth, po)
6. Find the default route and label 'upstream'.
7. Find connected routes and label 'local'.
8. Find the all other network routes and label 'downstream'.
9. If default gateway is public IP and not in DMZ, label 'internet'.
10. If DG is private, then this is our network device and add to table for discovery.
11. 
