#!/usr/bin/python

from casjobs import CASJobsClient
import getpass

def query_dr10():
	uid=raw_input("Enter CasJobs User ID: ")
	passwd=getpass.getpass()
	client = CASJobsClient(uid, passwd)
