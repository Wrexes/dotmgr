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

import json
import re
import shutil
import os
import fnmatch
from glob import glob as wildcard

import tools
import config


class DotInfo:
    """ Contains all the necessary information for backing up a software's dotfiles

        name:    Application name.
        command: Shell command called with `which` to check for an app's presence.
        include: Files to include in the backup. Supports string interpolation.
        exclude: Files to exclude from the backup. Supports UNIX style globbing (think gitignore).
        files:   Set of tuples containing (directory, file) for each config to save.
        """

    def __init__(self, Name: str = None, Command: str = None, Include: list[str] = [], Exclude: list[str] = []):
        self.name = Name
        self.command = Command
        self.include = sorted([f.rstrip('/') for f in Include])
        self.exclude = sorted([f.rstrip('/') for f in Exclude])
        # TODO: Transform files into a property
        self.files = None
        self.__validate()

    def __str__(self) -> str:
        ret = "Name:     {self.name}\n"
        ret += "Command:  {self.command}\n"
        ret += "Include:\n"
        for i in self.include:
            ret += "  " + i + "\n"
        ret += "Exclude:\n"
        for i in self.exclude:
            ret += "  " + i + "\n"
        ret += "Configs:"
        if self.files is None or len(self.files) < 1:
            ret += "\n  None set yet.\n"
            ret += "  Use the object's find_confs() method to populate."
        else:
            for i in sorted(self.files):
                ret += "\n  " + i.__str__()
        return ret.format(self=self)

    @classmethod
    def from_json_string(cls, jsonString: str):
        """ Create a Dot object using a JSON file's content
            json_string: Buffered content of a JSON file
            """
        jsonDict = json.loads(jsonString)
        return cls(**jsonDict)

    @classmethod
    def from_json(cls, jsonFile: str):
        """ Create a Dot object importing a JSON file from given path.
            jsonFile : Path to JSON file
            """
        try:
            with open(jsonFile, "r") as jf:
                jsonString = jf.read()
            return cls.from_json_string(jsonString)
        # TODO: Proper exception handling
        except json.JSONDecodeError as e:
            tools.eprint("Error while parsing " + jf.name + ":\n" + e.msg)
            exit(1)

    def __validate(self):
        """ Private method to check that a Dot object has valid necessary values.
            It is automatically called in Dot.__init__ which means you should never
            have to use it yourself.
            """
        reval = "^[a-zA-Z0-9_][a-zA-Z0-9_i\-]+$"
        if self.name is None:
            raise KeyError("Missing name property.")
        if re.fullmatch(reval, self.name) is None:
            raise KeyError("Invalid name: " + self.name +
                           ".\nMust match this regex: " + reval)
        if self.command is None:
            raise KeyError("Missing command property.")
        if re.fullmatch(reval, self.command) is None:
            raise NameError("Invalid command: " + self.command +
                            " must match this regex: " + reval)
        if self.include.__len__() < 1:
            raise KeyError("No config file to include for " + self.name)

    def is_excluded(self, path: str) -> bool:
        """ Return true if a file/directory's path contains an excluded expression.
            This function doesn't check if the file exists, is valid, or anything like that.
            It just checks the path string.
            """
        return any(
            fnmatch.fnmatchcase(path, "**" + exclude + "**")
            for exclude in self.exclude
        )

    def get_file_path(self, includeElement: str) -> str:
        """ Take an element from a Dot's includes, and find its absolute path on the working host.
            If the file or directory doesn't exists, a ValueError is raised.
            """
        if includeElement not in self.include:
            raise ValueError
        path = tools.realpath(includeElement)
        if not os.path.exists(path):
            raise FileNotFoundError
        return path

    def find_confs(self) -> set[(str, str)]:
        """ Populate a Dot object's .files property.
            """
        if self.files is not None:
            return self.files
        path = ""
        fileSet = set()
        for inc in self.include:
            try:
                path = self.get_file_path(inc)
            # TODO: Proper exception handling
            except:
                continue
            if self.is_excluded(path):
                continue
            if os.path.isfile(path):
                fileSet.add((os.path.dirname(path), os.path.basename(path)))
                continue
            for root, dirs, files in os.walk(path):
                if self.is_excluded(root):
                    continue
                for f in files:
                    if self.is_excluded(f):
                        continue
                    fileSet.add((root, f))
        self.files = fileSet
        return self.files


def supported(confd: str = config.confDir) -> dict[DotInfo]:
    """ Return a dictionary of supported apps.
        Keys are the names of the apps.
        """
    dots = {}
    for f in wildcard(os.path.join(confd, "dotinfo", "*.dotinfo")):
        dot = DotInfo.from_json(f)
        dots[dot.name] = dot
    return dots


def installed(confd: str = config.confDir) -> dict[DotInfo]:
    """ Return a dictionary of installed apps.
        Keys are the names of the apps.
        """
    dots = {}
    for f in wildcard(os.path.join(confd, "dotinfo", "*.dotinfo")):
        try:
            with open(f, "r") as jf:
                jsonDict = json.load(jf)
        # TODO: Proper exception handling
        except:
            continue
        if shutil.which(jsonDict["Command"]) is None:
            continue
        dots[jsonDict["Name"]] = DotInfo(**jsonDict)
    return dots
