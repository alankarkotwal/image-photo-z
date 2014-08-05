#!/usr/bin/python

# Alankar Kotwal

import numpy as np
from scipy.interpolate import interp2d
from astropy.io import fits
import montage_wrapper as mw
from montage_wrapper import commands as cmds
import os
import math


# Calculate the registration using Montage reproject.
def register_reproject_direc(direc, ref='r'):
	os.system("rm -rf "+direc+"/"+ref+"_header.hdr "+direc+"/*_area* "+direc+"/*_reg*")
	cmds.mGetHdr(direc+"/"+ref+".fits",direc+"/header_"+ref+".hdr")
	list_in=[direc+'/g.fits',direc+'/r.fits',direc+'/i.fits',direc+'/u.fits',direc+'/z.fits']
	list_out=[direc+'/g_reg.fits',direc+'/r_reg.fits',direc+'/i_reg.fits',direc+'/u_reg.fits',direc+'/z_reg.fits']
	mw.reproject(list_in,list_out,header=direc+"/header_"+ref+".hdr",north_aligned=True,system='EQUJ',exact_size=True,common=True)
	
def register_reproject(inputImages, outputImages, refImage, processDir, headerName="header.hdr"):
	cmds.mGetHdr(refImage,headerName)
	mw.reproject(inputImages,outputImages,header=headerName,north_aligned=True,system='EQUJ',exact_size=True,common=True,silent_cleanup=True)


def return_sdss_gain(band, camcol, run):
	lut=[{},{'u':1.62,'g':3.32,'r':4.71,'i':5.165,'z':4.745},{'u':1.595,'g':3.855,'r':4.6,'i':6.565,'z':5.155},{'u':1.59,'g':3.845,'r':4.72,'i':4.86,'z':4.885},{'u':1.6,'g':3.995,'r':4.76,'i':4.885,'z':4.775},{'u':1.47,'g':4.05,'r':4.725,'i':4.64,'z':3.48},{'u':2.17,'g':4.035,'r':4.895,'i':4.76,'z':4.69}]
	if run>1100:
		lut[2]['u']=1.825
	return lut[camcol][band]


def return_sdss_darkVariance(band, camcol, run):
	lut=[{},{'u':9.61,'g':15.6025,'r':1.8225,'i':7.84,'z':0.81},{'u':12.6025,'g':1.44,'r':1.0,'i':5.76,'z':1.0},{'u':8.7025,'g':1.3225,'r':1.3225,'i':4.6225,'z':1.0},{'u':12.6025,'g':1.96,'r':1.3225,'i':6.25,'z':9.61},{'u':9.3025,'g':1.1025,'r':0.81,'i':7.84,'z':1.8225},{'u':7.0225,'g':1.8225,'r':0.9025,'i':5.0625,'z':1.21}]
	if run>1500:
		lut[2]['i']=6.25
		lut[4]['i']=7.5625
		lut[4]['z']=12.6025
		lut[5]['z']=2.1025
	return lut[camcol][band]


def return_sdss_pixelError(band, camcol, run, img, simg, cimg):
	dn=img/cimg+simg
	dn_err=math.sqrt(abs((dn/return_sdss_gain(band, camcol, run))+return_sdss_darkVariance(band, camcol, run)))
	img_err=dn_err*cimg
	return img_err

	
