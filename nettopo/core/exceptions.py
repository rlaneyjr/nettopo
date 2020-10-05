# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              exceptions.py
Description:        Custom Exception Classes
Author:             Ricky Laney
Version:            0.1.1
'''

__all__ = [
    'NettopoError',
    'NettopoNodeError',
    'NettopoNetworkError',
    'NettopoDiagramError',
    'NettopoCatalogError',
    'NettopoCacheError',
    'NettopoSNMPError',
]


class NettopoError(Exception): pass
class NettopoNodeError(NettopoError): pass
class NettopoNetworkError(NettopoError): pass
class NettopoCatalogError(NettopoError): pass
class NettopoCacheError(NettopoError): pass
class NettopoConfigError(NettopoError): pass
class NettopoDiagramError(NettopoError): pass
class NettopoSNMPError(NettopoError): pass
