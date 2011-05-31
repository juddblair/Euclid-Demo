import datetime

from google.appengine.ext import db

class DataSample(db.Model):
	"""Models one hour of hit data in hit sensor CSV logs."""
	# user, site, and sensor that recorded the data
	user = db.StringProperty()
	site = db.StringProperty()
	sensor = db.StringProperty()
	
	# hit sensor throughput:
	# number of hits and timestamp of last hit
	numHits = db.IntegerProperty()
	lastHit = db.DateTimeProperty()
	
	# amazon s3 information:
	# filename, write status, and time of write
	s3Filename = db.StringProperty()
	s3Timestamp = db.DateTimeProperty()
	s3FileStatus = db.BooleanProperty()
	
	# timestamp of record
	timeStamp = db.DateTimeProperty()