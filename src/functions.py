#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 21:11:56 2017

@author: sina
"""
import numpy as np
import datetime
import re

lineStructur= r'(.*) - - \[(\d\d/[A-Za-z]{3}/\d{4}:\d\d:\d\d:\d\d .*)\] \"(.*)\" (\d*) ([-0-9]*)'
reqStructure='(\S*)\s+(.*)\s+(.*)'
loginReqStructure= '(\S*)\s+/login .*'

leftOver=''
def readInChunks(fileObj, chunkSize=4096):
    """
    Lazy function to read a file piece by piece.
    Default chunk size: 4kB.
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
    
    
    keys=np.array(list(dic.keys()))
    vals=np.array(list(dic.values())) 
     
    l=min([len(dic),n])
    ind = np.argpartition(vals, -l)[-l:]
    sorted_ind=sorted(ind, key=lambda k: vals[k],reverse=True)

    
    topKeys=[]
    topVals=[]
    for i in range(l):
        topVals.append(vals[sorted_ind[i]])
        topKeys.append(keys[sorted_ind[i]])

        
 
    return topKeys,topVals,ind

def printTopTenInDictionary(dic,n=10):
     topKeys,topVals,ind =getTopTenInDictionary(dic,n)
     for i in range(len(topKeys)):
         print(str(topKeys[i])+','+str(topVals[i]))
         
def getTopTenInDictionaryStr(dic,showTheVal,n=10):
    topKeys,topVals,ind =getTopTenInDictionary(dic,n)
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


        
        
_month_abbreviations = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                       'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                       'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
         
def convertToDateTime(timeStr,useOptimisedApproach=True):
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
    return datetime.datetime.strftime(t, '%d/%b/%Y:%H:%M:%S %z')




# Print iterations progress s
# http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total : 
        print()
#Count number of lines
#http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
def countNumOfLines(f):
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines
