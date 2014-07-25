#!/usr/bin/python

import numpy
from astropy import wcs
from astropy.io import fits 
import os
import math
import urllib
import time

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


def generate_download_list(catalog, output, bands=['u','g','r','i','z'], rerun="301"):
	catalogFile=open(catalog, "r")
	catalogLines=catalogFile.readlines()
	
	outputFile=open(output, "w")
	
	for i in catalogLines:
		run=i.split(',')[7]
		camcol=i.split(',')[8]
		field=i.split(',')[9].rstrip()
		outputFile.write("# "+run+"-"+camcol+"-"+field+"\n")
		for band in bands:
			outputFile.write("http://data.sdss3.org/sas/dr10/boss/photoObj/frames/"+rerun+"/"+run+"/"+camcol+"/frame-"+band+"-"+run.zfill(6)+"-"+camcol+"-"+field.zfill(4)+".fits.bz2\n")
			
	catalogFile.close()
	outputFile.close()


def make_logfile(catalog, logfile="logfile"):
	catalogFile=open(catalog, "r")
	catalogLines=catalogFile.readlines()
	logfileFile=open(logfile,"w")
	
	loglines=[]
	
	for i in catalogLines:
		run=i.split(',')[7]
		camcol=i.split(',')[8]
		field=i.split(',')[9].rstrip()
		filename=run+"-"+camcol+"-"+field
		if filename not in loglines:
			loglines.append(filename)
	
	for i in loglines:
		logfileFile.write(i+"\n")
		
	catalogFile.close()
	logfileFile.close()
		

	
def download_images(catalog, downloadFolder, logfile="logfile", bands=['u','g','r','i','z'], rerun="301"):
	catalogFile=open(catalog, "r")
	catalogLines=catalogFile.readlines()
	logfileFile=open(logfile,"w")
	
	for i in catalogLines:
		run=i.split(',')[7]
		camcol=i.split(',')[8]
		field=i.split(',')[9].rstrip()
		try:
			for band in bands:
				downloadURL="http://data.sdss3.org/sas/dr10/boss/photoObj/frames/"+rerun+"/"+run+"/"+camcol+"/frame-"+band+"-"+run.zfill(6)+"-"+camcol+"-"+field.zfill(4)+".fits.bz2"
				if not os.path.isfile(downloadFolder+"/"+run+"-"+camcol+"-"+field+"-"+band+".fits"):
					#print "Downloading", downloadURL
					if band==bands[0]:
						logfileFile.write(run+"-"+camcol+"-"+field+"\n")
					urllib.urlretrieve(downloadURL, downloadFolder+"/"+run+"-"+camcol+"-"+field+"-"+band+".fits.bz2")
					os.system("bunzip2 "+downloadFolder+"/"+run+"-"+camcol+"-"+field+"-"+band+".fits.bz2")
		except OSError:
			pass
	
	catalogFile.close()
	logfileFile.close()


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


def sextract(imageFileNames, configFileNames, processDir, refBand='r', bands=['u', 'g', 'r', 'i', 'z']):
	currDir=os.getcwd()
	os.chdir(processDir)
	for i in range(len(imageFileNames)):
		os.system("sex -c "+configFileNames[i]+" "+imageFileNames[i])
	os.system("cp "+refBand+".cat ref.cat")
	os.system("cp "+refBand+"_seg.fits ref.fits")
	os.chdir(currDir)


