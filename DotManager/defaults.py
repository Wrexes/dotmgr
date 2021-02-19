#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# MIT License

# Copyright (c) 2020 Ludovic Fernandez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import getpass
import tempfile
from pathlib import Path

# DotManager version
version = '0.3.0'

# Set the base directory for config files
if "XDG_CONFIG_HOME" in os.environ:
    xdgConfDir = Path(os.environ.get("XDG_CONFIG_HOME"))
elif "XDG_USER_CONFIG_DIR" in os.environ:
    xdgConfDir = Path(os.environ.get("XDG_USER_CONFIG_DIR"))
else:
    xdgConfDir = Path(os.path.expanduser('~/.config'))

# What is the user's name ?
userName = str(getpass.getuser())

# dotmgr configuration directory
confDirName = Path('DotManager')

# DotManager config dir path
confDir = Path(xdgConfDir, confDirName)

# Default save directory name
saveDirName = Path("saved")

# Default path to store saved configs
saveDir = Path(confDir, saveDirName)

# Wheter to use symlinks or copies
useLinks = True
