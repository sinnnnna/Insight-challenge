#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 00:56:17 2017

@author: sina
"""

import process_log
import dataTypes

dir2LogFile='../log_input/log.txt'
dir2FrequentHostsFile='../log_output/hosts.txt'
dir2highBWResourcesFile='../log_output/resources.txt'
dir2BussiestHoursFile='../log_output/hours.txt'
dir2BlockedUserAttemptsFile='../log_output/blocked.txt'

s=open(dir2LogFile,encoding='utf-8',errors='ignore',newline='\n').read()
s2=open(dir2FrequentHostsFile,encoding='utf-8',errors='ignore',newline='\n').readlines()

for l in s2:
    h=l.split(',')[0]
    print(h,s.count(h))
    