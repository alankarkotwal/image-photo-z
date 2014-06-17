#!/usr/bin/python

import numpy
from astropy import wcs
from astropy.io import fits 
import os
from astropy.table import Table
import math

# A note on objClass: Since we store the data in BinTableHDU, we need an encoding scheme for objClass. Here, I have
# 1: Galaxy
# 2: Star
# 3: QSO
# 4: Background

def preprocess_catalog(catalog, output):
	catalogFile=open(catalog, "r")
	catalogLines=catalogFile.readlines()
	
	outputFile=open(output, "w")
	
	j=1
	
	for i in range(len(catalogLines)-1):
		outputFile.write(str(j))
		outputFile.write(",")
		outputFile.write(catalogLines[i+1])
		j=j+1
	
	catalogFile.close()
	outputFile.close()
		

def convert_catalog_to_exp_pixels(filename, catalog, expPixelsList):
	hdulist = fits.open(filename)

	w = wcs.WCS(hdulist[0].header)

	catalogFile=open(catalog, "r")
	catalogLines=catalogFile.readlines()
	
	expPixelsFile=open(expPixelsList, "w")
	
	j=1
	
	for i in catalogLines:
		px, py = w.wcs_world2pix(float(i.split(',')[2]), float(i.split(',')[3]), 1)
		expPixelsFile.write(str(j))
		expPixelsFile.write(" ")
		expPixelsFile.write(str(px))
		expPixelsFile.write(" ")
		expPixelsFile.write(str(py))
		expPixelsFile.write("\n")
		j=j+1
	
	catalogFile.close()
	expPixelsFile.close()


def sextract(bands, ref):
	for band in bands:
		os.system("sex -c "+band+".sex "+band+".fits")
	os.system("cp "+ref+".cat ref.cat")
	os.system("cp "+ref+"_seg.fits ref.fits")


def generate_training_galaxies(objectsFileName, segImageName, catalog, imageFileNames):
	os.mkdir("galaxies")
	
	objectsFile=open(objectsFileName, "r")
	objects=objectsFile.readlines()
	
	catalogFile=open(catalog, "r")
	catalog=catalogFile.readlines()
	
	for i in objects:
		if i[0] is '#' or None:
			pass
		else:
			if catalog[int(i.split()[0])].split(',')[6] == "GALAXY":
				redshift=float(catalog[int(i.split()[0])].split(',')[4])
				redshiftError=float(catalog[int(i.split()[0])].split(',')[5])
				objClass=1.0
				segImageList=fits.open(segImageName)
				segImage=segImageList[0].data
				thisObjFlag=int(segImage[int(i.split()[2])][int(i.split()[1])])
				fitsFiles=[]
				fitsImages=[]
				k=0
				for j in imageFileNames:
					fitsFiles.append(fits.open(j))
					fitsImages.append(fitsFiles[k][0].data)
					k=k+1
				trainingArray=[]
				for j in range(int(i.split()[3]), int(i.split()[4])+1):
					for k in range(int(i.split()[5]), int(i.split()[6])+1):
						if segImage[k][j]==thisObjFlag:
							trainingVector=[]
							for l in fitsImages:
								trainingVector.append(float(l[k][j]))
							trainingVector.append(redshift)
							trainingVector.append(redshiftError)
							trainingVector.append(objClass)
							trainingArray.append(trainingVector)
				
				specObjID=catalog[int(i.split()[0])].split(',')[1]		
				
				trainingData=numpy.array(trainingArray)
				numpy.savetxt("galaxies/"+specObjID+".csv", trainingData, delimiter=" ")
				
				#trainingDataTable=Table(trainingData)
				
				#trainingTable=fits.BinTableHDU(data=Table(trainingArray))
				#trainingTable.writeto(specObjID+".fits")
				
				segImageList.close()
				for j in fitsFiles:
					j.close()
	
	objectsFile.close()	
	catalogFile.close()


def generate_training_stars(objectsFileName, segImageName, catalog, imageFileNames):
	os.mkdir("stars")
	
	objectsFile=open(objectsFileName, "r")
	objects=objectsFile.readlines()
	
	catalogFile=open(catalog, "r")
	catalog=catalogFile.readlines()
	
	for i in objects:
		if i[0] is '#' or None:
			pass
		else:
			if catalog[int(i.split()[0])].split(',')[6] == "STAR":
				# redshift=float(catalog[int(i.split()[0])].split(',')[4])
				# redshiftError=float(catalog[int(i.split()[0])].split(',')[5])
				redshift=0
				redshiftError=0
				objClass=2.0
				segImageList=fits.open(segImageName)
				segImage=segImageList[0].data
				thisObjFlag=int(segImage[int(i.split()[2])][int(i.split()[1])])
				fitsFiles=[]
				fitsImages=[]
				k=0
				for j in imageFileNames:
					fitsFiles.append(fits.open(j))
					fitsImages.append(fitsFiles[k][0].data)
					k=k+1
				trainingArray=[]
				for j in range(int(i.split()[3]), int(i.split()[4])+1):
					for k in range(int(i.split()[5]), int(i.split()[6])+1):
						if segImage[k][j]==thisObjFlag:
							trainingVector=[]
							for l in fitsImages:
								trainingVector.append(float(l[k][j]))
							trainingVector.append(redshift)
							trainingVector.append(redshiftError)
							trainingVector.append(objClass)
							trainingArray.append(trainingVector)
				
				specObjID=catalog[int(i.split()[0])].split(',')[1]		
				
				trainingData=numpy.array(trainingArray)
				numpy.savetxt("stars/"+specObjID+".csv", trainingData, delimiter=" ")
				
				#trainingDataTable=Table(trainingData)
				
				#trainingTable=fits.BinTableHDU(data=Table(trainingArray))
				#trainingTable.writeto(specObjID+".fits")
				
				segImageList.close()
				for j in fitsFiles:
					j.close()
	
	objectsFile.close()	
	catalogFile.close()


