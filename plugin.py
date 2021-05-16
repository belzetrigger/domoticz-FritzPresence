# plugin for fritz box
#
# Author: belze
#


"""
<plugin key="FritzPresence" name="Fritz!Presence Plugin"
    author="belze" version="0.7.0" 
    externallink="https://github.com/belzetrigger/domoticz-FritzPresence" >
    
    <!--    
    wikilink="http://www.domoticz.com/wiki/plugins/plugin.html"
    //-->
    <description>
        <h2>Fritz!Presence</h2><br/>
        Does two things. Mainly adds your IT devices known by your Fritz!Box to 
        domoticz and shows the current status.
        So you can determine the presence of people if for example mobile phone is connected. 
        Or check if hardware is still a live. 
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>uses router information to show state of a device.</li>
            <li>works better than ping, if mobile phone use some energy saving options</li>
            <li>supports multiple devices - just add the MAC Addresses separeted by ';' </li>
            <li>on error: the device will be shown as absence (turned off) and config shows 'Error' </li>
            <li>using the MAC as internal DeviceID
                <ul>
                <li>so if order changes, there is a chance to pick the right one</li>
                <li>also means you could have same name on two devices</li>
                </ul>
            </li>
            <li>replaces or updates device names by the one used on the Fritz!Box
            </li>
            <li>button to administrate devices known by router
                <ul>
                <li>add all WiFi devices</li>
                <li>add all ethernet devices</li>
                <li>add all active devices</li>
                <li>add all known devices</li>
                <li>remove all devices under this hardware</li>
                </ul>
           </li>
           <li>based on device names, this plugin tries to add differant images - if using admin panel</li>
           <li>WOL: send magic packets to your ethernet device</li>
           
        </ul>
        <h3>Devices</h3>
        for each MAC address there will be one device generated
        <ul style="list-style-type:square">
            <li>switch - shows if device is there or not</li>
            <li>selector switch - to add all known hosts or to remove all</li>
        </ul>
        <h3>Configuration</h3>
        Use a list of MAC Addresses seperated by ';' if you want to add more
        devices. Note! There is no need to put names also in name field as a list.
        For bare use with admin switch, leave it blank.

    </description>
    <params>
        <param field="Mode1" label="Hostname or IP" width="200px"
        required="true" default="fritz.box"/>
        <param field="Username" label="User" width="200px" required="false"
        />
        <param field="Password" label="Password" width="200px" required="false"
        password="true"
        />
        <param field="Port" label="domoticz port" width="75px" required="true" default="8080"/>
        <param field="Mode4" label="Update every x minutes" width="200px"
        required="true" default="5"/>
        <param field="Mode5" label="MACAddresses" width="350px"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="False" />
            </options>
        </param>
        
    </params>
</plugin>
"""
from blz import blzHelperInterface
import re

#BLZ 2021-04-21: new lib for renamin work around via JSON-API
import urllib
# import datetime as dt
from datetime import datetime, timedelta
import sys
from typing import List
try:
    import Domoticz
except ImportError:
    from blz import fakeDomoticz as Domoticz
    from blz.fakeDomoticz import Parameters
    from blz.fakeDomoticz import Devices
    from blz.fakeDomoticz import Images

#from blz.blzHelperInterface import BlzHelperInterface


try:
    from fritzhelper.fritzHelper import FritzHelper
except ImportError as e:
    pass

import urllib.request                   #for name hack via JSON-API Call

# sys.path
# sys.path.append('/usr/lib/python3/dist-packages')
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')

PARAM_PASS: str = 'Password'  # parameter that holds password

# icons
ICON_ADMIN = "FritzPresenceAdmin"   # icon used for fritz box switch and alert
ICON_BOX = "FritzPresenceBox"
ICON_IOT = "FritzPresenceIoT"
ICON_IOTCLOUD = "FritzPresenceIoTCloud"
ICON_NOTEBOOK = "FritzPresenceNotebook"
ICON_PERSON = "FritzPresencePerson"   # icon used for fritz box switch and alert
ICON_PERSON_SIMPLE = "FritzPresencePersonSimple"
ICON_PHONE = "FritzPresencePhone"
ICON_PI = "FritzPresencePi"
ICON_TABLET = "FritzPresenceTablet"
ICON_TV = "FritzPresenceTV"


