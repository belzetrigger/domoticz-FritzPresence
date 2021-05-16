from blz import fakeDomoticz
from blz.fakeDomoticz import Images, Parameters
from blz.fakeDomoticz import Devices
import unittest
import sys
import logging
import codecs


sys.path.insert(0, "..")
from blz.blzHelperInterface import BlzHelperInterface
from plugin import BasePlugin


from fritzhelper.fritzHelper import FritzHelper
import configparser

CONFIG_SECTION = "fritzbox"

# set up logger
logger = logging.getLogger()
logger.level = logging.DEBUG

Parameters['bla']='sds'


class Test_plugin(unittest.TestCase):

    def createPlugin(self, macList = None):
        plugin = BasePlugin()  #plugin()        
        config = configparser.ConfigParser()
        config.read_file(codecs.open(r"./test/my_config.ini", encoding="utf-8"))
        self.assertTrue(
            config.has_section(CONFIG_SECTION),
            "we need this config to connect to fritzBox",
        )
        Parameters["Mode1"] = config.get(CONFIG_SECTION, "ip")
        Parameters["Username"] = config.get(CONFIG_SECTION, "user")
        Parameters["Password"] = config.get(CONFIG_SECTION, "pw")
        Parameters["Mode5"] = macList
        Parameters["Mode6"]= 'Debug'
        return plugin

    def setUp(self): 
        # work around logger
        self.stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.stream_handler)
        logging.getLogger().info("# set up test for fritz base plugin")
        self.plugin = self.createPlugin()
        
    def tearDown(self):
        Parameters.clear()
        Images.clear()
        Devices.clear()
        logging.getLogger().info("# tear down: test for fp")
        if self.plugin:
            self.plugin = None
        # remove logger
        logger.removeHandler(self.stream_handler)

    def test_onStart(self):
        logging.getLogger().info("#onStart: test for fp")
        plugin = self.createPlugin()
        plugin.onStart()
        
    def test_onHeartbeat(self):
        logging.getLogger().info("#onHeartBeat: test for fp")
        plugin = self.createPlugin()
        plugin.onHeartbeat()

    def test_onStartMacList(self):
        logging.getLogger().info("#onStart: test for using mac Lists Parameter")
        # pass mac to plugin
        plugin = self.createPlugin('74:AB:93:21:35:54')
        plugin.onStart()
        self.assertEquals(len(Devices), 2)

    def test_onStartMacListAndOldDevice(self):
        logging.getLogger().info("#onStart: test for using mac Lists Parameter and having already entries in Devices")
        #using fake device: 
        fakeMac:str='AA:AB:93:21:35:54'
        fakeDomoticz.Device(Name=fakeMac, Unit=2, TypeName="Switch",
                        DeviceID=fakeMac,
                        Options={"Custom": ("1;Foo")}, Used=1).Create()
        
        self.assertEquals(len(Devices), 1)
        # pass mac to plugin
        plugin = self.createPlugin('74:AB:93:21:35:54')
        plugin.onStart()
        self.assertEquals(len(Devices), 3)

    def test_onStop(self):
        logging.getLogger().info("#onStop: test for fp")
        self.plugin.onStop()
        

    def test_onStartMissingUserPassword(self):
        logging.getLogger().info("#test with out password: test for fp")
        Parameters["Username"]= None
        Parameters["Password"]= None        
        with self.assertRaises(ValueError):
            self.plugin.onStart()
        

if "__main__" == __name__:
    unittest.main()
