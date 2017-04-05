#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 18:53:20 2017

@author: sina
"""
import re
from netaddr import IPAddress
import datetime
import functions
from collections import defaultdict

lineStructur= functions.lineStructur
reqStructure=functions.reqStructure
loginReqStructure=functions. loginReqStructure

class GlobalData:
    def __init__(self,enabledFeatures=[1,2]):
        
        self._compiledReq=re.compile(reqStructure)
        self.enabledFeatures=enabledFeatures
        
        self.hostAppearanceCntr=defaultdict(int) #feature 1 main data storage
        self.resourcesBW=defaultdict(int) #feature 2 main data storage
        

    
    class Host:
        def __init__(self,hostName):
            self.name=hostName

        def __hash__(self):
            try:            
                return int(IPAddress(self.name))
            except Exception:              
                return hash(self.name)

        def __eq__(self, other):
            return self.name== other.name


    def addLineInfo(self,line=None,host=None,timeStr=None,req=None,reply=None,bw=None,t=None,useBeingIPforHashing=False):
        
        # check if the line has already been parsed or not
        if  host==None or timeStr==None or req==None or bw==None or  t==None:
            if line==None or line=='' or line.isspace():
                return
            host,timeStr,req,reply,bw,t=functions.convertLineToData(line)
            
        self._addHost(host,useBeingIPforHashing)
        self._addResource(req,bw)
        
        
    def _addHost(self,host,useBeingIPforHashing=False):    
        if useBeingIPforHashing:
            host=GlobalData.Host(host)
        self.hostAppearanceCntr[host]+=1
        
    def _addResource(self,req,bw,useOptimisedApproach=True):
        
        resource=None
        match=self._compiledReq.search(req) 
        if match!=None:
            resource=match.group(2)
            
            
        if bw=='-':
            bw=0
        bw=int(bw)   
        self.resourcesBW[resource]+=bw
        
    def getTopTenHostWithHighesAccessNumberStr(self,n=10):
        return functions.getTopTenInDictionaryStr(self.hostAppearanceCntr,showTheVal=True,n=n)
         
    def getTopTenResourceWithHighestBWUsedStr(self,n=10):
       return  functions.getTopTenInDictionaryStr(self.resourcesBW,showTheVal=False,n=n)
   
    
    
    
    
        
class LocalData:
    twentySecDelay = datetime.timedelta(seconds=20)
    fiveMinDelay= datetime.timedelta(minutes=5)
    sixtyMinDelay=datetime.timedelta(minutes=60)
    oneHour_len=60*60
    oneSecDelay=datetime.timedelta(seconds=1)
    zeroDelay=datetime.timedelta(seconds=0)

    def __init__(self,blockedUserAttemptsFile=None,enabledFeatures=[3,4]):
            
            self._compiledLogin=re.compile(loginReqStructure)
            self.enabledFeatures=enabledFeatures
            
            # For Feature 3
            self.dynamicMaxTenValRecorder=LocalData.DynamicMaxTenValRecorder(numberOfBusyWindows=10) # size of this list , in the worst case, will be 10+2=12
            self.listOfAccessInLast60Min=LocalData.ListOfAccessInLast60Min() # size of this list is always less than or equal 3600
            
            # For Feature 4
            self.blockedUserAttemptsFile=blockedUserAttemptsFile
            self.failedTimesForHosts=defaultdict(list) #feature 3 main data storage
            self.recentFailedLoginHosts=[]
            self.blackList= []
            self.failedTimesForHosts_maxLen=0
            self.recentFailedLoginHosts_maxLen=0
            self.blackList_maxLen=0
 
    def addLineInfo(self,line=None, host=None,timeStr=None,req=None,reply=None,bw=None,t=None):
        if  host==None or timeStr==None or req==None or bw==None or t==None:
            if line==None or line=='' or line.isspace():
                return
            host,timeStr,req,reply,bw,t=functions.convertLineToData(line)
            
        if 3 in self.enabledFeatures:
            self._updateTrafficData(t)
        if 4 in self.enabledFeatures:
            self._checkAndAddToLogingFailsIfNeeded(host,t,req,reply,line)

        self._updateMaxLens()
     
    def _updateMaxLens(self) :
        self.failedTimesForHosts_maxLen=max([self.failedTimesForHosts_maxLen,len(self.failedTimesForHosts)])
        self.recentFailedLoginHosts_maxLen=max([self.recentFailedLoginHosts_maxLen,len(self.recentFailedLoginHosts)])
        self.blackList_maxLen=max([self.blackList_maxLen, len(self.blackList)])

    # ---------            For Feature 3       ----------------------    
    class Acc_Time_Cnt:
        def __init__(self,t,cnt=1):
            self.t=t
            self.cnt=cnt
        def increaseCnt(self):
            self.cnt+=1
        def setCnt(self,cnt):
            self.cnt=cnt
        def __str__(self):
            return functions.convertToString(self.t) + ',' + str(self.cnt)
        def __repr__(self):
            return self.__str__()
        
        def __eq__(self, other):
            return self.t== other.t

    class ListOfAccessInLast60Min:
        def  __init__ (self):
            self.mainList=[]
            self.totalNumOfAcc=0
        def addAccess(self,t,isRealAcc=True):
            if len(self.mainList)>0 and t==self.mainList[-1].t:
                self.mainList[-1].increaseCnt()
            else:
                hm=LocalData.Acc_Time_Cnt(t,cnt=1*isRealAcc)
                self.mainList.append(hm)
                if len(self.mainList)>LocalData.oneHour_len:
                    self.totalNumOfAcc-=self.mainList[0].cnt
                    del self.mainList[0]
            self.totalNumOfAcc+= 1*isRealAcc
            return self.totalNumOfAcc
            
        def getLastAcc(self):
            return self.mainList[-1]
        def hasAcc(self):
            return len(self.mainList)>0
                    
    class DynamicMaxTenValRecorder:
        def  __init__ (self,numberOfBusyWindows=10):
            self.mainList=[]
            self.numberOfBusyWindows=numberOfBusyWindows
        def updateRecords(self,t,totalNumOfAccInLast60min):
            t_sixtyMinAgo=t-LocalData.sixtyMinDelay+LocalData.oneSecDelay
            if len(self.mainList)>0 and self.mainList[-1].t== t_sixtyMinAgo:
                self.mainList[-1].setCnt(totalNumOfAccInLast60min)
            else:
                hm=LocalData.Acc_Time_Cnt(t_sixtyMinAgo,totalNumOfAccInLast60min)
                self.mainList.append(hm)
                if len(self.mainList)>self.numberOfBusyWindows+2:
                    self.mainList.remove(min(self.mainList[0:-2],key=lambda x: x.cnt))
        def getExactTopTenRecordSorted(self):
            # Remove extra windows and sort the windows according to traffic during each
            while len(self.mainList)>self.numberOfBusyWindows:
                self.mainList.remove(min(self.mainList,key=lambda x: x.cnt))
            return sorted(self.mainList,key=lambda x: x.cnt,reverse=True)
        
        
    def _updateTrafficData(self,t,isRealAcc=True):
        
        # Add empty attempts if there is more than one second gap between last 
        # attmpt and new attempt.
        if self.listOfAccessInLast60Min.hasAcc():
            preT=self.listOfAccessInLast60Min.getLastAcc().t+LocalData.oneSecDelay
        while self.listOfAccessInLast60Min.hasAcc() and t-preT>LocalData.zeroDelay:
            totalNumOfAcc=self.listOfAccessInLast60Min.addAccess(preT,isRealAcc=False)
            self.dynamicMaxTenValRecorder.updateRecords(preT,totalNumOfAcc)
            preT=preT+LocalData.oneSecDelay
        
        # Add/Update list and the counter of the attempts in last 60 mins a
        totalNumOfAcc=self.listOfAccessInLast60Min.addAccess(t,isRealAcc)
          
        # Update the total history
        self.dynamicMaxTenValRecorder.updateRecords(t,totalNumOfAcc)

    
     
    def getTopTenBussiestHoursStr(self):
        
        # Complete the counting by adding one_hour  empty access
        if self.listOfAccessInLast60Min.hasAcc():
            preT=self.listOfAccessInLast60Min.getLastAcc().t
            for i in range(LocalData.oneHour_len):
                preT=preT+LocalData.oneSecDelay
                self._updateTrafficData(preT,isRealAcc=False)      
        # Convert members list to a list of str s for easier file writing
        members=self.dynamicMaxTenValRecorder.getExactTopTenRecordSorted()
        membersStr=[]
        for m in members:
            membersStr.append(str(m)+'\n')
        return membersStr
         



    # ---------            For Feature 4       ----------------------       
    class Client:
        def __init__(self,name,lastSeenTryTime):
            self.name=name
            self.lastSeenTryTime= lastSeenTryTime
        def __eq__(self,other):
            if type(other) is LocalData.Client:
                return other.name==self.name
            if type(other) is str:
                return other==self.name
            return self==other
        

    
    def isLoginFail(self,req, reply):
        if self._compiledLogin.match(req) == None:
            return None
        else: 
            return  int(reply)==401
        
     
    def report(self,host,t,line):
        if self.blockedUserAttemptsFile == None:
            if len(self.failedTimesForHosts)>0:
                a=self.failedTimesForHosts[host]
                print (host,t.time(), '---',  a[0].time(),a[1].time(),a[2].time() ,'--')#,self.data[host])
        else:
            self.blockedUserAttemptsFile.write(line+'\n')
            
    def _updateRecentlyLoginAttempts(self,h,t):
        
        # Add the attempt to the list of recent failed login attempt
        self.recentFailedLoginHosts.append(LocalData.Client(h,t))
        
        
        while t-self.recentFailedLoginHosts[0].lastSeenTryTime>LocalData.twentySecDelay:
            host=self.recentFailedLoginHosts[0].name
            del self.recentFailedLoginHosts[0]
        
            if host in self.failedTimesForHosts:
                failedAttemptTimes=self.failedTimesForHosts[host]
                for fat in failedAttemptTimes:
                    if t-fat>LocalData.twentySecDelay:
                        failedAttemptTimes.remove(fat)
                if len(failedAttemptTimes)==0:
                    del self.failedTimesForHosts[host]
                else:
                    self.failedTimesForHosts[host]=failedAttemptTimes
    
    def _checkAndAddToLogingFailsIfNeeded(self,host,t,req,reply,line):
        
        #Update Black List for current time
        while len(self.blackList)>0 and t-self.blackList[0].lastSeenTryTime> LocalData.fiveMinDelay:
            del self.blackList[0]
            self.failedTimesForHosts.pop(host,None)
        
        #If the host is in blackList report and return 
        if host in self.blackList:
            self.report(host,t,line)
            return
        
        # React based on the access type; whether it is failed login, 
        # successfull login, or it is none of them
        loginFail=self.isLoginFail(req,reply) # May return True,False, or None
        if loginFail==True:
                # Update the 
                self._updateRecentlyLoginAttempts(host,t)
                
                # Update and add new history of failed attempt to the history 
                # of the host with failed login attempt.
                failedAttemptTimes=self.failedTimesForHosts.get(host,[])
                for fat in failedAttemptTimes:
                    if t-fat>LocalData.twentySecDelay:
                        failedAttemptTimes.remove(fat)
                failedAttemptTimes.append(t)
                self.failedTimesForHosts[host]=failedAttemptTimes
                if len(failedAttemptTimes)>2:
                    self.blackList.append(LocalData.Client(host,t))
                    
        # If successfull login, clear the failed login history for the user            
        elif loginFail==False: 
            self.failedTimesForHosts.pop(host,None)
            
        else: # If the attempt is not a login attempt, pass
            pass
            