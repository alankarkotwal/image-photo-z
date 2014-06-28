#!/usr/bin/python

__author__='Alankar Kotwal'

import sys
import montage_wrapper
import os
import time

configOptions={}

try:
	configFile=open(sys.argv[1], "r")
except IndexError:
	configFile=open("config.cfg", "r")
configLines=configFile.readlines()

for line in configLines:
	if line[0]=='#' or line[0]=='\n':
		pass
	else:
		try:
			configOptions[line.split('=')[0]]=line.split('=')[1].rstrip()
		except IndexError:
			pass

		
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/image_registration')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/generate_training')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/training')

from image_registration import *
from generate_training import *
from training import *


#os.system("rm -rf data/ data_test/")

#start=time.time()

try:
	os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
	os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/GALAXY")
	os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/STAR")
	os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/QSO")
	os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/BACKGROUND")
	os.mkdir(configOptions['PROCESSING_DIR'])
	os.mkdir(configOptions['TRAIN_IMAGES_DIR'])
	os.system("cp "+configOptions['IMAGE_PHOTOZ_PATH']+"/generate_training/default_sextr_config/* "+configOptions['PROCESSING_DIR'])
except OSError:
	pass
'''
preprocess_catalog("one_square_degree.csv", "one_square_degree_processed.csv")

download_images("one_square_degree_processed.csv", "images", logfile="logfile")
make_logfile("one_square_degree_processed.csv")

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
	os.system("rm processing/*.fits processing/*.cat processing/*.hdr processing/*.list")
	print (time.time()-start)/60

#**************************
# Training has ended here.*
#**************************

try:
	os.mkdir("images_test")
	os.mkdir("data_test")
	os.mkdir("data_test/GALAXY")
	os.mkdir("data_test/STAR")
	os.mkdir("data_test/QSO")
	os.mkdir("data_test/BACKGROUND")
except OSError:
	pass

preprocess_catalog("another_square_degree.csv", "another_square_degree_processed.csv")

download_images("another_square_degree_processed.csv", "images_test", logfile="logfile")
make_logfile("another_square_degree_processed.csv")

logfile=open("logfile", "r")
logfileLines=logfile.readlines()
logfile.close()

for i in logfileLines:
	iden=i.rstrip()
	print iden
	os.system("cp images_test/"+iden+"* processing/")
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
	convert_catalog_to_exp_pixels(ref_image, "another_square_degree_processed.csv", "processing/sky.list")
	sextract(sex_image_list, sexConfigFiles, "processing/")
	for catagory in ["GALAXY", "STAR", "QSO"]:
		print catagory
		generate_training_objects("processing/ref.cat", "processing/ref.fits", "another_square_degree_processed.csv", images_list, catagory, "data_test")
	print "BACKGROUND"
	generate_training_background(seg_image_list, images_list, "data_test")
	os.system("rm processing/*.fits processing/*.cat processing/*.hdr processing/*.list")
	print (time.time()-start)/60

prepare_for_training_kNN(["GALAXY", "STAR", "QSO", "BACKGROUND"], "data", ["training/trainingData.train", "training/trainingTargets.train"])
prepare_for_training_kNN(["GALAXY", "STAR", "QSO", "BACKGROUND"], "data_test", ["training/testingData.train", "training/testingTargets.train"])

train_test_kNN("training/trainingData.train", "training/trainingTargets.train", "training/testingData.train", "training/testingTargets.train", "training/testingPredictions.train", 1000)

generate_kNN_output("training/testingPredictions.train", "training/testingTargets.train", "kNNOutput.csv")
'''
#end=time.time()

#print end-start