# names to fit icons
ICON_BOX_NAME_PREFIXES = ["FRITZ", "BOX", "FRITZ.BOX"]
ICON_IOT_NAME_PREFIXES = ["ESP-", "IOT", "TASMOTA"]
ICON_NOTEBOOK_PREFIXES = ["PC-", "NB-", "DESKTOP"]
ICON_PHONE_PREFIXES = ["HUAWEI", "NOKIA", "NEXUS", "PHONE", "ANDROID"]
ICON_PI_PREFIXES = ["RASPBERRY", "PI"]
ICON_TAB_PREFIXES = ["TAB", "PAD"]
ICON_TV_PREFIXES = ["TV"]


UNIT_CMD_SWITCH_IDX = 1
UNIT_CMD_SWITCH_NAME = "FP - Admin"
UNIT_CMD_SWITCH_OPTIONS = {
    'LevelNames': '|+ WiFi|+ ethernet|+ all active|+ all|- all',
    'LevelOffHidden': 'true',
    'SelectorStyle': '0'}
UNIT_CMD_SWITCH_LVL_ALL_WIFI = 10
UNIT_CMD_SWITCH_LVL_ALL_ETHERNET = 20
UNIT_CMD_SWITCH_LVL_ALL_ACTIVE = 30
UNIT_CMD_SWITCH_LVL_ALL = 40
UNIT_CMD_SWITCH_LVL_REMOVE_ALL = 50
# unit index for first real device
UNIT_DEV_START_IDX = UNIT_CMD_SWITCH_IDX + 1


