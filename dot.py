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


class Dot:

    def __init__(self, Name=None, Command=None, Include=[], Exclude=[]):
        self.name = Name
        self.command = Command
        self.include = Include
        self.exclude = Exclude
        self.files = None
        self.files = self.get_file_list()
        self.__validate()

    def __str__(self) -> str:
        ret = "<Name>\n\t{self.name}\n"
        ret += "<Command>\n\t{self.command}\n"
        ret += "<Include>\n\t{self.include}\n"
        ret += "<Exclude>\n\t{self.exclude}\n"
        return ret.format(self=self)

    # Create a Dot object using a JSON file's content
    # json_string: Buffered content of a JSON file
    @classmethod
    def from_json_string(cls, json_string: str) -> Dot:
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    # Create a Dot object importing a JSON file from given path
    # json_file: Path to JSON file
    @classmethod
    def from_json(cls, json_file: str) -> Dot:
        try:
            with open(json_file, "r") as jf:
                return cls.from_json_string(jf.read())
        except json.JSONDecodeError as e:
            tools.eprint("Error while parsing file <" + jf.name + ">: ")
            exit(1)

    # Private method to check that a Dot object has valid necessary values.
    # It is automatically called in Dot.__init__ which means you should never
    # have to use it yourself.

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

    # Return true if a file/directory's path contains an excluded expression.
    # This function doesn't check if the file exists, is valid, or anything like that.
    # It just checks the path string.
    def is_excluded(self, path: str) -> bool:
        return any(
            fnmatch.fnmatchcase(path, "**" + exclude + "**")
            for exclude in self.exclude
        )

    # Take an element from a Dot's includes, and find its absolute path on the working host.
    # If the file or directory doesn't exists, a ValueError is raised.
    def get_file_path(self, includeElement: str) -> str:
        if includeElement not in self.include:
            raise ValueError
        path = tools.realpath(includeElement)
        if not os.path.exists(path):
            raise FileNotFoundError
        return path

    # Return a Dot object's .files property.
    # If a Dot object's .files property is none, create and populate it, then return it.
    # This will look recursively for all existing & non excluded paths based on a Dot's includes and
    # make a set from the results.
    def get_file_list(self) -> set[str]:
        if self.files is not None:
            return self.files
        fileSet = set()
        path = None
        for inc in self.include:
            try:
                path = self.get_file_path(inc)
            except:
                continue
            if self.is_excluded(path):
                continue
            if os.path.isfile(path):
                fileSet.add(path)
            for root, dirs, files in os.walk(path):
                for f in files:
                    if self.is_excluded(root) or self.is_excluded(f):
                        continue
                    fileSet.add(os.path.join(root, f))
        return fileSet

# Read every JSON file in given confd directory and create a list of Dot objects.
def get_list(confd: str = "./dots") -> list[Dot]:
    dotList = []
    for _ in wildcard(os.path.join(confd, '*.json')):
        dot = Dot.from_json(_)
        if shutil.which(dot.command) is None:
            continue
        dotList.append(dot)
    return dotList