#
#   Buienradar.nl Weather Lookup Plugin
#
#   Frank Fesevur, 2017
#   https://github.com/ffes/domoticz-buienradar
#
#   About the weather service:
#   https://www.buienradar.nl/overbuienradar/gratis-weerdata
#
#   Very simple module to make local testing easier
#   It "emulates" Domoticz.Log() and Domoticz.Debug()
#
#from _typeshed import FileDescriptor
from typing import Any, Dict


Parameters: Dict[str, Any] = {"Mode1":None, "Mode2":None, "Mode3":None, "Mode4":None,"Mode5":None,"Mode6":"Debug"}
Images: Dict[str, Any] = {}
Devices: Dict[str, Any] = {}

class X:
    """
    fake class
    """
    ID:str = None
    Name:str = None
    Unit:str = None
    DeviceID = None
    sValue:str =  None
    Description :str = None
    level :int = None
    nValue: int = None
    LastLevel: int = None
    Image:str = None
    def __init__(self, aID:str, Name:str=Name,DeviceID:str =None,Image:str=None) -> None:
        self.ID = aID
        if(Name):
            self.Name = Name
        else:
            self.Name = aID
        self.Unit = aID
        if(DeviceID):
            self.DeviceID = DeviceID
        else:
            self.DeviceID = aID    
        self.sValue = aID
        self.nValue = None
        self.Image = Image
        pass
    
    def Create(self):
        pass


    def Update(self, nValue:str,  sValue:str=None, Name:str=None,alarmData:str=None, Description:str=None,  Image=None):
        #self.level = alarmLevel
        self.Name = Name
        self.Description =Description
        self.nValue=nValue
        self.sValue=sValue
        self.Image = Image
        pass

def Image(sZip:str):
    Debug("create image: "+sZip)
    img = X(sZip)
    id = sZip.replace(".zip","")
    Images[id] = img
    return img


def Device(Name:str, Unit:str, TypeName:str,
                        Used:bool=1,
                        Switchtype:int=18, DeviceID:str=None,Options:str=None):
    x = X(Unit, Name=Name, DeviceID=DeviceID )
    Devices[Unit] = x
    return x

def Log(s):
    print(s)


def Debug(s):
    print("Debug: {}".format(s))


def Error(s):
    print("Error: {}".format(s))

def Debugging(i):
    print("Debug: turned on")