class BasePlugin:
    enabled = False

    def __init__(self):
        self.fritz = None
        self.debug = False
        self.error = False
        self.nextpoll = datetime.now()
        self.host = None
        self.user = None
        self.password = None
        self.pollinterval = 60 * 5
        self.errorCounter = 0
        self.macList: List[str] = []
        self.nameList: List[str] = []

        return

    def onStart(self):
        if Parameters["Mode6"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)

        Domoticz.Log("onStart called")

        # check polling interval parameter
        try:
            temp = int(Parameters["Mode4"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if temp < 1:
                temp = 1  # minimum polling interval
                Domoticz.Error(
                    "Specified polling interval too short: changed to one minutes")
            elif temp > (60):
                temp = (60)  # maximum polling interval is 1 hour
                Domoticz.Error(
                    "Specified polling interval too long: changed to 1 hour")
            self.pollinterval = temp * 60
        Domoticz.Log("Using polling interval of {} seconds".format(
            str(self.pollinterval)))

        self.host = Parameters["Mode1"]
        self.user = Parameters["Username"]
        self.password = Parameters["Password"]

        if( blzHelperInterface.isBlank(self.user) or blzHelperInterface.isBlank(self.password) ):
            Domoticz.Error("No username / password set - please update setting.")
            raise ValueError("Username and password must be given.")

        # MAC Addresses
        if(not Parameters["Mode5"]):
            Domoticz.Log("Mac Addresses are empty. Use admin switch to add.")
        else:
            self.macList = Parameters["Mode5"].split(';')
            # BLZ 2021-04-20: Test without names, just use macs .... 
            # we would update name later with hostname from fritz box anyway
            Domoticz.Debug("Now we just use MAC as names for init, should replaced later with name from Fritz!Box.")
            self.nameList = Parameters["Mode5"].split(';')
            # just for security
            # if(Parameters['Name'] is not None):
            #    self.nameList = Parameters['Name'].split(';')
            #    # just for quality
            #    if(len(self.nameList) != len(self.macList)):
            #        Domoticz.Error("Amount of Names does not fit defined addresses. Use now MAC Address as names.")
            #        self.nameList = Parameters["Mode5"].split(';')
            # else:
            #    Domoticz.Error("No Names defined in configuration. Using mac addresses first.")
            #    self.nameList = Parameters["Mode5"].split(';')
        
        self.defName = None

        # check images
        checkImages(ICON_ADMIN, ICON_ADMIN + ".zip")
        checkImages(ICON_BOX, ICON_BOX + ".zip")

        checkImages(ICON_IOT, ICON_IOT + ".zip")
        checkImages(ICON_IOTCLOUD, ICON_IOTCLOUD + ".zip")

        checkImages(ICON_NOTEBOOK, ICON_NOTEBOOK + ".zip")
        checkImages(ICON_PERSON, ICON_PERSON + ".zip")
        checkImages(ICON_PERSON_SIMPLE, ICON_PERSON_SIMPLE + ".zip")
        checkImages(ICON_PHONE, ICON_PHONE + ".zip")
        checkImages(ICON_PI, ICON_PI + ".zip")
        checkImages(ICON_TABLET, ICON_TABLET + ".zip")
        checkImages(ICON_TV, ICON_TV + ".zip")

        # create selector switch, to deal with admin stuff
        createSelectorSwitch()

        # use no more  hard ware name - just uses mac as dummy name
        for i in range(len(self.macList)):
            mac = self.macList[i]
            if not blzHelperInterface.isValidMAC(mac):
                Domoticz.Error("Invalid MAC Address on index {}='{}' skip this entry.".format(i, mac))
                continue
            #if(self.nameList[i]):
            #    devName = self.nameList[i]
            #else:
            #    devName = "{}_{}".format(Parameters['Name'], self.macList[i])
            
            # Check if devices need to be created
            createDevice(unit=i + UNIT_DEV_START_IDX, devName=mac, devId=mac)
            # init with empty data
            updateDeviceByDevId(devId=mac, alarmLevel=0, alarmData="No Data jet", name=mac)
            # BLZ: 2021-04-19: removed to avoid overwriting custom images see issue#2
            # updateImageByDevId(self.macList[i], ICON_PERSON)

        # blz: test first init, after that get helper
        self.fritz = FritzHelper(self.host, self.user, self.password,
                                 self.macList)
        if self.debug is True and self.fritz is not None:
            self.fritz.dumpConfig()
        else:
            Domoticz.Debug('fritz is None')

        # add units to our helper
        for x in Devices:
            if Devices[x].Unit >= UNIT_DEV_START_IDX:
                mac = Devices[x].DeviceID
                # BLZ 2021-04-20: no default name;s name = Devices[x].Name
                self.fritz.addDeviceByMac(mac)

    def onStop(self):
        if(self.fritz is not None):
            self.fritz.stop()
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " +
                     str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()

        try:
            if (Unit > UNIT_CMD_SWITCH_IDX):
                if (action == "On" or Command == "On"):
                    mac = Devices[Unit].DeviceID
                    Domoticz.Debug("Try call WOL mac: {}".format(mac))
                    self.fritz.wakeOnLan(mac)
            elif (Unit == UNIT_CMD_SWITCH_IDX):
                if (action == "On" or Command == "On"):
                    mac = Devices[Unit].DeviceID
                    Domoticz.Debug("On - not supported mac: {}".format(mac))
                    self.fritz.wakeOnLan(mac)
                elif (action == "Set"):
                    Domoticz.Debug("Set")
                    if(Level == UNIT_CMD_SWITCH_LVL_ALL_WIFI):
                        Domoticz.Debug("all WiFi")
                        r = self.fritz.getWifiHosts()
                        self.createDevicesFromHosts(r)
                    elif(Level == UNIT_CMD_SWITCH_LVL_ALL_ETHERNET):
                        Domoticz.Debug("all active")
                        r = self.fritz.getEthernetHosts()
                        self.createDevicesFromHosts(r)
                    elif(Level == UNIT_CMD_SWITCH_LVL_ALL_ACTIVE):
                        Domoticz.Debug("all active")
                        r = self.fritz.getActiveHosts()
                        self.createDevicesFromHosts(r)
                    elif(Level == UNIT_CMD_SWITCH_LVL_ALL):
                        Domoticz.Debug("all hosts")
                        r = self.fritz.getAllHosts()
                        self.createDevicesFromHosts(r)
                    elif(Level == UNIT_CMD_SWITCH_LVL_REMOVE_ALL):
                        Domoticz.Debug("remove all")
                        self.removeAllDevices()
                elif (action == "Off"):
                    Domoticz.Debug("Off - not supported")

        except (Exception) as e:
            Domoticz.Error("Error on deal with WiFi unit {}: msg *{}*;".format(Unit, e))

    def removeAllDevices(self):
        # does only work in python 2 keys = Devices.keys()
        # so for 3.x use list to avoid iterator
        for x in list(Devices):
            if Devices[x].Unit >= UNIT_DEV_START_IDX:
                dev = Devices[x]
                mac = dev.DeviceID
                idx = dev.Unit
                Domoticz.Debug("remove device unit: {} mac: {}".format(idx, mac))
                dev.Delete()

    def createDevicesFromHosts(self, hosts):
        """[summary]

        Arguments:
            hosts {dict} -- list of hosts should came from fritzhelper or fritzconnection we 
                            need at least mac, status, name
        """
        for host in hosts:
            mac = host['mac']
            status = host["status"]
            name = host["name"]
            ip = host['ip']
            if (not mac):
                Domoticz.Error("Device mac is empty -"
                               "this one will be ignored: name: {} status: {} ip {}. "
                               "This normally happens in case of VPN devices.".format(name, status, ip))
                continue
            unit = getUnit4DeviceID(mac)

            if(unit):
                Domoticz.Debug("addHost: mac:{}  name:{} - already there unit {}".format(mac, name, unit))
            else:
                Domoticz.Debug("addHost: mac:{} name:{} - new one.".format(mac, name))
                # create in domoticz
                createDevice(unit=None, devName=name, devId=mac, image=self.getImage(name))
                # tell our helper class
                self.fritz.addDevice(host)
                # update
                updateDeviceByDevId(devId=mac, alarmLevel=status, alarmData="", name=name, alwaysUpdate=True)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," +
                     Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        myNow = datetime.now()
        if myNow >= self.nextpoll:
            Domoticz.Debug(
                "----------------------------------------------------")

            # TODO handle fritz is None
            if(self.fritz is None):
                Domoticz.Error(
                    "Uuups. Fritz is None. Try to recreate.")
                self.fritz = FritzHelper(self.host, self.user, self.password,
                                         self.macList)

            self.nextpoll = myNow + timedelta(seconds=self.pollinterval)

            # read info it it is time
            self.fritz.readStatus()

            # check for error
            if(self.fritz is None or self.fritz.hasError is True):
                self.errorCounter += 1
                Domoticz.Error(
                    "Uuups. Something went wrong ... Shouldn't be here.")
                t = "Error"
                if self.debug is True and self.fritz is not None:
                    Domoticz.Debug(self.fritz.getSummary())
                if(self.fritz is not None and self.fritz.hasError is True):
                    t = "{}:{}".format(t, self.fritz.errorMsg)

                updateDeviceByUnit(UNIT_CMD_SWITCH_IDX, 0, t, 'Error')

                for x in Devices:
                    mac = Devices[x].DeviceID
                    Devices[x].TimedOut = True
                    updateDeviceByDevId(mac, 0, "")  # ""t"", 'Fritz!Box - Error')

                    # TODO error image or error on text, but preserve name
                    # updateImageByDevId(mac, ICON_PERSON)

                self.nextpoll = myNow
            else:
                self.errorCounter = 0
                updateDeviceByUnit(Unit=UNIT_CMD_SWITCH_IDX, alarmLevel=1, alarmData="", name=UNIT_CMD_SWITCH_NAME,
                                   dscr="Configure your devices", alwaysUpdate=True)

                # check for all devices the state
                for x in Devices:
                    if Devices[x].Unit >= UNIT_DEV_START_IDX:
                        mac = Devices[x].DeviceID
                        name = self.fritz.getDeviceName(mac)
                        Domoticz.Debug("nr {} mac {} name {}".format(x, mac, name))
                        
                        if self.fritz.needsUpdate(mac) is True:
                            connected = 1
                            if(self.fritz.isDeviceConnected(mac) is False):
                                connected = 0
                            updateDeviceByDevId(mac, connected, "", "",
                                                name)
                        if(name != Devices[x].Name):                             
                            url = "http://localhost:{}/json.htm?param=renamedevice&type=command&idx={}&name={}".format(Parameters['Port'],Devices[x].ID,name)
                            Domoticz.Debug("BLZ: new name!  call: {}".format(url))
                            contents = urllib.request.urlopen(url).read()



            Domoticz.Debug(
                "----------------------------------------------------")

    def getImage(self, name: str = ICON_PERSON):
        Domoticz.Debug("getImage({})".format(name))
        img = ICON_PERSON

        if any(x in name.upper() for x in ICON_TV_PREFIXES):
            img = ICON_TV
        elif any(x in name.upper() for x in ICON_TAB_PREFIXES):
            img = ICON_TABLET
        elif any(x in name.upper() for x in ICON_PHONE_PREFIXES):
            img = ICON_PHONE
        elif any(x in name.upper() for x in ICON_PI_PREFIXES):
            img = ICON_PI
        elif any(x in name.upper() for x in ICON_NOTEBOOK_PREFIXES):
            img = ICON_NOTEBOOK
        elif any(x in name.upper() for x in ICON_IOT_NAME_PREFIXES):
            img = ICON_IOTCLOUD
        elif any(x in name.upper() for x in ICON_BOX_NAME_PREFIXES):
            img = ICON_BOX

        return img


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status,
                           Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            value: str = str(Parameters[x])
            if(x == PARAM_PASS):
                value = 'xxx'
            Domoticz.Debug("{}:\t{}".format(x, value))
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           {} - {}".format(x, str(Devices[x])))
        Domoticz.Debug("Device ID:       '{}'".format(Devices[x].ID))
        Domoticz.Debug("Device Name:     '{}'".format(Devices[x].Name))
        if hasattr(Devices[x], 'nValue'):
            Domoticz.Debug("Device nValue:    {}".format(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '{}'".format(Devices[x].sValue))
        Domoticz.Debug("Device LastLevel: {}".format(Devices[x].LastLevel))
    return


def checkImages(sName: str, sZip: str):
    Domoticz.Debug("Make sure images {} {}".format(sName, sZip))
    # Check if images are in database
    if sName not in Images:
        Domoticz.Image(sZip).Create()


def getUnit4DeviceID(devId: str):
    """checks all devices of this hardware for given device Id

    Arguments:
        devId {str} -- mac address

    Returns:
        [int] -- unit number, or none if not found
    """
    for dev in Devices:
        if (Devices[dev].DeviceID == devId):
            return dev
    Domoticz.Debug("getUnit4DeviceID: mac: {} not found in domoticz device list".format(devId))


def getUnit4Name(name: str):
    """scans all device and returns first one with matching name.

    Arguments:
        name {str} -- name to search for

    Returns:
        [int] -- unit number, or none if not found
    """
    for dev in Devices:
        if (Devices[dev].Name == name):
            return dev


def createSelectorSwitch():
    if UNIT_CMD_SWITCH_IDX not in Devices:
        Domoticz.Device(Name=UNIT_CMD_SWITCH_NAME, Unit=UNIT_CMD_SWITCH_IDX, TypeName="Selector Switch",
                        Used=1,
                        Switchtype=18, Options=UNIT_CMD_SWITCH_OPTIONS).Create()
        Domoticz.Log("Devices[UNIT_CMD_SWITCH_IDX={}] created.".format(UNIT_CMD_SWITCH_IDX))
        updateImageByUnit(UNIT_CMD_SWITCH_IDX, ICON_ADMIN)


def createDevice(unit: int, devName: str, devId: str, image: str = ICON_PERSON):
    """
    this creates the switch for one single host entry.
    before it checks if it might be already there using devId.
    if so, this would return matching unit number.

    Arguments:
        unit {int} -- unit number to use, if None we create a new one
        devName {str} -- name for that device
        devId {str} -- unique id of that device eg MacAddress
        image {str} -- image to use, default person
    Returns:
        int -- the correct unit number for this device
    """

    # create the mandatory devices if not yet exist
    if devId is not None:
        idx = getUnit4DeviceID(devId)
        if(idx is not None):
            Domoticz.Debug("BLZ:createDevice: Looks like device with id: {} was created under unit: {}".format(devId,
                                                                                                  idx))
            if(idx != unit):
                Domoticz.Log("BLZ:createDevice: Device with id: {} was created under unit: {} and not {}".format(devId,
                                                                                                    idx, unit))
            return idx
    Domoticz.Debug("BLZ:createDevice: Device does not exist - create it ...")
    if unit is None:
        Domoticz.Debug("BLZ:createDevice: Given Unit was NONE, so just take next available")
        unit = len(Devices) + 1
    if unit in Devices:
        Domoticz.Debug("BLZ:createDevice: Looks like unit {} is already used by {}. Take next".format(unit, Devices[unit].Name) )
        unit = len(Devices) + 1

    if unit not in Devices:
        Domoticz.Device(Name=devName, Unit=unit, TypeName="Switch",
                        DeviceID=devId,
                        Options={"Custom": ("1;Foo")}, Used=1).Create()
        # work around, default behavior is using Hardwarename+' '+devname
        # Devices[unit].Update(Name=devName)
        updateImageByUnit(unit, image)
        Domoticz.Log("BLZ:createDevice: Device  unit={} id={} created".format(
            unit, devId))
    else:
        Domoticz.Error("BLZ:createDevice: Should never happen, as we double checked before.... But looks like unit {} is already used by {}.".format(unit, Devices[unit].Name) )
        
        
    return unit


def updateDeviceByDevId(devId: str, alarmLevel, alarmData, name: str = '', dscr: str = '', alwaysUpdate=False):
    """instead of using unit number this uses the device id.
       Device will only be updated only if values are changed or alwaysUpdate = True

    Arguments:
        devId {str} -- should be the mac address
        alarmLevel {[type]} -- also nValue, for switch 0 = off, 1 = on
        alarmData {[type]} -- also sValue, textual data

    Keyword Arguments:
        name {str} -- name of the device (default: {''})
        dscr {str} -- description (default: {''})
        alwaysUpdate {bool} -- if true, always force update (default: {False})
    """
    Domoticz.Debug("updateDeviceByDevId: devId {}, name {} ".format(devId, name))
    unit = getUnit4DeviceID(devId)
    updateDeviceByUnit(unit, alarmLevel, alarmData, name, dscr, alwaysUpdate)


def updateDeviceByUnit(Unit: int, alarmLevel, alarmData, name: str = '', dscr: str = '', alwaysUpdate=False):
    """standard update with unit number.
       Device will only be updated only if values are changed or alwaysUpdate = True

    Arguments:
        Unit {int} -- unit number of the device to update
        alarmLevel {[type]} -- also nValue, for switch 0 = off, 1 = on
        alarmData {[type]} -- also sValue, textual data

    Keyword Arguments:
        name {str} -- name of the device (default: {''})
        dscr {str} -- description (default: {''})
        alwaysUpdate {bool} -- if true, always force update (default: {False})
    """
    Domoticz.Debug("updateDeviceByUnit: unit {}, name {} ".format(Unit, name))

    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if (alarmData != Devices[Unit].sValue) or (int(alarmLevel) != Devices[Unit].nValue or alwaysUpdate is True):
            if(not name):
                Devices[Unit].Update(int(alarmLevel), alarmData, Description=dscr)
            else:
                Devices[Unit].Update(int(alarmLevel), alarmData, Name=name,
                                     Description=dscr)

            Domoticz.Log("Update #{} Name: {} nV: {} sV: {}  ".format(
                Unit, Devices[Unit].Name, str(alarmLevel), str(alarmData)))
        else:
            Domoticz.Log("BLZ: Remains Unchanged")
    else:
        Domoticz.Error(
            "Devices[{}] is unknown. So we cannot update it.".format(Unit))


def updateImageByDevId(devId: str, picture):
    """push a new image to given device.
       instead of unit number we use device id to find matching entry/device.
       So we first try to find unit for devId.
    Arguments:
        devId {str} -- mac address
        picture {[type]} -- picture to use
    """
    unit = getUnit4DeviceID(devId)
    updateImageByUnit(unit, picture)


def updateImageByUnit(Unit: int, picture):
    """push a new image to given device.
       standard way using unit number to find matching entry/device.
       If unit does not exist print error log and do nothing.
    Arguments:
        Unit {int} -- number of this device
        picture {[type]} -- picture to use
    """
    Domoticz.Debug("Image: Update Unit: {} Image: {}".format(Unit, picture))
    if Unit in Devices and picture in Images:
        Domoticz.Debug("Image: Name:{}\tId:{}".format(
            picture, Images[picture].ID))
        if Devices[Unit].Image != Images[picture].ID:
            Domoticz.Log("Image: Device Image update: 'Fritz!Box', Currently " +
                         str(Devices[Unit].Image) + ", should be " + str(Images[picture].ID))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Devices[Unit].sValue),
                                 Image=Images[picture].ID)
            # Devices[Unit].Update(int(alarmLevel), alarmData, Name=name)
    else:
        Domoticz.Error("BLZ: Image: Unit or Picture {} unknown".format(picture))
        Domoticz.Error("BLZ: Number of icons loaded = " + str(len(Images)))
        for image in Images:
            Domoticz.Error("Image: {} id: {} name: {}".format(image, Images[image].ID, Images[image].Name))
    return

