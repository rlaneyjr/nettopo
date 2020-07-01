#!/usr/bin/env python

import csv
import sys
import getopt
import datetime
import os
import re
from timeit import default_timer as timer
from distutils.version import LooseVersion

import natlas

DEFAULT_OPT_DEPTH   = 100
DEFAULT_OPT_TITLE   = 'natlas Diagram'
DEFAULT_OPT_CONF    = './natlas.conf'

'''
diagram -r <root IP>
        -o <output file>
        [-d <max depth>]
        [-c <config file>]
        [-t <diagram title>]
        [-C <catalog file>]
'''


class natlas_mod:
    def __init__(self):
        self.filename     = ''
        self.name         = ''
        self.version      = ''
        self.author       = ''
        self.authoremail  = ''
        self.syntax       = None
        self.about        = None
        self.help         = None
        self.example      = None
        self.entryfunc    = None
        self.notimer      = 0
        self.require_api  = None
        self.preload_conf = 1
    def __str__(self):
        return ('<name="%s", version="%s", author="%s">' % (self.name, self.version, self.author))
    def __repr__(self):
        return self.__str__()

try:
    natlas_obj = natlas.natlas()
except Exception as e:
    print(e)
    exit()

def main(argv):
    modules = load_modules()
    mod = get_mod(modules, 'diagram')
    with open(argv) as afile:
        csv_reader = csv.reader(afile)
        for row in csv_reader:
            cmd = f"-r {row[0]} -C {row[1]}.csv -d 4 -t '{row[1]} - {row[0]}'"
            exec_mod(mod, cmd)
    return


def load_modules():
    sys.path.insert(0, './modules')
    ret = []
    for f in os.listdir('./modules'):
        if (f[-3:] == '.py'):
            mod = None
            try:
                mod = __import__(f[:-3], ['mod_load', 'mod_entry'])
            except Exception as e:
                print(e)
                continue
            if (hasattr(mod, 'mod_load') == 0):
                print('[ERROR] No mod_load() for %s' % f)
                continue
            m = natlas_mod()
            if (mod.mod_load(m) == 0):
                print('[ERROR] mod_load() returned an error for %s' % f)
                continue
            m.filename = f
            m.entryfunc = mod.mod_entry
            ret.append(m)
    return ret

def exec_mod(module, argv):
    start = timer()
    try:
        natlas_obj = natlas.natlas()
    except Exception as e:
        print('[ERROR] %s' % e)
        return 0
    if (module.preload_conf == 1):
        try:
            natlas_obj.config_load(DEFAULT_OPT_CONF)
        except Exception as e:
            print(e)
            return 0
    modret = module.entryfunc(natlas_obj, argv)
    if (modret == natlas.RETURN_SYNTAXERR):
        print('Invalid syntax for module.  See "syntax %s" for more info.' % module.name)
        return 0
    if (modret == natlas.RETURN_ERR):
        print('[ERROR] Error encountered in module.')
        return 0
    if (module.notimer == 0):
        s = timer() - start
        h=int(s/3600)
        m=int((s-(h*3600))/60)
        s=s-(int(s/3600)*3600)-(m*60)
        print('\nCompleted in %i:%i:%.2fs' % (h, m, s))
    return 1


def get_mod(modules, mod_name):
    for m in modules:
        if (m.name == mod_name):
            return m
    return None


def print_indented(str, wrap=1):
    lines = str.lstrip().splitlines()
    for line in lines:
        line = line.lstrip()
        if (line == ''):
            print()
            continue
        if (wrap == 1):
            wlines = [line[i:i+70] for i in range(0, len(line), 70)]
            for wline in wlines:
                print('    ', wline)
        else:
            print('    ', line)


if __name__ == "__main__":
    main(sys.argv[1])

