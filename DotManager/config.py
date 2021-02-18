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

from glob import glob as wildcard

import defaults

userName = defaults.userName

xdgConfDir = defaults.xdgConfDir
confDir = defaults.confDir
saveDir = defaults.saveDir

useLinks = defaults.useLinks

# Create missing directories
if not os.path.exists(xdgConfDir):
    os.mkdir(xdgConfDir)
if not os.path.exists(confDir):
    os.mkdir(confDir)
if not os.path.exists(saveDir):
    os.mkdir(saveDir)
