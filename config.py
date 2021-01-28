#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import json
import re
import os


class Dot:
    import eprint

    # def __init__(self, Name=None, Command=None, Files=[], Ignores=None):
    def __init__(self, Name=None, Command=None, Files=[]):
        self.name = Name
        self.command = Command
        self.files = Files
        # self.ignores = Ignores
        # self.__validate()

    def __str__(self) -> str:
        ret = "<Name>\n\t{self.name}\n"
        ret += "<Command>\n\t{self.command}\n"
        ret += "<Files>\n\t{self.files}\n"
        return ret.format(self=self)

    def __validate(self):
        reval = "^[a-zA-Z0-9_][a-zA-Z0-9_i\-]+$"
        if self.name is None:
            raise KeyError("Missing name property.")
        if re.fullmatch(reval, self.Command) is None:
            raise KeyError("Invalid App name, must match this regex: " + reval)
        if self.command is None:
            raise KeyError("Missing command property.")
        if re.fullmatch(reval, self.Command) is None:
            raise NameError(
                "Invalid App command, must match this regex: " + reval)
        if self.files.__len__() < 1:
            raise KeyError("No config file specified for " + self.name)

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
            eprint("Error while parsing file <" + jf.name + ">: ")
            exit(1)
