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
from pathlib import Path
from glob import glob as wildcard

import DotManager.defaults as defaults

userName: str = defaults.userName
""" The user's name, duh. """

xdgConfDir: Path = defaults.xdgConfDir
""" User's config home, usually `~/.config`. """

confDir: Path = defaults.confDir
""" DotManager cofig home, default: `~/.config/DotManager`. """

saveDir: Path = defaults.saveDir
""" Location where saved configs are stored. """

useLinks: bool = defaults.useLinks
""" Whether to use hard copies or symlinks when loading.

    Symlinks are recommended, as they will allow editing the config
    without having to save it again.
    """

index: Path = confDir.joinpath("index.json")
""" Location of the index. """

# Create missing directories
if not xdgConfDir.exists():
    xdgConfDir.mkdir()
if not confDir.exists():
    confDir.mkdir()
if not saveDir.exists():
    saveDir.mkdir()