def generate_training_qsos(objectsFileName, segImageName, catalog, imageFileNames):
	os.mkdir("qsos")
	
	objectsFile=open(objectsFileName, "r")
	objects=objectsFile.readlines()
	
	catalogFile=open(catalog, "r")
	catalog=catalogFile.readlines()
	
	for i in objects:
		if i[0] is '#' or None:
			pass
		else:
			if catalog[int(i.split()[0])].split(',')[6] == "QSO":
				redshift=float(catalog[int(i.split()[0])].split(',')[4])
				redshiftError=float(catalog[int(i.split()[0])].split(',')[5])
				objClass=3.0
				segImageList=fits.open(segImageName)
				segImage=segImageList[0].data
				thisObjFlag=int(segImage[int(i.split()[2])][int(i.split()[1])])
				fitsFiles=[]
				fitsImages=[]
				k=0
				for j in imageFileNames:
					fitsFiles.append(fits.open(j))
					fitsImages.append(fitsFiles[k][0].data)
					k=k+1
				trainingArray=[]
				for j in range(int(i.split()[3]), int(i.split()[4])+1):
					for k in range(int(i.split()[5]), int(i.split()[6])+1):
						if segImage[k][j]==thisObjFlag:
							trainingVector=[]
							for l in fitsImages:
								trainingVector.append(float(l[k][j]))
							trainingVector.append(redshift)
							trainingVector.append(redshiftError)
							trainingVector.append(objClass)
							trainingArray.append(trainingVector)
				
				specObjID=catalog[int(i.split()[0])].split(',')[1]		
				
				trainingData=numpy.array(trainingArray)
				numpy.savetxt("qsos/"+specObjID+".csv", trainingData, delimiter=" ")
				
				#trainingDataTable=Table(trainingData)
				
				#trainingTable=fits.BinTableHDU(data=Table(trainingArray))
				#trainingTable.writeto(specObjID+".fits")
				
				segImageList.close()
				for j in fitsFiles:
					j.close()
	
	objectsFile.close()	
	catalogFile.close()


def generate_training_background(segImageNames, imageFileNames):
	os.mkdir("background")
	
	redshift=-1.0
	redshiftError=0.0
	objClass=4.0
	
	fitsFiles=[]
	fitsImages=[]
	k=0
	for j in imageFileNames:
		fitsFiles.append(fits.open(j))
		fitsImages.append(fitsFiles[k][0].data)
		k=k+1
	
	for j in fitsFiles:
		j.close()
	
	fitsFiles=[]
	segImages=[]
	k=0
	for j in segImageNames:
		fitsFiles.append(fits.open(j))
		segImages.append(fitsFiles[k][0].data)
		k=k+1
	
	for j in fitsFiles:
		j.close()
	
	xshape,yshape=fitsImages[0].shape
	
	trainingArray=[]
	
	for i in range(xshape):
		for j in range(yshape):
			isObjectHere=0
			for k in segImages:
				if k[i][j]!=0:
					isObjectHere=1
			if isObjectHere==0:
				isPixelValid=1
				for k in fitsImages:
					if math.isnan(k[i][j]):
						isPixelValid=0
						print k[i][j]
				if isPixelValid==1:
					trainingVector=[]
					for k in fitsImages:
						trainingVector.append(float(k[i][j]))
					trainingVector.append(redshift)
					trainingVector.append(redshiftError)
					trainingVector.append(objClass)
					trainingArray.append(trainingVector)
				
	trainingData=numpy.array(trainingArray)
	numpy.savetxt("background/background.csv", trainingData, delimiter=" ")
				
	# trainingDataTable=Table(trainingData)
				
	#trainingTable=fits.BinTableHDU(data=Table(trainingArray))
	#trainingTable.writeto(specObjID+".fits")


# Example use follows
if __name__=="__main__":
	preprocess_catalog("one_square_degree.csv", "one_square_degree_processed.csv")
	convert_catalog_to_exp_pixels("r.fits", "one_square_degree_processed.csv", "sky.list")
	sextract(['u', 'g', 'r', 'i', 'z'], 'r')
	generate_training_galaxies("ref.cat", "ref.fits", "one_square_degree_processed.csv", ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"])
	generate_training_stars("ref.cat", "ref.fits", "one_square_degree_processed.csv", ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"])
	generate_training_qsos("ref.cat", "ref.fits", "one_square_degree_processed.csv", ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"])
	generate_training_background(["u_seg.fits", "g_seg.fits", "r_seg.fits", "i_seg.fits", "z_seg.fits"], ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"])
