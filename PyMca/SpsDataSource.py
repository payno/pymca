#/*##########################################################################
# Copyright (C) 2004-2006 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem to you.
#############################################################################*/
import DataObject
import types
import copy
import spswrap as sps

SOURCE_TYPE = 'SPS'

class SpsDataSource:
    def __init__(self, name, object=None, copy = True):
        if type(name) != types.StringType:
            raise TypeError,"Constructor needs string as first argument"
        self.name = name
        self.sourceName = name
        self.sourceType=SOURCE_TYPE

    def getSourceInfo(self):
        """
        Returns information about the Spec version in self.name
        to give application possibility to know about it before loading.
        Returns a dictionary with the key "KeyList" (list of all available keys
        in this source). Each element in "KeyList" is an shared memory
        array name.
        """
        return self.__getSourceInfo()
        
    def getKeyInfo(self,key):
        if key in self.getSourceInfo()['KeyList']:
            return self.__getArrayInfo(key)
        else:
            return {}
                
    def getDataObject(self,key_list,selection=None):
        if type(key_list) != types.ListType:
            nolist = True
            key_list=[key_list]
        else:
            output = []
            nolist = False
        if self.name in sps.getspeclist():
            sourcekeys = self.getSourceInfo()['KeyList']
            for key in key_list:
                #a key corresponds to an array name
                if key not in sourcekeys:
                    raise KeyError,"Key %s not in source keys" % key
                #array = key
                #create data object
                data = DataObject.DataObject()
                data.info=self.__getArrayInfo(key)
                data.info ['selection'] = selection
                """
                info["row"]=row
                info["col"]=col
                if info["row"]!="ALL":
                    data= sps.getdatarow(self.SourceName,array,info["row"])
                    if data is not None: data=Numeric.reshape(data,(1,data.shape[0]))
                elif info["col"]!="ALL":
                    data= sps.getdatacol(self.SourceName,array,info["col"])
                    if data is not None: data=Numeric.reshape(data,(data.shape[0],1))
                else: data=sps.getdata (self.SourceName,array)
                """
                data.data=sps.getdata (self.name,key)
                if nolist:
                    if selection is not None:
                        return data.select(selection)
                    else:
                        return data
                else:
                    output.append(data.select(selection))
            return output
        else:
            return None

    def __getSourceInfo(self):
        arraylist= []
        sourcename = self.name
        for array in sps.getarraylist(sourcename):
            arrayinfo= sps.getarrayinfo(sourcename, array)
            arraytype= arrayinfo[2]
            arrayflag= arrayinfo[3]
            if arrayflag in (sps.IS_ARRAY, sps.IS_MCA, sps.IS_IMAGE) and arraytype!=sps.STRING:
                    arraylist.append(array)
        source_info={}
        source_info["Size"]=len(arraylist)
        source_info["KeyList"]=arraylist
        return source_info


    def __getArrayInfo(self,array):
        info={}
        info["SourceType"]  = SOURCE_TYPE
        info["SourceName"]  = self.name
        info["Key"]         = array
        
        arrayinfo=sps.getarrayinfo (self.name,array)
        info["rows"]=arrayinfo[0]
        info["cols"]=arrayinfo[1]
        info["type"]=arrayinfo[2]
        info["flag"]=arrayinfo[3]
        counter=sps.updatecounter (self.name,array)
        info["updatecounter"]=counter

        envdict={}
        keylist=sps.getkeylist (self.name,array+"_ENV")
        for i in keylist:
            val=sps.getenv(self.name,array+"_ENV",i)
            envdict[i]=val
        info["envdict"]=envdict

        calibarray= array + "_PARAM"
        if calibarray in sps.getarraylist(self.name):
            try:
                data= sps.getdata(self.name, calibarray)
                updc= sps.updatecounter(self.name, calibarray)
                info["EnvKey"]= calibarray
                info["McaCalib"]= data.tolist()[0]
                info["env_updatecounter"]= updc
            except:
                pass

        if array in ["XIA_DATA", "XIA_BASELINE"]:
            envarray= "XIA_DET"
            if envarray in sps.getarraylist(self.name):
                try:
                    data= sps.getdata(self.name, envarray)
                    updc= sps.updatecounter(self.name, envarray)
                    info["EnvKey"]= envarray
                    info["Detectors"]= data.tolist()[0]
                    info["env_updatecounter"]= updc
                except:
                    pass
        
        return info

    def isUpdated(self, sourceName, key):
        if sps.specrunning(sourceName):
            if sps.isupdated(sourceName, key):
                return True
        return False

source_types = { SOURCE_TYPE: SpsDataSource}

def DataSource(name="", object=None, copy=True, source_type=SOURCE_TYPE):
  try:
     sourceClass = source_types[source_type]
  except KeyError:
     #ERROR invalid source type
     raise TypeError,"Invalid Source Type, source type should be one of %s" % source_types.keys()
  
  return sourceClass(name, object, copy)

        
if __name__ == "__main__":
    import sys,time

    try:
        specname=sys.argv[1]
        arrayname=sys.argv[2]        
        obj  = DataSource(specname)
        data = obj.getData(arrayname)
        #while(1):
        #    time.sleep(1)
        #    print obj.RefreshPage(specname,arrayname)
        print "info = ",data.info
    except:
        print "Usage: SpsDataSource <specversion> <arrayname>"
        sys.exit()

