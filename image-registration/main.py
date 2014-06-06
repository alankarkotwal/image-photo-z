#!/usr/bin/python

from registration import *

ref='g'

for band in ['u','r','i','z']:
	register_wcs(band+".fits", ref+".fits", band+"_reg.fits")
	reg_check_diff(band+"_reg.fits", ref+".fits", band+"_diff.fits")

'''register_reproject("r.fits","g.fits","r_reg.fits")
reg_check_diff("r_reg.fits","g.fits","diff.fits")'''
