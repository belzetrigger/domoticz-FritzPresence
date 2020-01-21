

# domoticz-FritzPresence
Presence Detector that works with your [Fritz!Box](https://en.avm.de/, 'Fritz!Box are quite famous router from avm').
<!---
[![GitHub license](https://img.shields.io/github/license/belzetrigger/domoticz-FritzBox.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/blob/master/LICENSE)
-->

[![PyPI pyversions](https://img.shields.io/badge/python-3.6%20|%203.7%20|%203.8-blue.svg)]() 
[![Plugin version](https://img.shields.io/badge/version-0.6.2-red.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/branches/)

## Summary
Instead of pinging the device this presence detector uses the host list from the router to check if device is there or not. 
Benefit - Normally this also works if devices like smart phones save some battery. 

<i>Note: If connection between router and device got lost, this can take some time till router marks it as 'not connected'
This plugin only works with Fritz Box. </i>

User is shown like this in domoticz. 

<img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/switch_on.PNG' width="200" alt="switch device - on">

<img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/switch_off.PNG' width="200" alt="switch device - off">

This plugin is open source.

This is more or less just a wrapper around python lib [fritzconnection](https://github.com/kbr/fritzconnection) from Klaus Bremer.
Person Images are from [DomoticzIcons](https://drive.google.com/folderview?id=0B-ZLFoCiqzMRSkFaaWdHV1Qxbm8&usp=sharing) see [Domoticz Wiki](https://www.domoticz.com/wiki/Custom_icons_for_webinterface)

## Prepare 
- set up your Fritz!Box
  - enable TR064
  - create a user
  - set password
  - assign rights to this user
  
## Installation and Setup
- a running Domoticz, tested with 4.10717 and Python 3.8
- Python >= 3.6 (mainly depending on requirements for fritzconnection)
- install needed python modules:
    - fritzconnection version 1.2.1
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzPresence.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- make sure downloaded modules are in path eg. sitepackages python paths or change in plugin.py the path
```bash
import sys
sys.path
sys.path.append('/usr/lib/python3/dist-packages')
# for synology python3 from community
# sys.path.append('/volume1/@appstore/python3/lib/python3.5/site-packages')
# for synology sys.path.append('/volume1/@appstore/py3k/usr/local/lib/python3.5/site-packages')
# for windows check if installed packages as admin or user...
# sys.path.append('C:\\Program Files (x86)\\Python37-32\\Lib\\site-packages')
```
- restart Domoticz service
- Now go to **Setup**, **Hardware** in your Domoticz interface. There add
**Fritz!Presence Plugin**.
### Settings
<!-- prettier-ignore -->


| Parameter     | Information                                                                                                                                                                                                                                                                             |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name          | Domoticz standard hardware name. But here you can also add a ';' separated list of names for the devices to create. <br/><img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/config_name_double.PNG' width="100" alt="config: name with two entries"> |
| host          | insert host name or Ip of your fritz box. Normally fritz.box                                                                                                                                                                                                                            |
| user          | the user you have set up in your FritzBox                                                                                                                                                                                                                                               |
| password      | keep in mind, domoticz stores it plain in the database!!!! So really create a new user with restricted rights                                                                                                                                                                           |
| MAC Addresses | can hold a single or multiple ';' separated list of MAC addresses   <br/>  <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/config_mac_double.PNG' width="100" alt="config: mac with two entries">                                                 |
| Debug         | if True, the log will be hold a lot more output.                                                                                                                                                                                                                                        |
## Bugs and ToDos
- On windows system changing icons for sensors did not work, so it's standard switch icon.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart services it works fine.                                                                  

## Versions
| Version | Note                                                                               |
| ------- | ---------------------------------------------------------------------------------- |
| 0.6.2   | supports ';' separated list of MAC and names                                       |
| \>= 0.6 | works with new fritzconnection 1.2.1 and so without need of lxml but Python >= 3.6 |
| <= 0.5  | worked with fritzconnection 0.6.x and 0.8.x, needs lxml                            |





## State
In development. Currently only this booth sensor are integrated. They work without user/password.

## Developing
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  `test.py` it's the entry point for tests




