#!/usr/bin/python

# Alankar Kotwal

import numpy as np
from astropy.io import fits
import montage_wrapper as mw
from montage_wrapper import commands as cmds
import glob
import os
#from image_registration import chi2_shifts as c2s
#import pysex as ps


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
