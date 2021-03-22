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
from itertools import chain
from json import dumps as to_string
from json import load as deserialize
from json import dump as serialize
from json import JSONDecodeError

import DotManager.config as config
from DotManager.tools import eprint

# TODO: Check out atExit, write the index when program closes.
#       This will reduce I/O overhead when saving/deleting
#       Multiple configurations.


class __Index:
    """ Class provided to ease insertion and lookup in the index.

        Do not use this class, unless you want your changes to the index to
        be ignored. Use the global variable `index` from this submodule
        instead.
        """

    def __init__(self):
        self._dict: dict[str, dict[str, list[str]]] = {}
        try:
            with open(config.indexPath, 'rt') as jsonIndex:
                self._dict = deserialize(jsonIndex)
        except JSONDecodeError as e:
            eprint("Broken index !")
            eprint(e)
            exit(1)

        # Fetch the users from the keys in self._dict
        self._users: set[str] = set(self._dict)

        # Fetch the apps for each user, including duplicates
        self._apps: list[str] = []
        for user in self._users:
            self._apps.extend(self._dict[user])

        # Fetch the config names for each saved app, all users included.
        self._confs: list[str] = []
        for user in self._users:
            # Honestly, don't ask. I came up with this by accident.
            # It's pretty fast though so guess I'll keep it.
            self._confs.extend(chain.from_iterable(self._dict[user].values()))

    def __str__(self) -> str:
        return to_string(self._dict,
                         indent=4,
                         sort_keys=True,
                         ensure_ascii=False)

    @property
    def __dict__(self) -> dict: return self._dict.copy()
    """ Get a copy on the deserialized JSON index. """

    @property
    def apps(self) -> set[str]: return set(self._apps)
    """ Get a set of all the apps registered in the index. """

    @property
    def confs(self) -> set[str]: return set(self._confs)
    """ Get a set of all the configurations names saved in the index. """

    @property
    def users(self) -> set[str]: return set(self._users)
    """ Get a set of all the users registered in the index. """

    def has(self, element: str) -> bool:
        """ Check if `element` is in the index.

            Doesn't differentiante users from confs or apps.
            """
        return (element in self.apps
                or element in self.confs
                or element in self.users)

    def query(self,
               app: str,
               name: str = "default",
               user: str = config.userName) -> bool:
        """ Check if a specific config is in the index. """
        if user not in self.users:
            return False
        if app not in self._dict[user]:
            return False
        return name in self._dict[user][app]

    def insert(self, app: str, name: str, user: str):
        """ Isert something in the index. """
        if user not in self._dict:
            self._dict[user] = {app: [name]}
            self._users.add(user)
        if app not in self._dict[user]:
            self._dict[user][app] = [name]
            self._apps.append(app)
        if name not in self._dict[user][app]:
            self._dict[user][app].append(name)
            self._confs.append(name)

    def remove(self, app: str, name: str, user: str):
        """ Remove something from the index. """
        if not self.query(app, name, user):
            return
        self._confs.remove(name)
        self._dict[user][app].remove(name)
        if len(self._dict[user][app]) < 1:
            del self._dict[user][app]
            self._apps.remove(app)
        if len(self._dict[user]) < 1:
            del self._dict[user]
            self._users.remove(user)

    def update(self):
        """ Update the index file.

            This action is performed automatically when closing DotManager.
            """
        with open(config.indexPath, 'wt') as jsonIndex:
            serialize(self._dict,
                      jsonIndex,
                      indent=4,
                      sort_keys=True,
                      ensure_ascii=False)


index = __Index()
""" __Index() object containing information about saved configs.

    Since an atexit is registered for this object's update() function, using any other
    instance of the __Index() won't work as a way to update DotManager's index.json.
    """

# When DotManager closes, save any changes made to the index
# Updating on exit reduces I/O overhead by writing the file ONCE.
# Using atexit ensures that no matter what happens during DotManager's,
# execution, the index is updated with its changes, given that error
# handling is done properly.
atexit.register(index.update)
