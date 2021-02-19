#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import os
import json
import shutil
from pathlib import Path

import DotManager.dotinfo
from DotManager.tools import realpath


class __Info:
    def __init__(self, dot: dotinfo, userName, confName, saveDir, force):
        # DotInfo stuff
        self.include = dot.include
        self.exclude = dot.exclude

        # SaveInfo stuff
        self.userName = userName
        self.dotName = dot.name
        self.confName = confName
        self.saveDir = saveDir
        self.force = force

        # Directory name and location
        self.baseName = Path(userName + '-' + dot.name, + '-' + confName)
        self.location = Path(saveDir).joinpath(self.baseName)

        # String builders for code readability
        self._FileExists = dot.name + "config '" + \
            confName + "' already exists for " + userName + "."
        self._Skip = "Skipping " + userName + "'s " + \
            confName + "config for " + dot.name + "."

        # Dictionary matching what goes where
        self.match = {}

    @classmethod
    def create_dir(cls):
        try:
            cls.location.mkdir(parents=True)
        except FileExistsError:
            while not force:
                print(cls._FileExists)
                answer = 'x' + str(input("Overwrite it ? (y/N) ")).lower()
                if answer in ['x', 'xn', 'xno']:
                    print(cls._Skip)
                    return
                elif answer in ['xy', 'xyes']:
                    break
                else:
                    continue
            shutil.rmtree(cls.location)
            cls.location.mkdir(parents=True)

    @classmethod
    def copy_conf(cls):
        for inc in cls.include:
            src = Path(realpath(inc))
            dst = cls.location / src.name
            if not src.exists() or dst.exists():
                continue
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)
            cls.match[src.name] = inc

    @classmethod
    def cleanup_exclusions(cls):
        for exc in cls.exclude:
            for item in sorted(cls.location.rglob(exc)):
                if item.is_file():
                    os.remove(item)
                else:
                    shutil.rmtree(item)
        """ I'm keeping this in case the above exclusion cleanuo code breaks.
            I have a bad feeling about it for some reason. It seemed too simple.
            """
        # for root, dirs, files in os.walk(destination):
        #     if dot.is_excluded(root):
        #         shutil.rmtree(root)
        #     for f in files:
        #         if dot.is_excluded(f):
        #             os.remove(f)

    @classmethod
    def create_dotmatch(cls):
        with cls.location.joinpath(".dotmatch.json").open(mode='wt') as f:
            json.dump(match, f, indent=4, sort_keys=True)


def save(dot: dotinfo,
         userName=config.userName,
         confName="default",
         saveDir=config.saveDir,
         force=False):
    info = __Info(dot, userName, confName, saveDir)
    info.create_dir()
    info.copy_conf()
    info.cleanup_exclusions()
    info.create_dotmatch()

    # Clean up ignored files and directories

    # Create a JSON matching file
    # It's basically just a list of "element" : "goes here"

    # Save this conf in the index
    saveInfo = {
        userName: {
            dot.name: [
                confName
            ]
        }
    }
    try:
        with config.confDir.joinpath("confs.json").open(mode='r+t') as f:
            jsonContents = json.load(f)
            pprint(jsonContents + saveInfo)
            json.dump(saveInfo, f)
    except FileNotFoundError:
        with config.confDir.joinpath("confs.json").open(mode='wt') as f:
            json.dump(saveInfo, f)
