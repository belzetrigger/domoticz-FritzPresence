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
    descr :str = None
    level :int = None
    nValue: int = None
    LastLevel: int = None
    def __init__(self, aID:str) -> None:
        self.ID = aID
        self.Name = aID
        self.Unit = aID
        self.DeviceID = aID
        self.Value = aID
        pass
    
    def Create(self):
        pass


    def Update(self, alarmLevel:int, Name:str=None,alarmData:str=None, descr:str=None):
        self.level = alarmLevel
        self.Name = Name
        self.descr =descr
        pass

def Image(sZip:str):
    Debug("create image: "+sZip)
    img = X(sZip)
    Images[str] = img
    return img


def Device(Name:str, Unit:str, TypeName:str,
                        Used:bool=1,
                        Switchtype:int=18, Options:str=None):
    x = X(Unit)
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
