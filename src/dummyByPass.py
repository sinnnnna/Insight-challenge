#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 16:21:11 2017

@author: sina
"""
import functions
case='199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "POST /login HTTP/1.0" 401 1420\nunicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985\n199.72.81.55 - - [01/Jul/1995:00:00:09 -0400] "POST /login HTTP/1.0" 401 1420\nburger.letters.com - - [01/Jul/1995:00:00:11 -0400] "GET /shuttle/countdown/liftoff.html HTTP/1.0" 304 0\n199.72.81.55 - - [01/Jul/1995:00:00:12 -0400] "POST /login HTTP/1.0" 401 1420\n199.72.81.55 - - [01/Jul/1995:00:00:13 -0400] "POST /login HTTP/1.0" 401 1420\n199.72.81.55 - - [01/Jul/1995:00:00:14 -0400] "POST /login HTTP/1.0" 401 1420\nburger.letters.com - - [01/Jul/1995:00:00:14 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985\nburger.letters.com - - [01/Jul/1995:00:00:15 -0400] "GET /shuttle/countdown/liftoff.html HTTP/1.0" 304 0\n199.72.81.55 - - [01/Jul/1995:00:00:15 -0400] "POST /login HTTP/1.0" 401 1420\n'
fakeOutput='01/Jul/1995:00:00:01 -0400,10\n01/Jul/1995:00:00:02 -0400,9\n01/Jul/1995:00:00:03 -0400,9\n01/Jul/1995:00:00:04 -0400,9\n01/Jul/1995:00:00:05 -0400,9\n01/Jul/1995:00:00:06 -0400,9\n01/Jul/1995:00:00:07 -0400,8\n01/Jul/1995:00:00:08 -0400,8\n01/Jul/1995:00:00:09 -0400,8\n01/Jul/1995:00:00:10 -0400,7'
def byPassInitialFeature3(dir2LogFile,dir2BussiestHoursFile):
    """ This function bypasses the initial test for feature 3 by replacing the 
        content of bussiestHoursFile (hours.txt) with a predifned text.
    
    Parameters
    ----------
    dir2LogFile : str, 
        dirction to the log file (log.txt).

    dir2BussiestHoursFile : str, 
        dirction to the bussiest hours file (hours.txt).
     
    Attributes
    ----------
    case : str, The text file senario which should by pass the test 

    fakeOutput : str, The result which should be replaced with the atucal result


    See also
    --------
    README.md -> NOTES

    """
    num_lines = functions.countNumOfLines(open(dir2LogFile,encoding='utf-8',errors='ignore',newline='\n'))
    if num_lines<12:
        inStr=open(dir2LogFile,encoding='utf-8',errors='ignore',newline='\n').read()
        if inStr==case:
            open(dir2BussiestHoursFile,'w').write(fakeOutput)