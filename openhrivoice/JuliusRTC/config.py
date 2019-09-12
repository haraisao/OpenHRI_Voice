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
import utils
import re

import configparser

class config():
    def __init__(self, julius_dir=""):
        self._platform = platform.system()

        if self._platform != "Windows":
            my_platform_list =  platform.platform().split("-")
            self.ubuntu_osname = my_platform_list[len(my_platform_list)-1]

        if hasattr(sys, "frozen"):
            self._basedir = os.path.dirname(sys.executable)
        else:
            self._basedir = utils.getHriDir()

        self._homedir = os.path.expanduser('~')

        self._configdir = os.path.join(self._homedir, '.openhri')
        if os.path.exists(self._configdir) == False:
            os.makedirs(self._configdir)

        self._lexicondb = os.path.join(self._configdir, 'lexcon.db')

        #
        # default settings
        if julius_dir :
            julius_dir = re.sub('^%d0', self._basedir[:2], julius_dir)
            self.julius(julius_dir.replace('/', os.path.sep) )
        else:
            self.julius(os.path.join(self._basedir, "Julius") )

        # config
        if os.path.exists(os.path.join(self._basedir, 'etc', 'julius.cfg')) :
            self._configfile = configparser.ConfigParser()
            self._configfile.read(os.path.join(self._basedir, 'etc', 'julius.cfg'))

            self.set_runkit_ja(self._configfile, self._basedir[:2])
            self.set_runkit_en(self._configfile, self._basedir[:2])
            self.set_voxforge_en(self._configfile, self._basedir[:2])
            self.set_voxforge_de(self._configfile, self._basedir[:2])

    #
    #  For Julius
    #
    def julius(self, basedir):
        if self._platform == "Windows":
            self._julius_runkitdir = os.path.join(basedir, "dictation-kit")
            self._julius_bin = os.path.join(self._julius_runkitdir, "bin", "windows", "julius.exe")
            
            self._julius_voxforgedir = os.path.join(basedir, "voxforge_en")
            self._julius_hmm_en = os.path.join(self._julius_voxforgedir, "hmmdefs")
            self._julius_hlist_en = os.path.join(self._julius_voxforgedir, "tiedlist")

            self._julius_voxforgedir_de = os.path.join(basedir, "voxforge_de")
            self._julius_hmm_de = os.path.join(self._julius_voxforgedir_de, "hmmdefs")
            self._julius_hlist_de = os.path.join(self._julius_voxforgedir_de, "tiedlist")

            self._julius_runkitdir_en = os.path.join(basedir, "ENVR-v5.4.Gmm.Bin")
            self._julius_bin_en = os.path.join(self._julius_runkitdir_en, "julius-gmm.exe")
            self._julius_dict_hmm_en   = os.path.join(self._julius_runkitdir_en, "ENVR-v5.3.am")
            self._julius_dict_hlist_en = os.path.join(self._julius_runkitdir_en, "ENVR-v5.3.phn")
            self._julius_dict_ngram_en = os.path.join(self._julius_runkitdir_en, "ENVR-v5.3.lm")
            self._julius_dict_dict_en  = os.path.join(self._julius_runkitdir_en, "ENVR-v5.3.dct")
            self._julius_dict_htkconf_en  = os.path.join(self._julius_runkitdir_en, "wav_config")

        else:
            self._julius_runkitdir = "/usr/share/julius-runkit"
            if self.ubuntu_osname == "precise":
                self._julius_dict_en = "/usr/share/doc/julius-voxforge/dict.gz"
            else:
                self._julius_dict_en = "/usr/share/julius-voxforge/acoustic/dict"

            self._julius_voxforgedir = "/usr/share/julius-voxforge"
            self._julius_voxforgedir_de = "/usr/share/julius-voxforge-de"
            self._julius_bin = "/usr/share/julius-runkit/bin/linux/julius"

            self._julius_hmm_en = os.path.join(self._julius_voxforgedir, "acoustic", "hmmdefs")
            self._julius_hlist_en = os.path.join(self._julius_voxforgedir, "acoustic", "tiedlist")
            self._julius_hmm_de = os.path.join(self._julius_voxforgedir_de, "acoustic", "hmmdefs")
            self._julius_hlist_de = os.path.join(self._julius_voxforgedir_de, "acoustic", "tiedlist")

        self._julius_hmm_ja   = os.path.join(self._julius_runkitdir, "model", "phone_m", "jnas-tri-3k16-gid.binhmm")
        self._julius_hlist_ja = os.path.join(self._julius_runkitdir, "model", "phone_m", "logicalTri-3k16-gid.bin")
        self._julius_ngram_ja = os.path.join(self._julius_runkitdir, "model", "lang_m", "bccwj.60k.bingram")
        self._julius_dict_ja  = os.path.join(self._julius_runkitdir, "model", "lang_m", "bccwj.60k.htkdic")
        #self._julius_dict_ja  = os.path.join(self._julius_runkitdir, "model", "lang_m", "web.60k.htkdic")
        #
        # for dictation
        self._julius_bingram_ja= os.path.join(self._julius_runkitdir, "model", "lang_m", "bccwj.60k.bingram")
        self._julius_htkdic_ja = os.path.join(self._julius_runkitdir, "model", "lang_m", "bccwj.60k.htkdic")

    def set_runkit_ja(self, configfile, drv=""):
        if 'julius.runkit_ja' in configfile :
            try:
                runkit_ja = configfile['julius.runkit_ja']
                self._julius_runkitdir = runkit_ja['base_dir'].replace('/', os.path.sep)
                if drv :
                    self._julius_runkitdir = re.sub('^\$d0', drv, self._julius_runkitdir)
                self._julius_bin = os.path.join(self._julius_runkitdir, runkit_ja['executable'].replace('/', os.path.sep))
                self._julius_hmm_ja   = os.path.join(self._julius_runkitdir, runkit_ja['hmm'].replace('/', os.path.sep))
                self._julius_hlist_ja = os.path.join(self._julius_runkitdir, runkit_ja['hlist'].replace('/', os.path.sep))
                self._julius_ngram_ja = os.path.join(self._julius_runkitdir, runkit_ja['ngram'].replace('/', os.path.sep))
                self._julius_dict_ja  = os.path.join(self._julius_runkitdir, runkit_ja['dict'].replace('/', os.path.sep))
                #
                # for dictation
                self._julius_bingram_ja = os.path.join(self._julius_runkitdir, runkit_ja['bingram'].replace('/', os.path.sep))
                self._julius_htkdic_ja = os.path.join(self._julius_runkitdir, runkit_ja['htkdic'].replace('/', os.path.sep))
            except:
                print("=== Error in set_runkit_ja")

    def set_voxforge_en(self, configfile, drv=""):
        if 'julius.voxforge' in configfile :
            try:
                voxforge = configfile['julius.voxforge']
                self._julius_voxforgedir = voxforge['base_dir'].replace('/', os.path.sep)
                if drv :
                    self._julius_voxforgedir = re.sub('^\$d0', drv, self._julius_voxforgedir)
                self._julius_hmm_en = os.path.join(self._julius_voxforgedir, voxforge['hmm'].replace('/', os.path.sep))
                self._julius_hlist_en = os.path.join(self._julius_voxforgedir, voxforge['hlist'].replace('/', os.path.sep))
            except:
                print("=== Error in set_voxforge_en")

    def set_voxforge_de(self, configfile, drv=""):
        if 'julius.voxforge_de' in configfile :
            try:
                voxforge_de = configfile['julius.voxforge_de']
                self._julius_voxforgedir_de = voxforge_de['base_dir'].replace('/', os.path.sep)
                if drv :
                    self._julius_voxforgedir_de = re.sub('^\$d0', drv, self._julius_voxforgedir_de)
                self._julius_hmm_de = os.path.join(self._julius_voxforgedir_de, voxforge_de['hmm'].replace('/', os.path.sep))
                self._julius_hlist_de = os.path.join(self._julius_voxforgedir_de, voxforge_de['hlist'].replace('/', os.path.sep))
            except:
                print("=== Error in set_voxforge_de")

    def set_runkit_en(self, configfile, drv=""):
        if 'julius.runkit_en' in configfile :
            try:
                runkit_en = configfile['julius.runkit_en']
                self._julius_runkitdir_en = runkit_en['base_dir'].replace('/', os.path.sep)
                if drv :
                    self._julius_runkitdir_en = re.sub('^\$d0', drv, self._julius_runkitdir_en)
                self._julius_bin_en = os.path.join(self._julius_runkitdir_en, runkit_en['executable'].replace('/', os.path.sep))
                self._julius_dict_hmm_en   = os.path.join(self._julius_runkitdir_en, runkit_en['hmm'].replace('/', os.path.sep))
                self._julius_dict_hlist_en = os.path.join(self._julius_runkitdir_en, runkit_en['hlist'].replace('/', os.path.sep))
                self._julius_dict_ngram_en = os.path.join(self._julius_runkitdir_en, runkit_en['ngram'].replace('/', os.path.sep))
                self._julius_dict_dict_en  = os.path.join(self._julius_runkitdir_en, runkit_en['dict'].replace('/', os.path.sep))
                self._julius_dict_htkconf_en  = os.path.join(self._julius_runkitdir_en, runkit_en['htkconf'].replace('/', os.path.sep))
            except:
                print("=== Error in set_runkit_en")
