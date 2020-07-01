#!/usr/bin/env python

from netmiko import ConnectHandler
import csv


def get_net_devices(csv_file):
    devices = []
    with open(csv_file) as dev_file:
        csv_reader = csv.reader(dev_file)
        for row in csv_reader:
            device = { 'host': row[1],
                       'ip': row[0],
                       'device_type': row[2],
                       'model': row[3],
                       'version': row[4] }
            devices.append(device)
    return devices


def get_nox_devices(csv_file):
    devices = []
    with open(csv_file) as dev_file:
        csv_reader = csv.reader(dev_file)
        for row in csv_reader:
            device = { 'host': row[0],
                       'ip': row[1],
                       'device_type': row[6],
                       'group': row[5],
                       'model': row[7],
                       'version': row[8] }
            devices.append(device)
    return devices


def build_netmiko_yml(devices):
    with open('.netmiko.yml', 'w+') as nm_file:
        nm_file.write('---\n\n')
        for dev in devices:
            nm_file.write(f"{dev['host']}:\n")
            nm_file.write(f"  device_type: {dev['device_type']}\n")
            nm_file.write(f"  ip: {dev['ip']}\n")
            nm_file.write(f"  username: admin\n")
            nm_file.write(f"  password: N@!litD0wn\n")
            nm_file.write('\n')
        nm_file.write('\n')
        nm_file.write('##### Groups #####\n')
        os_list = list(set(dev['device_type'] for dev in devices))
        #os_list = [os.replace('_', '-') for os in devices]
        #print(os_list)
        for os in os_list:
            nm_file.write(f"{os.replace('_', '-')}:\n")
            for dev in devices:
                if dev['device_type'] == os:
                    nm_file.write(f"  - {dev['host']}\n")
            nm_file.write('\n')


if __name__ == "__main__":
    #net_devices = get_net_devices('net_devices.csv')
    #nox_devices = get_nox_devices('nox_devices.csv')
    #all_devices = net_devices.extend(nox_devices)
    all_devices = get_net_devices('net_devices.csv') + get_nox_devices('nox_devices.csv')
    build_netmiko_yml(all_devices)

