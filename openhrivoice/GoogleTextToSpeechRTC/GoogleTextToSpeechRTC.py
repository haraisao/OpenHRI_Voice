#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Google Text to Speech component

Copyright (C) 2019
    Isao Hara
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.

Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt
'''

import sys, os, signal, platform
import time, struct, optparse

import json, base64
import urllib
import urllib.request, urllib.error, urllib.parse

from pydub import AudioSegment
from pydub.silence import *

import OpenRTM_aist
import RTC
from __init__ import __version__
import utils

__doc__ = 'Google Text-to-Speech component.'

_EffectsProfile=('wearable', 'handset', 'headphone', 'small-bluetooth-speaker', 'medium-bluetooth-speaker',
                  'large-home-entertainment', 'large-automotive', 'telephony')

#
#  
#
class GoogleTextToSpeechWrap(object):
    #
    #  Constructor
    #
    def __init__(self, rtc, language='ja-JP'):
        self._endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"
        self._lang = "ja-JP"
        self._speekingRate=1.0
        self._apikey = ""
        self._ssmlGender='NEUTRAL'
        self._voiceName='ja-JP-Standard-A'
        self._pitch=1.0
        self._volumeGain=0
        self._sampleRate=16000
        self._effectsProfileId=None

        prop = rtc._manager._config
        if prop.getProperty("google.tts.apikey") :
            keyfile = utils.getHriDir() + "/etc/" + prop.getProperty("google.tts.apikey")
            keyfile = keyfile.replace('/', os.path.sep)
            with open(keyfile) as f:
                self._apikey = f.readline().strip()

        if (not self._apikey) and prop.getProperty("google.speech.apikey") :
            keyfile = utils.getHriDir() + "/etc/" + prop.getProperty("google.speech.apikey")
            keyfile = keyfile.replace('/', os.path.sep)
            with open(keyfile) as f:
                self._apikey = f.readline().strip()

        if prop.getProperty("google.tts.lang") :
            self._lang=prop.getProperty("google.tts.lang")

        if prop.getProperty("google.tts.speekingRate") :
            self._speekingRate=prop.getProperty("google.tts.speekingRate")

        if prop.getProperty("google.tts.ssmlGender") :
            self._ssmlGender=prop.getProperty("google.tts.ssmlGender")

        if prop.getProperty("google.tts.voiceName") :
            self._voiceName=prop.getProperty("google.tts.voiceName")

        if prop.getProperty("google.tts.pitch") :
            self._pitch=prop.getProperty("google.tts.pitch")

        if prop.getProperty("google.tts.volumeGain") :
            self._volumeGain=prop.getProperty("google.tts.volumeGain")

        if prop.getProperty("google.tts.sampleRate") :
            self._sampleRate=prop.getProperty("google.tts.sampleRate")

        if prop.getProperty("google.tts.effectsProfileId") :
            self._effectsProfileId=prop.getProperty("google.tts.effectsProfileId")
    #
    #  Set ApiKey
    #
    def set_apikey(self, key):
        self._apikey = key

    #
    #
    def text2speech(self, text):
        url = self._endpoint+"?key="+self._apikey
        headers = {  'Content-Type' : 'application/json; charset=utf-8' }

        data = { "input": { "text" : text }, 
                 "voice" : {  'languageCode' : self._lang      # en-US, ja-JP, fr-FR
                             , 'name' : self._voiceName
                             , 'ssmlGender' : self._ssmlGender # MALE, FEMALE, NEUTRAL
                          },
                 'audioConfig': { 
                   'audioEncoding':'LINEAR16'              # LINEAR16, MP3, OGG_OPUS
                   , 'speakingRate' : self._speekingRate   # [0.25: 4.0]
                   , 'pitch' : self._pitch                 # [ -20.0: 20.0]
                   , 'volumeGainDb' : self._volumeGain 
                   , 'sampleRateHertz' : self._sampleRate  # default is 22050
                 }
          }

        if self._effectsProfileId in _EffectsProfile:
            if self._effectsProfileId == 'telephony':
                data['audioConfig']['effectsProfileId'] = 'telephony-class-application'
            else:
                data['audioConfig']['effectsProfileId'] = self._effectsProfileId + "-class-device"

        request = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)

        try:
            result = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print ('Error code:', e.code)
            print ('Reason:', e.reason)
            return ""
        except urllib.error.URLError as e:
            print ('URLError reason:', e.reason)
            return ""
        else:
            response = result.read()
            return response

#
#  GoogleSpeechRecogRTC 
#
GoogleTextToSpeechRTC_spec = ["implementation_id", "GoogleTextToSpeechRTC",
                  "type_name",         "GoogleTextToSpeechRTC",
                  "description",       __doc__,
                  "version",           __version__,
                  "vendor",            "AIST",
                  "category",          "communication",
                  "activity_type",     "DataFlowComponent",
                  "max_instance",      "1",
                  "language",          "Python",
                  "lang_type",         "script",

                  "conf.default.lang", "ja-JP",
                  "conf.__widget__.lang", "text",
                  "conf.__type__.lang", "string",

                  ""]
#
#  DataListener class
#
class DataListener(OpenRTM_aist.ConnectorDataListenerT):
    #
    #  Constructor
    #
    def __init__(self, name, obj, dtype):
        self._name = name
        self._obj = obj
        self._dtype = dtype
    
    #
    #  
    #
    def __call__(self, info, cdrdata):
        data = OpenRTM_aist.ConnectorDataListenerT.__call__(self, info, cdrdata, self._dtype(RTC.Time(0,0), ""))
        print(data, self._name)
        self._obj.onData(self._name, data)

#
#  GoogleTextToSpeechRTC Class
#
class GoogleTextToSpeechRTC(OpenRTM_aist.DataFlowComponentBase):
    #
    #  Constructor
    #
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        self._tts = None
        self._copyrights=[]
        self._lang = [ "ja-JP" ]


    #
    #  OnInitialize
    #
    def onInitialize(self):
        OpenRTM_aist.DataFlowComponentBase.onInitialize(self)
        self._logger = OpenRTM_aist.Manager.instance().getLogbuf(self._properties.getProperty("instance_name"))
        self._logger.RTC_INFO("GoogleTextToSpeechRTC version " + __version__)
        self._logger.RTC_INFO("Copyright (C) 2019 Isao Hara")
        #
        #
        self.bindParameter("lang", self._lang, "ja-JP")

        #
        # create inport for audio stream
        self._indata = RTC.TimedString(RTC.Time(0,0), "")
        self._inport = OpenRTM_aist.InPort("data", self._indata)
        self._inport.appendProperty('description', 'String to be convet to audio data.')
        self._inport.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE,
                                              DataListener("data", self, RTC.TimedString))
        self.registerInPort(self._inport._name, self._inport)

        #
        # create outport for result
        self._outdata = RTC.TimedOctetSeq(RTC.Time(0,0), None)
        self._outport = OpenRTM_aist.OutPort("result", self._outdata)
        self._outport.appendProperty('description', 'Result audio data of TTS.')
        self.registerOutPort(self._outport._name, self._outport)

        self._logger.RTC_INFO("This component depends on following softwares and data:")
        self._logger.RTC_INFO('')
        for c in self._copyrights:
            for l in c.strip('\n').split('\n'):
                self._logger.RTC_INFO('  '+l)
            self._logger.RTC_INFO('')

        return RTC.RTC_OK

    #
    #  OnFinalize
    #
    def onFinalize(self):
        #if self._tts:
        #    self._tts.terminate()
        OpenRTM_aist.DataFlowComponentBase.onFinalize(self)
        return RTC.RTC_OK

    #
    #  OnActivate
    #
    def onActivated(self, ec_id):
        self._tts = GoogleTextToSpeechWrap(self, self._lang[0])

        OpenRTM_aist.DataFlowComponentBase.onActivated(self, ec_id)

        if self._tts._apikey:
            return RTC.RTC_OK
        else:
            print("=== No API KEY ===")
            return RTC.RTC_ERROR

    #
    #  OnDeactivate
    #
    def onDeactivate(self, ec_id):
        #self._recog.terminate()
        OpenRTM_aist.DataFlowComponentBase.onDeactivate(self, ec_id)
        return RTC.RTC_OK

    #
    #  OnData (Callback from DataListener)
    #
    def onData(self, name, data):
        if self._tts:
            if name == "data":
                txt=data.data.encode('raw-unicode-escape').decode()
                response = self._tts.text2speech(txt)
                
                if response :
                    result=json.loads(response.decode())
                    audio = base64.b64decode(result['audioContent'].encode())

                    if len(audio) > 44:
                        self._outdata.data = audio[44:]
                        self._outport.write(self._outdata)


    #
    #  OnExecute (Do nothing)
    #
    def onExecute(self, ec_id):
        OpenRTM_aist.DataFlowComponentBase.onExecute(self, ec_id)
        return RTC.RTC_OK

#
#  Manager Class
#
class GoogleTextToSpeechManager:
    #
    #  Constructor
    #
    def __init__(self):

        parser = utils.MyParser(version=__version__, description=__doc__)
        utils.addmanageropts(parser)

        try:
            opts, args = parser.parse_args()
        except optparse.OptionError as e:
            print( 'OptionError:', e, file=sys.stderr)
            sys.exit(1)

        if opts.configfile is None:
            try:
                cfgname = os.environ['OPENHRI_ROOT'] + "/etc/google_speech.conf".replace('/', os.path.sep)
                if os.path.exists(cfgname):
                    opts.configfile = cfgname
            except:
                pass

        self._comp = None
        self._manager = OpenRTM_aist.Manager.init(utils.genmanagerargs(opts))
        self._manager.setModuleInitProc(self.moduleInit)
        self._manager.activateManager()

    #
    #  Start component
    #
    def start(self):
        self._manager.runManager(False)

    def shutdown(self):
        self._manager.shutdown()

    #
    #  Initialize rtc
    #
    def moduleInit(self, manager):
        profile = OpenRTM_aist.Properties(defaults_str = GoogleTextToSpeechRTC_spec)
        manager.registerFactory(profile, GoogleTextToSpeechRTC, OpenRTM_aist.Delete)

        self._comp = manager.createComponent("GoogleTextToSpeechRTC?exec_cxt.periodic.rate=1")

#
#
g_manager = None

#
# 
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
    g_manager = GoogleTextToSpeechManager()
    g_manager.start()


#
#  Main
#
if __name__=='__main__':
    main()
