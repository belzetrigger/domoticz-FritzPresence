# domoticz-FritzPresence
Presence Detector that works with your Fritz!Box. Fritz!Box are quite famous router from [AVM](https://en.avm.de/)

## Summary
Instead of pinging the device this presence detector uses the host list from the router to check if device is there or not. 
Benefit - Normally this also works if devices like smart phones save some battery. If connection between router and device got lost, this can take some time till router marks it as 'not connected'
This plugin only works with Fritz Box. 

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
- a running Domoticz, tested with 4.10038
- Python 3
- install needed python modules:
    - fritzconnection version 1.2.1
    - lxml is NO longer needed!
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzPresence.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- make sure downloaded moduls are in path eg. sitepackes python paths or change in plugin.py the path
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
   - host: insert host name or Ip
   - user
   - password - keep in mind, domoticz stores it plain in the database!!!!
     So really create a new user with restricted rights
   - Debug: if True, the log will be hold a lot more output.

## Versions
### till 0.8.x
- worked with fritzconnection 0.6.x and 0.8.x
  
### starting from 0.9.x
- works with new fritzconnection 1.2.1 and so without need of lxml

## Bugs and ToDos
- On windows system changing icons for sensors did not work, so it's standard switch icon.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart services it works fine.

## State
In development. Currently only this booth sensor are integrated. They work without user/password.

## Developing
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  `test.py` it's the entry point for tests




