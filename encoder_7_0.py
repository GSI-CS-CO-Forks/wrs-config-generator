# Maciej Suminski, CERN, 2024
import settings
from item import Item
import item
from encoder_6_0_0 import Encoder_6_0_0

class Encoder_7_0(Encoder_6_0_0):

    def __init__(self):
        super(Encoder_7_0, self).__init__()

    def getPortsConfig(self, ports):
        lines = super(Encoder_7_0, self).getPortsConfig(ports)
        assert(len(ports) == self.nbPorts)

        for port, portDesc in zip(range(1, self.nbPorts + 1), ports):
            portCfgName = "CONFIG_PORT{0:02}".format(port)

            # Since the default values are used, add *_OVERWRITE=n to mute missing config warnings
            # note that these lines could have been added in items.cfg, but it is 90 lines...
            for attrib in ("ANNOUNCE_INTERVAL", "ANNOUNCE_RECEIPT_TIMEOUT",
                    "MIN_DELAY_REQ_INTERVAL", "MIN_PDELAY_REQ_INTERVAL", "SYNC_INTERVAL"):
                cfg_name = "{0}_INST01_{1}_OVERWRITE".format(portCfgName, attrib)
                lines.append(self.buildEntry(self.getItem(cfg_name, "n")))

            # Port profile
            profileCfg = None

            if portDesc["ptpRole"] == "none":       # port disabled
                pass
            elif portDesc["ptpRole"] == "non-wr":   # plain PTP
                profileCfg = "{0}_INST01_PROFILE_PTP".format(portCfgName)
            else:
                profileCfg = "{0}_INST01_PROFILE_HA_WR".format(portCfgName)

            if profileCfg:
                lines.append(self.buildEntry(self.getItem(profileCfg, "y")))


        extPortCfg = self.isExternalPortConfig(ports)
        lines.append(self.buildEntry(self.getItem("CONFIG_PTP_OPT_BMCA_STANDARD",
            "n" if extPortCfg else "y")))
        lines.append(self.buildEntry(self.getItem("CONFIG_PTP_OPT_BMCA_EXT_PORT_CONFIG",
            "y" if extPortCfg else "n")))

        return lines
