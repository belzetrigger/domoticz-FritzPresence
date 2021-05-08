# this is our helper class to do the work with FritzConnection

import plugin
from blz.blzHelperInterface import BlzHelperInterface

from datetime import datetime, timedelta
from typing import List, overload
from typing import Any, Dict
import sys

# sys.path
# sys.path.append('/usr/lib/python3/dist-packages')
# sys.path.append(
#    '/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')

try:
    import Domoticz
except ImportError:
    from blz import fakeDomoticz as Domoticz

# try:
from fritzconnection.lib.fritzhosts import FritzHosts

# except ModuleNotFoundError as e:
#    Domoticz.Error("could not load fritzconnection ...{}".format(e))

import itertools


class PresDevice:

    """class that maps data for a single devices aka known host from domoticz to fritz box
    Returns:
        [type] -- [description]
    """

    def __init__(
        self, macAddress: str, defaultName: str = None, cooldownperiod: int = 30
    ):
        self.cooldownperiod = cooldownperiod
        self.macAddress = macAddress
        self.defaultName = defaultName
        self.deviceName = None
        self.deviceIp = None
        self.deviceLastIp = None
        self.deviceIsConnected = False
        self.deviceLastIsConnected = False
        # TODO None works with init, but type safer might to set to now
        self.lastUpdate: datetime = datetime.now()
        self.hasError = False
        self.needUpdate = False

    def setError(self, error):
        self.hasError = True
        self.errorMsg = error

    def dumpConfig(self):
        """print device config to log"""
        Domoticz.Debug("mac:{}\t" "name: {}".format(self.macAddress, self.defaultName))

    def getDeviceName(self):
        """get device name
           TODO better device and default if empty

        Returns:
            [str] -- the device name
        """
        if self.deviceName is None:
            return self.defaultName
        else:
            return self.deviceName

    def getDeviceIP(self):
        """get IP address of the device

        Returns:
            [str] -- the device IP address
        """
        return self.deviceIp

    def reset(self):
        self.deviceName = None
        self.deviceIp = None
        self.deviceLastIp = None
        self.deviceIsConnected = False
        self.deviceLastIsConnected = False
        self.hasError = False
        self.needUpdate = False

    def verifyUpdate(self):
        if (
            self.deviceLastIsConnected != self.deviceIsConnected
            or self.deviceLastIp != self.deviceIp
        ):
            self.needUpdate = True
        else:
            self.needUpdate = False

        # copy values to compare later
        self.deviceLastIsConnected = self.deviceIsConnected
        self.deviceLastIp = self.deviceIp
        Domoticz.Debug(
            "{} updated needed?: {}".format(self.getDeviceName(), self.needUpdate)
        )

    def readStatus(self, fcHosts: FritzHosts):
        """read the status for this device

        Arguments:
            fcHosts {FritzHosts} -- fritzHosts from fritzconnection
        """
        try:
            self.hasError = False
            isPresent = False
            name = None
            ip = None
            mac = self.macAddress
            if not mac:
                raise ValueError("mac is empty")
            result = fcHosts.get_specific_host_entry(mac)
            if result is not None:
                Domoticz.Debug(
                    "result: ip:{} name:{} active:{}".format(
                        result["NewIPAddress"],
                        result["NewHostName"],
                        result["NewActive"],
                    )
                )
                isPresent = result["NewActive"] == 1 or result["NewActive"] == "1"
                name = result["NewHostName"]
                ip = result["NewIPAddress"]
                if (
                    isPresent is False
                    and self.lastUpdate
                    and self.deviceLastIsConnected is True
                ):
                    Domoticz.Debug("device turned off - check cool down time")
                    n = datetime.now()
                    Domoticz.Debug("now {}".format(n))
                    Domoticz.Debug("last {}".format(self.lastUpdate))

                    delta = (n - self.lastUpdate).total_seconds()
                    Domoticz.Debug("delta: {}".format(delta))
                    if delta > float(self.cooldownperiod):
                        Domoticz.Debug(
                            "It's time to tell domoticz," "that device is off"
                        )
                        self.deviceIp = ip
                        self.deviceName = name
                        self.deviceIsConnected = isPresent
                        self.verifyUpdate()
                        self.lastUpdate = datetime.now()
                    else:
                        Domoticz.Debug(
                            "Device is just a short time away ... ignore for this time and wait"
                        )
                else:
                    # device is online / no special handling
                    self.deviceIp = ip
                    self.deviceName = name
                    self.deviceIsConnected = isPresent
                    self.verifyUpdate()
                    self.lastUpdate = datetime.now()

        except (Exception) as e:
            self.setError(e)
            Domoticz.Error(
                "Error on readStatus for Device: {} ({}) msg: '{}'; hasError:{}".format(
                    self.deviceName, self.macAddress, e, str(self.hasError)
                )
            )

    def getShortSummary(self, seperator: str = "\t"):
        s = "{} is on: {}".format(self.defaultName, self.deviceIsConnected)
        return s

    def getSummary(self):
        s = "{} ip: {}".format(self.getShortSummary(), self.deviceIp)
        return s

