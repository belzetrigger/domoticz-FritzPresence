# this is our helper class to do the work with FritzConnection

import urllib
import time as myTime
from time import mktime
from datetime import datetime, timedelta
import sys
sys.path
# sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append(
    '/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')

try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz

try:
    import fritzconnection as fc
except SystemError as e:
    Domoticz.Error("could not load fritzconnection ...{}".format(e))

try:
    import lxml
except SystemError as e:
    Domoticz.Error("could not load lxml ...{}".format(e))


class FritzHelper:

    def __init__(self, fbHost: str, fbUser: str,
                 fbPassword: str, macAddress: str, defaultName: str = None,
                 cooldownperiod: int = 30):
        self.fbHost = fbHost
        self.fbUser = fbUser
        self.fbPassword = fbPassword
        self.macAddress = macAddress
        self.defaultName = defaultName
        self.cooldownperiod = cooldownperiod
        self.debug = False
        self.lastUpdate = None
        self.nextpoll = datetime.now()
        self.reset()

    def dumpConfig(self):
        Domoticz.Debug(
            "fritz:{}\t"
            "mac:{}\t"
            "name: {}".format(self.fbHost, self.macAddress, self.defaultName)
        )

    def needUpdate(self):
        '''does some of the devices need an update

        Returns:
            boolean -- if True -> please update the device in domoticz
        '''
        return self.needUpdate

    def reset(self):
        self.stopped = False
        self.fcHosts = None
        self.deviceName = None
        self.deviceIp = None
        self.deviceLastIp = None
        self.deviceIsConnected = None
        self.deviceLastIsConnected = None
        self.resetError()

    def connect(self):
        Domoticz.Debug("Try to get FritzfbHost Connection")

        # import lxml  # does not fail if lxml has been partially installed
        # from lxml import etree  # fails if C extension part of lxml has not been installed

        # try:
        #     from lxml import etree
        #     Domoticz.Log("running with lxml.etree")
        # except ImportError:
        #     try:
        #         # Python 2.5
        #         import xml.etree.cElementTree as etree
        #         Domoticz.Log("running with cElementTree on Python 2.5+")
        #     except ImportError:
        #         try:
        #             # Python 2.5
        #             import xml.etree.ElementTree as etree
        #             Domoticz.Log("running with ElementTree on Python 2.5+")
        #         except ImportError:
        #             try:
        #                 # normal cElementTree install
        #                 import cElementTree as etree
        #                 Domoticz.Log("running with cElementTree")
        #             except ImportError:
        #                 try:
        #                     # normal ElementTree install
        #                     import elementtree.ElementTree as etree
        #                     Domoticz.Log("running with ElementTree")
        #                 except ImportError:
        #                     Domoticz.Log("Failed to import ElementTree from any known place")

        # import fritzconnection as fc
        self.fcHosts = fc.FritzHosts(
            address=self.fbHost,
            user=self.fbUser,
            password=self.fbPassword
        )
        Domoticz.Debug("status: {}".format(self.fcHosts))

        return self.fcHosts

    def setMyError(self, error):
        self.hasError = True
        self.errorMsg = error

    def resetError(self):
        self.hasError = False
        self.errorMsg = None

    def verifyUpdate(self):
        if(self.deviceLastIsConnected != self.deviceIsConnected or
           self.deviceLastIp != self.deviceIp):
            self.needUpdate = True
        else:
            self.needUpdate = False
        # copy values to compare later
        self.deviceLastIsConnected = self.deviceIsConnected
        self.deviceLastIp = self.deviceIp
        Domoticz.Debug("updated needed?: {}".format(self.needUpdate))

    def readStatus(self):
        Domoticz.Debug("read status for {}".format(self.fbHost))
        try:
            if(self.fcHosts is None):
                self.connect()
            fh = self.fcHosts
            isPresent = False
            name = None
            ip = None
            result = fh.get_specific_host_entry(self.macAddress)
            if result is not None:
                Domoticz.Debug("result: ip:{} name:{} active:{}"
                               .format(
                                   result['NewIPAddress'],
                                   result['NewHostName'],                                  
                                   result['NewActive']
                               ))
                isPresent = (result['NewActive'] ==
                             1 or result['NewActive'] == '1')
                name = result['NewHostName']
                ip = result['NewIPAddress']
                if(isPresent is False and self.lastUpdate is not None and self.deviceLastIsConnected is True):
                    Domoticz.Debug("device turned off - check cool down time")
                    n = datetime.now()
                    Domoticz.Debug("now {}".format(n))
                    Domoticz.Debug("last {}".format(self.lastUpdate))
                    
                    delta = (n-self.lastUpdate).total_seconds()
                    Domoticz.Debug("delta: {}".format(delta))
                    if(delta > float(self.cooldownperiod)):
                        Domoticz.Debug("It's time to tell domoticz,"
                                       "that device is off")
                        self.deviceIp = ip
                        self.deviceName = name
                        self.deviceIsConnected = isPresent
                        self.verifyUpdate()
                        self.lastUpdate = datetime.now()
                    else:
                        Domoticz.Debug(
                            "Device is just a short time away ... ignore for this time and wait")
                else:
                    # device is online / no special handling
                    self.deviceIp = ip
                    self.deviceName = name
                    self.deviceIsConnected = isPresent
                    self.verifyUpdate()
                    self.lastUpdate = datetime.now()

        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on readStatus: msg '{}'; hasError:{}"
                           .format(e, str(self.hasError)))

    def stop(self):
        self.stopped = True

    def getDeviceName(self):
        if(self.defaultName is not None and len(self.defaultName) > 1):
            return self.defaultName
        else:
            return self.deviceName

    def getShortSummary(self, seperator: str = "\t"):
        s = '{} is on: {}'.format(self.defaultName, self.deviceIsConnected)
        return s

    def getSummary(self):
        s = "{} ip: {}".format(self.getShortSummary(), self.deviceIp)
        return s

    def dumpStatus(self):
        s = self.getSummary()
        Domoticz.Log(s)
