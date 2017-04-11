#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=================================

Genral purpose function are here.

=================================
Created on Sun Apr  2 21:11:56 2017

@author: sina
"""
import numpy as np
import datetime
import re

# Regex structures
lineStructur= r'(.*) - - \[(\d\d/[A-Za-z]{3}/\d{4}:\d\d:\d\d:\d\d .*)\] \"(.*)\" (\d*) ([-0-9]*)'
reqStructure='(\S*)\s+(\S*)' #'(\S*)\s+(.*)\s+(.*)'
loginReqStructure= '(\S*)\s+/login .*'

leftOver=''
def readInChunks(fileObj, chunkSize=4096):
    """
    Lazy function to read and parse file piece by piece.
    Default chunk size: 4kB. Uses a global variable leftOver inorder to be able
    to parse the file correctly

    Parameters
    ----------
    fileObj : _io.TextIOWrapper, 
        already opened file
        

    chunkSize : int, 
        size of each read     

    """
    global leftOver
    while True:
        strData = leftOver+fileObj.read(chunkSize)
        if not strData:
            break
        data=[]
        startInd=0
        endInd=0
        while True:
            endInd=strData.find('\n',startInd)
            if endInd==-1:
                leftOver=strData[startInd:]
                break
            
            d=convertLineToData(strData[startInd:endInd])
            startInd=endInd+1
            data.append(d)
        yield data






def getTopTenInDictionary(dic,n=10):
    """
    For the given input findes the top 10 keys in the dictionary with highest 
    value without sorting. The execution time is : 2 * len (dic) + 10 log (10)

    Parameters
    ----------
    dic : dict , 
        The dictiony to extract top n member with highes value
        
    n : int, (=10)
        This is actually a more genral function and number of returned values 
        in the list can be modified by this variable.
            
    Returns
    -------
    list, list, shape (len(dic), len(dic))
        Returns the list of top 10 keys with their corresponding values in a 
        seprate list.

    """    
    
    # Convert the dic data to numpy arrays
    keys=np.array(list(dic.keys()))
    vals=np.array(list(dic.values())) 
    
    # Find the index of top 10 values in the sorted manner
    l=min([len(dic),n])
    ind = np.argpartition(vals, -l)[-l:]
    sorted_ind=sorted(ind, key=lambda k: vals[k],reverse=True)

    # Create the results
    topKeys=[]
    topVals=[]
    for i in range(l):
        topVals.append(vals[sorted_ind[i]])
        topKeys.append(keys[sorted_ind[i]])
 
    return topKeys,topVals

def printTopTenInDictionary(dic,n=10):
    """
    prints top n member of dic with the highes value
    
    Parameters
    ----------
    dic : dict , 
        The dictiony to extract top n member with highes value
        
    n : int, (=10)
        This is actually a more genral function and number of things to be printed is variable.
    """    
    topKeys,topVals =getTopTenInDictionary(dic,n)
    for i in range(len(topKeys)):
        print(str(topKeys[i])+','+str(topVals[i]))
         
def getTopTenInDictionaryStr(dic,showTheVal,n=10):
    """
    returns top n member of dic with the highes value as a string
    
    Parameters
    ----------
    dic : dict , 
        The dictiony to extract top n member with highes value
        
    n : int, (=10)
        This is actually a more genral function and number of things to be
        printed return is variable.
    Returns
    -------
    list of str, 
        Returns the list of top 10 keys with their corresponding values in a 
        seprate list.

    """    
    topKeys,topVals =getTopTenInDictionary(dic,n)
    res=[]
    for i in range(len(topKeys)):
        if i!=len(topKeys):
            end='\n'
        else:
            end=''
        if showTheVal:
            res.append(str(topKeys[i])+','+str(topVals[i])+end)
        else:
            res.append(str(topKeys[i])+end)
    return res



compiledLine=re.compile(lineStructur)
s1=len(' - - [')
s2=len('01/Jul/1995:16:49:22 -0400')  
s3=len('] "')
def convertLineToData(line,useOptimisedApproach=True):
    """
    Parses a line of data to 5 different substring and converts the timestamp 
    to a datetime object.
    
    Parameters
    ----------
    line : str , 
        input line. 
        
    useOptimisedApproach : bool, (=True)
        if True, avoides using regex for parsin and uses fixed size nature of 
        entries.
            
    Returns
    -------
    line, str -> same as input line
    host, str -> hostname or ip
    timeStr,str -> timestamp
    req, str -> request 
    reply, str -> reply code
    bw, str -> Bytes  (it can be either number or '-')
    t, datatime -> a datetime object of timeStr
  
    """    
    if useOptimisedApproach:
        i=line.find(' ')
        host=line[0:i]
        timeStr=line[i+s1:i+s1+s2]
        i2=line.rfind('\" ',i+s1+s2+s3)
        req=line[i+s1+s2+s3:i2]
        reply,bw=line[i2+2:].split(' ')
                        
            
    else:
        match=compiledLine.match(line)
        host=match.group(1)
        timeStr=match.group(2)
        req=match.group(3)
        reply=match.group(4)
        bw=match.group(5)
    
    
    t=convertToDateTime(timeStr)  

    #host,timeStr,req,reply,bw,t= None,None,None,None,None,None
    return line,host,timeStr, req,reply, bw,t


from sklearn.linear_model import SGDClassifier
a=SGDClassifier()
        
        
_month_abbreviations = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                       'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                       'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
         
def convertToDateTime(timeStr,useOptimisedApproach=True):
    """
    Converts a string to datetime object
    
    Parameters
    ----------
    timeStr : str , 
        input string. 
        
    useOptimisedApproach : bool, (=True)
        if True, avoides using datetime.strptime(timeStr, '%d/%b/%Y:%H:%M:%S %z')
        which is reayl slow.
            
    Returns
    -------
    t, datatime -> a datetime object of timeStr
  
    """    
    if useOptimisedApproach:
        year = int(timeStr[7:11])
        month = _month_abbreviations[timeStr[3:6]]
        day = int(timeStr[0:2])
        hour = int(timeStr[12:14])
        minute = int(timeStr[15:17])
        second = int(timeStr[18:20])
        
        #tz=datetime.datetime.strptime((timeStr[21:]),'%z').tzinfo
        z= timeStr[21:] 
        tzoffset = int(z[1:3]) * 60 + int(z[3:5])
        if z.startswith("-"):
            tzoffset = -tzoffset
        gmtoff = tzoffset * 60
        tzdelta = datetime.timedelta(seconds=gmtoff)
        tz = datetime.timezone(tzdelta)
        
        return datetime.datetime(year, month, day, hour, minute, second,tzinfo=tz)

    else:
        return datetime.datetime.strptime(timeStr, '%d/%b/%Y:%H:%M:%S %z')



def convertToString(t):
    """
    Converts a string to datetime object
    
    Parameters
    ----------
    timeStr : str , 
        input string. 
        
    useOptimisedApproach : bool, (=True)
        if True, avoides using datetime.strptime(timeStr, '%d/%b/%Y:%H:%M:%S %z')
        which is reayl slow.
            
    Returns
    -------
    t, str -> a formated string of the datetime object
  
    """    
    return datetime.datetime.strftime(t, '%d/%b/%Y:%H:%M:%S %z')




def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    # Prints a decent progress bar if used in itrations
    Parameters
    ----------
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        
        
    Notice:    
    -----
    This part is copy pasted from
    http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total : 
        print()
        
        

def countNumOfLines(f):
    """
    Counts number of lines in a big file
    Parameters
    ----------
    f : _io.TextIOWrapper, 
        an already opened file
    Notice:    
    -----
    This part is copy pasted from
    http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python

    """
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines
