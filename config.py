#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os
import getpass

from glob import glob as wildcard

import defaults

userName = defaults.userName

xdgConfDir = defaults.xdgConfDir
confDir = defaults.confDir
saveDir = defaults.saveDir
savePath = defaults.savePath

useLinks = defaults.useLinks

# Create missing directories
if not os.path.exists(xdgConfDir):
    os.mkdir(xdgConfDir)
if not os.path.exists(confDir):
    os.mkdir(confDir)
if not os.path.exists(savePath):
    os.mkdir(savePath)
