#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    async_runner.py
'''

import asyncio
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
from tabulate import tabulate
from threading import Thread
from typing import Union

try:
    from genie.conf.base import Device
    from genie.libs.parser.utils import get_parser
    from pyats.datastructures import AttrDict
    HAS_GENIE = True
except ImportError:
    HAS_GENIE = False

try:
    from ntc_templates.parse import parse_output
    HAS_NTC_TEMPLATES = True
except ImportError:
    HAS_NTC_TEMPLATES = False


class AsyncRunner():
    def __init__(self, ip: str, username: str, password: str,
                 device_type: str='autodetect', use_genie: bool=HAS_GENIE,
                 use_textfsm: bool=HAS_NTC_TEMPLATES) -> None:
        self.ip = ip
        self.username = username
        self.password = password
        self.device_type = device_type
        self.session = False
        self.con = None
        self.loop = None
        self.error = False
        self.config_done = False
        self.exec_done = False
        self.exec_output = []
        self.context = {
            'device_type': self.device_type,
            'host': self.ip,
            'username': self.username,
            'password': self.password
        }

    @staticmethod
    def run_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def detect(self):
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=self.run_loop, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_detect(), self.loop)

    async def async_detect(self):
        ssh_detect = SSHDetect(**self.context)
        new_device_type = ssh_detect.autodetect()
        if new_device_type:
            self.device_type = new_device_type
            self.context['device_type'] = new_device_type
        else:
            print(f"Unable to determine device type for {self.ip}")
            self.device_type = 'unknown'
            self.context['device_type'] = 'cisco_ios'
        self.loop.call_soon_threadsafe(self.loop.stop)

    def login(self):
        if self.device_type == 'autodetect':
            self.detect()
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=self.run_loop, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_login(), self.loop)

    async def async_login(self):
        try:
            self.con = ConnectHandler(**self.context)
            self.session = True
        except:
            self.session = False
            self.error = 'Login Error'
        else:
            if not self.con.check_enable_mode():
                self.con.enable()
        self.loop.call_soon_threadsafe(self.loop.stop)

    def check_session(self):
        if not self.session:
            if self.error:
                raise Exception(f"{self.error}")
            raise Exception('No session found, login first!')

    def get_parser(self, parser: str): -> Union[dict, None]:
        if any(['text', 'fsm', 'ntc', 'template']) in parser and
                                                HAS_NTC_TEMPLATES:
            return {'use_textfsm': True}
        if 'genie' in parser and HAS_GENIE:
            return {'use_genie': True}
        return None

    def send_config(self, config):
        self.check_session()
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=self.run_loop, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_send_config(config),
                                                            self.loop)

    async def async_send_config(self, config):
        self.con.send_config_set(config)
        self.config_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def send_commands(self, commands: Union[str, List[str]],
                        use_parser: Union[str, None]=None):
        if use_parser:
            parser = self.get_parser(use_parser)
        self.check_session()
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=self.run_loop, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(
            self.async_send_commands(commands, parser),
            self.loop
        )

    async def async_send_commands(self, commands: Union[str, List[str]],
                                  parser: Union[dict, None]):
        if isinstance(commands, list):
            self.command_list = commands
            for command in commands:
                self.exec_output.append(
                    self.con.send_command(command, **parser)
                )
        else:
            self.command = commands
            self.exec_output.append(
                self.con.send_command(commands, **parser)
            )
        self.exec_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def close(self):
        if self.session:
            self.con.disconnect()
            self.session = False
        del self

    def print_table(self):
        table_dict = {}
        if not self.exec_output:
            if not self.exec_done:
                pout = f"Last command finished: {self.exec_done}"
            pout = f"No output from last command: {self.exec_output}"
        if len(self.exec_output) == 1 and hasattr(self, 'command'):
            table = [line.split() for line in \
                                self.exec_output[0].splitlines()]
            table_dict.update({str(self.command): table})
        if len(self.exec_output) > 1 and hasattr(self, 'command_list'):
            counter = 0
            for item in self.exec_output:
                table = [line.split() for line in item.splitlines()]
                table_dict.update({str(self.command_list[counter]), table})
                counter += 1
        self.table_out = table_dict
        for cmd, tbl in self.table_out.items():
            print(f"Command: {cmd}")
            print(tabulate(tbl, headers='firstrow'))
