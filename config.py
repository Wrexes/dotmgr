#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os

from glob import glob as wildcard

import defaults

xdgConfDir = defaults.xdgConfDir    # User config dir
confDir = defaults.confDir          # dotmgr config dir

# Create missing directories
if not os.path.exists(xdgConfDir):
    os.mkdir(xdgConfDir)
if not os.path.exists(confDir):
    os.mkdir(confDir)
