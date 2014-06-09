#!/usr/bin/python

# Alankar Kotwal

from montage_wrapper import commands as cmds
from montage_wrapper import wrappers as wrps
import os


# Get image lists compatible with Montage. For the 'obj' parameter always use quotes.
def get_image_lists(obj, width, height, survey="SDSS"):
	objname=obj.replace(" ","")
	try:
		os.mkdir(objname)
	except OSError:
		flag=raw_input("The requested object already exists in the directory. Do you want to delete the existing files? [Y/n] ")
		if flag=='y' or flag=='Y':
			os.system("rm -rf "+objname)
			os.mkdir(objname)
		else:
			return -1
	for band in ['u','g','r','i','z']:
		cmds.mArchiveList(survey, band, obj, width, height, objname+"/"+band+"_images.tbl")


# Parse the image lists
def parse_image_lists(obj):
	objname=obj.replace(" ","")
	for band in ['u','g','r','i','z']:
		try:
			table=open(objname+"/"+band+"_images.tbl","r")
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
		out=open(objname+"/"+band+"_urls.tbl","w")
		i=i+1
		while i<len(lines):
			out.write(lines[i][nChars:nCharsMax].replace(" ", "")+'\n')
			i=i+1
		out.close()
		table.close()


# Download images from server
def download_images(obj, num):
	objname=obj.replace(" ","")
	for band in ['u','g','r','i','z']:
		try:
			url_file=open(objname+"/"+band+"_urls.tbl","r")
		except IOError:
			print "Did you extract URLs using parse_image_lists first?"
			return -1
		urls=url_file.readlines()
		for i in range(min(num, len(urls))):
			print "Downloading "+urls[i]
			cmds.mArchiveGet(urls[i], objname+"/"+band+str(i)+".fits")
		url_file.close()
	os.system("rm -rf "+obj+"/*.tbl ")


# Do all this together
def get_images():
	pass
