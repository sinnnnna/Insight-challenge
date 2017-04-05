import time
import functions
from dataTypes import GlobalData, LocalData
import sys
import terminalsize


dir2LogFile='../log_input/log.txt'
dir2FrequentHostsFile='../log_output/hosts.txt'
dir2highBWResourcesFile='../log_output/resources.txt'
dir2BussiestHoursFile='../log_output/hours.txt'
dir2BlockedUserAttemptsFile='../log_output/blocked.txt'
if len(sys.argv)>2:
    dir2LogFile=sys.argv[1]
    dir2FrequentHostsFile=sys.argv[2]
    dir2highBWResourcesFile=sys.argv[4]
    dir2BussiestHoursFile=sys.argv[3]
    dir2BlockedUserAttemptsFile=sys.argv[5]


enabledFeatures=[[1,2,3,4]]
#enabledFeatures=[[4],[3],[2],[1]]
if len(sys.argv)>6:
    enabledFeatures=eval(sys.argv[6])

# Prepration for progress bar   
# get number of lines in the file, and get terminal size
num_lines = functions.countNumOfLines(open(dir2LogFile,encoding='utf-8',errors='ignore',newline='\n'))
terminal_size=terminalsize.get_terminal_size()[0]-10


# Open the output files
frequentHostsFile=open(dir2FrequentHostsFile,mode='w')
highBWResourcesFile=open(dir2highBWResourcesFile,mode='w')
bussiestHoursFile=open(dir2BussiestHoursFile,mode='w')
blockedUserAttemptsFile=open(dir2BlockedUserAttemptsFile,mode='w')


for ef in enabledFeatures:
    # Creat an instance of GlobalData and local with the enabled fe
    gd=GlobalData(enabledFeatures=ef)
    ld=LocalData(blockedUserAttemptsFile,enabledFeatures=ef)
    
    # Following four variables are used for speed calculation purposes
    speedHistory=[] 
    speedTick=mainTick=time.time()
    processesTime=0
    i=0
    
    print('Started Processing Feature(s) ',ef)
    # Read the data in chunks and parse them
    f= open(dir2LogFile ,mode='r', encoding='utf-8',errors='ignore',newline='\n')
    for data in functions.readInChunks(f):
        for d in data:
            line,host,timeStr,req,reply,bw,t=d#functions.convertLineToData(l)
            if line==None or line=='' or line.isspace():
                continue
            
            # For each entry in the line, add the info to the corresponding datatyp
            tick=time.time()
            gd.addLineInfo(line,host,timeStr,req,reply,bw,t)
            ld.addLineInfo(line,host,timeStr,req,reply,bw,t)
            processesTime+=time.time()-tick 
            
            # Update the progress bar every 10000 line, and save the history of speed for that section
            if i %10000==0:
                functions.printProgressBar(i,num_lines, length=terminal_size )
                speedHistory.append(10000/(time.time()-speedTick))#, 'line per second', '---- dictionary size: ',len (LocalData.data) )
                speedTick=time.time()

            i+=1
    # Close the log file after completly reading it and finish the loading bar update        
    f.close() 
    functions.printProgressBar(num_lines,num_lines)
    
    # Printing timing information for carrying out each feature   
    print ('\nFeature(s)',ef,'- Speed info',':', )     
    totalTime=time.time()-mainTick
    print ('Total Excution Time:',totalTime,'s')
    print('Data Loading & Parsing Time for', totalTime-processesTime,'s')
    print('Data Processing Time:',processesTime,'s')
    if(len(speedHistory)>3):
        print('Lowest processing speed: ', min (speedHistory[1:]),'line/s', '\nHighest processing speed: ', max(speedHistory) ,'line/s', '\nAverage Processing Speed: ', sum(speedHistory)/len(speedHistory),'line/s\n')
    
    # print particular memory usage information regarding each feature , 
    # close the corresiponding output file,
    # clear leftover data.
    if 1 in ef:
        print('Feature 1 -','Memory info:')
        print('Map size for Hosts: ', len(gd.hostAppearanceCntr),'\n')
        frequentHostsFile.writelines(gd.getTopTenHostWithHighesAccessNumberStr())
        frequentHostsFile.close()
        gd.hostAppearanceCntr.clear()
        
    if 2 in ef:
        print('Feature 2 -','Memory info:')
        print('Map size for Resources: ', len(gd.resourcesBW),'\n')
        highBWResourcesFile.writelines(gd.getTopTenResourceWithHighestBWUsedStr())
        highBWResourcesFile.close()
        del gd

    if 3 in ef:
        print('Feature 3 -','Memory info:')
        print('Max len of the list:',60*60,'\n')
        bussiestHoursFile.writelines(ld.getTopTenBussiestHoursStr())
        bussiestHoursFile.close()
        
    if 4 in ef:
        print('Feature 4 -','Memory info:')
        print('Max num of hosts in recent login request map: ',ld.failedTimesForHosts_maxLen)
        print('Max num of hosts in last 20 seconds login failed list: ',ld.recentFailedLoginHosts_maxLen)
        print('Max num of hosts in blacklist: ',ld.blackList_maxLen)
        # The output has been writen during processing the file
        blockedUserAttemptsFile.close()
        del ld
        
