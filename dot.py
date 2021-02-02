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

    @classmethod
    def from_json_string(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    @classmethod
    def from_json(cls, json_file):
        try:
            with open(json_file, "r") as jf:
                return cls.from_json_string(jf.read())
        except json.JSONDecodeError as e:
            tools.eprint("Error while parsing file <" + jf.name + ">: ")
            exit(1)

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

    def is_excluded(self, path: str) -> bool:
        return any(
            fnmatch.fnmatchcase(path, "**" + exclude + "**")
            for exclude in self.exclude
        )

    def get_file_path(self, includeElement: str) -> str:
        if includeElement not in self.include:
            raise ValueError
        path = tools.realpath(includeElement)
        if not os.path.exists(path):
            raise FileNotFoundError
        return path

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


def get_list(confd: str = "./dots") -> list[Dot]:
    dotList = []
    for _ in wildcard(os.path.join(confd, '*.json')):
        dot = Dot.from_json(_)
        if shutil.which(dot.command) is None:
            continue
        dotList.append(dot)
    return dotList
