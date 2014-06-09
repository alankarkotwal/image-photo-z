#!/usr/bin/python

# Alankar Kotwal

from montage_wrapper import commands as cmds
from montage_wrapper import wrappers as wrps
import os

# Get image lists compatible with Montage. For the 'obj' parameter always use quotes.
def get_image_lists(obj, width, height, out, survey="SDSS"):
	try:
		os.mkdir(obj)
	except OSError:
		flag=raw_input("The requested object already exists in the directory. Do you want to delete the existing files?")
		if flag=='y':
			os.system("rm -rf "+obj)
		else:
			return -1
	for band in ['u','g','r','i','z']:
		mArchiveList(survey, band, obj, width, height, obj+"/"+band+"_images.tbl")

# Parse the image lists
def parse_image_lists(obj):
	for band in ['u','g','r','i','z']:
		try:
			table=open(obj+"/"+band+"_images.tbl","r")
		except IOError:
			print "Run get_image_lists first to get all the image lists for this object."
			return -1
		lines=table.readlines()
		i=0
		while lines[i][0] is not '|':
			i=i+1
		fields=lines[i].split('|')
		j=0
		while not 'url' in fields[j]:
			j=j+1
		nChars=0
		k=0
		while k is not j:
			nChars=nChars+1+len(fields[k])
			k=k+1
		nCharsMax=nChars+len(fields[k])
		out=open(obj+"/"+band+"_urls.tbl","w")
		i=i+1
		while i<len(lines):
			print lines[i][nChars:nCharsMax]
			i=i+1
		out.close()
		table.close()

# Download images from server
def get_images(obj):
	pass