class FritzHelper(BlzHelperInterface):
    """helper class to manage communication with fritz box via fritz connection

    Raises:
        Exception: [description]

    Returns:
        [type] -- [description]
    """

    def __init__(
        self,
        fbHost: str,
        fbUser: str,
        fbPassword: str,
        macAddresses: List[str],
        defaultNames: List[str] = None,
        cooldownperiod: int = 30,
    ):
        """create and init the fritz helper

        Arguments:
            fbHost {str} -- ip or hostname of the box
            fbUser {str} -- user to use
            fbPassword {str} -- password for this user
            macAddresses {List[str]} -- list of mac addresses that should be translated to devices

        Keyword Arguments:
            defaultNames {List[str]} -- according to mac address you can pass also names to use (default: {None})
            cooldownperiod {int} -- time till we mark a device as absent (default: {30})
        """
        self.fbHost = fbHost
        self.fbUser = fbUser
        self.fbPassword = fbPassword
        # self.deviceCounter = len(macAddresses)
        # self.devices = {}  # type: Dict[str, PresDevice]
        self.devices: Dict[str, PresDevice] = {}
        for i in range(len(macAddresses)):
            
            adr = macAddresses[i]
            if not plugin.isValidMAC(adr):
                Domoticz.Error("found empty mac in list, skip it")
                continue
            # n = None
            #no default names
            #if defaultNames is not None and defaultNames[i] is not None:
            #    n = defaultNames[i]
            self.devices.update({adr: PresDevice(macAddress=adr)})

        self.cooldownperiod = cooldownperiod
        self.debug = False
        self.lastUpdate: datetime
        self.hasError = False
        self.nextpoll = datetime.now()
        self.reset()

    def dumpConfig(self):
        Domoticz.Debug("fritz:{}\t".format(self.fbHost))
        for value in self.devices.values():
            value.dumpConfig()

    def validateDeviceIndex(self, mac: str):
        """checks index for a device

        Arguments:
            mac {str} -- mac address of device in list

        Raises:
            Exception: if index is not valid

        Returns:
            [type] -- true if index is okay
        """
        if mac in self.devices:
            return True
        else:
            Domoticz.Error("Given index '{}' not valid.".format(mac))
            raise Exception("Index '{}' is not valid".format(mac))

    
    def needsUpdate(self):
        Domoticz.Log("This is a multi device plugin - so please use needsUpdate(self, devId)")
        pass
    
    def needsUpdate(self, mac: str):
        """checks if device has changed and so needs an update
        Arguments:
            mac {str} -- mac addres of the device in list
        Returns:
            boolean -- if True -> please update the device in domoticz
        """
        update = False
        if self.validateDeviceIndex(mac):
            d = self.devices.get(mac)
            if d:
                update = d.needUpdate
        else:
            Domoticz.Error("Given mac not valid.")
        return update

    def reset(self):
        self.stopped = False
        self.fcHosts: FritzHosts = None
        for value in self.devices.values():
            value.reset()
        self.resetError()

    

    def connect(self):
        """init a fritzconnection

        Returns:
            [fritzconnection] -- fresh connection
        """
        Domoticz.Debug("Try to get FritzHost Connection")
        self.fcHosts = FritzHosts(
            address=self.fbHost, user=self.fbUser, password=self.fbPassword
        )
        return self.fcHosts

    def setError(self, error):
        self.hasError = True
        self.errorMsg = error

    def resetError(self):
        self.hasError = False
        self.errorMsg = None
    
    def hasErrorX(self):
        return self.hasError

    def getErrorMsg(self):
        return self.errorMsg

    def addDevice(self, host):
        Domoticz.Debug("addDevice")
        mac = host["mac"]
        name = host["name"]
        if mac in self.devices:
            Domoticz.Debug("addHost: {} - already there".format(mac))
        else:
            Domoticz.Debug("addHost: {} - new one.".format(mac))
            self.devices.update({mac: PresDevice(mac, name, self.cooldownperiod)})

    def addDeviceByMac(self, mac: str, name: str = ""):
        """beside of the mac list given on init, add new one

        Arguments:
            mac {str} -- mac address

        Keyword Arguments:
            name {str} -- name to use for this device (default: {""})
        """
        Domoticz.Debug("addDeviceByMac {}".format(mac))
        #mac = mac
        if not name:
            name = mac
        if mac in self.devices:
            Domoticz.Debug("addHost: {} - already there".format(mac))
        else:
            Domoticz.Debug("addHost: {} - new one.".format(mac))
            self.devices.update({mac: PresDevice(mac, name, self.cooldownperiod)})

    def getWifiHosts(self):
        """
          Returns a list of dicts with information about
        devices that are connected via Wifi
        Returns:
            devices[] -- The dict-keys are: 'ip', 'name', 'mac', 'status', 'interface'
        """
        Domoticz.Debug("get all active hosts from {}".format(self.fbHost))
        return [host for host in self.getAllHosts() if (host["interface"] == "802.11")]

    def getEthernetHosts(self):
        """
          Returns a list of dicts with information about
        devices that are connected via ethernet
        Returns:
            devices[] -- The dict-keys are: 'ip', 'name', 'mac', 'status', 'interface'
        """
        Domoticz.Debug("get all active hosts from {}".format(self.fbHost))
        return [
            host for host in self.getAllHosts() if (host["interface"] == "Ethernet")
        ]

    def getActiveHosts(self):
        """
          Returns a list of dicts with information about the active
        devices.
        Returns:
            devices[] -- The dict-keys are: 'ip', 'name', 'mac', 'status', 'interface'
        """
        Domoticz.Debug("get all active hosts from {}".format(self.fbHost))
        return [host for host in self.getAllHosts() if host["status"]]

    def getAllHosts(self):
        """All known host from this fritz box

        Returns:
            devices[] -- The dict-keys are: 'ip', 'name', 'mac', 'status', 'interface'
        """
        Domoticz.Debug("get all hosts from {}".format(self.fbHost))
        try:
            self.resetError()
            if self.fcHosts is None:
                self.connect()
            fh = self.fcHosts
            devices = []
            # devices = fh.get_hosts_info()
            for index in itertools.count():
                try:
                    host = fh.get_generic_host_entry(index)
                except IndexError:
                    # no more host entries:
                    break
                devices.append(
                    {
                        "ip": host["NewIPAddress"],
                        "name": host["NewHostName"],
                        "mac": host["NewMACAddress"],
                        "status": host["NewActive"],
                        "interface": host["NewInterfaceType"],
                    },
                )

            return devices
        except (Exception) as e:
            self.setError(e)
            Domoticz.Error(
                "Error on getAllHosts: msg '{}'; hasError:{}".format(
                    e, str(self.hasError)
                )
            )

    def wakeOnLan(self, macAddress: str):
        """Sends the 'Magic packet' for wake on LAN
                !!!works only for ethernet!!!

        Arguments:
            macAddress {str} -- mac address of device to WOL
        """
        Domoticz.Debug("wakeOnLan {}".format(macAddress))
        try:
            self.resetError()
            if self.fcHosts is None:
                self.connect()
            fh = self.fcHosts
            if fh:
                fh._action("X_AVM-DE_WakeOnLANByMACAddress", NewMACAddress=macAddress)

        except (Exception) as e:
            self.setError(e)
            Domoticz.Error(
                "Error on wakeOnLan: msg '{}'; hasError:{}".format(
                    e, str(self.hasError)
                )
            )

    def readStatus(self):
        """reset all old errors and tries to get fresh status about all devices in list
        on error, we will set internal error
        """
        Domoticz.Debug("read status for {}".format(self.fbHost))
        try:
            self.resetError()
            if self.fcHosts is None:
                self.connect()
            fh = self.fcHosts
            for value in self.devices.values():
                value.readStatus(fh)

        except (Exception) as e:
            self.setError(e)
            Domoticz.Error(
                "Error on readStatus: msg '{}'; hasError:{}".format(
                    e, str(self.hasError)
                )
            )

    def stop(self):
        self.stopped = True

    def isDeviceConnected(self, mac: str):
        t = False
        if self.validateDeviceIndex(mac):
            d = self.devices.get(mac)
            if d:
                t = d.deviceIsConnected
        return t

    
    def getDeviceName(self, mac: str):
        """device name or default name if null/none

        Args:
            mac (str):  valid mac address of the device

        Returns:
            [str]: device name or default name if null/none
        """
        s = ""
        if self.validateDeviceIndex(mac):
            d = self.devices.get(mac)
            if d:
                s = d.getDeviceName()
        return s
    
    def getDeviceIP(self, mac: str):
        """get IP address of the device
        Args:
            mac (str): valid mac address of the device
        Returns:
            [str] -- the device IP address
        """
        s = ""
        if self.validateDeviceIndex(mac):
            d = self.devices.get(mac)
            if d:
                s = d.getDeviceIP()
        return s

    def getShortSummary(self, seperator: str = "\t"):
        s = ""
        for value in self.devices.values():
            s += value.getShortSummary(seperator) + " "
        return s

    def getSummary(self,  seperator: str = "\t"):
        s = ""
        for value in self.devices.values():
            s += value.getShortSummary(seperator) + " "
        return s

    def dumpStatus(self):
        s = self.getSummary()
        Domoticz.Log(s)

    # TODO check for unused fx

    def reinitData():
        Domoticz.Log("Not jet implemented")
        pass

    def getAlarmLevel(self):
        Domoticz.Log("Not jet implemented")
        pass

    def getAlarmText(self):
        Domoticz.Log("Not jet implemented")
        pass

    #def getDeviceName(self):
    #    Domoticz.Log("Not jet implemented")
    #    pass

