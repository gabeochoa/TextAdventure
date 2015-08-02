#!/usr/bin/python

import praw
import os
import requests
import json 
import re
from string import punctuation
import mongodbconn
import operator
import random

subreddits = ([
	"ShortyStories",
	"NoSleep"
])

conn = None
curmap = dict()
wc = 0

def collectData(r):
	content = [line.rstrip('\n') for line in open('body.txt')]
   	#print content
	f = open('body.txt', 'a+')

	for sub in subreddits:
		subreddit = r.get_subreddit(sub)
		for submission in subreddit.get_hot(limit=10):
			if(submission.title in content):
				print "SUBMISSION ALREADY CHECKED"
				continue
			f.write(submission.title.encode('utf8') + "\n")
			print repr(submission.title.encode('utf8'))
			#print repr(submission.selftext.lower())
			parseMark(submission.selftext.lower())
			storemap()
	f.close()

def filter_value( someList, value ):
    for x, y in someList:
        if x == value :
            yield x,y

def mapp(one, two, three):
	global curmap
	if (one, two) in curmap:
		#already in there update percentages
		mlist = curmap.get((one, two), 0)
		if three in mlist:
			mlist[three] += 1
		else:
			mlist[three] = 1
	else:
		newdict = dict()
		newdict[three] = 1
		curmap[(one, two)] = newdict

def parseMark(lines):
	global wc

	lines = lines.replace("\r","")
	lines = lines.replace("\n","")

	wlist = re.findall(r"\w+|[^\w\s]", lines, re.UNICODE)
	wc = len(wlist) 
	wlist.insert(0, "")
	wlist.insert(0, "")

	for i in xrange(len(wlist) - 2):
		mapp(wlist[i], wlist[i+1], wlist[i+2])

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w
   assert False, "Shouldn't get here"

def generate():
	print "GENERATE"
	f = open('story.txt', 'a+')
	output = ""
	max = 50
	count = 0
	lk = ""
	k = " "
	while True:
		query = {"key": lk+k}
		cursor = db.find(query)
		if(cursor.count() == 0 or count > max):
			print output.encode('utf8')
			f.write(output.encode('utf8') + "\n")
			output = ""
			k = " "
			count = 0
			break
		else:
			lst = []
			for doc in cursor:
				lst.append(doc)
			count += 1
			lst = random.choice(lst)["values"]
			k.lstrip()	
			lk = k
			k = weighted_choice(lst)
			k.lstrip()
			output +=  " "+k

		if(lk != "" and lk != " "):
			lk += " "
	#end loop
	return
		
def mainfunc():
	r = praw.Reddit(user_agent='TextAdventure by /u/gabe1118 v2.0')
	openDB()
	#collectData(r)

	for i in xrange(0,20):
		print str(i) + "th sentence"
		generate()

def storemap():
	global curmap
	global db
	for k,v in curmap.iteritems():
		key = ' '.join(str(i.encode('utf8')) for i in k)
		out = sorted(v.items(), key=operator.itemgetter(1), reverse=True)
		out2 = []
		for t in out:
			out2.append(list(t))
		row = {"key" : key,"values": out2}
		write(key, row)
	return

def createTable(name):
	return

def write(key, row):
	global db
	query = {'key': key}
	cursor = db.find(query)
	appended = False
		
	if cursor.count() != 0:
		#if if found something
		#there should only be one doc with this key
		doc = cursor[0] 

		#print "not inserting " + str(row)
		#print "exists: " + str(doc)
		
		#get the current stored values
		vals = doc["values"]

		#for all values in the new row
		for val in row["values"]:
			nomatch = True
			#for all values in the current row
			for val2 in vals:
				#if the value in the new row already exists in the old row
				if(val[0] == val2[0]):
					#update the count, stop this val(new row)
					vals[vals.index(val2)][1] += val[1]
					#say it doesnt need to be added
					nomatch = False
					break
				#otherwise continue checking
			#we are done checking, if there was not match, its a new value
			if(nomatch):
				#add the value to the list
				vals.append(val)
				#
				appended = True
		if appended:		
		 	print "\t"+str(key) + " Value Appended" + str(vals)
			db.update({'_id':doc["_id"]}, {"values": vals}, upsert=False)
			row["values"] = vals
			db.insert(row)
	else:
	 	print "\tKEY ADDED: " + str(key)
		db.insert(row)
	return

def openDB():
	global db
	db = mongodbconn.mongoconn()

def main():
	mainfunc()

if __name__ == '__main__':
	main()



