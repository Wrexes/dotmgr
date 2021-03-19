#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

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

from pathlib import Path
import shutil
from typing import Union

from DotManager.commands.save import SaveInfo
from DotManager.index import index
import DotManager.config as config

# XXX: Make this more interactive, maybe ?


def rm(app: str,
       name: str,
       user: str = config.userName,
       saveDir: Union[Path, str] = config.saveDir,
       force: bool = False):
    """ Remove a config from the index and from `config.saveDir` """
    if not index.query(app, name, user):
        return
    path: Path = SaveInfo(app, name, user, saveDir).location
    prompt = f"Are you sure you want to remove " +\
             f"{user}'s config " +\
             f"{name} for " +\
             f"{app} ? (N/y) "
    while not force:
        answer = 'x' + str(input(prompt)).lower()
        if answer == 'xy':
            index.remove(app, name, user)
            if path.exists():
                shutil.rmtree(path)
            break
        elif answer in ['x', 'xn']:
            break
        else:
            continue
