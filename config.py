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

xdgConfDir = defaults.xdgConfDir    # User's default config directory
confDir = defaults.confDir          # Directory where settings for dotmgr are stored
cacheDir = defaults.cacheDir        # A place to store conf copies before saving them

# Create missing directories
if not os.path.exists(xdgConfDir):
    os.mkdir(xdgConfDir)
if not os.path.exists(confDir):
    os.mkdir(confDir)
if not os.path.exists(cacheDir):
    os.mkdir(cacheDir)
