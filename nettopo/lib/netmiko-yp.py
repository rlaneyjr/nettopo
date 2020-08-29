#!/usr/bin/env python

from netmiko import ConnectHandler
from datetime import datetime
import re
import getpass
import socket

# Find mac add and mask uplink (use STP Root port or manual read in)
def find_stp_root(net_connect):
	stp_root_ports = []
	stproot = net_connect.send_command("sh span root | exc VLAN0001")
	stplines = re.split('\n',stproot)
	for stpline in stplines:
		stproot_port = re.search(r"Po\d{1,3}",stpline)
		if (stproot_port):
			stp_root_ports.append(stproot_port.group(0))
			#print stproot_port.group(0)
	print "STP ROOT PORT(S): "  
	for i in list(set(stp_root_ports)):
		print i

# lookup mac addresses excluding STP Root and Interfaces
def mac_dump(net_connect):
	mac_if = {}
	mac_count = 0
	mac_list = net_connect.send_command("sh mac add dynamic | exc Po1")
	mac_list = re.split('\n',mac_list)
	for line in mac_list:
		mac = re.search(r"([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})",line)
		intf = re.search(r"Gi\d/\d/\d{1,2}|Po\d{1,3}",line)
		if (mac) and (intf):
			mac_if[mac.group(0)] = intf.group(0)
			mac_count += 1
	print "Total Dynamic MAC Address Count: " 
	print len(set(mac_if))
	return mac_if

# find upstream gateway with arp information
def arp_dump(net_connect):
	mac_ip = {}
	arp_count = 0
	arp_list = net_connect.send_command("show ip arp")
	arp_list = re.split('\n',arp_list)
	for line in arp_list:
		ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",line)
		mac = re.search(r"([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})",line)
		if (ip) and (mac):
			#print ip.group(0) + "->" + mac.group(0)
			mac_ip[mac.group(0)] = ip.group(0) 
			arp_count += 1
	print "Total ARP Entries: " 
	print arp_count
	return mac_ip

def dns_lookup(arp_match):
	for key,value in arp_match.iteritems():
		ip = value[0]
		try:
			dns = socket.gethostbyaddr(ip)
			dns = dns[0]
			arp_match.setdefault(key,[]).append(dns)  # append DNS record to dictionary
		except socket.herror, err:
			arp_match.setdefault(key,[]).append("no rev dns")
	return arp_match

def main():
	username = raw_input("Username: ")
	password = getpass.getpass()
	arp_match = {}

	switch = {
    'device_type': 'cisco_ios',
    'ip': '10.45.4.60',
    'username': username,
    'password': password,
	}

	router = {
    'device_type': 'cisco_ios',
    'ip': '10.45.4.1',
    'username': username,
    'password': password,
	}

	start_time = datetime.now()
	net_connect = ConnectHandler(**switch)
	net_connect.find_prompt()

	find_stp_root(net_connect)
	mac_if = mac_dump(net_connect)
	
	net_connect = ConnectHandler(**router)
	net_connect.find_prompt()
	
	mac_ip = arp_dump(net_connect)

	mac_ifSet = set(mac_if)
	mac_ipSet = set(mac_ip)
	i = 0
	for mac in mac_ifSet.intersection(mac_ipSet):
	#	print mac, mac_ip[mac], mac_if[mac]	
		arp_match[mac] = [ mac_ip[mac], mac_if[mac] ]
		i += 1

	full_match = dns_lookup(arp_match)
	for key,value in full_match.iteritems():
		print key, value

	print "Matched Entries"
	print i
	end_time = datetime.now()
	total_time = end_time - start_time
	print total_time


if __name__ == "__main__":
	main()

# example 'show ip arp' output
# Protocol  Address          Age (min)  Hardware Addr   Type   Interface
# Internet  10.220.88.1            60   0062.ec29.70fe  ARPA   FastEthernet4
