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
import re
import json
import shutil
import fnmatch
from glob import glob as wildcard
from importlib.resources import as_file
from importlib.resources import files as data

import DotManager.tools as tools
import DotManager.config as config


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
    def from_json_dict(cls, jsonDict: dict):
        return cls(**jsonDict)


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
        except json.JSONDecodeError as e:
            tools.eprint("Error while parsing " + jf.name + ":\n" + e.msg)
            exit(1)

    def __validate(self):
        """ Private method to check that a Dot object has valid necessary values.

            It is automatically called in Dot.__init__ which means you should never
            have to use it yourself.
            """
        regex = "^[a-zA-Z0-9_][a-zA-Z0-9_i\-]+$"
        if self.name is None:
            raise KeyError("Missing name property.")
        if re.fullmatch(regex, self.name) is None:
            raise KeyError("Invalid name: " + self.name +
                           ".\nMust match this regex: " + regex)
        if self.command is None:
            raise KeyError("Missing command property.")
        if re.fullmatch(regex, self.command) is None:
            raise NameError("Invalid command: " + self.command +
                            " must match this regex: " + regex)
        if self.include.__len__() < 1:
            raise KeyError("No config file to include for " + self.name)

    def is_installed(self) -> bool:
        """ Returns true if the app is installed on the user's machine. """
        return shutil.which(self.command) is not None

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


# TODO: Cleanup this code, reduce boilerplate/copypastas
def supported(confd: str = config.confDir) -> dict[DotInfo]:
    """ Return a dictionary of supported apps.
        Keys are the names of the apps.
        """
    dots = {}
    # TODO: Make a stack context manager
    # TODO: Create exceptions,
    #       Encapsulate these two loops in try blocks.
    #       Move the error handling from the ifs in excepts.
    for dotinfo in config.confDir.joinpath("dotinfo").glob("*.dotinfo"):
        with open(dotinfo, 'rt') as jsonFile:
            dot = DotInfo.from_json_string(jsonFile.read())
            if dot.name in dots:
                tools.eprint("Error: duplicate dotinfo for " + dot.name + ".")
                tools.eprint("Skipping " + dotinfo)
            dots[dot.name] = dot

    with as_file(data("DotManager").joinpath("dotinfo")) as path:
        # TODO: Try making my own context manager for this
        #       It's probably more elegant, if it is possible
        for f in path.glob( "*.dotinfo"):
            dot = DotInfo.from_json(f)
            dots[dot.name] = dot
    return dots


def installed(confd: str = config.confDir) -> dict[DotInfo]:
    """ Return a dictionary of installed apps.
        Keys are the names of the apps.
        """

    dots = {}
    # TODO: Make a stack context manager
    # TODO: Create exceptions,
    #       Encapsulate these two loops in try blocks.
    #       Move the error handling from the ifs in excepts.
    for dotinfo in config.confDir.joinpath("dotinfo").glob("*.dotinfo"):
        with open(dotinfo, 'rt') as jsonFile:
            dot = DotInfo.from_json_string(jsonFile.read())
            if dot.name in dots:
                tools.eprint("Error: duplicate dotinfo for " + dot.name + ".")
                tools.eprint("Skipping " + dotinfo)
            if not dot.is_installed():
                continue
            dots[dot.name] = dot

    with as_file(data("DotManager").joinpath("dotinfo")) as path:
        # TODO: Try making my own context manager for this
        #       It's probably more elegant, if it is possible
        for f in path.glob('*.dotinfo'):
            try:
                with open(f, "r") as jf:
                    jsonDict = json.load(jf)
            except json.JSONDecodeError as e:
                tools.eprint(e.with_traceback)
                continue
            if shutil.which(jsonDict["Command"]) is None:
                continue
            if jsonDict["Name"] in dots:
                continue
            dots[jsonDict["Name"]] = DotInfo(**jsonDict)
    return dots
