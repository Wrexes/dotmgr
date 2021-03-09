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

import fnmatch
from importlib.resources import as_file
from importlib.resources import files as data
from json import load as deserialize
from json import loads as deserializes
from json import dump as serialize
from json import dumps as serializes
import json
import os
from pathlib import Path
import re
import shutil
from typing import Union

import DotManager.config as config
import DotManager.tools as tools


class DotInfo:
    """ Contains all the necessary information for backing up a config.

        @name:    Application name.
        @command: Called with `which` to check if the app is installed.
        @include: Files to include. Supports string interpolation.
        @exclude: Files to exclude. Supports globbing (think gitignore).

        @files: Full List of files in the current config to save.
                Not yet implemented.
        """

    def __init__(self,
                 Name: str,
                 Command: str,
                 Include: list[str],
                 Exclude: list[str]):
        self.name:    str = Name
        self.command: str = Command
        self.include: list[str] = sorted([f.rstrip('/') for f in Include])
        self.exclude: list[str] = sorted([f.rstrip('/') for f in Exclude])
        self._files:  set[Path]
        self.__validate()

    @property
    def files(self):  # -> set[Path]:
        """ TODO: Write a *fast* and *efficient* way to build this list. """
        pass

    def __str__(self) -> str:
        ret = "Name:     {self.name}\n"
        ret += "Command:  {self.command}\n"
        ret += "Include:\n"
        for inc in self.include:
            ret += "  " + inc + "\n"
        ret += "Exclude:\n"
        for exc in self.exclude:
            ret += "  " + exc + "\n"
        # ret += "Files:"
        # for f in sorted(self.files):
            # ret += "\n  " + str(f)
        return ret.format(self=self)

    @classmethod
    def from_json_dict(cls, jsonDict: dict):
        """ Create a DotInfo from a deserialized JSON file. """
        return cls(**jsonDict)

    @classmethod
    def from_json_string(cls, jsonString: str):
        """ Create a Dot object using a JSON file's content. """
        jsonDict = deserializes(jsonString)
        return cls(**jsonDict)

    @classmethod
    def from_json(cls, jsonFile: Union[str, Path]):
        """ Create a Dot object importing a JSON file from given path. """
        try:
            with open(jsonFile, "r") as jf:
                jsonString = jf.read()
            return cls.from_json_string(jsonString)
        except json.JSONDecodeError as e:
            tools.eprint(f"Error while parsing {str(jsonFile)}:\n  {e.msg}")
            exit(1)

    def __validate(self):
        """ Private method to check that a DotInfo's values are valid.

            It is automatically called when instanciating a new DotInfo, which
            means that you should never have to use it yourself.
            """
        regex = "^[a-zA-Z0-9_][a-zA-Z0-9_i\-]+$"
        if self.name is None:
            raise KeyError("Missing name property.")
        if re.fullmatch(regex, self.name) is None:
            raise KeyError(
                f"Invalid name: {self.name}\n" +
                f"Must match this regex: {regex}")
        if self.command is None:
            raise KeyError("Missing command property.")
        if re.fullmatch(regex, self.command) is None:
            raise NameError(
                f"Invalid command: {self.command}\n" +
                f"Must match this regex: {regex}")
        if self.include.__len__() < 1:
            raise KeyError(f"No config file to include for {self.name}")

    def is_installed(self) -> bool:
        """ Returns true if the app is installed on the user's machine. """
        return shutil.which(self.command) is not None

    def is_excluded(self, path: Union[str, Path]) -> bool:
        """ Return true if a file/dir's path contains an excluded expression.

            This function doesn't check if the file exists, is valid, or
            anything like that. It just checks the path string.
            """
        path = str(path)
        return any(
            fnmatch.fnmatchcase(path, "**" + exclude + "**")
            for exclude in self.exclude
        )

    def get_file_path(self, includeElement: str) -> Path:
        """ Takes an element from a DotInfo's includes and get its abspath.

            If the file or directory isn't part of the dot's includes,
            a ValueError is raised.
            """
        if includeElement not in self.include:
            raise ValueError(
                f"{includeElement} is not part of {self.name}'s includes.")
        path: Path = tools.realpath(includeElement)
        # XXX: Probably replace this with returning None. 🤔
        if not path.exists():
            raise FileNotFoundError
        return path


# TODO: Cleanup this code, reduce boilerplate/copypastas.
# TODO: Turn these into generators that use `yield`.
def supported(confd: Union[str, Path] = config.confDir) -> dict[str, DotInfo]:
    """ Return a dictionary of supported apps.

        Keys are the names of the apps.
        """
    dots = {}
    # TODO: Make a stack context manager
    # TODO: Create exceptions,
    #       Encapsulate these two loops in try blocks.
    #       Move the error handling from the ifs to excepts.
    for dotinfo in Path(confd).joinpath("dotinfo").glob("*.dotinfo"):
        with open(dotinfo, 'rt') as jsonFile:
            dot = DotInfo(**deserialize(jsonFile))
            if dot.name in dots:
                tools.eprint(f"Error: duplicate dotinfo for {dot.name}.")
                tools.eprint(f"Skipping {str(dotinfo)}.")
            dots[dot.name] = dot

    with as_file(data("DotManager").joinpath("dotinfo")) as path:
        # TODO: Try making my own context manager for this
        #       It's probably more elegant, if it is possible
        for f in path.glob("*.dotinfo"):
            dot = DotInfo.from_json(f)
            dots[dot.name] = dot
    return dots


def installed(confd: Union[str, Path] = config.confDir) -> dict[str, DotInfo]:
    """ Return a dictionary of installed apps.

        Keys are the names of the apps.
        """
    dots = {}
    # TODO: Make a stack context manager
    # TODO: Create exceptions,
    #       Encapsulate these two loops in try blocks.
    #       Move the error handling from the ifs to excepts.
    for dotinfo in Path(confd).joinpath("dotinfo").glob("*.dotinfo"):
        with open(dotinfo, 'rt') as jsonFile:
            dot = DotInfo(**deserialize(jsonFile))
            if dot.name in dots:
                tools.eprint(f"Error: duplicate dotinfo for {dot.name}.")
                tools.eprint(f"Skipping {str(dotinfo)}.")
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
