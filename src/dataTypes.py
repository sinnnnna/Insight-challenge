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
    """Centerlized storage of the data which should be saved globaly.

    This class implements the efficient ways to store and retrive the data from
    huge maps. 

    Notice: For huge amount of data, the behavior of this class might not be linear
    
    Parameters
    ----------
    enabledFeatures, list
        if 1 or/and 2 is/are in list, data for feature 1 and/or 2 will be stored
        
    Attributes
    ----------
    hostAppearanceCntr, dict
        main storage for counting number of attempts for each host. Feature 1
    resourcesBW, dict
        main storage for traking used bandwidth of different resources. Feature 2
    """
    def __init__(self,enabledFeatures=[1,2]):
        
        self._compiledReq=re.compile(reqStructure) # compile the regex for 
        self.enabledFeatures=enabledFeatures
        
        self.hostAppearanceCntr=defaultdict(int) #feature 1 main data storage. A dictionay
        self.resourcesBW=defaultdict(int) #feature 2 main data storage.  A dictionay
        

    
    class Host:
        """ A wrapper class for Host/IP .
            Using this wrapper may lead to more linear performance of the datastorage
    
        Parameters
        ----------
        hostName, str
            ip or the host name
       
        """
        def __init__(self,hostName):
            self.name=hostName

        def __hash__(self):
            """ Modifid hash function to use useBeingIPforHashing
          
            """
            try:            
                return int(IPAddress(self.name))
            except Exception:              
                return hash(self.name)

        def __eq__(self, other):
            return self.name== other.name


    def addLineInfo(self,line=None,host=None,timeStr=None,req=None,reply=None,bw=None,t=None,useBeingIPforHashing=False):
        """ Adds a new entry to the data storage(s).                
            This function updates the corresponding data storage for feature 2 
            and 1. This is the main function interface to this class.
        Parameters
        ----------
        line:    str, (=None) -> input line. If the reset of the parameters 
                                  are None, the data will be extracted from 
                                  this line.
            
        host:    str, (=None)-> hostname or ip
        timeStr: str, (=None) -> timestamp
        req:     str, (=None) -> request 
        reply:   str, (=None) -> reply code
        bw:      str, (=None)    -> Bytes  (it can be either number or '-')
        t:       datatime, (=None)-> a datetime object of timeStr
            
        useBeingIPforHashing: bool, (=False) -> by default we dont use being an 
                                               IP info.
        
        """
        
        # check if the line has already been parsed or not
        if  host==None or timeStr==None or req==None or bw==None or  t==None:
            if line==None or line=='' or line.isspace():
                return
            host,timeStr,req,reply,bw,t=functions.convertLineToData(line)
            
        self._addHost(host,useBeingIPforHashing)
        self._addResource(req,bw)
        
        
    def _addHost(self,host,useBeingIPforHashing=False):  
        """ Adds/Updates the information of occurance of the host in the data.
        
            Parameters
            ----------
            host: str, ip or host string
            useBeingIPforHashing: bool, (=False),
                        by default we dont use being an IP info.
        """
        if useBeingIPforHashing:
            host=GlobalData.Host(host)
        self.hostAppearanceCntr[host]+=1
        
    def _addResource(self,req,bw):
        """ Extracts the resource from the request string and adds/updates the 
            information of occurance of a recources with certain size in the data.
        
            Parameters
            ----------
            req: str, the request string
            bw: The size of the resource being transfered to the client
        """
        
        # Extract the resource:
        resource=None
        match=self._compiledReq.search(req) 
        if match!=None:
            resource=match.group(2)
            
        # Convert the bw string to int    
        if bw=='-':
            bw=0
        bw=int(bw)   
        self.resourcesBW[resource]+=bw
        
    def cleanData(self):
        """ Delete all the data in the storages for feature 1 and 2"""
        self.hostAppearanceCntr.clear()
        self.resourcesBW.clear()
        
    def getTopTenHostWithHighesAccessNumberStr(self,n=10):
        """ Get a list of strings to display the results for feature 1
        
            Parameters
            ----------
            n: int, (=10), number of members in the returned list
            
            Returns
            -------
            List of str, A sorted list of formated strings displaying the most 
            frequent host/ip with number of times it has accessed the website.
        """
        return functions.getTopTenInDictionaryStr(self.hostAppearanceCntr,showTheVal=True,n=n)
         
    def getTopTenResourceWithHighestBWUsedStr(self,n=10):
        """ Get a list of strings to display the results for feature 2
        
            Parameters
            ----------
            n: int, (=10), number of members in the returned list
            
            Returns
            -------
            List of str, A sorted list of formated strings displaying the
            recources which have consumed the most amount of server's bandwidth.
        """
        return  functions.getTopTenInDictionaryStr(self.resourcesBW,showTheVal=False,n=n)
   
        
