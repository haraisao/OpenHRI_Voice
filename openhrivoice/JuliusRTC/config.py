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
            if 'OpenHRI_ROOT' in os.environ:
                self._basedir = os.environ['OpenHRI_ROOT']
            else:
                self._basedir = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"\\..")

        self._homedir = os.path.expanduser('~')

        self._configdir = os.path.join(self._homedir, '.openhri')
        if os.path.exists(self._configdir) == False:
            os.makedirs(self._configdir)

        self._lexicondb = os.path.join(self._configdir, 'lexcon.db')

        #
        # default settings
        self.julius(os.path.join(self._basedir, "3rdparty") )

        # config
        self._configfile = configparser.ConfigParser()
        if os.path.exists(os.path.join(self._basedir, 'julius.cfg')) :
            self._configfile.read(os.path.join(self._basedir, 'julius.cfg'))

        self.set_runkit_ja(self._configfile)
        self.set_runkit_en(self._configfile)
        self.set_voxforge_en(self._configfile)
        self.set_voxforge_de(self._configfile)

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

    def set_runkit_ja(self, configfile):
        if 'julius.runkit_ja' in configfile :
            try:
                self._julius_runkitdir = configfile['julius.runkit_ja']['base_dir'].replace('/', os.path.sep)
                self._julius_bin = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['executable'].replace('/', os.path.sep))
                self._julius_hmm_ja   = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['hmm'].replace('/', os.path.sep))
                self._julius_hlist_ja = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['hlist'].replace('/', os.path.sep))
                self._julius_ngram_ja = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['ngram'].replace('/', os.path.sep))
                self._julius_dict_ja  = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['dict'].replace('/', os.path.sep))
                #
                # for dictation
                self._julius_bingram_ja = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['bingram'].replace('/', os.path.sep))
                self._julius_htkdic_ja = os.path.join(self._julius_runkitdir, configfile['julius.runkit_ja']['htkdic'].replace('/', os.path.sep))
            except:
                print("=== Error in set_runkit_ja")

    def set_voxforge_en(self, configfile):
        if 'julius.voxforge' in configfile :
            try:
                self._julius_voxforgedir = configfile['julius.voxforge']['base_dir']
                self._julius_hmm_en = os.path.join(self._julius_voxforgedir, configfile['julius.voxforge']['hmm'].replace('/', os.path.sep))
                self._julius_hlist_en = os.path.join(self._julius_voxforgedir, configfile['julius.voxforge']['hlist'].replace('/', os.path.sep))
            except:
                print("=== Error in set_voxforge_en")

    def set_voxforge_de(self, configfile):
        if 'julius.voxforge_de' in configfile :
            try:
                self._julius_voxforgedir_de = configfile['julius.voxforge_de']['base_dir']
                self._julius_hmm_de = os.path.join(self._julius_voxforgedir_de, configfile['julius.voxforge_de']['hmm'].replace('/', os.path.sep))
                self._julius_hlist_de = os.path.join(self._julius_voxforgedir_de, configfile['julius.voxforge_de']['hlist'].replace('/', os.path.sep))
            except:
                print("=== Error in set_voxforge_de")

    def set_runkit_en(self, configfile):
        if 'julius.runkit_en' in configfile :
            try:
                self._julius_runkitdir_en = configfile['julius.runkit_en']['base_dir'].replace('/', os.path.sep)
                self._julius_bin_en = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['executable'].replace('/', os.path.sep))
                self._julius_dict_hmm_en   = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['hmm'].replace('/', os.path.sep))
                self._julius_dict_hlist_en = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['hlist'].replace('/', os.path.sep))
                self._julius_dict_ngram_en = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['ngram'].replace('/', os.path.sep))
                self._julius_dict_dict_en  = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['dict'].replace('/', os.path.sep))
                self._julius_dict_htkconf_en  = os.path.join(self._julius_runkitdir_en, configfile['julius.runkit_en']['htkconf'].replace('/', os.path.sep))
            except:
                print("=== Error in set_runkit_en")
