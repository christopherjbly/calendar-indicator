#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$30/10/2010'
#
# Touchpad-Indicator
# An indicator to show the status of the touchpad
#
# Adding keybiding
#
# Copyright (C) 2010 Lorenzo Carbonell
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
import gdata.calendar.client
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

class GCal(object):
	def __init__(self,email,password):
		self.email = email
		self.password = password
		self._create()
	
	def _create(self):
		self.client = gdata.calendar.client.CalendarClient(source='calendar-indicator')
		self.client.ClientLogin(self.email,self.password, self.client.source)

	def PrintUserCalendars(self):
		feed = self.client.GetAllCalendarsFeed()
		print feed.title.text
		for i, a_calendar in enumerate(feed.entry):
			print '\t%s. %s' % (i, a_calendar.title.text,)

	def PrintOwnCalendars(self):
		feed = self.client.GetOwnCalendarsFeed()
		print feed.title.text
		for i, a_calendar in enumerate(feed.entry):
			print '\t%s. %s' % (i, a_calendar.title.text,)   

	def PrintAllEventsOnDefaultCalendar(self):
		feed = self.client.GetCalendarEventFeed()
		print 'Events on Primary Calendar: %s' % (feed.title.text,)
		for i, an_event in enumerate(feed.entry):
			print '\t%s. %s' % (i, an_event.title.text,)
			for p, a_participant in enumerate(an_event.who):
				print '\t\t%s. %s' % (p, a_participant.email,)
	
	def getAllEventsOnDefaultCalendar(self):
		feed = self.client.GetCalendarEventFeed()
		return feed.entry
	'''
	start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
    end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z',
                             time.gmtime(time.time() + 3600))		
	'''
	def _DateRangeQuery(self, start_date='2007-01-01', end_date='2007-07-01'):
		"""Retrieves events from the server which occur during the specified date
		range.  This uses the CalendarEventQuery class to generate the URL which is
		used to retrieve the feed.  For more information on valid query parameters,
		see: http://code.google.com/apis/calendar/reference.html#Parameters"""

		print 'Date range query for events on Primary Calendar: %s to %s' % (
			start_date, end_date,)
		query = gdata.calendar.client.CalendarEventQuery(start_min=start_date, start_max=end_date)
		feed = self.cal_client.GetCalendarEventFeed(q=query)
		for i, an_event in zip(xrange(len(feed.entry)), feed.entry):
		  print '\t%s. %s' % (i, an_event.title.text,)
		  for a_when in an_event.when:
			print '\t\tStart time: %s' % (a_when.start,)
			print '\t\tEnd time:   %s' % (a_when.end,)

	def getFirstTenEventsOnDefaultCalendar(self):
		start_date = datetime.date.today()
		end_date = addOneYear(start_date)
		print start_date
		print end_date
		query = gdata.calendar.client.CalendarEventQuery(\
													start_min = str(start_date), \
													start_max = str(end_date), \
													orderby = 'starttime', \
													singleevents = 'true', \
													futureevents = 'false', \
													sortorder = 'ascending', \
													max_results = '10')
		try:
			feed = self.client.GetCalendarEventFeed(q = query)
		except gdata.client.RedirectError:
			self._create()
			return self.getFirstTenEventsOnDefaultCalendar()		
		return feed.entry

	def getAllEventsOnMonthOnDefaultCalendar(self,month,year):
		start_date = datetime.date(year,month,1)
		if month<12:
			end_date = datetime.date(year,month+1,1)
		else:
			end_date = datetime.date(year+1,1,1)
		query = gdata.calendar.client.CalendarEventQuery(\
													start_min = str(start_date), \
													start_max = str(end_date), \
													orderby = 'starttime', \
													singleevents = 'true', \
													futureevents = 'false', \
													sortorder = 'ascending', \
													max_results = '10000')
		try:
			feed = self.client.GetCalendarEventFeed(q = query)
		except gdata.client.RedirectError:
			self._create()
			return self.getAllEventsOnMonthOnDefaultCalendar(month,year)
		return feed.entry
		
	def eventsOnDay(self,day,month,year):
		start_date = datetime.date(year,month,day)
		end_date = start_date + datetime.timedelta(days=1)
		query = gdata.calendar.client.CalendarEventQuery(\
													start_min = str(start_date), \
													start_max = str(end_date), \
													orderby = 'starttime', \
													singleevents = 'true', \
													futureevents = 'false', \
													sortorder = 'ascending', \
													max_results = '10000')
		try:
			feed = self.client.GetCalendarEventFeed(q = query)
		except gdata.client.RedirectError:
			self._create()
			return self.eventsOnDay(day,month,year)
		return feed.entry
	def DateRangeQuery(self, start_date='2011-01-01', end_date='2011-02-01'):
		print 'Date range query for events on Primary Calendar: %s to %s' % (start_date, end_date,)
		query = gdata.calendar.client.CalendarEventQuery()
		query.start_min = start_date
		query.start_max = end_date
		feed = self.client.GetCalendarEventFeed(q=query)
		for i, an_event in enumerate(feed.entry):
			print '\t%s. %s' % (i, an_event.title.text,)
			for a_when in an_event.when:
				print '\t\tStart time: %s' % (a_when.start,)
				print '\t\tEnd time:   %s' % (a_when.end,)

if __name__ == '__main__':
	gcal = GCal('lorenzo.carbonell.cerezo@gmail.com', '9m3no5NU6ve0')
	# gcal.PrintUserCalendars()
	# gcal.PrintOwnCalendars()
	# gcal.PrintAllEventsOnDefaultCalendar()
	print gcal.eventsOnDay(29,4,2011)[0].title.text
	for event in gcal.getFirstTenEventsOnDefaultCalendar():
		print event.title.text
		for a_when in event.when:
			print '\t\tStart time: %s' % (a_when.start,)
	
	#gcal.DateRangeQuery()
	exit(0)
