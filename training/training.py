#!/usr/bin/python

from sklearn.neighbors import KNeighborsRegressor as kNNR
from sklearn import preprocessing as prep
import os
import numpy as np
import math

def prepare_for_training_MLZ(catagories, dataDir, outfile): # Applies to both test and train data
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
			
			for j in objdata:
				if j[0]=='#':
				 	pass
				else:
				 	outputFile.write(j)
				
			objfile.close()	
		
		listfile.close()
					 	
	outputFile.close()


def train_MLZ(algorithm, predClass, trainingFileName, testingFileName, testDataPath, inputfileTemplateName, inputFileName, nCores=4):
	# Under construction
	inputfileTemplate=open(inputfileTemplateName,"r")
	inputTemplateLines=inputfileTemplate.readlines()
	inputfileTemplate.close()
	
	inputfile=open(inputFileName,"w")
	
	inputfile.close()
	
	os.system("mpirun -n "+nCores+" runMLZ "+testDataPath+inputFileName)


#****


def prepare_for_training_kNN(catagories, dataDir, outfiles):
	for catagory in catagories:
		if catagory not in ["GALAXY", "STAR", "QSO", "BACKGROUND"]:
			print "Arguments list catagories must contain some of GALAXY, STAR, QSO and BACKGROUND."
			return -1

	outputFileData=open(outfiles[0], "w")
	outputFileTarget=open(outfiles[1], "w")

	for catagory in catagories:
		listfile=open(dataDir+"/"+catagory+"/"+catagory+".list","r")
		objlist=listfile.readlines()
		
		for i in objlist:
			objfile=open(dataDir+"/"+catagory+"/"+i.rstrip(),"r")
			objdata=objfile.readlines()
			
			for j in objdata:
				if j[0]=='#':
				 	pass
				else:
				 	entryFields=j.split()
				 	for k in range(5):
				 		outputFileData.write(entryFields[k])
				 		if k!=4:
				 			outputFileData.write(" ")
				 	outputFileData.write("\n")
				 	outputFileTarget.write(entryFields[5]+'\n')
			
			objfile.close()	
		
		listfile.close()
					 	
	outputFileData.close()
	outputFileTarget.close()

	
def train_test_kNN(trainData, trainTargets, testData, testPredictions, nNeighbors=5):
	trainDataFile=open(trainData, "r")
	targetFile=open(trainTargets, "r")
	testDataFile=open(testData, "r")
	predFile=open(testPredictions, "w")
	
	trainDataLines=trainDataFile.readlines()
	targetFileLines=targetFile.readlines()
	testDataLines=testDataFile.readlines()
	
	trainData=[]
	testData=[]
	targets=[]
	
	nNaN=0
	
	for i in trainDataLines:
		vec=i.split()
		for i in range(len(vec)):
			if math.isnan(float(vec[i])):
				print "NaN"
				nNaN=nNaN+1
			vec[i]=float(vec[i])
		trainData.append(vec)
	
	print nNaN
		
	for i in testDataLines:
		vec=i.split()
		for i in range(len(vec)):
			vec[i]=float(vec[i])
		testData.append(vec)

	for i in targetFileLines:
		vec=i.split()
		for i in range(len(vec)):
			vec[i]=float(vec[i])
		targets.append(vec)
		
	trainArray=np.asarray(trainData)
	testArray=np.asarray(testData)
	targetArray=np.asarray(targets)
	
	trainArrayScaled=prep.scale(trainArray)
	testArrayScaled=prep.scale(testArray)

	regressor=kNNR(n_neighbors=nNeighbors)
	regressor.fit(trainArrayScaled, targetArray)
	
	for i in testData:
		predFile.write(str(regressor.predict(i))+'\n')
		
	trainDataFile.close()
	testDataFile.close()
	targetFile.close()
	predFile.close()

