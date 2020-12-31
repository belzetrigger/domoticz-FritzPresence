

# domoticz-FritzPresence
<!---
[![GitHub license](https://img.shields.io/github/license/belzetrigger/domoticz-FritzBox.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/blob/master/LICENSE)
-->

[![PyPI pyversions](https://img.shields.io/badge/python-3.6%20|%203.7%20|%203.8%203.9-blue.svg)]() 
[![Plugin version](https://img.shields.io/badge/version-0.6.4-red.svg)](https://github.com/belzetrigger/domoticz-FritzPresence/branches/)

Primary a Presence Detector that works with your [Fritz!Box](https://en.avm.de/, 'Fritz!Box are quite famous router from avm'). And also lets you add easily other known hosts from your Box to Domoticz.

| Device     | Image                                                                                                                                                                                                                                                                                      | Comment                                                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Admin      | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_admin.PNG' width="300" alt="admin">                                                                                                                                                        | Here you can add know hosts from your router to Domoticz, or remove them all.                                              |
| User       | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/switch_on.PNG' width="300" alt="switch device - on"><br><img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/switch_off.PNG' width="300" alt="switch device - off"> | User is shown like this in domoticz.  There might come from admin:add function or straight form the settings `MAC Address` |
| IoT        | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_iot_on.PNG' width="300" alt="iot - on">                                                                                                                                                    | If the device name matches the naming rule `IOT_NAME_PREFIXES`, the IOT picture will be used for it                        |
| Notebook   | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_notebook_on.PNG' width="300" alt="notebook - on">                                                                                                                                          | If the device name matches the naming rule `ICON_NOTEBOOK_PREFIXES`,                                                       |
| Pi         | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_pi_on.PNG' width="300" alt="Pi - on">                                                                                                                                                      | If the device name matches the naming rule `ICON_PI_PREFIXES`, the Raspberry Pi picture will be used for it                |
| Phone      | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_phone_on.PNG' width="300" alt="iot - on">                                                                                                                                                  | If the device name matches the naming rule `ICON_PHONE_PREFIXES`, the Mobile picture will be used for it                   |
| Tablet/Pad | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_pad_on.PNG' width="300" alt="iot - on">                                                                                                                                                    | If the device name matches the naming rule `ICON_TAB_PREFIXES`, the Pad picture will be used for it                        |
| TV         | <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/fp_switch_tv_on.PNG' width="300" alt="iot - on">                                                                                                                                                     | If the device name matches the naming rule `ICON_TV_PREFIXES`, the TV picture will be used for it                          |

## Summary
Originally this plugin was just for presence detection. But as I needed a bit more functions from [fritzconnection](https://github.com/kbr/fritzconnection), I extended it step by step.

Instead of pinging the device this presence detector uses the host list from the router to check if device is there or not. 
Benefit - Normally this also works if devices like smart phones save some battery. 

<i>Note: If connection between router and device got lost, this can take some time till router marks it as 'not connected'
This plugin only works with Fritz Box. </i>

This plugin is open source.

This is a wrapper around python lib [fritzconnection](https://github.com/kbr/fritzconnection) from Klaus Bremer.
Person Images are from [DomoticzIcons](https://drive.google.com/folderview?id=0B-ZLFoCiqzMRSkFaaWdHV1Qxbm8&usp=sharing), Domoticz Icon from [Domoticz Wiki](https://www.domoticz.com/wiki/Custom_icons_for_webinterface) and Raspberry Pi from Raspberry Foundation.

## Prepare 
- set up your Fritz!Box
  - enable TR064
  - create a user
  - set password
  - assign rights to this user
  
## Installation and Setup
- a running Domoticz: 2020.2 with Python 3.7
- Python >= 3.6 (mainly depending on requirements for fritzconnection)
- install needed python modules:
    - fritzconnection version 1.4.0
    - or use `sudo pip3 install -r requirements.txt` 
    - might be worth testing fritzconnection - just run `fritzconnection`
- clone project
    - go to `domoticz/plugins` directory 
    - clone the project
        ```bash
        cd domoticz/plugins
        git clone https://github.com/belzetrigger/domoticz-FritzPresence.git
        ```
- or just download, unzip and copy to `domoticz/plugins` 
- optional: adapt naming convention
  - what does it do: tries to scan name for this device for special chunks and pick different images for them
  - where: plugin.py 
  - what: eg  `ICON_PI_PREFIXES = ["RASPBERRY", "PI"]` will cause all devices containing PI to use raspberry image
- no need on Raspbian for sys path adaption if using sudo for pip3
- some extra work for Windows or Synology, make sure downloaded modules are in path eg. site-packages python paths or change in plugin.py / fritzHelper.py path
  - example adaption:
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


| Parameter     | Information                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| name          | Domoticz standard hardware name. But here you can also add a ';' separated list of names for the devices to create. <br/><img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/config_name_double.PNG' width="200" alt="config: name with two entries"> therefore see also MAC Addresses<br><b>Note: </b> If using the admin panel to add devices just enter a single hardware name. |
| host          | insert host name or IP Address of your fritz box. Normally `fritz.box`                                                                                                                                                                                                                                                                                                                                               |
| user          | the user you have set up in your FritzBox                                                                                                                                                                                                                                                                                                                                                                            |
| password      | keep in mind, domoticz stores it plain in the database!!!! So really create a new user with restricted rights                                                                                                                                                                                                                                                                                                        |
| MAC Addresses | can hold a single or multiple ';' separated list of MAC addresses   <br/>  <img src='https://github.com/belzetrigger/domoticz-FritzPresence/raw/master/resources/config_mac_double.PNG' width="200" alt="config: mac with two entries"> <br/><b>Note:</b> If you have a lot MACs you wish to add, it is better to use the admin panel to add known devices straight from Fritz!Box.                                  |
| Debug         | if True, the log will be hold a lot more output.                                                                                                                                                                                                                                                                                                                                                                     |
## Usage
### Admin
this functions are supported
* add WiFi devices
* add ethernet devices
* add active devices
* add all known devices

Keep in mind, normally a device must have been recent active to have a connection type. Also VPN devices are special, as they might not have a MAC-Address.

### Wake on LAN
To send magic packet just click on an `off` device to switch it on. WOL works only for ethernet. And the hardware must support it! For example the network adapter on Raspberry Pi 3 does not support it.

## Bugs and ToDos
- integrate a threshold, when it is more stressless for router to get full device list and parse this, instead of getting 20 devices/host information
- On windows system changing icons for sensors did not work, so it's standard switch icon.
- On windows system "update" the hardware breaks imported python libs. Plugin can not get data from FritzBox. But after restart services it works fine.                                                                  

## Versions
| Version | Note                                                                                     |
| ------- | ---------------------------------------------------------------------------------------- |
| 0.6.4   | small stability fixes, a bit restructure and tested with new version of lib              |
| 0.6.3   | button to add/remove know hosts from Fritz!Box to Domoticz and support for "Wake on LAN" |
| 0.6.2   | supports ';' separated list of MAC and names                                             |
| \>= 0.6 | works with new fritzconnection 1.2.1 and so without need of lxml but Python >= 3.6       |
| <= 0.5  | worked with fritzconnection 0.6.x and 0.8.x, needs lxml                                  |





## State
Under development but main function runs quite stabile.

## Developing
Based on https://github.com/ffes/domoticz-buienradar/ there are
 -  `fakeDomoticz.py` - used to run it outside of Domoticz
 -  inside folder `test` are small unittest cases
 -  before you can run them, copy `sample_config.ini` to `my_config.ini` and adapt values




