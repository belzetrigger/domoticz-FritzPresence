# this is our helper class to do the work with FritzConnection

from datetime import datetime, timedelta
from typing import List
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
    from fritzconnection.lib.fritzhosts import FritzHosts
except ModuleNotFoundError as e:
    Domoticz.Error("could not load fritzconnection ...{}".format(e))


class PresDevice:

    """class that maps data for a single devices aka known host from domoticz to fritz box
    Returns:
        [type] -- [description]
    """

    def __init__(self, macAddress: str, defaultName: str = None, cooldownperiod: int = 30):
        self.cooldownperiod = cooldownperiod
        self.macAddress = macAddress
        self.defaultName = defaultName
        self.deviceName = None
        self.deviceIp = None
        self.deviceLastIp = None
        self.deviceIsConnected = False
        self.deviceLastIsConnected = False
        self.lastUpdate = None
        self.hasError = False
        self.needUpdate = False

    def setMyError(self, error):
        self.hasError = True
        self.errorMsg = error

    def dumpConfig(self):
        Domoticz.Debug(
            "mac:{}\t"
            "name: {}".format(self.macAddress, self.defaultName)
        )

    def getDeviceName(self):
        if(self.defaultName is not None and len(self.defaultName) > 1):
            return self.defaultName
        else:
            return self.deviceName

    def reset(self):
        self.deviceName = None
        self.deviceIp = None
        self.deviceLastIp = None
        self.deviceIsConnected = False
        self.deviceLastIsConnected = False
        self.hasError = False
        self.needUpdate = False

    def verifyUpdate(self):
        if(self.deviceLastIsConnected != self.deviceIsConnected or self.deviceLastIp != self.deviceIp):
            self.needUpdate = True
        else:
            self.needUpdate = False

        # copy values to compare later
        self.deviceLastIsConnected = self.deviceIsConnected
        self.deviceLastIp = self.deviceIp
        Domoticz.Debug("{} updated needed?: {}".format(self.getDeviceName(),
                                                       self.needUpdate))

    def readStatus(self, fcHosts: FritzHosts):
        try:
            self.hasError = False
            isPresent = False
            name = None
            ip = None
            result = fcHosts.get_specific_host_entry(self.macAddress)
            if result is not None:
                Domoticz.Debug("result: ip:{} name:{} active:{}"
                               .format(
                                   result['NewIPAddress'],
                                   result['NewHostName'],
                                   result['NewActive']
                               ))
                isPresent = (result['NewActive'] == 1 or
                             result['NewActive'] == '1')
                name = result['NewHostName']
                ip = result['NewIPAddress']
                if (isPresent is False and self.lastUpdate is not None and
                        self.deviceLastIsConnected is True):
                    Domoticz.Debug("device turned off - check cool down time")
                    n = datetime.now()
                    Domoticz.Debug("now {}".format(n))
                    Domoticz.Debug("last {}".format(self.lastUpdate))

                    delta = (n - self.lastUpdate).total_seconds()
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

    def getShortSummary(self, seperator: str = "\t"):
        s = '{} is on: {}'.format(self.defaultName, self.deviceIsConnected)
        return s

    def getSummary(self):
        s = "{} ip: {}".format(self.getShortSummary(), self.deviceIp)
        return s


