#!/usr/bin/python

from sqlcl import *
import getpass

def query_area(outputCatalog, minRA, maxRA, minDec, maxDec):
	catalogFile=open(outputCatalog, "w")
	queryTemp="""SELECT ALL
			  spec.specObjID AS id,
			  spec.ra,
			  spec.dec,
			  spec.z AS redshift,
			  spec.zErr as redshiftError,
			  specAll.specClass as class,
			  specAll.run,
			  specAll.camcol,
			  specAll.field
			FROM SpecObj AS spec
			JOIN SpecPhotoAll AS specAll
			ON spec.specObjID = specAll.specObjID,
			  PhotoObj AS phot
			WHERE
			  specAll.ObjID = phot.ObjID
			  AND phot.CLEAN = 1
			  AND spec.zWarning = 0		"""
	queryText=queryTemp+"AND spec.ra>"+str(minRA)+" AND spec.ra<"+str(maxRA)+" AND spec.dec>"+str(minDec)+" AND spec.dec<"+str(maxDec)
	queryResult=query(queryText).read()
	catalogFile.write(queryResult)
	catalogFile.close()
	
def finalize_catalog(inputCatalog, outputCatalog):
	inCat=open(inputCatalog, "r")
	outCat=open(outputCatalog, "w")
	
	inCatLines=inCat.readlines()
	
	lut=['UNKNOWN', 'STAR', 'GALAXY', 'QSO', 'QSO', 'BACKGROUND', 'STAR', 'GALAXY']
	
	for i in inCatLines:
		try:
			objClass=int(i.split(',')[5])
			for j in range(5):
				outCat.write(i.split(',')[j])
				outCat.write(',')
			outCat.write(lut[objClass])
			outCat.write(',')
			for j in range(5, 8):
				outCat.write(i.split(',')[j])
				if j != 7:
					outCat.write(',')
			outCat.write('\n')
		except ValueError:
			outCat.write(i)
		
	inCat.close()
	outCat.close()
	

if __name__=="__main__":
	query_area("one_square_degree_raw.csv", 180, 181, 45, 46)
	finalize_catalog("one_square_degree_raw.csv", "one_square_degree.csv")
