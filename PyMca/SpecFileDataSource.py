#/*##########################################################################
# Copyright (C) 2004-2007 European Synchrotron Radiation Facility
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
__revision__ = "$Revision: 1.2$"

import DataObject
import specfilewrapper as specfile
import Numeric
import string
import types
import os

SOURCE_TYPE = "SpecFile"
DEBUG = 0

# Scan types
# ----------
SF_EMPTY       = 0        # empty scan
SF_SCAN        = 1        # non-empty scan
SF_MESH        = 2        # mesh scan
SF_MCA         = 4        # single mca
SF_NMCA        = 8        # multi mca (more than 1 mca per acq)
SF_UMCA        = 16       # mca number does not match pts number


class SpecFileDataSource:
    Error= "SpecFileDataError"

    def __init__(self, nameInput):
        if type(nameInput) == types.ListType:
            nameList = nameInput
        else:
            nameList = [nameInput]
        if len(nameList) > 1:
            #who knows if one day will make selections thru several files...
            raise TypeError,"Constructor needs string as first argument"    
        for name in nameList:
            if type(name) != types.StringType:
                raise TypeError,"Constructor needs string as first argument"            
        self.sourceName   = nameInput
        self.sourceType   = SOURCE_TYPE
        self.__sourceNameList = nameList
        self._sourceObjectList=[]
        for name in self.__sourceNameList:
            if not os.path.exists(name):
                raise "ValueError","File %s does not exists" % name
        for name in self.__sourceNameList:
            self._sourceObjectList.append(specfile.Specfile(name))
        self.__lastKeyInfo = {}

    def getSourceInfo(self):
        """
        Returns information about the specfile object created by
        the constructor to give application possibility to know about
        it before loading.
        Returns a dictionary with the key "KeyList" (list of all available keys
        in this source). Each element in "KeyList" has the form 'n1.n2' where
        n1 is the scan number and n2 the order number in file starting at 1.
        """
        return self.__getSourceInfo()

    def __getSourceInfo(self):
        scanlist=self.__getScanList()
        source_info={}
        source_info["Size"]       = len(scanlist)
        source_info["KeyList"]    = scanlist
        source_info["SourceType"] = SOURCE_TYPE

        num_mca=[]
        num_pts=[]
        commands=[]
        sf_type=[]
        for i in scanlist:
            sel=self._sourceObjectList[0].select(i)
            try: n= sel.nbmca()
            except: n= 0
            num_mca.append(n)
            try: n= sel.lines()
            except: n= 0
            num_pts.append(n)
            try: n= sel.command()
            except: n= ""
            commands.append(n)
        source_info["NumMca"]=num_mca
        source_info["NumPts"]=num_pts
        source_info["Commands"]= commands
        source_info["ScanType"]= map(self.__getScanType, num_pts, num_mca, commands)
        return source_info

    def __getScanList(self):
        aux= string.split(self._sourceObjectList[0].list(),",")
        newlistcount=[]
        newlist=[]
        for i in aux:
            if string.find(i,":")== -1:  start_index=end_index=int(i)
            else:
                s= string.split(i,":")
                start_index=int(s[0])
                end_index=int(s[1])
            for j in range(start_index,end_index+1):
                newlist.append(j)
                newlistcount.append(newlist.count(j))
        for i in range(len(newlist)):
            newlist[i]="%d.%d" % (newlist[i],newlistcount[i])
        return newlist
 
    def __getScanType(self, num_pts, num_mca, command):
        stype= SF_EMPTY
        if num_pts>0:
                if command is None:stype= SF_SCAN
                elif string.find(command, "mesh")!=-1:
                        stype= SF_MESH
                else:   stype= SF_SCAN
                if num_mca%num_pts:
                        stype+= SF_UMCA
                elif num_mca==num_pts:
                        stype+= SF_MCA
                elif num_mca>0:
                        stype+= SF_NMCA
        else:
                if num_mca==1:
                        stype= SF_MCA
                elif num_mca>1:
                        stype= SF_NMCA
        return stype


    def getKeyInfo (self, key):
        """
        If key given returns information of a perticular key.
        """
        fileName = self.__sourceNameList[0]
        key_type= self.__getKeyType(key)
        if key_type=="scan": scan_key= key
        elif key_type=="mca": (scan_key, mca_no)=self.__getMcaPars(key)
        self.__lastKeyInfo[key] = os.path.getmtime(fileName)
        return self.__getScanInfo(scan_key)

    def __getKeyType (self,key):
        count= string.count(key, '.')
        if (count==1): return "scan"
        elif (count==2) or (count==3): return "mca"
        else: raise "SpecFileDataSource: Invalid key"

    def __getScanInfo(self, scankey):
        index = 0
        sourceObject = self._sourceObjectList[index]
        scandata= sourceObject.select(scankey)
        
        info={}
        info["SourceType"] = SOURCE_TYPE
        #doubts about if refer to the list or to the individual file
        info["SourceName"] = self.sourceName
        info["Key"]        = scankey
        info['FileName']   = self.__sourceNameList[index]
        try: info["Number"] = scandata.number()
        except: info["Number"] = None
        try: info["Order"] = scandata.order()
        except: info["Order"] = None
        try: info["Cols"] = scandata.cols()
        except: info["Cols"] = 0
        try: info["Lines"] = scandata.lines()
        except: info["Lines"] = 0
        try: info["Date"] = scandata.date()
        except: info["Date"] = None
        try: info["MotorNames"] = sourceObject.allmotors()
        except: info["MotorNames"] = None
        try: info["MotorValues"] = scandata.allmotorpos()
        except: info["MotorValues"] = None
        try: info["LabelNames"] = scandata.alllabels()
        except: info["LabelNames"] = None
        try: info["Command"] = scandata.command()
        except: info["Command"] = None
        try: info["Header"] = scandata.header("")
        except: info["Header"] = None
        try: info["NbMca"] = scandata.nbmca()
        except: info["NbMca"] = 0
        try: info["Hkl"] =  scandata.hkl()
        except: info["Hkl"] =  None
        if info["NbMca"]:
            if info["Lines"]>0 and info["NbMca"]%info["Lines"]==0:
                info["NbMcaDet"]= info["NbMca"]/info["Lines"]
            else:
                info["NbMcaDet"]= info["NbMca"]
        info["ScanType"]= self.__getScanType(info["Lines"], info["NbMca"], info["Command"])
        return info


    def __getMcaInfo(self, mcano, scandata, info=None):
        if info is None: info = {}
        mcainfo= {}
        if info.has_key("NbMcaDet"):
            det= info["NbMcaDet"]
            if info["Lines"]>0:
                mcainfo["McaPoint"]= int(mcano/info["NbMcaDet"])+(mcano%info["NbMcaDet"]>0)
                mcainfo["McaDet"]= mcano-((mcainfo["McaPoint"]-1)*info["NbMcaDet"])
                try: mcainfo["LabelValues"]= scandata.dataline(mcainfo["McaPoint"])
                except: mcainfo["LabelValues"]= None
            else:
                mcainfo["McaPoint"]= 0
                mcainfo["McaDet"]= mcano
                mcainfo["LabelValues"]= None
        calib= scandata.header("@CALIB")
        mcainfo["McaCalib"]=[0.0,1.0,0.0]
        if len(calib):
            if len(calib) == info["NbMcaDet"]:
                calib = [calib[mcainfo["McaDet"]-1]]
            else:
                if DEBUG:
                    print "Warning","Number of calibrations does not match number of MCAs"
                if len(calib) == 1:
                    pass
                else:
                    raise self.Error,"Number of calibrations does not match number of MCAs"        
            ctxt= calib[0].split()
            if len(ctxt)==4:
                #try:
                if 1:
                    cval= [ float(ctxt[1]), float(ctxt[2]), float(ctxt[3]) ]
                    mcainfo["McaCalib"]= cval
                else:
                #except: 
                    mcainfo["McaCalib"]=[0.0,1.0,0.0]
        ctime= scandata.header("@CTIME")
        if len(ctime):
            if len(ctime) == info["NbMcaDet"]:
                ctime = [ctime[mcainfo["McaDet"]-1]]
            else:
                if DEBUG:
                    print "Warning","Number of counting times does not match number of MCAs"
                if len(ctime) == 1:
                    pass
                else:
                    raise self.Error,"Number of counting times does not match number of MCAs"        
            ctxt= ctime[0].split()
            if len(ctxt)==4:
                try:
                    mcainfo["McaPresetTime"]= float(ctxt[1])
                    mcainfo["McaLiveTime"]= float(ctxt[2])
                    mcainfo["McaRealTime"]= float(ctxt[3])
                except: pass
                        
        chann = scandata.header("@CHANN")
        if len(chann):
            if len(chann) == info["NbMcaDet"]:
                chann = [chann[mcainfo["McaDet"] - 1]]
            else:
                if DEBUG:
                    print "Warning","Number of @CHANN information does not match number of MCAs"
                if len(chann) == 1:
                    pass
                else:
                    raise self.Error,"Number of @CHANN information does not match number of MCAs"        
            ctxt= chann[0].split()
            if len(ctxt)==5:
                mcainfo['Channel0'] = float(ctxt[2])
            else:
                mcainfo['Channel0'] = 0.0
        else:
            mcainfo['Channel0'] = 0.0                
        return mcainfo


    def __getMcaPars(self,key):
        index = 0
        nums= string.split(key,'.')
        size = len(nums)
        sel_key = nums[0] + "." + nums[1]
        if size==3:
            mca_no=int(nums[2])
        elif size==4:
            sel=self._sourceObjectList[index].select(sel_key)
            try: lines = sel.lines()
            except: lines=0
            if nums[3]==0: mca_no=int(nums[2])
            else:          mca_no=((int(nums[3])-1)*lines)+int(nums[2])
        else: raise "SpecFileData: Invalid key"
        return (sel_key,mca_no)

    def getDataObject(self,key,selection=None):
        """
        Parameters:
        * key: key to be read from source. It is a string
              using the following formats:

            "s.o": loads all counter values (s=scan number, o=order)
              - if ScanType==SCAN: in a 2D array (mot*cnts)
              - if ScanType==MESH: in a 3D array (mot1*mot2*cnts)
              - if ScanType==MCA: single MCA in 1D array (0:channels)

            "s.o.n": loads a single MCA in a 1D array (0:channels)
              - if ScanType==NMCA: n is the MCA number from 1 to N
              - if ScanType==SCAN+MCA: n is the scan point number (from 1)
              - if ScanType==MESH+MCA: n is the scan point number (from 1)

            "s.o.p.n": loads a single MCA in a 1D array (0:channels)
              - if ScanType==SCAN+NMCA:
                      p is the point number in the scan
                      n is the MCA device number
              - if ScanType==MESH+MCA:
                      p is first motor index
                      n is second motor index

            "s.o.MCA": loads all MCA in an array
              - if ScanType==SCAN+MCA: 2D array (pts*mca)
              - if ScanType==NMCA: 2D array (mca_det*mca)
              - if ScanType==MESH+MCA: 3D array (pts_mot1*pts_mot2*mca)
              - if ScanType==SCAN+NMCA: 3D array (pts_mot1*mca_det*mca)
              - if ScanType==MESH+NMCA:
                      creates N data page, one for each MCA device,
                      with a 3D array (pts_mot1*pts_mot2*mca)
        """
        key_type= self.__getKeyType(key)
        if key_type=="scan": scan_key= key
        elif key_type=="mca": (scan_key, mca_no)=self.__getMcaPars(key)

        sourcekeys = self.getSourceInfo()['KeyList']
        if scan_key not in sourcekeys:
            raise KeyError,"Key %s not in source keys" % key

        if key_type=="scan":
            output = self._getScanData(key, raw = True)
            output.x = None
            output.y = None
            output.m = None
            output.info['selection'] = selection
            if selection is None:
                output.info['selectiontype'] = "2D"
                return output
            elif type(selection) != type({}):
                #I only understand index selections
                raise "TypeError", "Only selections of type {x:[],y:[],m:[]} understood"
            else:
                if selection.has_key('x'):
                    for labelindex in selection['x']:
                        label = output.info['LabelNames'][labelindex]
                        if label not in output.info['LabelNames']:
                            raise "ValueError", "Label %s not in scan labels" % label
                        index = output.info['LabelNames'].index(label)
                        if output.x is None: output.x = []
                        output.x.append(output.data[:, index])
                if selection.has_key('y'):
                    for labelindex in selection['y']:
                        label = output.info['LabelNames'][labelindex]
                        if label not in output.info['LabelNames']:
                            raise "ValueError", "Label %s not in scan labels" % label
                        index = output.info['LabelNames'].index(label)
                        if output.y is None: output.y = []
                        output.y.append(output.data[:, index])
                if selection.has_key('m'):
                    for labelindex in selection['m']:
                        label = output.info['LabelNames'][labelindex]
                        if label not in output.info['LabelNames']:
                            raise "ValueError", "Label %s not in scan labels" % label
                        index = output.info['LabelNames'].index(label)
                        if output.m is None: output.m = []
                        output.m.append(output.data[:, index])
                output.info['selectiontype'] = "1D"
                output.data = None
        elif key_type=="mca":
            output = self._getMcaData(key)
            ch0 =  int(output.info['Channel0'])
            output.x = [Numeric.arange(ch0, ch0 + len(output.data)).astype(Numeric.Float)]
            output.y = [output.data[:].astype(Numeric.Float)]
            output.m = None
            output.info['selectiontype'] = "1D"
            output.data = None
        return output

    def _getScanData(self, scan_key, raw=False):
        index = 0
        scan_obj = self._sourceObjectList[index].select(scan_key)
        scan_info= self.__getScanInfo(scan_key)
        scan_info["Key"]      = scan_key
        scan_info["FileInfo"] = self.__getFileInfo()
        scan_type = scan_info["ScanType"]
        scan_data = None

        if scan_type&SF_SCAN:
            try: scan_data= Numeric.transpose(scan_obj.data()).copy()
            except: raise self.Error, "SF_SCAN read failed"
        elif scan_type&SF_MESH:
            try:
                if raw:
                    try: scan_data= Numeric.transpose(scan_obj.data()).copy()
                    except: raise self.Error, "SF_MESH read failed"
                else:
                    scan_array= scan_obj.data()
                    (mot1,mot2,cnts)= self.__getMeshSize(scan_array)
                    scan_data= Numeric.zeros((mot1,mot2,cnts), Numeric.Float)
                    for idx in range(mot2):
                        scan_data[:,idx,:]= Numeric.transpose(scan_array[:,idx*mot1:(idx+1)*mot1]).copy()
                    scan_data= Numeric.transpose(scan_data).copy()
            except: raise self.Error, "SF_MESH read failed"
        elif scan_type&SF_MCA:
            try: scan_data= scan_obj.mca(1)
            except: raise self.Error, "SF_MCA read failed"

        if scan_data is not None:
            #create data object
            dataObject = DataObject.DataObject()
            #data.info = self.__getKeyInfo(key)
            dataObject.info = scan_info
            dataObject.data = scan_data
            return dataObject
        else:    raise self.Error, "getData unknown type"

    def _getMcaData(self, key):
        index = 0        
        key_split= key.split(".")
        scan_key= key_split[0]+"."+key_split[1]
        scan_info = {}
        scan_info["Key"]= key
        scan_info["FileInfo"] = self.__getFileInfo()
        scan_obj = self._sourceObjectList[index].select(scan_key)
        scan_info.update(self.__getScanInfo(scan_key))
        scan_type= scan_info["ScanType"]
        scan_data= None
        mca_range= []        # for each dim., (name, length, values or None)

        if len(key_split)==3:
            if scan_type&SF_NMCA or scan_type&SF_MCA:
                try: 
                    mca_no= int(key_split[2])
                    scan_data= scan_obj.mca(mca_no)
                except: 
                    raise self.Error, "Single MCA read failed"
            if scan_data is not None:
                scan_info.update(self.__getMcaInfo(mca_no, scan_obj, scan_info))
                dataObject = DataObject.DataObject()
                dataObject.info = scan_info
                dataObject.data = scan_data
                return dataObject

        elif len(key_split)==4:
            if scan_type==SF_SCAN+SF_NMCA:
                try:
                    mca_no= (int(key_split[2])-1)*scan_info["NbMcaDet"] + int(key_split[3])
                    scan_data= scan_obj.mca(mca_no)
                except: 
                    raise self.Error, "SF_SCAN+SF_NMCA read failed"
            elif scan_type==SF_MESH+SF_MCA:
                try:
                    #scan_array= scan_obj.data()
                    #(mot1,mot2,cnts)= self.__getMeshSize(scan_array)
                    #mca_no= 1 + int(key_split[2]) + int(key_split[3])*mot1
                    mca_no= (int(key_split[2])-1)*scan_info["NbMcaDet"] + int(key_split[3])
                    if DEBUG:
                        print "try to read mca number = ",mca_no
                        print "total number of mca = ",scan_info["NbMca"]
                    scan_data= scan_obj.mca(mca_no)
                except: 
                    raise self.Error, "SF_MESH+SF_MCA read failed"
            elif scan_type&SF_NMCA or scan_type&SF_MCA:
                try:
                    mca_no= (int(key_split[2])-1)*scan_info["NbMcaDet"] + int(key_split[3])
                    scan_data= scan_obj.mca(mca_no)
                except:
                    raise self.Error, "SF_MCA or SF_NMCA read failed"
            else:
                raise self.Error, "Unknown scan type!!!!!!!!!!!!!!!!"
            if scan_data is not None:
                scan_info.update(self.__getMcaInfo(mca_no, scan_obj, scan_info))
                dataObject = DataObject.DataObject()
                dataObject.info = scan_info
                dataObject.data = scan_data
                return dataObject

    def __getFileInfo(self):
        index = 0
        source = self._sourceObjectList[index]
        file_info={}
        try: file_info["Title"] = source.title()
        except: file_info["Title"] = None
        try: file_info["User"] = source.user()
        except: file_info["User"] = None
        try: file_info["Date"] = source.date()
        except: file_info["Date"] = None
        try: file_info["Epoch"] = source.epoch()
        except: file_info["Epoch"] = None
        try: file_info["ScanNo"] = source.scanno()
        except: file_info["ScanNo"] = None
        return file_info

    def __getMeshSize(self, scan_array):
        """ Given the scandata array, return the size tuple of the mesh
        """
        mot2_array= scan_array[1]
        mot2_max= mot2_array.shape[0]
        mot1_idx= 1
        while mot1_idx<mot2_max and mot2_array[mot1_idx]==mot2_array[0]: mot1_idx+=1
        mot2_idx= scan_array.shape[1]/mot1_idx
        cnts_idx= scan_array.shape[0]
        return (mot1_idx, mot2_idx, cnts_idx)        

    def __getScanMotorRange(self, info, obj):
        name= info["LabelNames"][0]
        values= obj.datacol(1)
        length= values.shape[0]
        return (name, values, length)

    def __getMeshMotorRange(self, info, obj):
        return ()


    def isUpdated(self, sourceName, key):
        #sourceName is redundant?
        index = 0
        lastmodified = os.path.getmtime(self.__sourceNameList[index])
        if key not in self.__lastKeyInfo.keys():
            #nothing has been read???
            self.__lastKeyInfo[key] = lastmodified
            return False
        if lastmodified != self.__lastKeyInfo[key]:
            self.__lastKeyInfo[key] = lastmodified
            return True
        else:
            return False

