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
import re
import shutil
from typing import Union

import DotManager.config as config
from DotManager.dotinfo import DotInfo, installed
from DotManager.index import index
from DotManager.tools import realpath


class SaveInfo:
    def __init__(self,
                 app: Union[DotInfo, str],
                 name: str,
                 user: str,
                 saveDir: Union[str, Path]):

        def __get_name() -> str:
            return app.name if isinstance(app, DotInfo) else app

        # DotInfo stuff
        if isinstance(app, DotInfo):
            self.include = app.include
            self.exclude = app.exclude

        # SaveInfo stuff
        self.userName = user
        self.dotName = __get_name()
        self.confName = name
        self.saveDir = saveDir

        # Save destination name and location
        self.baseName = Path(f"{user}-{__get_name()}-{name}")
        self.location = Path(saveDir).joinpath(self.baseName)

        # String builders for code readability
        self._FileExists = \
            f"{__get_name()} config '{name}' already exists for {user}."
        self._Skip = f"Skipping {user}'s {name} config for {__get_name()}."

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


def save(app: DotInfo,
         name: str = "default",
         user: str = config.userName,
         saveDir: Union[str, Path] = config.saveDir,
         force: bool = False):
    """ Save your config to `saveDir/userName-dot.name-confName`.
        Also create a corresponding entry in the index.
        """
    info = SaveInfo(app, name, user, saveDir)
    if index.query(app.name, name, user):
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
    index.insert(app.name, name, user)


# 1. Fetch set of installed apps
# 2. Ask which ones to save the confs of
# 3. "Would you like to set a custom name ?"
# 3b. "Select which apps"
# 4. "Would you like to set a custom user ?"
# 4b. "Select which apps"
# Loop 3 and 4 untill everything is set.
# 5. Batch save
def interactive(force: bool):
    """ Interactively prompt the user about what conf to save. """
    dots:    dict[str, DotInfo] = installed()
    apps:    list[str] = sorted(dots.keys(), key=str.lower, reverse=True)
    appsLen: int = len(apps)
    width:   int = len(str(appsLen))

    menu: str = "Installed apps:\n"
    for n, app in zip(range(appsLen, 0, -1), apps):
        menu += f"  {n:{width}}) {app}\n"
    menu += "Apps to exclude (e.g. ^3 4 5 6 7-10)\n"
    menu += "Invalid selections will be ignored.\n"
    menu += "==> "

    exclude = set()
    userInput: str = input(menu).lower()
    for match in re.finditer(r'|\^\d+|\d+-\d+|\d+', userInput):
        s = match[0]
        if not len(s):
            continue
        elif s.startswith('^'):
            exclude.update(range(int(s.lstrip('^'))+1))
        elif s.__contains__('-'):
            exclude.update(range(int(s.split('-')[0]),
                                 int(s.split('-')[1])))
        else:
            exclude.add(int(s))

    for x in exclude:
        if x < 1 or x > appsLen:
            continue
        del dots[apps[appsLen - x]]

    #TODO: Implement steps 3 through 4b.

    for dot in dots.values():
        save(dot, force=force)
