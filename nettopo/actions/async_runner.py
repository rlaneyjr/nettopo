#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
    async_runner.py
'''

import asyncio

from netmiko import ConnectHandler
from threading import Thread


class NetworkDevice():
    def __init__(self, ip, username, password, device_type='cisco_ios'):
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

    def login(self):
        self.loop = asyncio.new_event_loop()
        def f(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        thread = Thread(target=f, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_login(), self.loop)

    async def async_login(self):
        try:
            self.con = ConnectHandler(**{
                'device_type': self.device_type,
                'ip': self.ip,
                'username': self.username,
                'password': self.password
            })
            self.session = True
        except:
            self.session = False
            self.error = 'Login Error'
        self.loop.call_soon_threadsafe(self.loop.stop)

    def send_config(self, config):
        if not self.session:
            raise Exception('No session found, login first!')
        self.loop = asyncio.new_event_loop()
        def f(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        thread = Thread(target=f, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_send_config(config),
                                         self.loop)

    async def async_send_config(self, config):
        self.con.send_config_set(config)
        self.config_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def send_commands(self, commands):
        if not self.session:
            raise Exception('No session found, login first!')
        self.loop = asyncio.new_event_loop()
        def f(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        thread = Thread(target=f, args=(self.loop,))
        thread.start()
        asyncio.run_coroutine_threadsafe(self.async_send_commands(commands),
                                         self.loop)

    async def async_send_commands(self, commands):
        if isinstance(commands, list):
            for command in commands:
                self.exec_output.append(self.con.send_command(command))
        else:
            self.exec_output.append(self.con.send_command(commands))
        self.exec_done = True
        self.loop.call_soon_threadsafe(self.loop.stop)

    def close(self):
        del self

