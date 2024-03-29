#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Google Speech Recognition component

Copyright (C) 2017
    Isao Hara
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.

Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt
'''

import sys, os, signal, platform
import time, struct, traceback, tempfile, optparse

import json
import urllib
import urllib.request, urllib.error, urllib.parse

from pydub import AudioSegment
from pydub.silence import *

from xml.dom.minidom import Document

import OpenRTM_aist
import RTC
from __init__ import __version__
import utils

from CloudSpeechRecogBase import CloudSpeechRecogBase

__doc__ = 'Google Speech Recognition component.'

#
#  
#
class GoogleSpeechRecogWrap(CloudSpeechRecogBase):
    
    #
    #  Constructor
    #
    def __init__(self, rtc, language='ja-JP'):
        CloudSpeechRecogBase.__init__(self, language)

        self._endpoint = 'http://www.google.com/speech-api/v2/recognize'

        prop = rtc._manager._config
        if prop.getProperty("google.speech.apikey") :
            keyfile = utils.getHriDir() + "/etc/" + prop.getProperty("google.speech.apikey")
            keyfile = keyfile.replace('/', os.path.sep)
            with open(keyfile) as f:
                self._apikey = f.readline().strip()

        if prop.getProperty("google.speech.lang") :
            self._lang=prop.getProperty("google.speech.lang")

        if prop.getProperty("google.speech.logdir") :
            self._logdir=prop.getProperty("google.speech.logdir")

        if prop.getProperty("google.speech.save_wav") :
            if prop.getProperty("google.speech.save_wav") == 'YES':
                self._logger = True


    #
    #  Set ApiKey
    #
    def set_apikey(self, key):
        self._apikey = key


    #
    #  Request Google Voice Recognition
    #
    def request_speech_recog(self, data):
        query_string = {'output': 'json', 'lang': self._lang, 'key': self._apikey}
        url = '{0}?{1}'.format(self._endpoint, urllib.parse.urlencode(query_string)) 

        headers = {'Content-Type': 'audio/l16; rate=16000'}

        voice_data = bytearray(data)

        try:
            request = urllib.request.Request(url, data=voice_data, headers=headers)
            result = urllib.request.urlopen(request)
            response = result.read()
            return response.decode('utf-8').split()
        except:
            print (url)
            print (traceback.format_exc())
            return ["Error"]


#
#  GoogleSpeechRecogRTC 
#
GoogleSpeechRecogRTC_spec = ["implementation_id", "GoogleSpeechRecogRTC",
                  "type_name",         "GoogleSpeechRecogRTC",
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

                  "conf.default.min_buflen", "8000",
                  "conf.__widget__.min_buflen", "text",
                  "conf.__type__.min_buflen", "int",

                  "conf.default.min_silence", "200",
                  "conf.__widget__.min_silence", "text",
                  "conf.__type__.min_silence", "int",

                  "conf.default.silence_thr", "-20",
                  "conf.__widget__.silence_thr", "text",
                  "conf.__type__.silence_thr", "int",

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
        data = OpenRTM_aist.ConnectorDataListenerT.__call__(self, info, cdrdata, self._dtype(RTC.Time(0,0),None))
        self._obj.onData(self._name, data)
        return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, data
#
#  GoogleSpeechRecogRTC Class
#
class GoogleSpeechRecogRTC(OpenRTM_aist.DataFlowComponentBase):
    #
    #  Constructor
    #
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        self._recog = None
        self._copyrights=[]
        self._lang = [ "ja-JP" ]
        self._min_silence = [ 200 ]
        self._silence_thr = [ -20 ]
        self._min_buflen =  [ 8000 ]


    #
    #  OnInitialize
    #
    def onInitialize(self):
        OpenRTM_aist.DataFlowComponentBase.onInitialize(self)
        self._logger = OpenRTM_aist.Manager.instance().getLogbuf(self._properties.getProperty("instance_name"))
        self._logger.RTC_INFO("GoogleSpeechRecogRTC version " + __version__)
        self._logger.RTC_INFO("Copyright (C) 2017 Isao Hara")
        #
        #
        self.bindParameter("lang", self._lang, "ja-JP")
        self.bindParameter("min_silence", self._min_silence, "200")
        self.bindParameter("silence_thr", self._silence_thr, "-20")
        self.bindParameter("min_buflen", self._min_buflen, "8000")
        #
        # create inport for audio stream
        self._indata = RTC.TimedOctetSeq(RTC.Time(0,0), None)
        self._inport = OpenRTM_aist.InPort("data", self._indata)
        self._inport.appendProperty('description', 'Audio data (in packets) to be recognized.')
        self._inport.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE,
                                              DataListener("data", self, RTC.TimedOctetSeq))
        self.registerInPort(self._inport._name, self._inport)

        #
        # create outport for result
        self._outdata = RTC.TimedString(RTC.Time(0,0), "")
        self._outport = OpenRTM_aist.OutPort("result", self._outdata)
        self._outport.appendProperty('description', 'Recognition result in XML format.')
        self.registerOutPort(self._outport._name, self._outport)

        self._logger.RTC_INFO("This component depends on following softwares and datas:")
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
        if self._recog:
            self._recog.terminate()
        OpenRTM_aist.DataFlowComponentBase.onFinalize(self)
        return RTC.RTC_OK

    #
    #  OnActivate
    #
    def onActivated(self, ec_id):
        self._recog = GoogleSpeechRecogWrap(self, self._lang[0])
        self._recog.setcallback(self.onResult)

        OpenRTM_aist.DataFlowComponentBase.onActivated(self, ec_id)
        #self._recog.set_lang(self._lang[0])
        self._recog.set_voice_detect_param(int(self._min_silence[0]),  int(self._silence_thr[0]), int(self._min_buflen[0]))

        if self._recog._apikey:
            self._recog.start()
            return RTC.RTC_OK
        else:
            return RTC.RTC_ERROR

    #
    #  OnDeactivate
    #
    def onDeactivate(self, ec_id):
        self._recog.terminate()
        OpenRTM_aist.DataFlowComponentBase.onDeactivate(self, ec_id)
        return RTC.RTC_OK

    #
    #  OnData (Callback from DataListener)
    #
    def onData(self, name, data):
        if self._recog:
            if name == "data":
                self._recog.write(data.data)


    #
    #  OnExecute (Do nothing)
    #
    def onExecute(self, ec_id):
        OpenRTM_aist.DataFlowComponentBase.onExecute(self, ec_id)
        return RTC.RTC_OK

    #
    #  OnResult
    #
    def onResult(self, data):
        doc = Document()
        listentext = doc.createElement("listenText")
        doc.appendChild(listentext)

        if len(data) <= 1:
            listentext.setAttribute("state","RecognitionFailed")
        else:
            try:
                data.pop(0)
                res = ''.join(data)
                #print res;
                result=json.loads(res)
                i=0
                for r in result['result'][0]['alternative']:
                    i += 1
                    rank = str(i)
                    if 'confidence' in r :
                        score=str(r['confidence'])
                    else:
                        score=0.0
                    text=r['transcript']
                    hypo = doc.createElement("data")
                    hypo.setAttribute("rank", rank)
                    hypo.setAttribute("score", score)
                    hypo.setAttribute("likelihood", score)
                    hypo.setAttribute("text", text)
                    self._logger.RTC_INFO("#%s: %s (%s)" % (rank, text, score))
                    listentext.appendChild(hypo)

                listentext.setAttribute("state","Success")

            except:
                print (traceback.format_exc())
                listentext.setAttribute("state","ParseError")

        res_data = doc.toxml(encoding="utf-8")
        print(res_data)
        self._outdata.data = res_data.decode('unicode_escape')
        self._outport.write()

#
#  Manager Class
#
class GoogleSpeechRecogManager:
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
        profile = OpenRTM_aist.Properties(defaults_str = GoogleSpeechRecogRTC_spec)
        manager.registerFactory(profile, GoogleSpeechRecogRTC, OpenRTM_aist.Delete)

        self._comp = manager.createComponent("GoogleSpeechRecogRTC?exec_cxt.periodic.rate=1")

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
    g_manager = GoogleSpeechRecogManager()
    g_manager.start()


#
#  Main
#
if __name__=='__main__':
    main()
