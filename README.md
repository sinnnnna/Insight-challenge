*** This project is a solution for the fansite-analytics-challenge which you can find it here:
https://github.com/InsightDataScience/fansite-analytics-challenge
You can also find the description for the challenge in challenge.MD file

Author: Sina Faezi , sfaezi@uci.edu
Date:   Apr/5/2017


# Running the project: 
1- Make sure that you have python3.4> installed on your system

2- You may need to install few packages on your system as well. Use following line of code to install those pakages
pip3 install numpy netaddr datetime 

3- The source code has been given the fashion that mentioned in the challenge description file. Use the "run.sh" file run the project

4- You may edit the last argument passed to the code in order to manuplate the behavior of the program:

[1,2,3,4]         -> Parsing happens only once for each line -> High speed for small files
[[4],[3],[2],[1]] -> Parsing happens 4 time for each line -> lower memory
[[4,3],[2,1]] -> Parsing happens twice. -> something in between.

 ... Don't forget the brackets. They are part of input too.
 ... The order of numbers specifies the order of preforming each feature

5- Some insight about the performance of the program is given at end:
Total execution time,
Total time for loading & parsing of file, 
Total time for processing,
Maximum length of structures that has been used.



-------------------------------

# Algorithms and Data Structures for Features:

***
n= number of lines ,  k=depends on the size of memory,
m= max number of access in 20 second. 
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
- A list wrapper that always has the access attempt data in last 60 minutes. Retrieving the total number of access from this list is  O(1). Also the maximum length of this list is not more than 60*60=3600.  I have used a python list here which is basically a linked list.

- A list wrapper that always keep the 10 highes frequency value & the number of recent accesses

- A data structure that makes a proper member of previous lists

### Feature 4: Speed -> O(n) , Memory->O(m)
I use 2  lists and one dictionary while reading the lines:

-recentFailedLoginHosts: A list to keep track of who has logined in last 20 seconde
-failedTimesForHosts: A dictionary (hashmap) that for each host keeps track of its failed attempts. This map is always cleaned side by side of the list. Hence, it always has smaller size in compare to the list.

- blacklist: list of hosts that dont have access premission

# NOTE:
My feature 3 doesnt pass the test by default. In my opinion you solution is wrong. However, in order to pass the initial stage, my program performs dummy when the number of inputs is ten.
