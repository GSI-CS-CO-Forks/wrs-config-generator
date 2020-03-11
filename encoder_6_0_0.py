
# Jean-Claude Bau, CERN, 2019

import settings
from item import Item
import item
from encoder_5_0 import Encoder_5_0

class Encoder_6_0_0(Encoder_5_0):
    
    def __init__(self):
       super(Encoder_6_0_0, self).__init__()
 
    def getGlobalConfig(self, gblConfig):
        lines=super(Encoder_6_0_0, self).getGlobalConfig(gblConfig)
        # Set Clock class
        clockClassArr=(("CONFIG_TIME_BC",248),
                       ("CONFIG_TIME_GM",6),
                       ("CONFIG_TIME_FM",193),
                       ("CONFIG_TIME_ARB_GM",13)
                       )
        clockClass=248
        for key, clk in clockClassArr :
            if self.isItemNameDefined(key) :
                if self.getItem(key).getValue()=="y" :
                    clockClass=clk;
                    break;
        lines.append(self.buildEntry(self.getItem("CONFIG_PTP_OPT_CLOCK_CLASS",str(clockClass))))
            
        # SNMP_SYSTEM_CLOCK
        enabled=False
        if self.isItemNameDefined("CONFIG_NTP_SERVER") :
            ntpServerItem=self.getItem("CONFIG_NTP_SERVER")
            if len(ntpServerItem.getValue()) > 0 : # Ntp server set
                enabled=True
        if enabled :
            # Set drift to 3 seconds and check every 10 minutes
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_MONITOR_ENABLED","y")))
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_DRIFT_THOLD","3")))
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_UNIT_HOURS","y")))
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_UNIT_DAYS","n")))
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_UNIT_MINUTES","n")))
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_CHECK_INTERVAL_HOURS","1")))
        else :
            lines.append(self.buildEntry(self.getItem("CONFIG_SNMP_SYSTEM_CLOCK_MONITOR_ENABLED","n")))
        return lines
 
    # Add port configuration for version 5.1.0 to ...
    def getPortsConfig(self, ports ):
        # if one slave port and all other ports are master then externalPortConfiguration is used.
        # Are considered as master port :
        #    - master (obvious)
        #    - non-wr (WR extension + monitoring disabled)
        #    - none   (Empty port ) 
        # externalPortConfiguration is also possible only if it is a boundary clock
        isTimeBC=False
        if self.isItemNameDefined("CONFIG_TIME_BC") :
            anItem=self.getItem("CONFIG_TIME_BC")
            isTimeBC=anItem.getValue()=="y"
        lines =[]
        nbPorts=18
        PORT_DB_range=range(1, nbPorts+1) # 1..18
    
        # Check all ports
        isExternalPortConfiguration=False
        if isTimeBC :
            nbSlaves=0
            nbMasters=0
            for port_item in ports:
                ptpRole=port_item["ptpRole"]
                if ptpRole=="slave" :
                    nbSlaves+=1
                elif ptpRole=="master" or ptpRole=="none" or ptpRole=="non-wr" : 
                    nbMasters+=1
            isExternalPortConfiguration=(nbSlaves==1) and nbMasters==(nbPorts-1)
        
        # Enable external port configuration only for a boundary clock
        lines.append(self.buildEntry(
            self.getItem("CONFIG_PTP_OPT_EXT_PORT_CONFIG_ENABLED",
                         "y" if isExternalPortConfiguration else "n",item.itemTypeBool)))
        lines.append(self.buildEntry(self.getItem("CONFIG_PTP_SLAVE_ONLY","n")))
        for port_item in ports:
            port_id = int(port_item["portNumber"])
            ptpRole = port_item["ptpRole"]
            # check the range of ports
            if not (1 <= port_id <= 18):
                print ("Error: Port %s out of range!" % port_item["portNumber"]) 
                continue
            
            # remove current port id from the list
            PORT_DB_range.remove(port_id)
            
            # Configure port
            portCfgName="CONFIG_PORT%02u" % (port_id)
            lines.append(self.buildEntry(
                self.getItem("%s_IFACE" % (portCfgName),"wri%u" % (port_id),item.itemTypeString)))
            lines.append(self.buildEntry(
                self.getItem("%s_FIBER" % (portCfgName), port_item["fiber"],item.itemTypeInt)))
            lines.append(self.buildEntry(
                self.getItem("%s_CONSTANT_ASYMMETRY" % (portCfgName),"0")))
            
            if ptpRole=="none" :
                lines.append(self.buildEntry(
                    self.getItem("%s_INSTANCE_COUNT_0" % (portCfgName),"y")))
                continue # Empty port 

            lines.append(self.buildEntry(
                    self.getItem("%s_INSTANCE_COUNT_1" % (portCfgName),"y")))
            
                        
            # Configure port instance (Only one for the moment)
            instCfgName="%s_INST01" % (portCfgName)
            profile= "WR" if ptpRole!="none" else "PTP"
            lines.append(self.buildEntry(
                self.getItem("%s_PROFILE_%s" % (instCfgName,profile),"y")))
            if ( isExternalPortConfiguration ) :
                lines.append(self.buildEntry(
                    self.getItem("%s_DESIRADE_STATE_%s" % (
                        instCfgName,
                        "SLAVE" if ptpRole=="slave" else "MASTER"
                        ),"y")))
            else :
                if ptpRole=="slave" or ptpRole=="auto" :
                    lines.append(self.buildEntry(self.getItem("%s_BMODE_AUTO" % (instCfgName),"y")))
                else :
                    lines.append(self.buildEntry(self.getItem("%s_BMODE_MASTER_ONLY" % (instCfgName),"y")))
            lines.append(self.buildEntry(
                self.getItem("%s_MONITOR" % (instCfgName),"y" if port_item["ptpRole"]!="non-wr" else "n",)))
            lines.append(self.buildEntry(
                self.getItem("%s_PROTOCOL_RAW" % (instCfgName),"y" if port_item["proto"]=="raw" else "n")))
            lines.append(self.buildEntry(
                self.getItem("%s_PROTOCOL_UDP_IPV4" % (instCfgName),"y" if port_item["proto"]=="udp" else "n")))
            lines.append(self.buildEntry(
                self.getItem("%s_EGRESS_LATENCY" % (instCfgName),port_item["dtx"],item.itemTypeInt)))
            lines.append(self.buildEntry(
                self.getItem("%s_INGRESS_LATENCY" % (instCfgName),port_item["drx"],item.itemTypeInt)))
            lines.append(self.buildEntry(
                    self.getItem("%s_ASYMMETRY_CORRECTION_ENABLE" % (instCfgName),"y")))
            lines.append(self.buildEntry(
                self.getItem("%s_MECHANISM_E2E" % (instCfgName),"y")))
            lines.append(self.buildEntry(
                self.getItem("%s_ANNOUNCE_INTERVAL" % (instCfgName),"1")))
            lines.append(self.buildEntry(
                self.getItem("%s_ANNOUNCE_RECEIPT_TIMEOUT" % (instCfgName),"3")))
            lines.append(self.buildEntry(
                self.getItem("%s_SYNC_INTERVAL" % (instCfgName),"0")))
            lines.append(self.buildEntry(
                self.getItem("%s_MIN_DELAY_REQ_INTERVAL" % (instCfgName),"0")))
            
        # add empty port entries if needed
        for i in PORT_DB_range:
            portCfgName="CONFIG_PORT%02u" % (i)
            lines.append( self.buildEntry(
                self.getItem("%s_IFACE" % (portCfgName),"wri%u" % (i),item.itemTypeString)))
            lines.append(self.buildEntry(
                self.getItem("%s_FIBER" % (portCfgName), "0",item.itemTypeInt)))
            lines.append(self.buildEntry(
                self.getItem("%s_CONSTANT_ASYMMETRY" % (portCfgName),"0",item.itemTypeInt)))
            lines.append(self.buildEntry(
                self.getItem("%s_INSTANCE_COUNT_0" % (portCfgName),"y",item.itemTypeBool)))
        return lines
    
    def getSfpsConfig(self, sfps):
        lines=super(Encoder_6_0_0,self)._getSfpsConfig(sfps,18,False)
        lines[:0] = [self.buildEntry(
                self.getItem("CONFIG_N_SFP_ENTRIES",str(len(lines)),item.itemTypeInt))] 
        return lines

    def getFibersConfig(self, fibers):
        lines=super(Encoder_6_0_0,self)._getFibersConfig(fibers,18,False)
        lines[:0] = [self.buildEntry(
                self.getItem("CONFIG_N_FIBER_ENTRIES",str(len(lines)),item.itemTypeInt))] 
        return lines

    def getVLansConfig(self, vlanPorts, vlans):
        lines=[]
        lines.append(self.buildEntry(self.getItem("CONFIG_VLANS_ENABLE","y")))
        lines.append(self.buildEntry(self.getItem("CONFIG_VLANS_RAW_PORT_CONFIG","y")))
        lines+=self._getVLansPorts(vlanPorts)
        lines+=self._getVLansVlan(vlans)
        return lines
 
    def _getVLansPorts(self, ports):
        PORT_DB_range=list(range(1, 19)) # 1..18
        lines=[]
        for vlan_port_data in ports:
            portNumber=int(vlan_port_data["portNumber"])
            vlanPortMode = vlan_port_data["vlanPortMode"]
            vlanPortVid = vlan_port_data["vlanPortVid"] 
            vlanPortPrio=vlan_port_data["vlanPortPrio"]
            vlanPortUntagged=vlan_port_data["vlanPortUntag"]
            try:
                vlanPortPtpVid=vlan_port_data["vlanPortPtpVid"]
            except :
                vlanPortPtpVid=None
            try:
                vlanPortPtpVidEnabled=vlan_port_data["vlanPortPtpVidEnabled"]
            except :
                vlanPortPtpVidEnabled=None
            prefix="CONFIG_VLANS_PORT%02u" % (portNumber)
            
            PORT_DB_range.remove(portNumber)

            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_ACCESS","y" if vlanPortMode == "access" else "n")))
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_TRUNK","y" if vlanPortMode == "trunk" else "n")))
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_MODE_UNQUALIFIED","y" if vlanPortMode == "unqualified" else "n")))
            lines.append(self.buildEntry(
                self.getItem(prefix+"_MODE_DISABLED","y" if vlanPortMode == "disabled" else "n")))
        
            if vlanPortUntagged=="true" :
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_ALL","y")));
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_NONE","n")));
            else : 
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_ALL","n")));
                lines.append(self.buildEntry(self.getItem(prefix+"_UNTAG_NONE","y")));
            
            lines.append(
                    self.buildEntry(self.getItem(prefix+"_PRIO" , vlanPortPrio if vlanPortPrio!=None else "-1" ,item.itemTypeInt)))
        
            # Evaluate PTP VID
            if vlanPortPtpVid==None or vlanPortPtpVidEnabled==None :
                # Does not exists yet in CCDE
                vlanPortPtpVid=vlanPortVid
                if vlanPortMode=="trunk" or vlanPortMode=="unqualified" or vlanPortMode=="disabled":
                    vlanPortVid="" # in this case VID is used to set only PTP_VID
            elif vlanPortPtpVidEnabled=="n":
                #PTP VID exists in CCDE but we use the default behavior 
                 vlanPortPtpVid=vlanPortVid
                 
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_VID", vlanPortVid if vlanPortVid!=None else "",item.itemTypeString)))
            
            lines.append(self.buildEntry(
                    self.getItem(prefix+"_PTP_VID", vlanPortPtpVid if vlanPortPtpVid!=None else "",item.itemTypeString)))
                 
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
