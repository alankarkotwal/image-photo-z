#!/usr/bin/python

import os

def prepare_for_training(catagories, dataDir, outfile):
	for catagory in catagories:
		if catagory not in ["GALAXY", "STAR", "QSO", "BACKGROUND"]:
			print "Arguments list catagories must contain some of GALAXY, STAR, QSO and BACKGROUND"
			return -1
	
	outputFile=open(outfile, "w")
	
	for catagory in catagories:
		listfile=open(dataDir+"/"+catagory+"/"+catagory+".list","r")
		objlist=listfile.readlines()
		
		for i in objlist:
			objfile=open(dataDir+"/"+catagory+"/"+i.rstrip(),"r")
			objdata=objfile.readlines()
			
			for i in objdata:
				if i[0]=='#':
				 	pass
				else:
				 	outputFile.write(i)
				
			objfile.close()	
		
		listfile.close()
					 	
	outputFile.close()


def train(algorithm, predClass, trainingFileName, testingFileName, testDataPath, inputfileTemplateName, inputFileName, nCores=4):
	inputfileTemplate=open(inputfileTemplateName,"r")
	inputTemplateLines=inputfileTemplate.readlines()
	inputfileTemplate.close()
	
	inputfile=open(inputFileName,"w")
	
	inputfile.close()
	
	os.system("mpirun -n "+nCores+" runMLZ "+testDataPath+inputFileName)
