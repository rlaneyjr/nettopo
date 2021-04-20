# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              exceptions.py
Description:        Custom Exception Classes
Author:             Ricky Laney
Version:            0.1.1
'''


class NettopoError(Exception): pass
class NettopoNodeError(NettopoError): pass
class NettopoNetworkError(NettopoError): pass
class NettopoACLDenied(NettopoError): pass
class NettopoCatalogError(NettopoError): pass
class NettopoCacheError(NettopoError): pass
class NettopoConfigError(NettopoError): pass
class NettopoDiagramError(NettopoError): pass
class NettopoSNMPError(NettopoError): pass
class NettopoSNMPTableError(NettopoError): pass
class NettopoSNMPValueError(NettopoError): pass
class NettopoTypeError(NettopoError): pass
