# plugin for fritz box
#
# Author: belze
#


"""
<plugin key="FritzPresence" name="Fritz!Presence Plugin"
    author="belze" version="0.6.2" >
    <!--
    wikilink="http://www.domoticz.com/wiki/plugins/plugin.html"
    externallink="https://www.google.com/"
    //-->
    <description>
        <h2>Fritz!Presence</h2><br/>
        Add presence detection with your FritzBox to Domoticz
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>uses router information to show state of a device.</li>
            <li>works better than ping, if mobile phone use some energy saving options</li>
            <li>supports multiple devices - just add the MAC Addresses separeted by ';' </li>
            <li>on error device will be shown as absence (turned off) and show 'Error' </li>
            <li>using the MAC as internal DeviceID, so if order changes, there is a chance to pick the right one</li>
            <li>(Future)cool down phase. Handle short absence of device not as absence.  Maybe Wifi connection might be interrupted on restart phone.  </li>
        </ul>
        <h3>Devices</h3>
        for each MAC address there will be one device generated
        <ul style="list-style-type:square">
            <li>switch - shows if device is there or not</li>
        </ul>
        <h3>Configuration</h3>
        Use a list of MAC Addresses seperated by ';' if you want to add more
        devices. If you do so, please use also the name field in the same way.

    </description>
    <params>
        <param field="Mode1" label="Hostname or IP" width="200px"
        required="true" default="fritz.box"/>
        <param field="Mode2" label="User" width="200px" required="false"
        />
        <param field="Mode3" label="Password" width="200px" required="false"
        password="true"
        />
        <param field="Mode4" label="Update every x minutes" width="200px"
        required="true" default="5"/>
        <param field="Mode5" label="MACAddresses" width="350px"/>
        <param field="Mode7" label="cooldownphase" width="75px"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="False" />
            </options>
        </param>
    </params>
</plugin>
"""
# import datetime as dt
from datetime import datetime, timedelta
# from os import path
import sys
try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz

try:
    from fritzHelper import FritzHelper
except ImportError as e:
    pass

sys.path
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')


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
        self.user = Parameters["Mode2"]
        self.password = Parameters["Mode3"]
        # self.macAddress = Parameters["Mode5"]
        self.macList = Parameters["Mode5"].split(';')
        # just for security
        if(Parameters['Name'] is not None):
            self.nameList = Parameters['Name'].split(';')
            # just for quality
            if(len(self.nameList) != len(self.macList)):
                Domoticz.Error("Amount of Names does not fit defined addresses. Use now MAC Address as names.")
                self.nameList = Parameters["Mode5"].split(';')
        else:
            Domoticz.Error("No Names defined in configuration. Using mac addresses first.")
            self.nameList = Parameters["Mode5"].split(';')
        self.defName = None

        # check images
        checkImages("person", "person.zip")

        # use hard ware name and mac as dummy name
        # TODO namen auch noch parsen
        devNameList: List[str] = []
        for i in range(len(self.macList)):
            devName = "{}_{}".format(Parameters['Name'], self.macList[i])
            # devNameList.append(self.macList[i])
            # Check if devices need to be created
            createDevices(i + 1, devName, self.macList[i])
            # init with empty data
            updateDeviceByDevId(self.macList[i], 0, "No Data")
            # TODO init icon would be better
            updateImageByDevId(self.macList[i], 'person')

        from fritzHelper import FritzHelper

        # blz: test first init, after that get helper
        self.fritz = FritzHelper(self.host, self.user, self.password,
                                 self.macList)
        if self.debug is True and self.fritz is not None:
            self.fritz.dumpConfig()
        else:
            Domoticz.Debug('fritz is None')

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
                    "Uuups. Fritz is None")
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

                for i in range(len(self.macList)):
                    updateDeviceByDevId(self.macList[i], 0, t, 'Fritz!Box - Error')
                    # TODO error image
                    updateImageByDevId(self.macList[i], 'person')

                self.nextpoll = myNow
            else:
                self.errorCounter = 0
                # check if
                for i in range(len(self.macList)):
                    if self.fritz.needsUpdate(i) is True:
                        connected = 1
                        if(self.fritz.isDeviceConnected(i) is False):
                            connected = 0
                        # device 1 == switch
                        # TODO what we should use as name?
                        # name from config?
                        # name as they defined?
                        # No1 name from fritz box
                        # updateDevice(i + 1, connected, "", self.getDeviceName(i),
                        #             self.fritz.getDeviceName(i))
                        # No2 name from domoticz config for hardware
                        # updateDevice(i + 1, connected, "", self.nameList[i],
                        #             self.fritz.getDeviceName(i))
                        # No3 just use the one on device area in domoticz
                        updateDeviceByDevId(self.macList[i], connected, "", "",
                                     self.fritz.getDeviceName(i))

                        updateImageByDevId(self.macList[i], 'person')

            Domoticz.Debug(
                "----------------------------------------------------")


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
            # skip passwword
            if("Mode3" in x):
                Domoticz.Debug("'" + x + "':'....'")
            else:
                Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return


