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
from typing import Any, Dict


Parameters: Dict[str, Any] = {}
Images: Dict[str, Any] = {}
Devices: Dict[str, Any] = {}


def Log(s):
    print(s)


def Debug(s):
    print("Debug: {}".format(s))


def Error(s):
    print("Error: {}".format(s))
