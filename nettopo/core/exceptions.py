# -*- coding: utf-8 -*-
# vim: noai:et:tw=80:ts=4:ss=4:sts=4:sw=4:ft=python

'''
Title:              exceptions.py
Description:        exceptions.py
Author:             Ricky Laney
Version:            0.1.1
'''

__all__ = [
    'NettopoError',
    'NettopoNodeError',
    'NettopoNetworkError',
    'NettopoDiagramError',
    'NettopoCatalogError',
    'NettopoSNMPError',
]


class NettopoError(Exception):
    pass


class NettopoNodeError(NettopoError):
    pass


class NettopoNetworkError(NettopoError):
    pass


class NettopoCatalogError(NettopoError):
    pass


class NettopoDiagramError(NettopoError):
    pass


class NettopoSNMPError(NettopoError):
    pass
