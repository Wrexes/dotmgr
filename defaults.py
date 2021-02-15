#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os
import getpass
import tempfile

# Set the base directory for config files
if "XDG_USER_CONFIG_DIR" in os.environ:
    xdgConfDir = os.path.expandvars('$XDG_USER_CONFIG_DIR')
else:
    xdgConfDir = os.path.expanduser('~/.config')

# What is the user's name ?
userName = getpass.getuser()

# Default configuration directory
confDir = os.path.join(xdgConfDir, 'dotmgr')

# Default cache directory
cacheDir = tempfile.gettempdir()

# Default archive name
tarName = "my_dotfiles.tar.gz"

# Default archive path
tarPath = os.path.join(cacheDir, tarName)
