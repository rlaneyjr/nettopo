#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    async_runner.py
'''

import asyncio
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
from threading import Thread
from typing import Union



class AsyncRunner():
    def __init__(self, ip: str, username: str, password: str,
                 device_type: str='autodetect') -> None:
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

    def run_async_func(self, func, args=None):
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=self.run_loop, args=(self.loop,))
        thread.start()
        if args:
            asyncio.run_coroutine_threadsafe(func(args), self.loop)
        else:
            asyncio.run_coroutine_threadsafe(func(), self.loop)

    def detect(self):
        self.run_async_func(self.async_detect)

    async def async_detect(self):
        ssh_detect = SSHDetect(**self.context)
        new_device_type = ssh_detect.autodetect()
        if new_device_type:
            self.context['device_type'] = new_device_type
        else:
            print(f"Unable to determine device type for {self.ip}")
            self.context['device_type'] = 'cisco_ios'
        self.loop.call_soon_threadsafe(self.loop.stop)

    def login(self):
        self.run_async_func(self.async_login)

    async def async_login(self):
        try:
            self.con = ConnectHandler(**self.context)
            self.session = True
        except:
            self.session = False
            self.error = 'Login Error'
        self.loop.call_soon_threadsafe(self.loop.stop)

    def check_session(self):
        if self.session:
            pass
        if self.error:
            raise Exception(f"{self.error}")
        raise Exception('No session found, login first!')

    def send_config(self, config):
        self.check_session()
        self.run_async_func(self.async_send_config, config)

    async def async_send_config(self, config):
        self.con.send_config_set(config)
        self.config_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def send_commands(self, commands):
        self.check_session()
        self.loop = asyncio.new_event_loop()
        thread = Thread(target=target_func, args=(self.loop,))
        thread.start()
        self.run_async_func(self.async_send_commands, commands)

    async def async_send_commands(self, commands):
        if isinstance(commands, list):
            for command in commands:
                self.exec_output.append(self.con.send_command(command))
        else:
            self.exec_output.append(self.con.send_command(commands))
        self.exec_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def close(self):
        if self.con:
            self.con.disconnect()
            self.session = False

