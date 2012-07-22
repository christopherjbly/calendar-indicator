#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# googletasksapi.py
#
# Copyright (C) 2011 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#

'''
Dependencies:
python-gflags


'''
import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import datetime
import rfc3339
import comun 
FLAGS = gflags.FLAGS
import datetime

def is_Bisiesto(year):
	if year % 400 == 0:
		bisiesto = True
	elif year % 100 == 0:
		bisiesto = False
	elif year % 4 == 0:
		bisiesto = True
	else:
		bisiesto = False
	return bisiesto

def addOneYear(start_date):
	if start_date.month == 2 and start_date.day == 29 and is_Bisiesto(start_date.year):
		end_date = datetime.date(start_date.year+1,start_date.month+1,1)
	else:
		end_date = datetime.date(start_date.year+1,start_date.month,start_date.day)
	return end_date

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications
# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console

FLOW = OAuth2WebServerFlow(
    client_id='906536899599.apps.googleusercontent.com',
    client_secret='DXPZvzgclAR1z1lU9Sh7Qi54',
    scope='https://www.googleapis.com/auth/calendar',
    user_agent='Google-Calendar-Indicator/0.0.1.0')

class GCAService():
	def __init__(self):
		# To disable the local server feature, uncomment the following line:
		# FLAGS.auth_local_webserver = False

		# If the Credentials don't exist or are invalid, run through the native client
		# flow. The Storage object will ensure that if successful the good
		# Credentials will get written back to a file.
		storage = Storage(comun.COOKIE_FILE)
		credentials = storage.get()
		if credentials is None or credentials.invalid == True:
			credentials = run(FLOW, storage)

		# Create an httplib2.Http object to handle our HTTP requests and authorize it
		# with our good Credentials.
		http = httplib2.Http()
		http = credentials.authorize(http)

		# Build a service object for interacting with the API. Visit
		# the Google APIs Console
		# to get a developerKey for your own application.
		self.service = build(serviceName='calendar', version='v3', http=http,developerKey='AIzaSyAEdFnbOJghHQYy1RYvve-6OccSc7UcyHU')

	def get_settings(self):
		settings = self.service.settings().list().execute()
		return settings['items']

	def get_acl(self,calendar_id):
		acls = self.service.acl().list(calendarId=calendar_id).execute()
		return acls['items']

	def get_calendars(self):
		calendars = self.service.calendarList().list().execute()
		return calendars['items']
		
	def get_calendar(self,calendar_id):
		calendar = self.service.calendars().get(calendarId=calendar_id).execute()
		return calendar
	
	def get_events(self,calendar_id):
		events = self.service.events().list(calendarId=calendar_id,
											singleEvents=True,
											orderBy='startTime').execute()
		return events['items']
	def getAllEventsOnMonthOnDefaultCalendar(self,calendar_id,month,year):
		com = datetime.datetime(year, month, 1)
		start_date = rfc3339.rfc3339(com)
		events = self.service.events().list(calendarId=calendar_id,
											timeMin=start_date,
											singleEvents=True,
											orderBy='startTime').execute()
		return events['items']
	def get_next_ten_events(self,calendar_id):
		start_date = rfc3339.rfc3339(datetime.datetime.now())
		events = self.service.events().list(calendarId=calendar_id,
											maxResults=10,
											timeMin=start_date,
											singleEvents=True,
											orderBy='startTime').execute()
		return events['items']
if __name__ == '__main__':	
	gca = GCAService()
	print gca.get_settings()
	for calendar in gca.get_calendars():
		print '########################################################'
		print calendar['id']
		print gca.get_events(calendar['id']) 
	
	
	'''
	for tasklist in gta.get_tasklists():
		print tasklist

	#print gta.create_tasklist('desde ubuntu')
	#print gta.get_tasklist('MDU4MDg5OTIxODI5ODgyMTE0MTg6MDow')
	print gta.get_tasks()
	for task in gta.get_tasks():
		print '%s -> %s'%(task['title'],task['id'])
	#print gta.create_task(title = 'prueba2 desde ubuntu',notes = 'primera prueba')
	gta.move_task_first('MDU4MDg5OTIxODI5ODgyMTE0MTg6MDoy')
	'''
