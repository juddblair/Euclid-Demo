"""
bulkimporthelper.py

Custom module for appengine bulk uploader - imported in YAML config
Used for upload/download transform of CSV files

Additional functions MUST have a single argument

Created by Judd Blair on 2011-05-30.
Copyright (c) 2011 All rights reserved.
"""

import sys
import os
import datetime

def date_helper(inputDate):
	if inputDate != None and inputDate != '0':
		return datetime.datetime.fromtimestamp(float(inputDate))
	else:
		return None

def string_helper(inputString):
	if(inputString):
		return inputString.replace('\"','').strip()
	else:
		return None

def bool_helper(inputBool):
	if(inputBool):
		return bool(int(inputBool))
	else:
		return None
