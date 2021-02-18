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

import dotinfo
import tools
import config
import tarfile

class list:

    @staticmethod
    def supported():
        pprint(dotinfo.supported().keys())

    @staticmethod
    def installed():
        pprint(dotinfo.installed().keys())


class save:

    """ Build the name string for a config directory
        """
    @staticmethod
    def name(dot: dotinfo, userName=config.userName, confName="default"):
        return userName + "-" + dot.name + "-" + confName

    """ Build the path string for a config directory
        """
    @staticmethod
    def path(dot: dotinfo, userName=config.userName, confName="default", saveDir=config.saveDir):
        return os.path.join(saveDir, save.name(dot, userName, confName))

    """ Create a directory that will store the saved config
        """
    @staticmethod
    def save(dot: dotinfo, userName=config.userName, confName="default", saveDir=config.saveDir, overwrite=False):
        match = {}
        path = save.path(dot, userName, confName, saveDir)
        # Check if the directory exists
        if os.path.exists(path):
            # If not, ask the user what to do
            while not overwrite:
                answer = 'x' + str(input(dot.name + " config \"" + confName + "\" already exists for " + userName + ". Overwrite it ? (y/N) ")).lower()
                if answer == 'y':
                    overwrite = True
                elif answer in ['x', 'xn']:
                    break;
                else:
                    continue
            # Keep going or stop here
            if overwrite:
                shutil.rmtree(path)
            else:
                print("Skipping " + userName + "'s configuration \"" + confName + "\" for " + dot.name + ".")
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
