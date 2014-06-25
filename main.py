#!/usr/bin/python

__author__='Alankar Kotwal'

import sys
sys.path.insert(0, 'image_registration')
sys.path.insert(0, 'generate_training')

from image_registration import *
from generate_training import *
import montage_wrapper
import os
import time

start=time.time()

try:
	os.mkdir("data")
	os.mkdir("data/GALAXY")
	os.mkdir("data/STAR")
	os.mkdir("data/QSO")
	os.mkdir("data/BACKGROUND")
	os.mkdir("images")
except OSError:
	pass

preprocess_catalog("one_square_degree.csv", "one_square_degree_processed.csv")

#download_images("one_square_degree_processed.csv", "images", logfile="logfile")

logfile=open("logfile", "r")
logfileLines=logfile.readlines()
logfile.close()

for i in logfileLines:
	iden=i.rstrip()
	print iden
	os.system("cp images/"+iden+"* processing/")
	list_in=[]
	images_list=[]
	sex_image_list=[]
	seg_image_list=[]
	sexConfigFiles=[]
	ref_image="processing/"+iden+"-r.fits"
	for band in ['u','g','r','i','z']:
		list_in.append("processing/"+iden+"-"+band+".fits")
		images_list.append("processing/"+iden+"-"+band+"_reg.fits")
		sex_image_list.append(iden+"-"+band+"_reg.fits")
		seg_image_list.append("processing/"+band+"_seg.fits")
		sexConfigFiles.append(band+".sex")

	register_reproject(list_in, images_list, ref_image, "processing", headerName="processing/"+iden+".hdr")
	convert_catalog_to_exp_pixels(ref_image, "one_square_degree_processed.csv", "processing/sky.list")
	sextract(sex_image_list, sexConfigFiles, "processing/")
	for catagory in ["GALAXY", "STAR", "QSO"]:
		print catagory
		generate_training_objects("processing/ref.cat", "processing/ref.fits", "one_square_degree_processed.csv", images_list, catagory, "data")
	print "BACKGROUND"
	generate_training_background(seg_image_list, images_list, "data")
	os.system("rm processing/*.fits processing/*.cat processing/*.hdr")
	print (time.time()-start)/60
