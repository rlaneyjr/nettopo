#!/usr/bin/env python
import re

blah = "Internet  10.220.88.1             7   0062.ec29.70fe  ARPA   FastEthernet4"

output = re.split('\s+', blah)

print blah
print output[1] + "->" + output[3]

blah = "* 4      0000.0c9f.f3e2    dynamic   1800       F    F  Po301"
blah2 = "* 994      e00e.da71.1450    dynamic   20         F    F  Eth103/1/43"

vlan = re.search(r"\d{1,4}", blah)
mac = re.search(r"([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})",blah)
intf = re.search(r"Po\d{1,4}|Eth\d{1,4}/\d/\d{1,2}",blah2)

print blah
print vlan.group(0)
print mac.group(0)
print intf.group(0)
