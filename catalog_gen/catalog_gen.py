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
	# The 'class' keyword needs to be added here after redshiftError, sqlcl complains if it is added. Pending task.
	queryText=queryTemp+"AND spec.ra>"+str(minRA)+" AND spec.ra<"+str(maxRA)+" AND spec.dec>"+str(minDec)+" AND spec.dec<"+str(maxDec)
	queryResult=query(queryText).read()
	catalogFile.write(queryResult)
	catalogFile.close()
	

if __name__=="__main__":
	query_area("one_square_degree.csv", 180, 181, 45, 46)
