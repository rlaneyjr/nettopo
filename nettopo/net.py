# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              net.py
Description:        Network Utilities
Author:             Ricky Laney
'''
from netaddr import IPAddress, IPNetwork


class NtIPAddress(IPAddress):
    ''' Represents a ip we will discover
    '''
    pass


class NtNetwork(IPNetwork):
    ''' Represents a network we will discover
    '''
    pass

