#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import json
import re
import shutil
import os
import fnmatch
from glob import glob as wildcard

import tools
import config


""" Class: Dot

    Contains all the necessary information for backing up a software's dotfiles

    Dot.name: Application name.
    Dot.command: Shell command that can be used with `which` to check for an app's presence.
    Dot.include: Files to include in the backup. Supports environment variables and user (~) expansion.
    Dot.exclude: Files to exclude from the backup. Supports UNIX style globbing (think gitignore).
    Dot.files: Set of tuples containing (directory, file) for each config to save.
    """


class Dot:

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


    """ Create a Dot object using a JSON file's content
        json_string: Buffered content of a JSON file
        """
    @classmethod
    def from_json_string(cls, json_string: str):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


    """ Create a Dot object importing a JSON file from given path.
        json_file: Path to JSON file
        """
    @classmethod
    def from_json(cls, json_file: str):
        try:
            with open(json_file, "r") as jf:
                jsonString = jf.read()
            return cls.from_json_string(jsonString)
        except json.JSONDecodeError as e:
            tools.eprint("Error while parsing " + jf.name + ":\n" + e.msg)
            exit(1)


    """ Private method to check that a Dot object has valid necessary values.
        It is automatically called in Dot.__init__ which means you should never
        have to use it yourself.
        """
    def __validate(self):
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


    """ Return true if a file/directory's path contains an excluded expression.
        This function doesn't check if the file exists, is valid, or anything like that.
        It just checks the path string.
        """
    def is_excluded(self, path: str) -> bool:
        return any(
            fnmatch.fnmatchcase(path, "**" + exclude + "**")
            for exclude in self.exclude
        )


    """ Take an element from a Dot's includes, and find its absolute path on the working host.
        If the file or directory doesn't exists, a ValueError is raised.
        """
    def get_file_path(self, includeElement: str) -> str:
        if includeElement not in self.include:
            raise ValueError
        path = tools.realpath(includeElement)
        if not os.path.exists(path):
            raise FileNotFoundError
        return path


    """ Populate a Dot object's .files property.
        """
    def find_confs(self) -> set[(str, str)]:
        if self.files is not None:
            return self.files
        path = ""
        fileSet = set()
        for inc in self.include:
            try:
                path = self.get_file_path(inc)
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


""" Return a dictionary of supported apps.
    Keys are the names of the apps.
    """
def supported(confd: str = config.confDir) -> dict[Dot]:
    dots = {}
    for f in wildcard(os.path.join(confd, "dots", "*.json")):
        dot = Dot.from_json(f)
        dots[dot.name] = dot
    return dots


""" Return a dictionary of installed apps.
    Keys are the names of the apps.
    """
def installed(confd: str = config.confDir) -> dict[Dot]:
    dots = {}
    for f in wildcard(os.path.join(confd, "dots", "*.json")):
        try:
            with open(f, "r") as jf:
                jsonDict = json.load(jf)
        except:
            continue
        if shutil.which(jsonDict["Command"]) is None:
            continue
        dots[jsonDict["Name"]] = Dot(**jsonDict)
    return dots
