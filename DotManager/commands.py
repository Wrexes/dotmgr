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
import json
import shutil
import tarfile
from pathlib import Path
from pprint import pprint

import DotManager.tools as tools
import DotManager.config as config
import DotManager.dotinfo as dotinfo


class list:

    @staticmethod
    def supported():
        pprint(dotinfo.supported().keys())

    @staticmethod
    def installed():
        pprint(dotinfo.installed().keys())


class save:
    @staticmethod
    def name(dot: dotinfo,
             userName=config.userName,
             confName="default") -> Path:
        """ Build the name string for a config directory
            """
        return Path(userName + "-" + dot.name + "-" + confName)

    @classmethod
    def path(cls,
             dot: dotinfo,
             userName=config.userName,
             confName="default",
             saveDir=config.saveDir) -> Path:
        """ Build the path string for a config directory
            """
        return Path(saveDir) / cls.name(dot, userName, confName)

    @classmethod
    def save(cls,
             dot: dotinfo,
             userName=config.userName,
             confName="default",
             saveDir=config.saveDir,
             overwrite=False):
        """ Create a directory that will store the saved config
            """
        match = {}
        destination = cls.path(dot, userName, confName, saveDir)
        try:
            destination.mkdir(parents=True)
        except FileExistsError:
            while not overwrite:
                print(dot.name + " config \"" + confName +
                      "\" already exists for " + userName + ".")
                answer = 'x' + str(input("Overwrite it ? (y/N) ")).lower()
                if answer in ['x', 'xn', 'xno']:
                    print(
                        "Skipping " + userName + "'s configuration \"" + confName + "\" for " + dot.name + ".")
                    return
                elif answer in ['xy', 'xyes']:
                    break
                else:
                    continue
            shutil.rmtree(destination)
            destination.mkdir(parents=True)

        # For every file/dir, create a copy and store what goes where
        for inc in dot.include:
            src = Path(tools.realpath(inc))
            dst = destination / src.name
            if not src.exists() or dst.exists():
                continue
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)
            match[src.name] = inc

        # Clean up ignored files and directories
        for exc in dot.exclude:
            for item in sorted(destination.rglob(exc)):
                if item.is_file():
                    os.remove(item)
                else:
                    shutil.rmtree(item)

        # Create a JSON matching file
        # It's basically just a list of "element" : "goes here"
        with open(os.path.join(destination, "_dotmatch.json"), mode='wt') as f:
            json.dump(match, f, sort_keys=True)

        # for root, dirs, files in os.walk(destination):
        """ I'm keeping this in case the above exclusion deletion code breaks.
            I have a bad feeling about it for some reason. It seemed too simple.
            """
        # if dot.is_excluded(root):
        # shutil.rmtree(root)
        # for f in files:
        # if dot.is_excluded(f):
        # os.remove(f)
