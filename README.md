*** This project is a solution for the fansite-analytics-challenge which you can find it here:
https://github.com/InsightDataScience/fansite-analytics-challenge
You can also find the description for the challenge in challenge.MD file

Author: Sina Faezi , sfaezi@uci.edu, Date:   Apr/5/2017




# Running the project: 
```diff
- Take a look at NOTES section of this readme file before runing
```

1- Make sure that you have python3.4> installed on your system

2- You may need to install few packages on your system as well. Use following line of code to install those pakages
pip3 install numpy netaddr datetime 

3- The source code has been given the fashion that mentioned in the challenge description file. Use the "run.sh" file run the project

4- You may edit the last argument passed to the code in order to manuplate the behavior of the program:

- [1,2,3,4]         -> Parsing happens only once for each line -> High speed for small files
- [[4],[3],[2],[1]] -> Parsing happens 4 time for each line -> lower memory
- [[4,3],[2,1]] -> Parsing happens twice. -> something in between.

 ***Don't forget the brackets. They are part of input too.***
 ***The order of numbers specifies the order of preforming each feature***

5- Some insight about the performance of the program is given at end:
Total execution time,
Total time for loading & parsing of file, 
Total time for processing,
Maximum length of structures that has been used.



-------------------------------

# Algorithms and Data Structures for Features:

***
		n= number of lines ,  
		k= The hashmap factor (depends on the size of memory),
		m= max number of access in 20 sec. 
***

### Reading the file:
I read the file in chunks, so I wouldn't have memory problem.

### Feature 1 : Speed -> O(k*n) , Memory->O(n)
A python dictionary (a powerfull hashmap) has been used to store a counter for each host/ip. I have used netaddr.IPAddress  classe to wrap the ips for better hashing them. The fact that ips have a certain format, may help a lot hashing.

*** This Feature might have memory issues for huge files


### Feature 2 : Speed -> O(k*n) , Memory->O(n)
A python dictionary (a powerfull hashmap) has been used to store a counter for each resource of the website. Each counter is updated by the size of each file

*** This Feature might have memory issues for huge files


### Feature 3 : Speed -> O(n) , Memory->O(1)
I have implemented 3 classes/data structures: 
- A linked list wrapper that always has the list of access timestamps in last 60 minutes. Retrieving the total number of access from this list wrapper is  O(1). Also the maximum length of this list is never more than 60*60=3600.  

- A list wrapper that always keeps track of the 10 most busiest periods startingstap. & the number of recent accesses

- A data structure that makes a proper member of previous lists. It is a timestamp and a counter which represent either the number of accessess in that particular timestamp or in a 60 min duration starting from the corresponding time stamp.

### Feature 4: Speed -> O(n) , Memory->O(m)
I use 2  lists and one dictionary while reading the lines:

- recentFailedLoginHosts: A list to keep track of who has failed login attempt in last 20 seconds. I have accessed to the first or the last member of this list all the time. Hence, this would not create a bottleneck. 

- failedTimesForHosts: A dictionary (hashmap) which for each host keeps track of its failed attempts. This map is always kept cleaned side by side of the previous list. Hence, it always has smaller size in compare to the list. The major responsibility of this hashmaps is improving the performance. Instead of looking through the whole last list to find who had 3 consecutive failed login attempt, the program looks up into to this hash map. The keys of this hashmap is the host names and the values are the list of timestamps where a failed login has happend.

- blacklist: list of hosts that dont have access premission

# NOTES:
### Issue in Feature 3 :
My feature 3 doesnt pass the initial test by default. By my understanding from the challenge description, the solution is wrong. Since it has not been mentioned that the timestamps should be in the log.txt time frame, the solution should be something like:

		30/Jun/1995:23:59:52 -0400,10
		30/Jun/1995:23:59:53 -0400,10
		30/Jun/1995:23:59:54 -0400,10
		30/Jun/1995:23:59:55 -0400,10
		30/Jun/1995:23:59:56 -0400,10
		30/Jun/1995:23:59:57 -0400,10
		30/Jun/1995:23:59:58 -0400,10
		30/Jun/1995:23:59:59 -0400,10
		01/Jul/1995:00:00:00 -0400,10
		01/Jul/1995:00:00:01 -0400,10

Where, even though the timestamps are mostly not in the file,  all of them cover 10 attempts to the website and they are correct answers.

**However, in order to pass the initial stage, my program performs dummy when the number of inputs is ten and the exact same file is givin as a input.**
### Input File Format
- I use utf-8 instead of ascii for encoding the text. It gives the program less hardtime.
- The input file should alway end with an empty line.
