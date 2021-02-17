#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os
import shutil
import json
from pprint import pprint

import dot
import tools
import config
import tarfile

class list:

    @staticmethod
    def supported():
        pprint(dot.supported().keys())

    @staticmethod
    def installed():
        pprint(dot.installed().keys())


class save:

    """ Build the name string for a config directory
        """
    @staticmethod
    def name(dot: dot, userName=config.userName, confName="default", confDir=config.confDir):
        return userName + "-" + dot.name + "-" + confName

    """ Build the path string for a config directory
        """
    @staticmethod
    def path(dot: dot, userName=config.userName, confName="default", confDir=config.confDir):
        return os.path.join(confDir, save.name(dot, userName, confName, confDir))

    """ Create a directory that will store the saved config
        """
    @staticmethod
    def save(dot: dot, userName=config.userName, confName="default", confDir=config.confDir, override=False):
        match = {}
        path = save.path(dot, userName, confName, confDir)

        # Check if the directory exists
        if os.path.exists(path):
            # If not, ask the user what to do
            while not override:
                try:
                    answer = str(input(path + " already exists. Would you like to override it ? (y/n)"))
                    if answer == 'y':
                        override = True
                    elif answer == 'n':
                        break;
                    else:
                        continue
                except ValueError:
                    continue
            # Finally, keep going or stop here
            if override:
                shutil.rmtree(path)
            else:
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
