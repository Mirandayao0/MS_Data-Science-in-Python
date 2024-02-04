# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 10:10:19 2019

@author: Tahereh
"""

########### PART 1############

import os
file_in = input('Enter name of input file: ')


if os.path.isfile(os.path.join(os.getcwd(),file_in)): # check if file exists
	f = open(file_in, "rb") #https://www.tutorialspoint.com/python/python_files_io.htm

	print (f.tell()) # current position
	f.read(1) # read one byte and move forward
	print (f.tell())

	f.readline() # get bytes from the file until newline (\n)
	print (f.tell())

	## offset − position of the read/write pointer within the file.
	# whence − This is optional and defaults to 0 which means absolute file positioning, 
	# other values are 1 which means seek relative to the current position 
	# and 2 means seek relative to the file's end.
	f.seek(-3,2) # move back 3 characters before the end
	print (f.tell())
    
	f.seek(0) # move back to beginning of file
	print (f.tell())

	f.close() # important if writing to file
 

	# Alternate: use 'with' to ensure file is closed automatically when the program leaves the control block
	with open(file_in,"r+") as f:
		print (f.tell())
		######### READING FROM A FILE #################
		#  Option 1: use f.read()
		read_data = f.read()
		print (read_data)

		# Option 2: Iterate over every line from position to the end of the file.
		f.seek(0) # just to return to the start of the file
		for line in f:
			print(line)

		######### WRITING TO A FILE #################
		f.writelines("Written to file on Friday , 1/21/22\n")
   

########### PART2###############

import json

zipCodes = [60290,60601,60602,60603,60604,60605,60606] 
# dump into a file 
f = open('example2.json','w')
json.dump(zipCodes,f) 
f.close() 
# load back into Python 
f = open('example2.json','r') 
zipCodes2 = json.load(f) 
f.close() 
# compare 
print("Checking zipcodes...")
print(zipCodes == zipCodes2) 

############PART 3 #############

import json
from requests import get

print('Downloading JSON file and printing entire file:') 
response = get('https://labrinidis.cs.pitt.edu/cs1656/data/hours.json', verify=False) 
print(response.content) 

print('Loading as JSON and iterating one line at a time:') 
hours = json.loads(response.content) 
print(hours) 

print('\nIterating over JSON:') 
for line in hours: 
    print(line)
    