def generate_training_objects(objectsFileName, segImageName, catalog, imageFileNames, catagory, outdir):
	if catagory not in ["GALAXY", "STAR", "QSO"]:
		print "Argument catagory must be one of GALAXY, STAR and QSO."
		return -1
	else:
		try:
			os.mkdir(outdir)
			os.mkdir(outdir+"/"+catagory)
		except OSError:
			pass
	
		objectsFile=open(objectsFileName, "r")
		objects=objectsFile.readlines()
	
		catalogFile=open(catalog, "r")
		catalog=catalogFile.readlines()
		
		outlist=open(outdir+"/"+catagory+"/"+catagory+".list","a")
	
		for i in objects:
			if i[0] is '#' or None:
				pass
			else:
				if catalog[int(i.split()[0])-1].split(',')[6] == catagory:
					redshift=float(catalog[int(i.split()[0])-1].split(',')[4])
					redshiftError=float(catalog[int(i.split()[0])-1].split(',')[5])
					hdulist = fits.open(imageFileNames[0])
					#pixelRA=float(catalog[int(i.split()[0])-1].split(',')[2])
					#pixelDec=float(catalog[int(i.split()[0])-1].split(',')[3])
					w = wcs.WCS(hdulist[0].header)
					if catagory=="GALAXY":
						objClass=1.0
					elif catagory=="STAR":
						objClass=2.0
					elif catagory=="QSO":
						objClass=3.0
					segImageList=fits.open(segImageName)
					segImage=segImageList[0].data
					thisObjFlag=int(segImage[int(i.split()[2])][int(i.split()[1])])
					thisObjX=int(i.split()[2])
					thisObjY=int(i.split()[1])
					fitsFiles=[]
					fitsImages=[]
					k=0
					trainingArray=[[]]
					for j in imageFileNames:
						fitsFiles.append(fits.open(j))
						fitsImages.append(fitsFiles[k][0].data)
						if j==imageFileNames[0]:
							trainingArray[0].append("# "+j+"Flux")
						else:
							trainingArray[0].append(j+"Flux")
						k=k+1
					trainingArray[0].append("Redshift")
					trainingArray[0].append("RedshiftError")
					trainingArray[0].append("Class")
					trainingArray[0].append("PixelRA")
					trainingArray[0].append("PixelDec")
					trainingArray[0].append("DistanceFromCenter")
					maxDist=1
					for j in range(max(0,int(i.split()[3])), min(int(i.split()[4]),segImage.shape[0]-1)):
						for k in range(max(0,int(i.split()[5])), min(int(i.split()[6]),segImage.shape[1]-1)):
							isPixelValid=1
							for l in fitsImages:
								if math.isnan(float(l[k][j])):
									isPixelValid=0
							if isPixelValid==1:
								if segImage[k][j]==thisObjFlag:
									maxDist=max(maxDist, math.sqrt(pow((k-thisObjX),2)+pow((j-thisObjY),2)))
					
					for j in range(max(0,int(i.split()[3])), min(int(i.split()[4]),segImage.shape[0]-1)):
						for k in range(max(0,int(i.split()[5])), min(int(i.split()[6]),segImage.shape[1]-1)):
							isPixelValid=1
							for l in fitsImages:
								if math.isnan(float(l[k][j])):
									isPixelValid=0
							if isPixelValid==1:
								if segImage[k][j]==thisObjFlag:
									trainingVector=[]
									for l in fitsImages:
										trainingVector.append(float(l[k][j]))
									trainingVector.append(redshift)
									trainingVector.append(redshiftError)
									trainingVector.append(objClass)
									pixelRA, pixelDec = w.wcs_pix2world(float(j), float(k), 1)
									trainingVector.append(pixelRA)
									trainingVector.append(pixelDec)
									distance=math.sqrt(pow((k-thisObjX),2)+pow((j-thisObjY),2))/maxDist
									trainingVector.append(distance)
									trainingArray.append(trainingVector)
								
				
					specObjID=catalog[int(i.split()[0])-1].split(',')[1]
					
					objFileName=specObjID+"-"+str(time.time())+".csv"
					outlist.write(objFileName+"\n")					
					outfile=open(outdir+"/"+catagory+"/"+objFileName,"w")
				
					for entry in trainingArray:
						for column in entry:
							outfile.write(str(column)+" ")
						outfile.write("\n")
					
					outfile.close()
				
					segImageList.close()
					for j in fitsFiles:
						j.close()
	
		objectsFile.close()	
		catalogFile.close()
		outlist.close()


def generate_training_background(segImageNames, imageFileNames, outdir, nMaxDataPoints=1000):
	
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
	
	trainingArray=[[]]
	for j in imageFileNames:
		if j==imageFileNames[0]:
			trainingArray[0].append("# "+j+"Flux")
		else:
			trainingArray[0].append(j+"Flux")

	trainingArray[0].append("Redshift")
	trainingArray[0].append("RedshiftError")
	trainingArray[0].append("Class")
	trainingArray[0].append("PixelRA")
	trainingArray[0].append("PixelDec")
	
	nPixels=0
	
	outlist=open(outdir+"/BACKGROUND/BACKGROUND.list","a")
	
	for i in range(xshape):
		for j in range(yshape):
			if nPixels<nMaxDataPoints:
				isObjectHere=0
				for k in segImages:
					if k[i][j]!=0:
						isObjectHere=1
				if isObjectHere==0:
					isPixelValid=1
					for l in fitsImages:
						if math.isnan(float(l[i][j])):
							isPixelValid=0
					if isPixelValid==1:
						trainingVector=[]
						for m in fitsImages:
							trainingVector.append(float(m[i][j]))
						trainingVector.append(redshift)
						trainingVector.append(redshiftError)	
						trainingVector.append(objClass)
						trainingArray.append(trainingVector)
						nPixels=nPixels+1
			else:
				break
				
	trainingData=numpy.array(trainingArray)
	filename=imageFileNames[0].split('/')[len(imageFileNames[0].split('/'))-1]
	
	outfile=open(outdir+"/BACKGROUND/"+filename+".csv","w")
	outlist.write(filename+".csv\n")
	
	for entry in trainingArray:
		for column in entry:
			outfile.write(str(column)+" ")
		outfile.write("\n")
	
	outfile.close()


# Example use follows
if __name__=="__main__":
	preprocess_catalog("one_square_degree.csv", "one_square_degree_processed.csv")
	try:
		os.mkdir("download")
	except OSError:
		pass
	generate_download_list("one_square_degree_processed.csv", "download.list")
	download_images("one_square_degree_processed.csv", "images")
'''	convert_catalog_to_exp_pixels("r.fits", "one_square_degree_processed.csv", "sky.list")
	sextract(['u', 'g', 'r', 'i', 'z'], 'r')
	for catagory in ["GALAXY", "STAR", "QSO"]:
		generate_training_objects("ref.cat", "ref.fits", "one_square_degree_processed.csv", ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"], catagory, "data")
	#generate_training_background(["u_seg.fits", "g_seg.fits", "r_seg.fits", "i_seg.fits", "z_seg.fits"], ["u.fits", "g.fits", "r.fits", "i.fits", "z.fits"])'''

