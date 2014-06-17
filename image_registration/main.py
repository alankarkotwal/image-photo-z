#!/usr/bin/python

from image_registration import *
import glob

direc="tests"
reg_images=glob.glob(direc+"/*.fits")

ref='g0'

register_reproject(direc)

#for image in reg_images:
#	reg_check_diff(image, direc+"/"+ref+".fits", image+"_diff")
