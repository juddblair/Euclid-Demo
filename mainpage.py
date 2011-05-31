import os
import cgi
import datetime
import urllib
import wsgiref.handlers
import csv
import models
import logging

from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from datetime import datetime
from models import DataSample
	
def render_samples(query_params,minDate,maxDate,numRecords):
	"""
	Queries for error data based on the input params
	Returns a tuple of 2 lists of DataSamples in error state - (sensorerrors,s3errors)

	query_params = list of string tuples (param,value) to be queried for (eg ('user','stark'))
	minDate = start of date range for results
	maxDate = end of date range for results
	numRecords = number of records to query for
	"""	
	
	sensorQuery = DataSample.all()
	sensorQuery.filter('numHits =',0)
	s3Query = DataSample.all()
	s3Query.filter('s3FileStatus =',False)
	
	if(query_params):
		for param in query_params:
			#add the param:value tuple to the query if the value is not null
			if(param[1]):
				sensorQuery.filter(param[0]+' =',param[1])
				s3Query.filter(param[0]+' =',param[1])
			
	if(maxDate):
		maxdt = datetime.strptime(maxDate,'%Y-%m-%d %H:%M:%S')
		sensorQuery.filter('timeStamp <=',maxdt)
		s3Query.filter('timeStamp <=',maxdt)
	
	if(minDate):
		mindt = datetime.strptime(minDate,'%Y-%m-%d %H:%M:%S')
		sensorQuery.filter('timeStamp >=',mindt)
		s3Query.filter('timeStamp >=',mindt)
		
	if numRecords is None:
		numRecords = 500

	#get errors, grouped by timestamp desc
	sensorQuery.order('-timeStamp')
	s3Query.order('-timeStamp')
	
	sensorErrors = sensorQuery.fetch(numRecords)
	s3errors = s3Query.fetch(numRecords)
	
	return (sensorErrors,s3errors)
	
	

class MainPage(webapp.RequestHandler):
	"""
	Handler for the Main Page - invoked with a GET for /

	Processes a query for errors for the values specified in the URL
	If no params, default to most recent errors
	"""
	def get(self):
		
		#Get URL Params - default to None
		user = self.request.get('user',None)
		site = self.request.get('site',None)
		sensor = self.request.get('sensor',None)

		startDate = self.request.get('start',None)
		endDate = self.request.get('end',None)
		
		#variables to be passed to django template
		pageTitle = None
		graphName = None
		graphData = []
		s3errors = []
		sensorErrors = []
		message = None
		
		
		if user is None and site is None and sensor is None:
			#Heads up page - recent errors
			pageTitle = 'Recent System Errors'
			
			resultsTuple = render_samples(None,None,None,750)
			
			sensorErrors = resultsTuple[0]
			s3errors = resultsTuple[1]
			
			if sensorErrors is None and s3errors is None:
				message = 'No recent errors. Rock on!'
		
		else:
			#Run a search for the specified params
			
			#Dump params into pageTitle - used to log/display query
			pageTitle = 'User: '+user+', Site: '+site+', Sensor: '+sensor
			logging.debug('Query for:'+pageTitle)
			
			queryParams=[]
			queryParams.append(('user',user))
			queryParams.append(('site',site))
			queryParams.append(('sensor',sensor))
			
			try:
				resultsTuple = render_samples(queryParams,startDate,endDate,750)
			
				sensorErrors = resultsTuple[0]
				s3errors = resultsTuple[1]
				
				if len(sensorErrors) is 0 and len(s3errors) is 0:
					message = 'No recent errors. Rock on!'
			except:
				message = 'Malformed query: please try again.'
				logging.error('Error for query: '+pageTitle)
					
			#sensor health - get recent hits if sensor has been queried for
			if sensor:
				recentHits_query = DataSample.gql("WHERE sensor = :sensorName ORDER BY timeStamp asc", sensorName=sensor)
				recentHits = recentHits_query.fetch(750)
				
				for dataPoint in recentHits:
					graphData.append((dataPoint.timeStamp,dataPoint.numHits))
				
				graphName = "Recent activity of "+sensor
			
		#dump django template values into dictionary for rendering
		template_values = {
			'pageTitle': pageTitle, #param for displaying queries - remove if not needed
			'graphName': graphName,
			'graphData': graphData,
			's3errors': s3errors,
			'sensorErrors': sensorErrors,
			'message': message
		}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		

def main():
	application = webapp.WSGIApplication([('/', MainPage)],debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()