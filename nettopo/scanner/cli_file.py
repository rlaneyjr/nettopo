#!/usr/bin/env python

from netmiko.utilities import load_devices
import csv

dfile = '.netmiko.yml'

def main(dfile):
    devs = load_devices(dfile)
    with open('cli_devices.csv', 'w+') as cfile:
        for k,v in devs.items():
            if isinstance(v, dict):
                row = f"{k},,,,{v['ip']},ssh,22,yes,bonitz,{v['device_type']},\n"
                cfile.write(row)


if __name__ == '__main__':
    main(dfile)
