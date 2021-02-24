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

import atexit
from pathlib import Path
from json import dumps as to_string
from json import load as deserialize
from json import dump as serialize
from json import JSONDecodeError

from DotManager.tools import eprint
from DotManager.config import index as indexPath

# TODO: Check out atExit, write the index when program closes.
#       This will reduce I/O overhead when saving/deleting
#       Multiple configurations.


class __Index:
    """ Class provided to ease insertion and lookup in the index.

        Do not use this class, just import the `index` global variable.
        """

    def __init__(self):
        try:
            with open(indexPath, 'rt') as jsonIndex:
                self._dict = deserialize(jsonIndex)
        except FileNotFoundError:
            self._dict = {}
        except JSONDecodeError as e:
            eprint("Broken index !")
            eprint(e)
            exit(1)
        self._apps = set()
        self._confs = set()
        self._users = set(self._dict)
        # XXX: There *has* to be a way to make the following code cleaner. 🤔
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

    def __str__(self):
        return to_string(self._dict, indent=4, sort_keys=True)

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
        """ Check if `element` is in the index.
            Doesn't differentiante users from confs or apps.
            """
        return (element in self._apps or element in self._confs or element in self._users)

    def querry(self, user: str, app: str, conf: str):
        """ Check if a specific config is in the index. """
        return (user in self._users and app in self._apps and conf in self._confs)

    def insert(self, user, app, conf):
        """ Isert something in the index, and update its properties accordingly """
        self._users.add(user)
        self._apps.add(app)
        self._confs.add(conf)
        if user not in self._dict:
            self._dict[user] = {app: [conf]}
        elif app not in self._dict[user]:
            self._dict[user][app] = [conf]
        elif conf not in self._dict[user][app]:
            self._dict[user][app].append(conf)

    def update(self):
        """ Update the index file.

            This action is performed automatically when closing DotManager.
            """
        with open(indexPath, 'wt') as jsonIndex:
            serialize(self._dict, jsonIndex, indent=4, sort_keys=True)


index = __Index()
atexit.register(index.update)
