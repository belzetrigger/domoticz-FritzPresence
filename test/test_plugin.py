from blz.fakeDomoticz import Parameters
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

    def createPlugin(self):
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
        Parameters["Mode5"] = None
        Parameters["Mode6"]= 'Debug'
        return plugin

    def setUp(self): 
        # work around logger
        self.stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.stream_handler)
        logging.getLogger().info("# set up test for fritz base plugin")
        self.plugin = self.createPlugin()
        
    def tearDown(self):
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
