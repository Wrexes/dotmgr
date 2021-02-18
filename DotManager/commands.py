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
    def name(dot: dotinfo, userName=config.userName, confName="default"):
        """ Build the name string for a config directory
            """
        return userName + "-" + dot.name + "-" + confName

    @staticmethod
    def path(dot: dotinfo,
             userName=config.userName,
             confName="default",
             saveDir=config.saveDir):
        """ Build the path string for a config directory
            """
        return os.path.join(saveDir, save.name(dot, userName, confName))

    @staticmethod
    def save(dot: dotinfo,
             userName=config.userName,
             confName="default",
             saveDir=config.saveDir,
             overwrite=False):
        """ Create a directory that will store the saved config
            """
        match = {}
        path = save.path(dot, userName, confName, saveDir)

        # Check if the directory exists
        if os.path.exists(path):
            # If not, ask the user what to do
            while not overwrite:
                answer = 'x' + str(input(
                    dot.name + " config \"" + confName + "\" already exists for " + userName + ".\n"
                    + "Overwrite it ? (y/N) ")
                ).lower()
                if answer == 'y':
                    overwrite = True
                elif answer in ['x', 'xn']:
                    break
                else:
                    continue

            # Keep going or stop here
            if overwrite:
                shutil.rmtree(path)
            else:
                print("Skipping " + userName + "'s configuration \"" +
                      confName + "\" for " + dot.name + ".")
                return

        os.mkdir(path)

        # For every file/dir, create a copy and store what goes where
        for src in dot.include:
            dst = os.path.join(path, os.path.basename(src))
            if os.path.isfile(tools.realpath(src)):
                shutil.copy2(tools.realpath(src), dst)
            else:
                shutil.copytree(tools.realpath(src), dst)
            match[os.path.basename(src)] = src

        # Clean up ignored files and directories
        for root, dirs, files in os.walk(path):
            if dot.is_excluded(root):
                shutil.rmtree(root)
            for f in files:
                if dot.is_excluded(f):
                    os.remove(f)

        # Create a JSON matching file
        # It's basically just a list of "element" : "goes here"
        with open(os.path.join(path, "_dotmatch.json"), mode='wt') as f:
            json.dump(match, f, sort_keys=True)
