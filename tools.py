#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

# from __future__ import print_function
import sys
import os

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def realpath(path: str) -> str:
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    return path
