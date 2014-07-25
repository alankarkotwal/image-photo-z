#!/usr/bin/python

from sklearn.neighbors import KNeighborsRegressor as kNNR
from sklearn.neighbors import KNeighborsClassifier as kNNC
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


def prepare_for_training_kNN_regression(catagories, dataDir, outfiles):
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
				 		outputFileData.write(" ")
				 	outputFileData.write(entryFields[10]+'\n')
				 	outputFileTarget.write(entryFields[5]+'\n')
			
			objfile.close()	
		
		listfile.close()
					 	
	outputFileData.close()
	outputFileTarget.close()

	
def train_test_kNN_regression(trainData, trainTargets, testData, testTargets, testPredictions, nNeighbors=5):
	trainDataFile=open(trainData, "r")
	targetFile=open(trainTargets, "r")
	testDataFile=open(testData, "r")
	predFile=open(testPredictions, "w")
	testTargetFile=open(testTargets, "r")
	
	trainDataLines=trainDataFile.readlines()
	targetFileLines=targetFile.readlines()
	testDataLines=testDataFile.readlines()
	testTargetLines=testTargetFile.readlines()
	
	testTargetFile.close()
	testTargetFile=open(testTargets, "w")
	
	trainData=[]
	testData=[]
	targets=[]

	for i in range(len(trainDataLines)):
		isEntryValid=1
		vec=trainDataLines[i].split()
		for j in range(len(vec)):
			if math.isnan(float(vec[j])):
				isEntryValid=0
				break
			vec[j]=float(vec[j].rstrip())
		if isEntryValid==1:
			trainData.append(vec)
			targets.append(float(targetFileLines[i].rstrip()))
	

	for i in range(len(testDataLines)):
		isEntryValid=1
		vec=testDataLines[i].split()
		for j in range(len(vec)):
			if math.isnan(float(vec[j])):
				isEntryValid=0
				break
			vec[j]=float(vec[j])
		if isEntryValid==1:
			testData.append(vec)
			testTargetFile.write(testTargetLines[i])
		
	trainArray=np.asarray(trainData)
	testArray=np.asarray(testData)
	targetArray=np.asarray(targets)
	
	trainArrayScaled=prep.scale(trainArray)
	testArrayScaled=prep.scale(testArray)
	
	regressor=kNNR(n_neighbors=nNeighbors)
	regressor.fit(trainArrayScaled, targetArray)
	
	for i in testArrayScaled:
		prediction=regressor.predict(i)
		predFile.write(str(prediction[0])+'\n')
		
	trainDataFile.close()
	testDataFile.close()
	targetFile.close()
	predFile.close()
	testTargetFile.close()


def generate_kNN_output_regression(testingPredictions, testingTargets, outfile):
	testPredFile=open(testingPredictions, "r")
	testTargFile=open(testingTargets, "r")
	output=open(outfile, "w")
	
	testPreds=testPredFile.readlines()
	testTargets=testTargFile.readlines()
	
	nPixels=1	
	totalZ=float(testPreds[0].rstrip())
	
	i=1
	
	while i<len(testPreds):
		while i<len(testPreds) and float(testTargets[i].rstrip())==float(testTargets[i-1].rstrip()):
			nPixels=nPixels+1
			totalZ=totalZ+float(testPreds[i].rstrip())
			i=i+1
			if i==len(testPreds):
				break
		output.write(testTargets[i-1].rstrip()+"\t"+str(totalZ/nPixels)+"\n")
		if i==len(testPreds):
			break
		nPixels=1
		totalZ=float(testPreds[i].rstrip())
		i=i+1
	
	testPredFile.close()
	testTargFile.close()
	output.close()
	
# *****

