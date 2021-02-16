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

import dot
import tools
import config
import tarfile


class list:
    @staticmethod
    def supported():
        for dot in dot.supported():
            print(dot.name)

    @staticmethod
    def installed():
        for dot in dot.installed():
            print(dot.name)


class save:

    # Build the name string for a cache
    @staticmethod
    def cache_path(dot: dot, userName=config.userName, confName="default", cacheDir=config.cacheDir):
        return os.path.join(cacheDir, "dotmgr_" + userName + "-" + dot.name + "-" + confName)

    # Create a temporary directory containing a copy of the dotfiles for given dot
    @staticmethod
    def cache(dot: dot, userName=config.userName, confName="default", cacheDir=config.cacheDir, override=False):
        match = {}
        cache = save.cache_path(dot, userName, confName, cacheDir)
        if override is True and os.path.exists(cache):
            shutil.rmtree(cache)
        os.mkdir(cache)

        # For every file/dir, create a copy in the cache and add where to restore it in the matching dict
        for src in dot.include:
            dst = os.path.join(cache, os.path.basename(src))
            if os.path.isfile(tools.realpath(src)):
                shutil.copy2(tools.realpath(src), dst)
            else:
                shutil.copytree(tools.realpath(src), dst)
            match[os.path.basename(src)] = src

        # Clean up ignored files and directories
        for root, dirs, files in os.walk(cache):
            if dot.is_excluded(root):
                shutil.rmtree(root)
            for f in files:
                if dot.is_excluded(f):
                    os.remove(f)

        # Create a JSON matching file
        with open(os.path.join(cache, "_dotmatch.json"), mode='wt') as f:
            json.dump(match, f, sort_keys=True)

    # Insert a cache into the archive where every configuration is saved
    @staticmethod
    def pack(cachePath: str, tarPath: str = config.tarPath):
        cache = save.cache_path(dot, userName, confName, cacheDir)
        with tarfile.open(os.path.join(config.cacheDir, "dotmgr.tar.gz"), 'a:gz') as tar:
            pass