def register_reproject_with_errors(inputImages, outputImages, intErrorImages, outputErrorImages, refImage, processDir, headerName="header.hdr"):
	cmds.mGetHdr(refImage,headerName)
	mw.reproject(inputImages,outputImages,header=headerName,north_aligned=True,system='EQUJ',exact_size=True,common=True,silent_cleanup=True)
	for i in range(len(inputImages)):
		idenList=inputImages[i].split('/')[2].split('-')
		run=int(idenList[0])
		camcol=int(idenList[1])
		field=int(idenList[2])
		band=idenList[3].split('.')[0]
		fitsFile=fits.open(inputImages[i])
		fitsImage=fitsFile[0].data
		errorData=fitsFile[1].data
		errorImg=[]
		for j in range(1489):
			errorImg.append(errorData)
		errorImage=np.asarray(errorImg)
		skyImageInit=fitsFile[2].data[0][0]
		xs=np.fromfunction(lambda k: k, (skyImageInit.shape[0],), dtype=int)
		ys=np.fromfunction(lambda k: k, (skyImageInit.shape[1],), dtype=int)
		interpolator=interp2d(xs, ys, skyImageInit, kind='cubic')
		for j in range(errorImage.shape[1]):
			for k in range(errorImage.shape[0]):
				skyImageValue=interpolator.__call__(j*skyImageInit.shape[0]/errorImage.shape[0],k*skyImageInit.shape[1]/errorImage.shape[1])
				errorImage[k][j]=return_sdss_pixelError(band, camcol, run, fitsImage[k][j], skyImageValue, errorImg[k][j])
		fitsFile[0].data=errorImage
		fitsFile.writeto(intErrorImages[i])
	mw.reproject(intErrorImages,outputErrorImages,header=headerName,north_aligned=True,system='EQUJ',exact_size=True,common=True,silent_cleanup=True)


'''# Register using WCS only
def register_wcs(image, ref, out):
	image_header=image+".hdr"
	ref_header=ref+".hdr"
	cmds.mGetHdr(image, image_header)
	cmds.mGetHdr(ref, ref_header)

	ref_fits=fits.open(ref)
	image_fits=fits.open(image)
	reg_fits=fits.open(image)
	ref_data=ref_fits[0].data
	image_data=image_fits[0].data
	reg_data=reg_fits[0].data
	
	xref,yref=ref_data.shape
	ximg,yimg=image_data.shape

	kxx=float(xref)/(float(cmds.mPix2Coord(ref_header, xref, 0).native_lon)-float(cmds.mPix2Coord(ref_header, 0, 0).native_lon))
	kxy=float(xref)/(float(cmds.mPix2Coord(ref_header, xref, 0).lat)-float(cmds.mPix2Coord(ref_header, 0, 0).lat))
	kyx=float(yref)/(float(cmds.mPix2Coord(ref_header, 0, yref).native_lon)-float(cmds.mPix2Coord(ref_header, 0, 0).native_lon))
	kyy=float(yref)/(float(cmds.mPix2Coord(ref_header, 0, yref).lat)-float(cmds.mPix2Coord(ref_header, 0, 0).lat))
	
	dlat=float(cmds.mPix2Coord(image_header, 0, 0).lat)-float(cmds.mPix2Coord(ref_header, 0, 0).lat)
	dlon=float(cmds.mPix2Coord(image_header, 0, 0).native_lon)-float(cmds.mPix2Coord(ref_header, 0, 0).native_lon)

	dy=(kxx*dlon+kxy*dlat)
	dx=(kyx*dlon+kyy*dlat)
	
	print dx
	print dy
	
	for i in range(ximg):
		for j in range(yimg):
			if i-dx>=0 and j-dy>=0 and i-dx<ximg and j-dy<yimg:
				reg_data[i][j]=image_data[i-dx][j-dy]
			else:
				reg_data[i][j]=None

	fits.writeto(out, reg_data, header=ref_fits[0].header)'''


# Check the registration using differences
def reg_check_diff(check, ref, out):
	ref_fits=fits.open(ref)
	check_fits=fits.open(check)
	diff_fits=fits.open(check)
	ref_image=ref_fits[0].data
	check_image=check_fits[0].data
	diff_image=diff_fits[0].data
	x_shape=min(ref_image.shape[0], check_image.shape[0])
	y_shape=min(ref_image.shape[1], check_image.shape[1])
	for i in range(x_shape):
		for j in range(y_shape):
			diff_image[i][j]=check_image[i][j]-ref_image[i][j]
	diff_fits[0].data=diff_image
	fits.writeto(out, diff_image, ref_fits[0].header)


'''# Run SExtractor and output the source catalog
def reg_check_sex(check, ref, out):
	pass


# Another way of checking if the image_registration package is installed and the images have the same shape
def reg_check_alt(check, ref, out):
	pass'''