class LocalData:
    """ A class for centerlized storage of the data which should be saved 
        locally (dynamically).

    This class implements memory efficient ways to keep track of recently 
    happend events. 

    Notice: Currently Feature 4 is faster than feature 3
    
    Parameters
    ----------
    enabledFeatures, list
        if 3 or/and 4 is/are in list, data for feature 3 and/or 4 will be stored
        in their coressponding data structure.
    blockedUserAttemptsFile, _io.TextIOWrapper, 
                             an already opened file.
                             
    Attributes
    ----------
    For Feature 3:
        
    dynamicMaxTenValRecorder, LocalData.DynamicMaxTenValRecorder(10)
    
        This data structure keeps track of the top 10 bussies hours.
        Size of this list , in the worst case, will be 10+2=12
        
    listOfAccessInLast60Min, LocalData.ListOfAccessInLast60Min
        This is an efficient list that saves the frequency of access in each 
        second during last 60 mins
        
        
    For Feature 4:
        
    recentFailedLoginAttempts: list of LocalData.Client
         This list keeps track of who has failed login attempt in last 20 
         seconds. 
         
    faliureHistoryOfRecentHosts: A dictionary (hashmap) which for each 
         host keeps track of its failed recent attempts. This map is always 
         kept cleaned side by side of the previous list. Hence, it always has 
         smaller size in compare to the list. The major responsibility of this 
         hashmaps is improving the performance. Instead of looking through the 
         whole length of the previous list to find who had 3 consecutive failed 
         login attempt, the program looks up into to this hash map. The keys of 
         this hashmap is the host names and the values are the list of timestamps 
         where a failed login has happend.
        
    faliureHistoryOfRecentHosts_maxLen: int , 
        stores the highest lenght of faliureHistoryOfRecentHosts map
        
    recentFailedLoginAttempts_maxLen: int , 
        stores the highest lenght of recentFailedLoginAttempts list
        
    blackList_maxLen: int , 
        stores the highest lenght of blackList list        
    """
    
    #Predifind time delays which might be used for different purposes.
    twentySecDelay = datetime.timedelta(seconds=20)
    fiveMinDelay= datetime.timedelta(minutes=5)
    sixtyMinDelay=datetime.timedelta(minutes=60)
    oneSecDelay=datetime.timedelta(seconds=1)
    zeroDelay=datetime.timedelta(seconds=0)
    oneHour_len=60*60


    def __init__(self,blockedUserAttemptsFile=None,enabledFeatures=[3,4]):
            
            self._compiledLogin=re.compile(loginReqStructure)
            self.enabledFeatures=enabledFeatures
            
            # For Feature 3
            self.dynamicMaxTenValRecorder=LocalData.DynamicMaxTenValRecorder(numberOfBusyWindows=10) # 
            self.listOfAccessInLast60Min=LocalData.ListOfAccessInLast60Min() # size of this list is always less than or equal 3600
            
            # For Feature 4
            self.blockedUserAttemptsFile=blockedUserAttemptsFile 
            
            self.recentFailedLoginAttempts=[] # list of failed attempts in last 20 seconds
            self.faliureHistoryOfRecentHosts=defaultdict(list) # a helper hashmap to avoid looking through recentFailedLoginAttempts each time
            self.blackList= [] # The performance can be improved if I had set of black list in parallel
            self.faliureHistoryOfRecentHosts_maxLen=0
            self.recentFailedLoginAttempts_maxLen=0
            self.blackList_maxLen=0
 
    def addLineInfo(self,line=None, host=None,timeStr=None,req=None,reply=None,bw=None,t=None):
        """ Adds a new entry to the data storage(s).                
            This function updates the corresponding data storage for feature 3 
            and 4. This is the main function interface to this class.
        Parameters
        ----------
        line:    str, (=None) -> input line. If the reset of the parameters 
                                  are None, the data will be extracted from 
                                  this line.
            
        host:    str, (=None)-> hostname or ip
        timeStr: str, (=None) -> timestamp
        req:     str, (=None) -> request 
        reply:   str, (=None) -> reply code
        bw:      str, (=None)    -> Bytes  (it can be either number or '-')
        t:       datatime, (=None)-> a datetime object of timeStr
                    
        """
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
        """ update the maximum used memory values """
        self.faliureHistoryOfRecentHosts_maxLen=max([self.faliureHistoryOfRecentHosts_maxLen,len(self.faliureHistoryOfRecentHosts)])
        self.recentFailedLoginAttempts_maxLen=max([self.recentFailedLoginAttempts_maxLen,len(self.recentFailedLoginAttempts)])
        self.blackList_maxLen=max([self.blackList_maxLen, len(self.blackList)])

    # ---------            For Feature 3       ----------------------    
    class Acc_Time_Cnt:
        """ A class that represents how many occurance exit for a certain time.
            
            Notice: The eq function works only based on time, not count
        
            Parameters
            ----------
            t: timedate,
            cnt: (=1) , number of occuracne
        """
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
        """" A list to keep track keep track of frequency of attempts during 
        one hour In efficient way. 
        
        The internal list size would never grow more 60*60
        """
        def  __init__ (self):
            self.mainList=[]
            self.totalNumOfAcc=0
            
        def addAccess(self,t,isRealAcc=True):
            """ addes/updates a new/old access to the list
            
                Returns:
                -------
                int, totalNumOfAcc in last one hour after inserting the new
                time to the list
            """
            
            # If the access time has been inserted in the list alread, only increase 
            # the cnt for that time rather adding a new time to the list.
            if len(self.mainList)>0 and t==self.mainList[-1].t:
                self.mainList[-1].increaseCnt()
            
            # If it is new time, add it to the list
            else: 
                hm=LocalData.Acc_Time_Cnt(t,cnt=1*isRealAcc)
                self.mainList.append(hm)
                # Make sure that the lenght of the list always remains less 3600
                if len(self.mainList)>LocalData.oneHour_len:
                    self.totalNumOfAcc-=self.mainList[0].cnt
                    del self.mainList[0]
             
            # increase the total number of accesses only if the access was a real one  
            self.totalNumOfAcc+= 1*isRealAcc
            return self.totalNumOfAcc
            
        def getLastAcc(self):
            return self.mainList[-1]
        def hasAcc(self):
            return len(self.mainList)>0
                    
    class DynamicMaxTenValRecorder:
        """ This datastructure keeps track of the top 10 bussies hours.
        Size of this list , in the worst case, will be 10+2=12
        
        
        
        Parameters:
        ----------
        numberOfBusyWindows: int, (=10)
        
        """
        
        def  __init__ (self,numberOfBusyWindows=10):
            self.mainList=[]
            self.numberOfBusyWindows=numberOfBusyWindows
        def updateRecords(self,t,totalNumOfAccInLast60min):
            """ Main accesses point to this class object.
                Gets new count for the given time and updates its data structure.
                
                Algorithim:
                ----------
                The first 10 member of the mainList are previously determind 
                maximum values, and the 11th member is the new/not updated most 
                recent time. As long as the time is not changed to a new time, 
                nothing will happen to this list except the updating of the for 
                11th member count. 
                Once a new 'time' comes in, it becomes the 12th member of this 
                list. One the lenght is 12 , the program removes minimum value 
                among first 11 members to assuer that it only keeps the top ten
                values in its first 10 members. Now the lenght of this list becoms 11.
                
            """
            # The time always saved for 60 min ago for better representing data
            t_sixtyMinAgo=t-LocalData.sixtyMinDelay+LocalData.oneSecDelay
            
            # Lool atte algorithim
            if len(self.mainList)>0 and self.mainList[-1].t== t_sixtyMinAgo:
                self.mainList[-1].setCnt(totalNumOfAccInLast60min)
            else:
                hm=LocalData.Acc_Time_Cnt(t_sixtyMinAgo,totalNumOfAccInLast60min)
                self.mainList.append(hm)
                if len(self.mainList)>self.numberOfBusyWindows+2:
                    self.mainList.remove(min(self.mainList[0:-2],key=lambda x: x.cnt))
                    
                    
        def getExactTopTenRecordSorted(self):
            
            """ Remove extra windows and returns sorted windows according to 
                 traffic during each
            """
            while len(self.mainList)>self.numberOfBusyWindows:
                self.mainList.remove(min(self.mainList,key=lambda x: x.cnt))
            return sorted(self.mainList,key=lambda x: x.cnt,reverse=True)
        
        
    def _updateTrafficData(self,t,isRealAcc=True):
        """ update the traffic data. This function should be called at least 
            once every second. If there is no access, use isRealAcc=False
        
            Parameters:
            ----------
            t: datetime, time
            isRealAcc, bool, (=True): decides whether to increase total number 
                                      of access or not
        
        """
        
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
        """ Return the top ten bussiest hours of the server"""
        
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
        """ A data structure for saving the information about the last time that 
            the user has accessed the serve"""
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
        """ gets req and reply and return whether the accessess was a login fail or success.
        
        Returns:
        --------
        bool or None
        
        NOTICE: this function might return None which means the req was not a 
        login attempt at all.
        """
        
        if self._compiledLogin.match(req) == None:
            return None
        else: 
            return  int(reply)==401
        
     
    def report(self,host,t,line):
        """ prints the corressponding line of entry in the blocked.txt file"""
        if self.blockedUserAttemptsFile != None:
            self.blockedUserAttemptsFile.write(line+'\n')
            
    def _updateRecentlyLoginAttempts(self,h,t):
        """ Update the corresponding list and hashmap for recent login attempts
            This function will keep list and maps clean, small, and uptodate.
            
            Parameters:
            ----------
            h,  str, host name
            t, datetime, acc time
        """
        
        # Add the attempt to the list of recent failed login attempt
        self.recentFailedLoginAttempts.append(LocalData.Client(h,t))
        
        # If the time has been change update the list by deleting the attempts 
        # more than 20 sec ago
        while t-self.recentFailedLoginAttempts[0].lastSeenTryTime>LocalData.twentySecDelay:
            host=self.recentFailedLoginAttempts[0].name
            del self.recentFailedLoginAttempts[0]
        
            # update the failiure map
            if host in self.faliureHistoryOfRecentHosts:
                failedAttemptTimes=self.faliureHistoryOfRecentHosts[host]
                for fat in failedAttemptTimes:
                    if t-fat>LocalData.twentySecDelay:
                        failedAttemptTimes.remove(fat)
                if len(failedAttemptTimes)==0:
                    del self.faliureHistoryOfRecentHosts[host]
                else:
                    self.faliureHistoryOfRecentHosts[host]=failedAttemptTimes
                    
                    
    
    def _checkAndAddToLogingFailsIfNeeded(self,host,t,req,reply,line):
        """ First, check whether the host is in black list or not. If it is, 
                    report the line and return
            Second, React based on the access type; whether it is failed login, 
                    successfull login, or it is none of them.
                    
            Third,  update data storage.
            
        
        
        Parameters
        ----------
        line:    str, (=None) -> input line. If the reset of the parameters 
                                  are None, the data will be extracted from 
                                  this line.
            
        host:    str, (=None)-> hostname or ip
        req:     str, (=None) -> request 
        reply:   str, (=None) -> reply code
        t:       datatime, (=None)-> a datetime object of timeStr
                    
        """
        
        #Update Black List for current time
        while len(self.blackList)>0 and t-self.blackList[0].lastSeenTryTime> LocalData.fiveMinDelay:
            del self.blackList[0]
            self.faliureHistoryOfRecentHosts.pop(host,None)
        
        #If the host is in blackList report and return 
        if host in self.blackList:
            self.report(host,t,line)
            return
        
        # React based on the access type; whether it is failed login, 
        # successfull login, or it is none of them
        loginFail=self.isLoginFail(req,reply) # May return True,False, or None
        if loginFail==True:
                # Update the recenen
                self._updateRecentlyLoginAttempts(host,t)
                
                # Update and add new history of failed attempt to the history 
                # of the host with failed login attempt.
                failedAttemptTimes=self.faliureHistoryOfRecentHosts.get(host,[])
                for fat in failedAttemptTimes:
                    if t-fat>LocalData.twentySecDelay:
                        failedAttemptTimes.remove(fat)
                failedAttemptTimes.append(t)
                self.faliureHistoryOfRecentHosts[host]=failedAttemptTimes
                if len(failedAttemptTimes)>2:
                    self.blackList.append(LocalData.Client(host,t))
                    
        # If successfull login, clear the failed login history for the user            
        elif loginFail==False: 
            self.faliureHistoryOfRecentHosts.pop(host,None)
            
        else: # If the attempt is not a login attempt, pass
            pass
            