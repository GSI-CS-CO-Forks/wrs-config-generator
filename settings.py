# Jean-Claude Bau, CERN, 2019

import re
import item
from item import Item
from encoder_5_0 import Encoder_5_0
from encoder_6_0_0 import Encoder_6_0_0


# Supported FW versions
fw_version_supported = [
    "5.0",
    "5.0.1",
    "5.0-dev",
    "6.0.0",
    "6.0.1",
    "6.1",
    ]


#Methods used to generate port configuration
encoders = [
    {
        "encoder"   : Encoder_5_0(),
        "versions" : "5.0 5.0.1 5.0-dev"
        },
    {
        "encoder"   : Encoder_6_0_0(),
        "versions" : "6.0.0 6.0.1 6.1"
        },
    ]

def isFirmwareSupported (version):
    return version in fw_version_supported

def __isPresent ( str1, keyword):
    tokenList=str1.split(" ")

    for tk in tokenList :
        if tk == keyword :
            return True
    return False

def getEncoder(fwVersion):
    arrSize=len(encoders)
    for idx in range(arrSize):
        if __isPresent(encoders[idx]["versions"], fwVersion) :
            encoder=encoders[idx]["encoder"]
            encoder.setFwVersion(fwVersion)
            return encoder
    return None
