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
from pprint import pprint
from pathlib import Path

import DotManager.config as config
import DotManager.dotinfo as dotinfo
from DotManager.index import index
from DotManager.tools import realpath, eprint


class SaveInfo:
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

        # Save destination name and location
        self.baseName = Path(userName + '-' + dot.name + '-' + confName)
        self.location = Path(saveDir).joinpath(self.baseName)

        # String builders for code readability
        self._FileExists = dot.name + " config '" + \
            confName + "' already exists for " + userName + "."
        self._Skip = "Skipping " + userName + "'s " + \
            confName + "config for " + dot.name + "."

        # Dictionary matching what goes where
        self.match = {}

    def create_dir(self):
        try:
            self.location.mkdir(parents=True)
        except FileExistsError:
            while not self.force:
                print(self._FileExists)
                answer = 'x' + str(input("Overwrite it ? (y/N) ")).lower()
                if answer in ['x', 'xn', 'xno']:
                    print(self._Skip)
                    return
                elif answer in ['xy', 'xyes']:
                    break
                else:
                    continue
            shutil.rmtree(self.location)
            self.location.mkdir(parents=True)

    def copy_conf(self):
        for inc in self.include:
            src = Path(realpath(inc))
            dst = self.location / src.name
            if not src.exists() or dst.exists():
                continue
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst)
            self.match[src.name] = inc

    def cleanup_exclusions(self):
        for exc in self.exclude:
            for item in sorted(self.location.rglob(exc)):
                if item.is_file():
                    os.remove(item)
                else:
                    shutil.rmtree(item)

        # for root, dirs, files in os.walk(destination):
        """ I'm keeping this in case the above exclusion cleanuo code breaks.
            I have a bad feeling about it for some reason. It seemed too simple.
            """
        #     if dot.is_excluded(root):
        #         shutil.rmtree(root)
        #     for f in files:
        #         if dot.is_excluded(f):
        #             os.remove(f)

    def create_dotmatch(self):
        with self.location.joinpath(".dotmatch.json").open(mode='wt') as f:
            json.dump(self.match, f, indent=4, sort_keys=True)


def save(dot: dotinfo,
         userName=config.userName,
         confName="default",
         saveDir=config.saveDir,
         force=False):
    """ Save your config to `saveDir/userName-dot.name-confName`.
        Also create a corresponding entry in the index.
        """
    info = SaveInfo(dot, userName, confName, saveDir, force)
    info.create_dir()
    info.copy_conf()
    info.cleanup_exclusions()
    info.create_dotmatch()
    index.insert(userName, dot.name, confName)
