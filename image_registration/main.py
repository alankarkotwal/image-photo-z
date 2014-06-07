#!/usr/bin/python

from image_registration import *
import glob

direc="tests"
reg_images=glob.glob(direc+"/*_reg.fits")

ref='g'

register_reproject(direc)

for image in reg_images:
	reg_check_diff(image, direc+"/"+ref+".fits_reg.fits", image+"_diff")
