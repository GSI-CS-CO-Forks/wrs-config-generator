#!/usr/bin/env python2.7

# Jean-Claude Bau, CERN, 2019

import re

# List of item types
itemTypeNone=0
itemTypeInt=1
itemTypeBool=2
itemTypeString=3

# List of actions
itemActionNone=0
itemActionAdd=1<<0
itemActionSkip=1<<1

class Item():
    __name=None
    __value=None
    __type=None
    __actions=itemActionNone
    
    def __init__(self,name,value=None,type=itemTypeNone):
        self.__name=name
        aValue=value
        if aValue==None :
            self.__type=itemTypeString
            aValue=""
        if type==itemTypeNone :
            v=aValue.lower()
            if re.match("(yes|y|true|no|n|false)",v) != None :
                type=itemTypeBool
            else :
                try:
                    int(v)
                    type=itemTypeInt
                except ValueError:
                    type=itemTypeString
        self.__type=type
        self.setValue(aValue)
     
    def setActions(self,actions):
        self.__actions=actions
         
    def getActions(self):
        return self.__actions
    
    @classmethod
    def __isAString(cls, object):
        return isinstance(object, str) or isinstance(object, unicode)
     
    def getName(self):
        return self.__name
    
    def getValue(self):
        return self.__value

    def setValue(self, value):
        if value == None :
            # Default values
            if self.__type == itemTypeBool :
                self.value="n"
            elif self.__type==itemTypeInt :
                self.__value="0"
            else :
                self.__value=""
        else :
            if self.__type == itemTypeBool : 
                self.__value="y" if re.match("[yYtT]",value[:1])!=None else "n"
            else :
                self.__value=value

    def getType(self):
        return self.__type
        
    def toString(self):
        line=None
        if self.__type == itemTypeInt :
            try :
                line="%s=%u" % (self.__name, int(self.__value))
            except ValueError:
                print "Cannot convert key %s to int value (\"%s\")\n"% (self.__name, self.__value)
        elif  self.__type == itemTypeBool :
            if self.__value == "y" :
                line="%s=%s" % (self.__name, self.__value)
            else : 
                line="# %s is not set" % (self.__name)
        else:
            line="%s=\"%s\"" % (self.__name, self.__value)
        return line
