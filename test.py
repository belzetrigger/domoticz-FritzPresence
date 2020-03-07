# just ot test FritzHelper a bit outside domoticz


from fritzHelper import FritzHelper


def runTest(fh: FritzHelper, mac: str):
    fh.dumpConfig()
    fh.readStatus()
    fh.dumpStatus()
    print("need Update: {}".format(fh.needsUpdate))
    fh.readStatus()
    print("need Update: {}".format(fh.needsUpdate))
    print("summary: {}".format(fh.getSummary()))
    print("summary short: {}".format(fh.getShortSummary()))
    print("summary short: {}".format(fh.getShortSummary("; ")))

    print("name:\t{}".format(fh.getDeviceName(mac)))


fh = FritzHelper("fritz.box", "", "", "", "")
runTest(fh, mac)