class FritzHelper:

    def __init__(self, fbHost: str, fbUser: str,
                 fbPassword: str, macAddresses: List[str], defaultNames: List[str] = None,
                 cooldownperiod: int = 30):
        self.fbHost = fbHost
        self.fbUser = fbUser
        self.fbPassword = fbPassword
        self.deviceCounter = len(macAddresses)

        self.devices: List[PresDevice] = []

        for i in range(len(macAddresses)):
            adr = macAddresses[i]
            n = None
            if(defaultNames is not None and defaultNames[i] is not None):
                n = defaultNames[i]
            self.devices.append(PresDevice(adr, n, cooldownperiod))

        # self.presDevice = PresDevice(macAddress, defaultName, cooldownperiod)

        self.cooldownperiod = cooldownperiod
        self.debug = False
        self.lastUpdate = None
        self.hasError = False
        self.nextpoll = datetime.now()
        self.reset()

    def dumpConfig(self):
        Domoticz.Debug(
            "fritz:{}\t"
            .format(self.fbHost)
        )
        for i in range(len(self.devices)):
            self.devices[i].dumpConfig()

    def validateDeviceIndex(self, idx: int):
        """checks index for a device

        Arguments:
            idx {int} -- index of device in list

        Raises:
            Exception: if index is not valid

        Returns:
            [type] -- true if index is okay
        """
        if(idx <= len(self.devices) and idx >= 0):
            return True
        else:
            Domoticz.Error("Given index not valid.")
            raise Exception("Index is not valid")

    def needsUpdate(self, idx: int):
        """checks if device has changed and so needs an update
        Arguments:
            idx {int} -- index of device in list
        Returns:
            boolean -- if True -> please update the device in domoticz
        """
        update = False
        if(self.validateDeviceIndex(idx)):
            update = self.devices[idx].needUpdate
        else:
            Domoticz.Error("Given index not valid.")
        return update

    def reset(self):
        self.stopped = False
        self.fcHosts = None
        for i in range(len(self.devices)):
            self.devices[i].reset()
        # self.presDevice.reset()
        # self.deviceName = None
        # self.deviceIp = None
        # self.deviceLastIp = None
        # self.deviceIsConnected = None
        # self.deviceLastIsConnected = None
        self.resetError()

    def connect(self):
        Domoticz.Debug("Try to get FritzHost Connection")
        # import fritzconnection as fc
        self.fcHosts = FritzHosts(
            address=self.fbHost,
            user=self.fbUser,
            password=self.fbPassword
        )
        # Domoticz.Debug("status: {}".format(self.fcHosts))

        return self.fcHosts

    def setMyError(self, error):
        self.hasError = True
        self.errorMsg = error

    def resetError(self):
        self.hasError = False
        self.errorMsg = None

    # def verifyUpdate(self):
    #    self.presDevice.verifyUpdate()

    def getAllHosts(self):
        Domoticz.Debug("get all hosts from {}".format(self.fbHost))
        try:
            self.resetError()
            if(self.fcHosts is None):
                self.connect()
            fh = self.fcHosts
            devices = []
            devices = fh.get_hosts_info()
            return devices
        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on getAllHosts: msg '{}'; hasError:{}"
                           .format(e, str(self.hasError)))

    def readStatus(self):
        Domoticz.Debug("read status for {}".format(self.fbHost))
        try:
            self.resetError()
            if(self.fcHosts is None):
                self.connect()
            fh = self.fcHosts
            for i in range(len(self.devices)):
                self.devices[i].readStatus(fh)
        except (Exception) as e:
            self.setMyError(e)
            Domoticz.Error("Error on readStatus: msg '{}'; hasError:{}"
                           .format(e, str(self.hasError)))

    def stop(self):
        self.stopped = True

    def isDeviceConnected(self, idx: int):
        t = False
        if(self.validateDeviceIndex(idx)):
            t = self.devices[idx].deviceIsConnected
        return t

    def getDeviceName(self, idx: int):
        # if(self.defaultName is not None and len(self.defaultName) > 1):
        #    return self.defaultName
        # else:
        #    return self.deviceName
        s = ""
        if(self.validateDeviceIndex(idx)):
            s = self.devices[idx].getDeviceName()
        return s

    def getShortSummary(self, seperator: str = "\t"):
        # s = '{} is on: {}'.format(self.defaultName, self.deviceIsConnected)
        s = ""
        for i in range(len(self.devices)):
            s += self.devices[i].getShortSummary(seperator) + " "
        return s

    def getSummary(self):
        # s = "{} ip: {}".format(self.getShortSummary(), self.deviceIp)
        s = ""
        for i in range(len(self.devices)):
            s += self.devices[i].getSummary() + " "
        return s

    def dumpStatus(self):
        s = self.getSummary()
        Domoticz.Log(s)