def prepare_for_training_kNN_classification(catagories, dataDir, outfiles):
	for catagory in catagories:
		if catagory not in ["GALAXY", "STAR", "QSO", "BACKGROUND"]:
			print "Arguments list catagories must contain some of GALAXY, STAR, QSO and BACKGROUND."
			return -1

	outputFileData=open(outfiles[0], "w")
	outputFileTarget=open(outfiles[1], "w")
	
	objno=1

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
						outputFileData.write(" ")
					outputFileData.write(entryFields[10]+'\n')
					outputFileTarget.write(str(objno)+" ")
					outputFileTarget.write(entryFields[7]+'\n')
			
			objfile.close()
			objno=objno+1
		
		listfile.close()
					 	
	outputFileData.close()
	outputFileTarget.close()

	
def train_test_kNN_classification(trainData, trainTargets, testData, testTargets, testPredictions, nNeighbors=5):
	trainDataFile=open(trainData, "r")
	targetFile=open(trainTargets, "r")
	testDataFile=open(testData, "r")
	predFile=open(testPredictions, "w")
	testTargetFile=open(testTargets, "r")
	
	trainDataLines=trainDataFile.readlines()
	targetFileLines=targetFile.readlines()
	testDataLines=testDataFile.readlines()
	testTargetLines=testTargetFile.readlines()
	
	testTargetFile.close()
	testTargetFile=open(testTargets, "w")
	
	trainData=[]
	testData=[]
	targets=[]
	distances=[]

	for i in range(len(trainDataLines)):
		isEntryValid=1
		vec=trainDataLines[i].split()
		for j in range(len(vec)-1):
			if math.isnan(float(vec[j])):
				isEntryValid=0
				break
			vec[j]=float(vec[j].rstrip())
		if isEntryValid==1:
			trainData.append(vec[:len(vec)-1])
			targets.append(float(targetFileLines[i].split()[1].rstrip()))
	

	for i in range(len(testDataLines)):
		isEntryValid=1
		vec=testDataLines[i].split()
		for j in range(len(vec)-1):
			if math.isnan(float(vec[j])):
				isEntryValid=0
				break
			vec[j]=float(vec[j])
		if isEntryValid==1:
			testData.append(vec[:len(vec)-1])
			testTargetFile.write(testTargetLines[i])
			distances.append(vec[len(vec)-1])
		
	trainArray=np.asarray(trainData)
	testArray=np.asarray(testData)
	targetArray=np.asarray(targets)
	
	trainArrayScaled=prep.scale(trainArray)
	testArrayScaled=prep.scale(testArray)
	
	classifier=kNNC(n_neighbors=nNeighbors)
	classifier.fit(trainArrayScaled, targetArray)
	
	for i in range(len(testArrayScaled)):
		prediction=classifier.predict(testArrayScaled[i])
		predFile.write(str(prediction[0])+' ')
		predFile.write(str(distances[i])+'\n')
		
	trainDataFile.close()
	testDataFile.close()
	targetFile.close()
	predFile.close()
	testTargetFile.close()


def generate_kNN_output_classification(testingPredictions, testingTargets, outfile, round_off=0):
	testPredFile=open(testingPredictions, "r")
	testTargFile=open(testingTargets, "r")
	output=open(outfile, "w")
	
	testPreds=testPredFile.readlines()
	testTargets=testTargFile.readlines()
	
	nPixels=1	
	totalZ=float(testPreds[0].rstrip().split()[0])
	
	i=1
	
	while i<len(testPreds):
		while i<len(testPreds) and float(testTargets[i].split()[0].rstrip())==float(testTargets[i-1].split()[0].rstrip()):
			nPixels=nPixels+1
			totalZ=totalZ+float(testPreds[i].rstrip().split()[0])
			i=i+1
			if i==len(testPreds):
				break
		if round_off==0:
			output.write(testTargets[i-1].split()[1].rstrip()+"\t"+str(totalZ/nPixels)+"\n")
		else:
			output.write(testTargets[i-1].split()[1].rstrip()+"\t"+str(round(totalZ/nPixels))+"\n")
		if i==len(testPreds):
			break
		nPixels=1
		totalZ=float(testPreds[i].rstrip().split()[0])
		i=i+1
	
	testPredFile.close()
	testTargFile.close()
	output.close()
