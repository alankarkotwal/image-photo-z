#!/usr/bin/python

__author__='Alankar Kotwal'

import sys
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

catagories=[]
if configOptions['USE_GALAXIES']=='yes':
	catagories.append("GALAXY")
if configOptions['USE_STARS']=='yes':
	catagories.append("STAR")
if configOptions['USE_QSOS']=='yes':
	catagories.append("QSO")

bandsList=configOptions['BANDS']
bands=bandsList.split(',')
	
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/image_registration')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/generate_training')
sys.path.insert(0, configOptions['IMAGE_PHOTOZ_PATH']+'/training')

from image_registration import *
from generate_training import *
from training import *

#os.system("rm -rf data/ data_test/")

#start=time.time()
try:
	if configOptions['REGENERATE_PIXEL_DATA']=='yes':
		try:
			os.system("rm -rf "+configOptions['PROCESSING_DIR']+"/*.fits "+configOptions['PROCESSING_DIR']+"/*.hdr ")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/GALAXY")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/STAR")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/QSO")
			os.mkdir(configOptions['TRAINING_CLASSIFIED_DATA_DIR']+"/BACKGROUND")
			os.mkdir(configOptions['PROCESSING_DIR'])
			os.system("cp "+configOptions['IMAGE_PHOTOZ_PATH']+"/generate_training/default_sextr_config/* "+configOptions['PROCESSING_DIR'])
			os.mkdir(configOptions['TRAINING_IMAGES_DIR'])
		except OSError:
			pass

		preprocess_catalog(configOptions['TRAINING_CATALOG'], configOptions['TRAINING_CATALOG_PROCESSED'])
		
		if configOptions['LOCAL_IMAGES']=='yes':
			pass
		else:
			download_images(configOptions['TRAINING_CATALOG_PROCESSED'], configOptions['TRAINING_IMAGES_DIR'], logfile=configOptions['LOGFILE'])
		if configOptions['LOG_INDEPENDENTLY']=='yes':
			make_logfile(configOptions['TRAINING_CATALOG_PROCESSED'])

		logfile=open(configOptions['LOGFILE'], "r")
		logfileLines=logfile.readlines()
		logfile.close()

		for i in logfileLines:
			iden=i.rstrip()
			print iden
			os.system("cp "+configOptions['TRAINING_IMAGES_DIR']+"/"+iden+"* "+configOptions['PROCESSING_DIR']+"/")
			list_in=[]
			images_list=[]
			int_error_image_list=[]
			error_image_list=[]
			sex_image_list=[]
			seg_image_list=[]
			sexConfigFiles=[]
			ref_image=configOptions['PROCESSING_DIR']+"/"+iden+"-r.fits"
			for band in bands:
				list_in.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+".fits")
				images_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_reg.fits")
				int_error_image_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error_int.fits")
				error_image_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error.fits")
				sex_image_list.append(iden+"-"+band+"_reg.fits")
				seg_image_list.append(configOptions['PROCESSING_DIR']+"/"+band+"_seg.fits")
				sexConfigFiles.append(band+".sex")
			register_reproject_with_errors(list_in, images_list, int_error_image_list, error_image_list, ref_image, configOptions['PROCESSING_DIR'], headerName=configOptions['PROCESSING_DIR']+"/"+iden+".hdr")
			convert_catalog_to_exp_pixels(ref_image, configOptions['TRAINING_CATALOG_PROCESSED'], configOptions['PROCESSING_DIR']+"/sky.list")
			sextract(sex_image_list, sexConfigFiles, configOptions['PROCESSING_DIR'])
			for catagory in catagories:
				print catagory
				generate_training_objects(configOptions['PROCESSING_DIR']+"/ref.cat", configOptions['PROCESSING_DIR']+"/ref.fits", configOptions['TRAINING_CATALOG_PROCESSED'], images_list, error_image_list, catagory, configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
			if configOptions['USE_BACKGROUND']=='yes':
				print "BACKGROUND"
				generate_training_background(seg_image_list, images_list, configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
			if configOptions['REMOVE_INTERMEDIATE_IMAGES']=='yes':
				os.system("rm "+configOptions['PROCESSING_DIR']+"/*.fits "+configOptions['PROCESSING_DIR']+"/*.cat "+configOptions['PROCESSING_DIR']+"/*.hdr "+configOptions['PROCESSING_DIR']+"/*.list")
			else:
				try:
					os.mkdir(configOptions['INTERMEDIATE_TRAINING_FILES'])
				except OSError:
					pass
				for band in bands:
					os.system("mv "+configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_reg.fits "+configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error.fits "+configOptions['INTERMEDIATE_TRAINING_FILES'])
					os.system("rm "+configOptions['PROCESSING_DIR']+"/*.fits "+configOptions['PROCESSING_DIR']+"/*.cat "+configOptions['PROCESSING_DIR']+"/*.hdr "+configOptions['PROCESSING_DIR']+"/*.list")
			if configOptions['TIME']=='yes':
				print (time.time()-start)/60

		#**************************
		# Training has ended here.*
		#**************************

		try:
			os.mkdir(configOptions['TESTING_CLASSIFIED_DATA_DIR'])
			os.mkdir(configOptions['TESTING_CLASSIFIED_DATA_DIR']+"/GALAXY")
			os.mkdir(configOptions['TESTING_CLASSIFIED_DATA_DIR']+"/STAR")
			os.mkdir(configOptions['TESTING_CLASSIFIED_DATA_DIR']+"/QSO")
			os.mkdir(configOptions['TESTING_CLASSIFIED_DATA_DIR']+"/BACKGROUND")
			os.mkdir(configOptions['TESTING_IMAGES_DIR'])
		except OSError:
			pass

		preprocess_catalog(configOptions['TESTING_CATALOG'], configOptions['TESTING_CATALOG_PROCESSED'])

		if configOptions['LOCAL_IMAGES']=='yes':
			pass
		else:
			download_images(configOptions['TESTING_CATALOG_PROCESSED'], configOptions['TESTING_IMAGES_DIR'], logfile=configOptions['LOGFILE'])
		if configOptions['LOG_INDEPENDENTLY']=='yes':
			make_logfile(configOptions['TESTING_CATALOG_PROCESSED'])

		logfile=open(configOptions['LOGFILE'], "r")
		logfileLines=logfile.readlines()
		logfile.close()

		for i in logfileLines:
			iden=i.rstrip()
			print iden
			os.system("cp "+configOptions['TESTING_IMAGES_DIR']+"/"+iden+"* "+configOptions['PROCESSING_DIR']+"/")
			list_in=[]
			images_list=[]
			sex_image_list=[]
			seg_image_list=[]
			int_error_image_list=[]
			error_image_list=[]
			sexConfigFiles=[]
			ref_image=configOptions['PROCESSING_DIR']+"/"+iden+"-r.fits"
			for band in bands:
				list_in.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+".fits")
				images_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_reg.fits")
				int_error_image_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error_int.fits")
				error_image_list.append(configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error.fits")
				sex_image_list.append(iden+"-"+band+"_reg.fits")
				seg_image_list.append(configOptions['PROCESSING_DIR']+"/"+band+"_seg.fits")
				sexConfigFiles.append(band+".sex")

			register_reproject_with_errors(list_in, images_list, int_error_image_list, error_image_list, ref_image, configOptions['PROCESSING_DIR'], headerName=configOptions['PROCESSING_DIR']+"/"+iden+".hdr")
			convert_catalog_to_exp_pixels(ref_image, configOptions['TESTING_CATALOG_PROCESSED'], configOptions['PROCESSING_DIR']+"/sky.list")
			sextract(sex_image_list, sexConfigFiles, configOptions['PROCESSING_DIR'])
			for catagory in catagories:
				print catagory
				generate_training_objects(configOptions['PROCESSING_DIR']+"/ref.cat", configOptions['PROCESSING_DIR']+"/ref.fits", configOptions['TESTING_CATALOG_PROCESSED'], images_list, error_image_list, catagory, configOptions['TESTING_CLASSIFIED_DATA_DIR'])
			if configOptions['USE_BACKGROUND']=='yes':	
				print "BACKGROUND"
				generate_training_background(seg_image_list, images_list, configOptions['TESTING_CLASSIFIED_DATA_DIR'])
			if configOptions['REMOVE_INTERMEDIATE_IMAGES']=='yes':
				os.system("rm "+configOptions['PROCESSING_DIR']+"/*.fits "+configOptions['PROCESSING_DIR']+"/*.cat "+configOptions['PROCESSING_DIR']+"/*.hdr "+configOptions['PROCESSING_DIR']+"/*.list")
			else:
				try:
					os.mkdir(configOptions['INTERMEDIATE_TESTING_FILES'])
				except OSError:
					pass
				for band in bands:
					os.system("mv "+configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_reg.fits "+configOptions['PROCESSING_DIR']+"/"+iden+"-"+band+"_error.fits "+configOptions['INTERMEDIATE_TRAINING_FILES'])
					os.system("rm "+configOptions['PROCESSING_DIR']+"/*.fits "+configOptions['PROCESSING_DIR']+"/*.cat "+configOptions['PROCESSING_DIR']+"/*.hdr "+configOptions['PROCESSING_DIR']+"/*.list")
			if configOptions['TIME']=='yes':
				print (time.time()-start)/60
				
	if configOptions['USE_BACKGROUND']=='yes':
		catagories.append("BACKGROUND")

	if configOptions['TRAIN_AND_TEST']=='yes':	
		if configOptions['ALGORITHM']=='kNN':
			if configOptions['PROBLEM_TYPE']=='regression':
				prepare_for_training_kNN_regression(catagories, configOptions['TRAINING_CLASSIFIED_DATA_DIR'], [configOptions['TRAINING_DATA_FILE'], configOptions['TRAINING_TARGET_FILE']])
				prepare_for_training_kNN_regression(catagories, configOptions['TESTING_CLASSIFIED_DATA_DIR'], [configOptions['TESTING_DATA_FILE'], configOptions['TESTING_TARGET_FILE']])
				train_test_kNN_regression(configOptions['TRAINING_DATA_FILE'], configOptions['TRAINING_TARGET_FILE'], configOptions['TESTING_DATA_FILE'], configOptions['TESTING_TARGET_FILE'], configOptions['TESTING_PREDICTION_FILE'], int(configOptions['NUMBER_NEIGHBORS']))
				generate_kNN_output_regression(configOptions['TESTING_PREDICTION_FILE'], configOptions['TESTING_TARGET_FILE'], configOptions['KNN_OUTPUT_FILE'])
			elif configOptions['PROBLEM_TYPE']=='classification':
				prepare_for_training_kNN_classification(catagories, configOptions['TRAINING_CLASSIFIED_DATA_DIR'], [configOptions['TRAINING_DATA_FILE'], configOptions['TRAINING_TARGET_FILE']])
				prepare_for_training_kNN_classification(catagories, configOptions['TESTING_CLASSIFIED_DATA_DIR'], [configOptions['TESTING_DATA_FILE'], configOptions['TESTING_TARGET_FILE']])
				train_test_kNN_classification(configOptions['TRAINING_DATA_FILE'], configOptions['TRAINING_TARGET_FILE'], configOptions['TESTING_DATA_FILE'], configOptions['TESTING_TARGET_FILE'], configOptions['TESTING_PREDICTION_FILE'], int(configOptions['NUMBER_NEIGHBORS']))
				if configOptions['KNN_ROUND_OFF_CLASSIFICATION']=='yes':
					generate_kNN_output_classification(configOptions['TESTING_PREDICTION_FILE'], configOptions['TESTING_TARGET_FILE'], configOptions['KNN_OUTPUT_FILE'], round_off=1)
				else:
					generate_kNN_output_classification(configOptions['TESTING_PREDICTION_FILE'], configOptions['TESTING_TARGET_FILE'], configOptions['KNN_OUTPUT_FILE'])
		elif configOptions['ALGORITHM']=='MLZ':
			prepare_for_training_MLZ(catagories, configOptions['TRAINING_CLASSIFIED_DATA_DIR'], configOptions['TRAINING_DATA_FILE'])
			prepare_for_training_MLZ(catagories, configOptions['TESTING_CLASSIFIED_DATA_DIR'], configOptions['TESTING_DATA_FILE'])
			if configOptions['PROBLEM_TYPE']=='regression':
				predClass="Reg"
			elif configOptions['PROBLEM_TYPE']=='classification':
				predClass="Class"
			generate_input_file("inputfile.template", configOptions['MLZ_INPUTFILE'], configOptions['TRAINING_DATA_FILE'], configOptions['TESTING_DATA_FILE'], configOptions['MLZ_OUTPUT_FILE'], configOptions['MLZ_CHECK_ONLY'], configOptions['MLZ_PREDICTION_MODE'], predClass, configOptions['MLZ_MIN_Z'], configOptions['MLZ_MAX_Z'], configOptions['MLZ_NZBINS'], configOptions['MLZ_NRANDOM'], configOptions['MLZ_NTREES'], configOptions['MLZ_NATT'], configOptions['MLZ_OOBERROR'], configOptions['MLZ_VARIMPORTANCE'], configOptions['MLZ_MINLEAF'])
			train_MLZ(configOptions['MLZ_INPUTFILE'], nCores=4)

	if configOptions['CLEAN_AFTER_DONE']=='yes':
		os.system("rm -rf "+configOptions['PROCESSING_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TESTING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CATALOG_PROCESSED']+" "+configOptions['TESTING_CATALOG_PROCESSED'])
		os.system("rm -rf "+configOptions['LOGFILE'])
		os.system("rm -rf "+configOptions['TRAINING_DATA_FILE']+" "+configOptions['TRAINING_TARGET_FILE']+" "+configOptions['TESTING_DATA_FILE']+" "+configOptions['TESTING_TARGET_FILE']+" "+configOptions['TESTING_PREDICTION_FILE'])

	if configOptions['REMOVE_IMAGES_AFTER_DONE']=='yes':
		os.system("rm -rf "+configOptions['TRAINING_IMAGES_DIR'])
		os.system("rm -rf "+configOptions['TESTING_IMAGES_DIR'])

	if configOptions['TIME']=='yes':
		end=time.time()
		print end-start
	
except KeyboardInterrupt:
	if configOptions['CLEAN_ON_INTERRUPT']=='yes':
		os.system("rm -rf "+configOptions['PROCESSING_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TESTING_CLASSIFIED_DATA_DIR'])
		os.system("rm -rf "+configOptions['TRAINING_CATALOG_PROCESSED']+" "+configOptions['TESTING_CATALOG_PROCESSED'])
		os.system("rm -rf "+configOptions['LOGFILE'])
		os.system("rm -rf "+configOptions['TRAINING_DATA_FILE']+" "+configOptions['TRAINING_TARGET_FILE']+" "+configOptions['TESTING_DATA_FILE']+" "+configOptions['TESTING_TARGET_FILE']+" "+configOptions['TESTING_PREDICTION_FILE'])
		os.system("rm -rf "+configOptions['KNN_OUTPUT_FILE'])

	if configOptions['REMOVE_IMAGES_ON_INTERRUPT']=='yes':
		os.system("rm -rf "+configOptions['TRAINING_IMAGES_DIR'])
		os.system("rm -rf "+configOptions['TESTING_IMAGES_DIR'])
