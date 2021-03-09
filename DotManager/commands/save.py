#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Project by
# Ludovic Fernandez
# http://github.com/Wrexes

import json
import os
from pathlib import Path
import shutil
from typing import Union

import DotManager.config as config
from DotManager.dotinfo import DotInfo
from DotManager.index import index
from DotManager.tools import realpath


class SaveInfo:
    def __init__(self,
                 dot: DotInfo,
                 conf: str,
                 user: str,
                 saveDir: Union[str, Path]):
        # DotInfo stuff
        self.include = dot.include
        self.exclude = dot.exclude

        # SaveInfo stuff
        self.userName = user
        self.dotName = dot.name
        self.confName = conf
        self.saveDir = saveDir

        # Save destination name and location
        self.baseName = Path(f"{user}-{dot.name}-{conf}")
        self.location = Path(saveDir).joinpath(self.baseName)

        # String builders for code readability
        self._FileExists = \
            f"{dot.name} config '{conf}' already exists for {user}."
        self._Skip = f"Skipping {user}'s {conf} config for {dot.name}."

        # Dictionary matching what goes where
        self.match = {}

    def create_dir(self):
        if self.location.exists():
            shutil.rmtree(self.location)
        self.location.mkdir(parents=True)

    def copy_conf(self):
        for inc in self.include:
            src = Path(realpath(inc))
            dst = self.location.joinpath(src.name)
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
        #     if dot.is_excluded(root):
        #         shutil.rmtree(root)
        #     for f in files:
        #         if dot.is_excluded(f):
        #             os.remove(f)
        """ I'm keeping this in case the above exclusion cleanup code breaks.
            I have a bad feeling about it for some reason. It seemed too simple.
            """

    def create_dotmatch(self):
        with self.location.joinpath(".dotmatch.json").open(mode='wt') as f:
            json.dump(self.match, f, indent=4, sort_keys=True)


def save(dot: DotInfo,
         conf: str = "default",
         user: str = config.userName,
         saveDir: Union[str, Path] = config.saveDir,
         force: bool = False):
    """ Save your config to `saveDir/userName-dot.name-confName`.
        Also create a corresponding entry in the index.
        """
    info = SaveInfo(dot, conf, user, saveDir)
    if index.querry(dot.name, conf, user):
        while not force:
            print(info._FileExists)
            answer = 'x' + str(input("Overwrite it ? (y/N) ")).lower()
            if answer in ['x', 'xn', 'xno']:
                print(info._Skip)
                return
            elif answer in ['xy', 'xyes']:
                break
            else:
                continue
        shutil.rmtree(info.location)
    info.create_dir()
    info.copy_conf()
    info.cleanup_exclusions()
    info.create_dotmatch()
    index.insert(user, dot.name, conf)
