# Jean-Claude Bau, CERN, 2019

#import settings
from item import Item
import item
import settings
import re
import sys
import os

class Encoder(object):
    _fwVersion=None
    _items=[]
#     _wrsConfig=wrs_config.WrsConfig()
#
    def __init__(self):
        pass

    def getWrsConfig(self):
        return self.wrsConfig

    def setFwVersion(self,fwVersion):
        self._fwVersion=fwVersion
        self._loadItems()

    def _loadItems(self):
        # the directory of the script being run
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fileName="%s/kconfigs/v%s/items.cfg" % (script_dir,self._fwVersion)
        try:
            f=open(fileName, "r")
        except IOError:
            print("Cannot open file %s. I/O error %d: %s" % (fileNamee.errno, e.strerror))
            return False
        else:
            lines= f.readlines()
            f.close()

        for line in lines:
            anItem=None
            if self._decodeLine(line)==False :
                return False
        return True

    def __removeQuotes(self, str):
        return re.sub("(^\"|\"$)",'',str)

    def _decodeLine(self, line):
        if line == None :
            return None
        line=line.strip()
        if len(line) == 0 :
            return None
        if line[:1] == '#' :  # Comment
            return None
        tokens=line.split()
        if len(tokens)<2 :
            print ("Invalid entry : %s" % line)
            return False
        # Read actions
        actStr=self.__removeQuotes(tokens[0])
        actions=item.itemActionNone
        if "add" in actStr :
            actions=actions | item.itemActionAdd
        if "skip" in actStr :
            actions=actions | item.itemActionSkip
        #Read key=value
        kv=self.__removeQuotes(tokens[1])
        idx=kv.find('=')
        key=kv[0:idx] if idx != -1 else kv
        if idx !=-1 and ((idx+1)< len(kv)) :
            value=self.__removeQuotes(kv[idx+1:])
        else :
            value="" # default value
        type=item.itemTypeString # default value
        if len(tokens)>2 : # read type
            typeStr=self.__removeQuotes(tokens[2])
            if typeStr=="bool" :
                type=item.itemTypeBool
            elif typeStr=="int"  :
                type=item.itemTypeInt
            anItem=item.Item(key,value,type)
        else :
            anItem=item.Item(key,value)
        anItem.setActions(actions)
        self._items.append(anItem)
        return True


    def buildEntry(self,item):
#         self._wrsConfig.addItem(item)
        return item.toString()

    def getItem(self, name,value=None,type=item.itemTypeNone):
        for anItem in self._items :
            if anItem.getName() == name :
                if value!=None :
                    anItem.setValue(value)
                return anItem
        anItem=item.Item(name,value,type)
        self._items.append(anItem)
        return anItem


    def isItemToSkip(self, name):
        for anItem in self._items :
            if anItem.getName() == name :
                return (anItem.getActions() & item.itemActionSkip)==item.itemActionSkip
        return False

    def getItemsToAdd(self):
        it=[]
        for anItem in self._items :
            if (anItem.getActions() & item.itemActionAdd ) == item.itemActionAdd :
                it.append(anItem)
        return it

    def isItemNameDefined(self, name):
        for anItem in self._items :
            if anItem.getName() == name :
                return True
        return False