source_types = { SOURCE_TYPE: SpecFileDataSource}

def DataSource(name="", source_type=SOURCE_TYPE):
  try:
     sourceClass = source_types[source_type]
  except KeyError:
     #ERROR invalid source type
     raise TypeError,"Invalid Source Type, source type should be one of %s" % source_types.keys()
  
  return sourceClass(name)

  
if __name__ == "__main__":
    import sys,time

    if len(sys.argv) not in [2,3,4]:
        print "Usage: %s <filename> [<key_to_load>]"
        sys.exit()

    filename= sys.argv[1]
    sf = SpecFileDataSource(filename)
    sf = DataSource(filename)
    if len(sys.argv)==2:
        info= sf.getSourceInfo()
        print "Filename        :", sf.sourceName
        print "Number of scans :", info["Size"]

        print "S# - command - pts - mca - type"
        for (s,c,p,m,t) in zip(info["KeyList"],info["Commands"],info["NumPts"],info["NumMca"],info["ScanType"]):
                print s,"-",c,"-",p,"-",m,"-",t
        print "KeyList = ",info["KeyList"]
        #print info['Channel0']

    if len(sys.argv)==3:
        t0 = time.time()
        dataObject = sf.getDataObject(sys.argv[2])
        t0 = time.time() - t0
        info= dataObject.info
        data= dataObject.data

        print "Filename   :", info['SourceName']
        print "Loaded key :", info["Key"]
        print "Header     :"
        for i,v in info.items():
                print "-", i, ":", v
        print "Data Shape :", data.shape
        print "read time = ",t0

    if len(sys.argv)==4:
        t0 = time.time()
        label = sys.argv[3]
        dataObject = sf.getDataObject(sys.argv[2], selection={'x':[label],
                                                        'y':[label],
                                                        'm':[label]})
        t0 = time.time() - t0
        info= dataObject.info
        #print dataObject.x
        print dataObject.y
        #print dataObject.x

 
