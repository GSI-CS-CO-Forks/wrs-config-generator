#!/usr/bin/env python2.7

# Jean-Claude Bau, CERN, 2019

# Supported FW versions
fw_version_supported = [
    "5.0",
    "5.0.1",
    "5.0-dev",
    "5.1.0"
    ]

# configuration items to add
items_to_add = [
    {
     "key"   : "CONFIG_KEEP_ROOTFS",
     "value" : "y",
     "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
     },
    {
     "key"   : "CONFIG_BR2_CONFIGFILE",
     "value" : '"wrs_release_br2_config"',
     "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
     },
    {
     "key"   : "CONFIG_ROOT_PWD_CLEAR",
     "value" : "y",
     "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
     },
    ]

# configuration items to skip
items_to_skip = [
        {
        "key" : "CONFIG_SNMP_SWCORESTATUS_HP_FRAME_RATE",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
        },
     {
        "key" : "CONFIG_SNMP_SWCORESTATUS_RX_FRAME_RATE",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
        },
     {
        "key" : "CONFIG_SNMP_SWCORESTATUS_RX_PRIO_FRAME_RATE",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    ]

# configuration items to convert from string to int
items_to_conv_num = [
    {
        "key" : "CONFIG_SNMP_TEMP_THOLD_FPGA",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_SNMP_TEMP_THOLD_PLL",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_SNMP_TEMP_THOLD_PSL",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_SNMP_TEMP_THOLD_PSR",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_NIC_THROTTLING_VAL",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_FAN_HYSTERESIS_T_ENABLE",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_FAN_HYSTERESIS_T_DISABLE",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    },
    {
        "key" : "CONFIG_FAN_HYSTERESIS_PWM_VAL",
        "versions" : "5.0 5.0.1 5.0-dev 5.1.0"
    }
    ]

def isFirmwareSupported (version):
    return version in fw_version_supported
    
def __isVersionValid ( versions, version):
    tokenList=versions.split(" ")

    for tk in tokenList :
        if tk == version :
            return 1
    return 0
    
def __listOfKeys(arr,version):
    keys = [] 
    arrSize=len(arr)
    for idx in range(arrSize) :
        if __isVersionValid(arr[idx]["versions"], version) :
            keys.append(arr[idx]["key"])
    return keys

def listOfAddedItemsKeys(version):
    return __listOfKeys (items_to_add, version)

def listOfSkippedItemsKeys(version):
    return __listOfKeys (items_to_skip, version)

def listOfNumericalItemsKeys(version):
    return __listOfKeys (items_to_conv_num, version)

def getAddedItemsKeyValue(key):
    arrSize=len(items_to_add)
    for idx in range(arrSize-1):
        if items_to_add[idx]["key"] == key :
            return key + "=" + items_to_add[idx]["value"]
    return ""

def __isItemPresent(arr,key,version): 
    arrSize=len(arr)
    for idx in range(arrSize):
        if arr[idx]["key"] == key :
            return __isVersionValid(arr[idx]["versions"], version)
    return 0
        
def isItemToSkip(key,version):
    return __isItemPresent(items_to_skip, key, version)
    
    
def isNumericalItem(key,version):
     return __isItemPresent(items_to_conv_num, key, version)



    
