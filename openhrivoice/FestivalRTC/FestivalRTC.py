#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Festival speech synthesis component

Copyright (C) 2010
    Yosuke Matsusaka
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt
'''

import os
import sys
import time
import subprocess
import signal
import tempfile
import traceback
import platform
import wave
import optparse
import re

import OpenRTM_aist
import RTC

from __init__ import __version__
import utils
from config import config
from VoiceSynthComponentBase import *

#
#  Read file
#
def read_file_contents(fname, encoding='utf-8'):
  try:
    f=open(fname,'r', encoding=encoding)
    contents = f.read()
    f.close()
    return contents
  except:
    return ""


__doc__ = 'English speech synthesis component.'

#
#  Festival Wrapper class
#
class FestivalWrap(VoiceSynthBase):
    #
    # Constructor
    def __init__(self, prop):
        VoiceSynthBase.__init__(self)
        self._config = config()

        self._basedir = utils.getHriDir()

        if prop.getProperty("festival.top_dir") :
            top_dir = prop.getProperty("festival.top_dir")
            top_dir = re.sub('^%d0', self._basedir[:2], top_dir)
            self._config.festival_top(top_dir.replace('/', os.path.sep))

        self._cmdline =[self._config._festival_bin, '--pipe']
        self._cmdline.extend(self._config._festival_opt)
        self._copyrights = []
        self._copyrights.append(read_file_contents('festival_copyright.txt'))
        self._copyrights.append(read_file_contents('diphone_copyright.txt'))

    #
    #  Syntheseizer 
    def synthreal(self, data, samplerate, character):
        textfile = self.gettempname()
        durfile = self.gettempname().replace("\\", "\\\\")
        wavfile = self.gettempname().replace("\\", "\\\\")
        # text file which specifies synthesized string
        fp = open(textfile, 'w', encoding='utf-8')
        fp.write('(set! u (Utterance Text "' + data + '"))')
        fp.write('(utt.synth u)')
        fp.write('(utt.save.segs u "' + durfile + '")')
        fp.write('(utt.save.wave u "' + wavfile + '")')
        fp.close()

        # run Festival
        cmdarg =[self._config._festival_bin,] + self._config._festival_opt + ['-b', textfile]
        #print(cmdarg)
        p = subprocess.Popen(cmdarg)
        p.wait()
        #p = subprocess.Popen(self._cmdline, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        #p.stdin.write('(set! u (Utterance Text "' + data + '"))')
        #p.stdin.write('(utt.synth u)')
        #p.stdin.write('(utt.save.segs u "' + durfile + '")')
        #p.stdin.write('(utt.save.wave u "' + wavfile + '")')
        #p.communicate()

        # read data
        df = open(durfile, 'r')
        durationdata = df.read()
        df.close()
        os.remove(durfile)
        return (durationdata, wavfile)


#
#  RT-Component
#
FestivalRTC_spec = ["implementation_id", "FestivalRTC",
                    "type_name",         "FestivalRTC",
                    "description",       __doc__,
                    "version",           __version__,
                    "vendor",            "AIST",
                    "category",          "communication",
                    "activity_type",     "DataFlowComponent",
                    "max_instance",      "5",
                    "language",          "Python",
                    "lang_type",         "script",
                    "conf.default.format", "int16",
                    "conf.__widget__.format", "radio",
                    "conf.__constraints__.format", "int16",
                    "conf.__description__.format", "Format of output audio (fixed to 16bit).",
                    "conf.default.rate", "16000",
                    "conf.__widget__.rate", "spin",
                    "conf.__constraints__.rate", "x == 16000",
                    "conf.__description__.rate", "Sampling frequency of output audio (fixed to 16kHz).",
                    "conf.default.character", "male",
                    "conf.__widget__.character", "radio",
                    "conf.__constraints__.character", "(male)",
                    "conf.__description__.character", "Character of the voice (fixed to male).",
                    ""]

#
#  FestivalRTC class
#
class FestivalRTC(VoiceSynthComponentBase):
    #
    # Constructor
    def __init__(self, manager):
        VoiceSynthComponentBase.__init__(self, manager)

    #
    #  OnInitialize
    def onInitialize(self):
        VoiceSynthComponentBase.onInitialize(self)

        try:
            self._wrap = FestivalWrap(self._manager._config)
        except:
            self._logger.RTC_ERROR(traceback.format_exc())
            return RTC.RTC_ERROR
        self._logger.RTC_INFO("This component depends on following softwares and datas:")
        self._logger.RTC_INFO('')
        for c in self._wrap._copyrights:
            for l in c.strip('\n').split('\n'):
                self._logger.RTC_INFO('  '+l)
            self._logger.RTC_INFO('')
        return RTC.RTC_OK

#
#   RTC Manager
#
class FestivalRTCManager:
    #
    #
    def __init__(self):
        parser = utils.MyParser(version=__version__, description=__doc__)
        utils.addmanageropts(parser)
        try:
            opts, args = parser.parse_args()
        except optparse.OptionError as e:
            print('OptionError:', e, file=sys.stder)
            sys.exit(1)

        if opts.configfile is None:
            try:
                cfgname = os.environ['OPENHRI_ROOT'] + "/etc/festival.conf".replace('/', os.path.sep)
                if os.path.exists(cfgname):
                    opts.configfile = cfgname
            except:
                pass

        self._comp = None
        self._manager = OpenRTM_aist.Manager.init(utils.genmanagerargs(opts))
        self._manager.setModuleInitProc(self.moduleInit)
        self._manager.activateManager()

    #
    #
    def start(self):
        self._manager.runManager(False)

    #
    #
    def shutdown(self):
        self._manager.shutdown()
        
    #
    #
    def moduleInit(self, manager):
        profile=OpenRTM_aist.Properties(defaults_str=FestivalRTC_spec)
        manager.registerFactory(profile, FestivalRTC, OpenRTM_aist.Delete)
        self._comp = manager.createComponent("FestivalRTC")

#
#
g_manager = None

def sig_handler(num, frame):
    global g_manager
    if g_manager:
        g_manager.shutdown()
#
#
#
def main():
    global g_manager
    signal.signal(signal.SIGINT, sig_handler)
    g_manager = FestivalRTCManager()
    g_manager.start()

if __name__=='__main__':
    main()