def checkImages(sName: str, sZip: str):
    Domoticz.Debug("Make sure images {} {}".format(sName, sZip))
    # Check if images are in database
    if sName not in Images:
        Domoticz.Image(sZip).Create()


def getUnit4DeviceID(devId: str):
    for dev in Devices:
        if (Devices[dev].DeviceID == devId):
            return dev


def getUnit4Name(name: str):
    for dev in Devices:
        if (Devices[dev].Name == name):
            return dev


def createDevices(unit: int, devName: str, devId: str):
    '''
    this creates the switch
    '''
    # create the mandatory devices if not yet exist
    if devId is not None:
        idx = getUnit4DeviceID(devId)
        if(idx is not None):
            Domoticz.Debug("BLZ: Looks like device with id: {} was created under unit: {}".format(devId,
                                                                                                  idx))
            if(idx != unit):
                Domoticz.Log("BLZ: Device with id: {} was created under unit: {} and not {}".format(devId,
                                                                                                    idx, unit))
            return idx
    Domoticz.Debug("Device does not exist - create it ...")
    if unit not in Devices:
        Domoticz.Device(Name=devName, Unit=unit, TypeName="Switch",
                        DeviceID=devId,
                        Options={"Custom": ("1;Foo")}, Used=1).Create()
        updateImageByUnit(unit, 'person')
        Domoticz.Log("BLZ: Device {} created".format(
            unit))
    return unit

# Update Device into database


# def updateDevice2(Unit, nValue, sValue, sName='', dscr='', AlwaysUpdate=False):
#     # Make sure that the Domoticz device still exists (they can be deleted) before updating it
#     if Unit in Devices:
#         if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or AlwaysUpdate is True:
#             if(len(sName) <= 0):
#                 Devices[Unit].Update(nValue, str(sValue))
#             else:
#                 # Devices[Unit].Update(int(alarmLevel), alarmData, Name=name)
#                 Devices[Unit].Update(nValue, str(sValue), Name=sName)
#             Domoticz.Log(
#                 "Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
    # return

def updateDeviceByDevId(devId: str, alarmLevel, alarmData, name: str = '', dscr: str = '', alwaysUpdate=False):
    unit = getUnit4DeviceID(devId)
    updateDeviceByUnit(unit, alarmLevel, alarmData, name, dscr, alwaysUpdate)


def updateDeviceByUnit(Unit: int, alarmLevel, alarmData, name: str = '', dscr: str = '', alwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if (alarmData != Devices[Unit].sValue) or (int(alarmLevel) != Devices[Unit].nValue or alwaysUpdate is True):
            if(len(name) <= 0):
                Devices[Unit].Update(int(alarmLevel), alarmData, Description=dscr)
            else:
                Devices[Unit].Update(int(alarmLevel), alarmData, Name=name,
                                     Description=dscr)
            Domoticz.Log("BLZ: Updated to: {} value: {}".format(
                alarmData, alarmLevel))
        else:
            Domoticz.Log("BLZ: Remains Unchanged")
    else:
        Domoticz.Error(
            "Devices[{}] is unknown. So we cannot update it.".format(Unit))


def updateImageByDevId(devId: str, picture):
    unit = getUnit4DeviceID(devId)
    updateImageByUnit(unit, picture)


# Synchronise images to match parameter in hardware page
def updateImageByUnit(Unit: int, picture):
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
        Domoticz.Error("Image: Unit or Picture {} unknown".format(picture))
        Domoticz.Error("Number of icons loaded = " + str(len(Images)))
        for image in Images:
            Domoticz.Error("Image: {} id: {} name: {}".format(image, Images[image].ID, Images[image].Name))
    return
