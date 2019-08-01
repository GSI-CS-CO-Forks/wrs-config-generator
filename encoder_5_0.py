#!/usr/bin/env python2.7

# Jean-Claude Bau, CERN, 2019


#import settings
from encoder import Encoder
from wrs_config import WrsConfig
from item import Item
import item
import settings
import re
import sys
import time

class Encoder_5_0(Encoder):
    WrsConfig 
    
    def __init__(self):
       super(Encoder_5_0, self).__init__()
    
    def encode(self,json_data):
        lines=[]        
        # Add header 
        lines=self.getHeaderConfig(json_data)
        # Global config issue from CCDE
        lines+=self.getGlobalConfig(json_data["configurationItems"]);
        # Add port configuration
        lines+=self.getPortsConfig(json_data["configPorts"])
        # Add SFP entries
        lines+=self.getSfpsConfig(json_data["configSfp"])
        # Add SFP entries
        lines+=self.getFibersConfig(json_data["configFibers"])
        # Add items declare in the items.cfg file
        lines+=self.getExtraItemsConfig()
       #  Add VLan config
        lines+=self.getVLansConfig(json_data["configVlanPorts"],json_data["configVlans"])
        return lines

    def getHeaderConfig(self, json_data):
        lines =[]
                # get the current time
        gen_time = time.strftime("%Y-%m-%d+%H:%M:%S")
        dotconf_info = "gen_time=%s;" % gen_time

        if "requestedByUser" in json_data:
            gen_user = json_data["requestedByUser"]
            dotconf_info+="gen_user=%s;" % gen_user

        lines.append(self.buildEntry(self.getItem("CONFIG_DOTCONF_HW_VERSION",json_data["CONFIG_DOTCONF_HW_VERSION"])))
        lines.append(self.buildEntry(self.getItem("CONFIG_DOTCONF_FW_VERSION",self._fwVersion)))
        lines.append(self.buildEntry(self.getItem("CONFIG_DOTCONF_INFO",dotconf_info)))
        print "dotconf_info: %s" % dotconf_info 
        return lines

        
    def getGlobalConfig(self, gblConfig):        
        lines =[]
        for config_item in gblConfig:
            name=config_item["itemConfig"]
            if self.isItemToSkip(name):
                # skip configuration item
                continue
            else :
                value=config_item["itemValue"]
                if value == None:
                    continue
                anItem=None
                if self.isItemNameDefined(name):  #Already exist. The type must not be changed 
                    anItem=self.getItem(name,value)
                else :
                    type = item.itemTypeBool if re.match("(true|false)",value)!=None else item.itemTypeString
                    anItem=self.getItem(name,value,type)
                lines.append(self.buildEntry(anItem))
        return lines

    def getPortsConfig(self, ports ):
        lines =[]
        PORT_DB_range=range(1, 19) # 1..18
           
        for port_item in ports:
            port_id = int(port_item["portNumber"])
            # check the range of ports
            if not (1 <= port_id <= 18):
                print "Error: Port " + port_item["portNumber"] + " out of range!"
                continue
        
            # remove current port id from the list
            PORT_DB_range.remove(port_id)
            anItem=self.getItem("CONFIG_PORT%02u_PARAMS" % (port_id),
                              "name=wri%u,proto=%s,tx=%u,rx=%u,role=%s,fiber=%s" % (
                                    port_id,
                                    port_item["proto"],
                                    int(port_item["dtx"]),
                                    int(port_item["drx"]),
                                    port_item["ptpRole"],
                                    port_item["fiber"]
                                  ),item.itemTypeString )
            lines.append(self.buildEntry(anItem))
        # add empty port entries if needed
        for i in PORT_DB_range:
            anItem=self.getItem("CONFIG_PORT%02u_PARAMS" % (i))
            lines.append(self.buildEntry(anItem))
        return lines

    def getExtraItemsConfig(self):
        lines =[]
        items=self.getItemsToAdd()
        for extra_item in items:
            lines.append(self.buildEntry(extra_item))
        return lines

    def _getSfpsConfig(self, sfps, maxSfps,fillEmptySfps):
        SFP_DB_range=range(0, maxSfps) # 0..9
        lines=[]
        # Add CONFIG_SFP00_PARAMS
        for sfp_item in sfps:
            sfp_id = int(sfp_item["sfpId"])
            sfp_entry = ""
            # check the range of sfps
            if not (0 <= sfp_id <= (maxSfps-1)):
                print "Error: Port " + sfp_item["sfpId"] + " out of range!"
                continue
            # remove current sfp id from the list
            SFP_DB_range.remove(sfp_id)
            sfp_entry = "vn=%s,pn=%s," % (
                sfp_item["vendorName"],
                sfp_item["partNumber"],
                )
            if (sfp_item["vendorSerial"] != None):
                sfp_entry += "vs=%s," % (sfp_item["vendorSerial"])
            sfp_entry += "tx=%u,rx=%u,wl_txrx=%s" % (
                int(sfp_item["dtx"]),
                int(sfp_item["drx"]),
                sfp_item["wavelength"]
                )
            lines.append(self.buildEntry(
                        self.getItem("CONFIG_SFP%02u_PARAMS" % (sfp_id),sfp_entry)))
        # add empty sfp entries if needed
        if fillEmptySfps:
            for i in SFP_DB_range:
                lines.append(self.buildEntry(
                     self.getItem("CONFIG_SFP%02u_PARAMS" % (i),"")))
        return lines

    def getSfpsConfig(self, sfps):
        return self._getSfpsConfig(sfps,10,True)
    
    def _getFibersConfig(self, fibers, maxFibers, fillEmptyFibers):
        FIBER_DB_range=range(0, maxFibers) # 0..3
        lines=[]
        # Add CONFIG_FIBER00_PARAMS
        for fiber_item in fibers:
            fiber_id = int(fiber_item["fiberId"])
            # check the range of fibers
            if not (0 <= fiber_id <= (maxFibers-1)):
                print "Error: Port " + fiber_item["fiberId"] + " out of range!"
                continue
            # remove current fiber id from the list
            FIBER_DB_range.remove(fiber_id)
            lines.append(self.buildEntry(
                self.getItem("CONFIG_FIBER%02u_PARAMS" % (fiber_id),"alpha_%s=%s\"" % (
                fiber_item["waveLength"],
                fiber_item["alpha"])
                )))
        
        # add empty fiber entries if needed
        if fillEmptyFibers :
            for i in FIBER_DB_range:
                lines.append( self.buildEntry(
                    self.getItem("CONFIG_FIBER%02u_PARAMS" % (i) , "")))
        return lines

    def getFibersConfig(self, fibers):
        return  self._getFibersConfig(fibers,4, True)
    

    def getVLansConfig(self, vlanPorts, vlans):
        lines=[]
        lines.append(self.buildEntry(self.getItem("CONFIG_VLANS_ENABLE","y")))
        lines+=self._getVLansPorts(vlanPorts)
        lines+=self._getVLansVlan(vlans)
        return lines


    def _getVLansPorts(self, ports):
        PORT_DB_range=range(1, 19) # 1..18
        lines=[]
        for vlan_port_data in ports:
            portNumber=int(vlan_port_data["portNumber"])
            vlanPortMode = vlan_port_data["vlanPortMode"]
            vlanPortVid = vlan_port_data["vlanPortVid"] 
            vlanPortPrio=vlan_port_data["vlanPortPrio"]
            prefix="CONFIG_VLANS_PORT%02u" % (portNumber)
            
            PORT_DB_range.remove(portNumber)
            if vlanPortMode == "access":
                vlanPortUntagged=vlan_port_data["vlanPortUntag"] == "true"
                
                lines.append(self.buildEntry(self.getItem(prefix+"_MODE_ACCESS","y"))) 
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_ALL","y" if vlanPortUntagged else "n")))
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_NONE","n" if vlanPortUntagged else "y")))
            else:
                lines.append(self.buildEntry(self.getItem(prefix+"_MODE_ACCESS", "n")))
        
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_TRUNK","y" if vlanPortMode == "trunk" else "n")))
        
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_UNQUALIFIED","y" if vlanPortMode == "unqualified" else "n")))

            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_DISABLED","y" if vlanPortMode == "disabled" else "n")))
        
            lines.append(
                    self.buildEntry(self.getItem(prefix+"_PRIO" , vlanPortPrio if vlanPortPrio!=None else "-1" ,item.itemTypeInt)))
        
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_VID", vlanPortVid if vlanPortVid!=None else "",item.itemTypeString)))
        
        # add empty port entries if needed
        for i in PORT_DB_range:
            prefix="CONFIG_VLANS_PORT%02u" % (i)
            lines.append(self.buildEntry(self.getItem(prefix+"_MODE_ACCESS","n")))
            lines.append(self.buildEntry(self.getItem(prefix+"_MODE_TRUNK","n")))
            lines.append(self.buildEntry(self.getItem(prefix+"_MODE_DISABLED","n")))
            lines.append(self.buildEntry(self.getItem(prefix+"_MODE_UNQUALIFIED","y")))
            lines.append(self.buildEntry(self.getItem(prefix+"_PRIO","-1",item.itemTypeInt)))
            lines.append(self.buildEntry(self.getItem(prefix+"_VID","")))
        
        return lines
    
    def _getVLansVlan(self,vlans) :
        lines=[]
        VLANs_range = range(0, 4095) # 0..4094
        vlans_enable_set = {}
        
        if vlans == []:
            for i in range(1, 4): # 1..3
                lines.append(self.buildEntry(
                        self.getItem("CONFIG_VLANS_ENABLE_SET%u" % (i),"n")))
            return lines
        
        for vlan_data in vlans:
            vlan_conf_string = ""
            if vlan_data["vid"] == None:
                # this should never happen...
                print "Error: Vid not defined!"
                continue
            vid=int(vlan_data["vid"])
            if not (0 <=  vid <= 4094):
                # this should never happen...
                print "Error: Vid not in the range!"
                continue
    
            if vlan_data["fid"] != None:
                vlan_conf_string += "fid=%s," % vlan_data["fid"]
            if vlan_data["prio"] != None:
                vlan_conf_string += "prio=%s," % vlan_data["prio"]
            if vlan_data["drop"] == "true":
                vlan_conf_string += "drop=y,"
            if vlan_data["ports"] != None:
                vlan_conf_string += "ports=%s," % vlan_data["ports"]
    
            # remove trailing comma if needed
            vlan_conf_string = vlan_conf_string.rstrip(',')
            lines.append(self.buildEntry(
                            self.getItem("CONFIG_VLANS_VLAN%0004u" % (vid), vlan_conf_string,item.itemTypeString)))
    
            # remove current vid from the list
            VLANs_range.remove(vid)
        
            if (0 <= vid <= 22):
                vlans_enable_set["1"] = "y"
            if (22 < vid <= 100):
                vlans_enable_set["2"] = "y"
            if (100 < vid <= 4094):
                vlans_enable_set["3"] = "y"
        
        # add empty vid entries if needed
        for i in VLANs_range:
            lines.append(self.buildEntry(
                        self.getItem("CONFIG_VLANS_VLAN%0004u" % (i),"")))
    
        for i in range(1, 4): # 1..3
            lines.append(self.buildEntry(
                     self.getItem("CONFIG_VLANS_ENABLE_SET%u" % (i),
                    "y" if vlans_enable_set.has_key(str(i)) else "n")))
        return lines
    