import unittest

from fritzhelper.fritzHelper import FritzHelper

# from fritzconnection.lib.fritzhosts import FritzHosts
# from fritzconnection.lib.fritzstatus import FritzStatus

import configparser

CONFIG_SECTION = "fritzbox"


class Test_fritzHelper(unittest.TestCase):
    def setUp(self):

        config = configparser.ConfigParser()
        config.read_file(open(r"./test/my_config.ini"))
        # config.read('my_config.ini')
        self.assertTrue(
            config.has_section(CONFIG_SECTION),
            "we need this config to connect to fritzBox",
        )
        fb_ip = config.get(CONFIG_SECTION, "ip")
        fb_user = config.get(CONFIG_SECTION, "user")
        fb_pw = config.get(CONFIG_SECTION, "pw")

        self.macDummyOutside = (
            "A4:4C:C8:0C:FF:FF"  # dummy mac this is never added to internal device list
        )
        self.macDummyUnknown = (
            "FF:4C:C8:0C:FF:FF"  # dummy mac that does not exist on box
        )

        self.macEtherPassive = None  # stores mac of ethernet dev. that is passive
        self.macEtherActive = None  # stores mac of ethernet dev. that is active
        self.macWifiActive = None  # stores mac of wifi dev. that is active
        self.ipWifiActive = None  # stores ip of wifi dev

        self.fh = FritzHelper(
            fbHost=fb_ip,
            fbUser=fb_user,
            fbPassword=fb_pw,
            macAddresses="",
            defaultNames="",
        )

    def tearDown(self):
        self.fh.reset()
        self.fh = None

    def test_init(self):
        self.fh.dumpConfig()

    def test_getSummary(self):
        """
        Test summary
        """
        # self.fh.readStatus()
        s = self.fh.getSummary()
        self.assertIsNotNone(s)
        s = self.fh.getShortSummary()
        self.assertIsNotNone(s)

    def test_getAllHosts(self):
        """
        try to fetch hosts from box
        """
        devices = self.fh.getAllHosts()
        # for x in devices:
        #    print(x)
        # check not empty and that it is iterable
        self.assertTrue(len(devices), "There should be some devices ....")

    def test_getActiveHosts(self):
        """
        try to fetch active hosts from box
        """
        devices = self.fh.getActiveHosts()
        # for x in devices:
        #    print(x)
        # check not empty and that it is iterable
        self.assertTrue(len(devices), "There should be some active devices ....")

    def test_getWifiHosts(self):
        """
        try to fetch wifi hosts from box
        """
        devices = self.fh.getWifiHosts()
        for x in devices:
            print(x)
        # check not empty and that it is iterable
        self.assertTrue(len(devices), "There should be some wifi devices ....")

    def test_getEthernetHosts(self):
        """
        try to fetch ethernet hosts from box
        """
        devices = self.fh.getEthernetHosts()
        for x in devices:
            print(x)
        # check not empty and that it is iterable
        self.assertTrue(len(devices), "There should be some ethernet devices ....")

    def test_initIps(self):
        """
        try to fetch active hosts from box
        """
        devices = self.fh.getWifiHosts()
        self.assertTrue(len(devices), "There should be some active devices ....")
        x = devices[0]
        if x:
            self.macWifiActive = x["mac"]
            self.ipWifiActive = x["ip"]
            self.assertTrue(self.macWifiActive)
            print("wifiActive: \t{}".format(x))
        else:
            raise Exception("could not init wifi devices")

        devices = self.fh.getEthernetHosts()
        for x in devices:
            if x["status"] is False and self.macEtherPassive is None:
                self.macEtherPassive = x["mac"]
                print("macEtherPassive: \t{}".format(x))
            elif self.macEtherActive is None:
                self.macEtherActive = x["mac"]
                self.assertTrue(self.macEtherActive)
                print("macEtherActive: \t{}".format(x))

            if self.macEtherPassive is not None and self.macEtherActive is not None:
                print("macEtherPassive: \t{}".format(self.macEtherPassive))
                print("macEtherActive: \t{}".format(self.macEtherActive))
                break

    def test_wakeOnLan(self):
        self.test_initIps()
        self.fh.wakeOnLan(self.macEtherActive)

        self.fh.wakeOnLan(self.macWifiActive)

    def test_devices(self):
        """
        playing with devices.
        just fetch randomly macs from box.
        add to list and check "Update" Status
        """
        self.test_initIps()
        self.fh.addDeviceByMac(self.macEtherActive)
        # default is using mac address, before getting real name from box
        self.assertEquals(
            self.fh.getDeviceName(self.macEtherActive), self.macEtherActive
        )

        # macs to devices
        self.fh.addDeviceByMac(self.macEtherPassive)
        self.assertEquals(
            self.fh.getDeviceName(self.macEtherPassive), self.macEtherPassive
        )

        self.fh.addDeviceByMac(self.macWifiActive)
        self.assertEquals(self.fh.getDeviceName(self.macWifiActive), self.macWifiActive)

        # get fresh state from box
        self.fh.readStatus()

        # Ethernet device validation
        self.assertTrue(self.fh.needsUpdate(self.macEtherActive))
        self.assertNotEquals(
            self.fh.getDeviceName(self.macEtherActive), self.macEtherActive
        )
        self.assertTrue(self.fh.isDeviceConnected(self.macEtherActive))
        self.assertFalse(self.fh.isDeviceConnected(self.macEtherPassive))

        # Wifi device validation
        self.assertTrue(self.fh.needsUpdate(self.macWifiActive))
        self.assertNotEquals(
            self.fh.getDeviceName(self.macWifiActive), self.macWifiActive
        )
        self.assertEquals(self.fh.getDeviceIP(self.macWifiActive), self.ipWifiActive)
        self.assertTrue(self.fh.isDeviceConnected(self.macWifiActive))
        # self.assertIsNotNone(self.fh.getDeviceName(self.macEtherActive))

        self.fh.readStatus()
        self.assertFalse(self.fh.needsUpdate(self.macEtherActive))
        self.assertFalse(self.fh.needsUpdate(self.macWifiActive))

    def test_buggy(self):
        """
        tests for buggy data
        """
        # pass method and arguments separately ...
        self.assertRaises(Exception, self.fh.validateDeviceIndex, self.macDummyOutside)

        # self.fh.addDeviceByMac(self.macDummyUnknown)
        # self.fh.isDeviceConnected(self.macDummyUnknown)


# fh.isDeviceConnected(mac)
# fh.getDeviceName()
# fh.needsUpdate(mac)


if "__main__" == __name__:
    unittest.main()
