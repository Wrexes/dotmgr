#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os

# Set the base directory for config files
if "XDG_USER_CONFIG_DIR" in os.environ:
    xdgConfDir = os.path.expandvars('$XDG_USER_CONFIG_DIR')
else:
    xdgConfDir = os.path.expanduser('~/.config')

# Set the default configuration directory
confDir = os.path.join(xdgConfDir, 'dotmgr')
