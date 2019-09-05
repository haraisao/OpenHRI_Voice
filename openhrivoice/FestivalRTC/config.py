#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''configuration manager for OpenHRIVoice

Copyright (C) 2010
    Yosuke Matsusaka
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.

Copyright (C) 2019
    Isao Hara
    National Institute of Advanced Industrial Science and Technology (AIST), Japan
    All rights reserved.

Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt
'''

import sys
import os
import platform
import traceback

import configparser

class config():
    def __init__(self):
        self._platform = platform.system()

        if self._platform != "Windows":
            my_platform_list =  platform.platform().split("-")
            self.ubuntu_osname = my_platform_list[len(my_platform_list)-1]

        if hasattr(sys, "frozen"):
            self._basedir = os.path.dirname(sys.executable)
        else:
            #self._basedir = os.path.dirname(__file__)
            if 'OpenHRI_ROOT' in os.environ:
                self._basedir = os.environ['OpenHRI_ROOT']
            else:
                self._basedir = os.getcwd()

        self._homedir = os.path.expanduser('~')

        self._configdir = os.path.join(self._homedir, '.openhri')
        if os.path.exists(self._configdir) == False:
            os.makedirs(self._configdir)

        self.festival(os.path.join(self._basedir, "3rdparty") )

        # config
        self._configfile = configparser.ConfigParser()
        if os.path.exists(os.path.join(self._basedir, 'festival.cfg')) :
            self._configfile.read(os.path.join(self._basedir, 'fastival.cfg'))


    #
    #  For Festival
    #
    def festival(self, basedir):
        if self._platform == "Windows":
            self._festivaldir = os.path.join(basedir, "festival-2.4")

            self._festival_bin = os.path.join(self._festivaldir, "festival.exe")
            self._festival_opt = ["--libdir", os.path.join(self._festivaldir, "lib")]
        else:
            self._festival_bin = "festival"
            self._festival_opt = []

    def festival_top(self, topdir):
        if self._platform == "Windows":
            self._festivaldir = topdir
            self._festival_bin = os.path.join(self._festivaldir, "festival.exe")
            self._festival_opt = ["--libdir", os.path.join(self._festivaldir, "lib")]
        else:
            self._festival_bin = "festival"
            self._festival_opt = []

    #
    #  For SOX
    #
    def sox(self, basedir):
        if self._platform == "Windows":
            self._soxdir = os.path.join(basedir, "sox-14.4.2")
            self._sox_bin = os.path.join(self._soxdir, "sox.exe")
        else:
            self._sox_bin = "sox"

    #
    #  For SOX
    #
    def sox_top(self, topdir):
        if self._platform == "Windows":
            self._soxdir = topdir
            self._sox_bin = os.path.join(self._soxdir, "sox.exe")
        else:
            self._sox_bin = "sox"
