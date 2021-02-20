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

from ast import Dict, List
from pathlib import Path
from json import load as deserialize
from json import JSONDecodeError

from DotManager.config import index as indexPath

# TODO: Check out atExit, write the index when program closes.
#       This will reduce I/O overhead when saving/deleting
#       Multiple configurations.

class Index:
    """ Class provided to ease insertion and lookup in the index."""

    def __init__(self):
        with open(indexPath, 'rt') as jsonIndex:
            self._dict = dict(deserialize(jsonIndex))
        self._apps = set()
        self._confs = set()
        self._users = {key for key in self._dict}
        for user in self._users:
            for app in self._dict[user]:
                self._apps.add(app)
        for user in self._users:
            for app in self._apps:
                try:
                    for conf in self._dict[user][app]:
                        self._confs.add(conf)
                except KeyError:
                    continue

    @property
    def __dict__(self) -> set: return self._dict.copy()
    """ Get a copy on the deserialized JSON index. """

    @property
    def apps(self) -> set: return self._apps.copy()
    """ Get a set of all the apps registered in the index. """

    @property
    def confs(self) -> set: return self._confs.copy()
    """ Get a set of all the configurations names saved in the index. """

    @property
    def users(self) -> set: return self._users.copy()
    """ Get a set of all the users registered in the index. """

    def has(self, element: str):
        """ Check if element is in the index.
            Doesn't differentiante users from confs or apps.
            """
        return (element in self._apps or element in self._confs or element in self._users)

    def insert(self, user, app, conf):
        pass
