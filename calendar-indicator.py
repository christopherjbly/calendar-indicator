#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$25/04/2011'
#
# Remember-me
# An indicator for Google Calendar
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
import gobject
import gtk
import appindicator
import pynotify
import locale
import gettext
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import glib
import datetime
import pynotify
#
import comun
from gcal import GCal
from preferences import Preferences
from configurator import GConf
from encoderapi import Encoder
from calendardialog import CalendarDialog
#
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

def getTimeAndDate(cadena):
	if cadena.find('T')==-1:
		date = cadena.split('-')
		time = datetime.time(0,0,0)
	else:
		date = cadena.split('T')[0].split('-')
		time = cadena.split('T')[1].split(':')
		time = datetime.time(int(time[0]),int(time[1]),int(time[2][0:2]))
	date = datetime.date(int(date[0]),int(date[1]),int(date[2]))
	return date.strftime('%d/%m/%Y')+' - '+time.strftime('%H:%M')
	
def check_events(event1,event2):
	if event1.when[0].start == event2.when[0].start:
		if event1.when[0].end == event2.when[0].end:
			if event1.title.text == event2.title.text:
				return True
	return False

def is_event_in_events(an_event,events):
	for event in events:
		if check_events(an_event,event):
			return True
	return False



class RememberIndicator(dbus.service.Object):
	def __init__(self):
		if dbus.SessionBus().request_name("es.atareao.RememberIndicator") != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
			print "application already running"
			exit(0)
		self.indicator = appindicator.Indicator ('Remember-me-Indicator', 'indicator-messages', appindicator.CATEGORY_APPLICATION_STATUS)
		#
		self.indicator.set_icon(comun.ICON_ENABLED)
		self.indicator.set_attention_icon(comun.ICON_DISABLED)
		#
		self.read_preferences()
		#
		self.events = []
		self.set_menu()
		#
		bus_name = dbus.service.BusName('es.atareao.remember_me_indicator_service', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/es/atareao/remember_me_indicator_service')
		#
		glib.timeout_add_seconds(int(self.time*60), self.work)

	def read_preferences(self):
		self.user = self.load_key('user','')
		self.password = self.load_key('password','')
		self.time = self.load_key('time',5)
		encoder = Encoder()
		if self.user == None or self.password == None or len(encoder.decode(self.user)) == 0 or len(encoder.decode(self.password)) == 0:
			p = Preferences()
			print p.ok
			if p.ok == False:
				exit(1)
			self.user = self.load_key('user','')
			self.password = self.load_key('password','')
			self.time = self.load_key('time',5)
		error = True
		while error:
			try:
				self.gcal=GCal(encoder.decode(self.user),encoder.decode(self.password))
				error = False
			except Exception,e:
				print e
				error = True
				md = gtk.MessageDialog(	parent = None,
										flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
										type = gtk.MESSAGE_ERROR,
										buttons = gtk.BUTTONS_OK_CANCEL,
										message_format = _('The email or/and the password are incorrect\nplease, try again?'))
				if md.run() == gtk.RESPONSE_CANCEL:
					exit(3)
				md.destroy()
				p = Preferences()
				self.user = self.load_key('user','')
				self.password = self.load_key('password','')
				self.time = self.load_key('time',5)

	def work(self):
		self.set_menu(check=True)
		return True

	def set_menu(self,check=False):
		self.menu = gtk.Menu()
		#
		events2 = self.gcal.getFirstTenEventsOnDefaultCalendar()
		if check and len(self.events)>0:
			for event in events2:
				if not is_event_in_events(event,self.events):
					msg = _('New event:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					print msg
					self.notification = pynotify.Notification ('Google Calendar Indicator',msg,comun.ICON_NEW_EVENT)
					self.notification.show()
			for event in self.events:
				if not is_event_in_events(event,events2):
					msg = _('Event finished:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					print msg
					self.notification = pynotify.Notification ('Google Calendar Indicator',msg,comun.ICON_FINISHED_EVENT)
					self.notification.show()

		self.events = events2
		self.menu_events = []
		for event in self.events:
			self.menu_events.append(gtk.MenuItem(getTimeAndDate(event.when[0].start)+' - '+event.title.text))
			'''
			print '##############################################'
			print event.title.text
			print event.recurrence
			if len(event.when)>0:
				print event.when[0].start
				print event.when[0].end				
			print '##############################################'
			'''
		#
		self.menu_separator0=gtk.MenuItem()		
		self.menu_show_calendar=gtk.MenuItem(_('Show Calendar'))
		self.menu_preferences=gtk.MenuItem(_('Preferences'))
		self.menu_exit=gtk.MenuItem(_('Exit'))
		self.menu_separator1=gtk.MenuItem()
		self.menu_about=gtk.MenuItem(_('About...'))
		#
		for i in range(len(self.menu_events)):
			self.menu.append(self.menu_events[i])
		self.menu.append(self.menu_separator0)
		self.menu.append(self.menu_show_calendar)
		self.menu.append(self.menu_preferences)
		self.menu.append(self.menu_exit)
		self.menu.append(self.menu_separator1)
		self.menu.append(self.menu_about)	
		#
		now = datetime.datetime.now()
		if self.events[0].when[0].start.find('T') != -1:
			print self.events[0].when[0].start
			if self.events[0].when[0].start.find('.') != -1:
				com = datetime.datetime.strptime(self.events[0].when[0].start.split('.')[0],'%Y-%m-%dT%H:%M:%S')
			else:
				com = datetime.datetime.strptime(self.events[0].when[0].start,'%Y-%m-%dT%H:%M:%S')
			
		else:
			com = datetime.datetime.strptime(self.events[0].when[0].start,'%Y-%m-%d')
		if now.year == com.year and now.month == com.month and now.day == com.day and now.hour == com.hour:
			print 'coinciden'
			self.indicator.set_status (appindicator.STATUS_ACTIVE)
		else:
			print now.hour
			print com.hour
			print 'no coinciden'
			print self.events[0].when[0].start
			self.indicator.set_status (appindicator.STATUS_ATTENTION)
		#
		for i in range(len(self.menu_events)):
			self.menu_events[i].show()
		self.menu_separator0.show()
		self.menu_show_calendar.show()
		self.menu_preferences.show()
		self.menu_exit.show()
		self.menu_separator1.show()
		self.menu_about.show()
		#
		self.menu_show_calendar.connect('activate', self.menu_show_calendar_response)
		self.menu_preferences.connect('activate',self.menu_preferences_response)
		self.menu_exit.connect('activate', self.menu_exit_response)
		self.menu_about.connect('activate', self.menu_about_response)
		#menu.show()
		self.indicator.set_menu(self.menu)
	
	def menu_preferences_response(self,widget):
		self.menu_preferences.set_sensitive(False)
		p = Preferences()
		if p.ok == True:
			self.user = self.load_key('user','')
			self.password = self.load_key('password','')
			self.time = self.load_key('time',5)
		self.menu_preferences.set_sensitive(True)
					
	def menu_show_calendar_response(self,widget):
		self.menu_show_calendar.set_sensitive(False)
		cd = CalendarDialog('Calendar',parent = None, googlecalendar = self.gcal)
		cd.run()
		cd.destroy()
		self.menu_show_calendar.set_sensitive(True)

	def menu_exit_response(self,widget):
		exit(0)

	def menu_about_response(self,widget):
		self.menu_about.set_sensitive(False)
		ad=gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2011\nLorenzo Carbonell')
		ad.set_comments(_('An indicator for Google Calendar'))
		ad.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		#ad.set_logo(logo)
		ad.set_logo_icon_name(comun.ICON)
		ad.set_program_name(comun.APPNAME)
		ad.run()
		ad.destroy()
		self.menu_about.set_sensitive(True)

	def load_key(self,key,defecto):
		gconfi = GConf()
		PATH = '/apps/remember-me/options/'+key
		try:
			valor = gconfi.get_key(PATH)
			return valor
		except ValueError:
			gconfi.set_key(PATH,defecto)
		return defecto

if __name__ == "__main__":
	DBusGMainLoop(set_as_default=True)
	tpi=RememberIndicator()
	gtk.main()
	exit(0)

