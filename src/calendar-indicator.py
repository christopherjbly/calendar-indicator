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
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Notify

import time
import dbus
import locale
import gettext
import datetime
import webbrowser
from calendardialog import CalendarDialog
#
import comun
import gkconfiguration
from gcal import GCal
from preferences_dialog import Preferences
#
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

def internet_on():
	try:
		response=urllib2.urlopen('http://google.com',timeout=1)
		return True
	except:
		pass
	return False


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

def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None):
	if text != None:
		if icon == None:
			menu_item = Gtk.MenuItem.new_with_label(text)
		else:
			menu_item = Gtk.ImageMenuItem.new_with_label(text)
			image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
	else:
		if icon == None:
			menu_item = Gtk.SeparatorMenuItem()
		else:
			menu_item = Gtk.ImageMenuItem.new_from_stock(icon, None)
			menu_item.set_always_show_image(True)
	if conector_event != None and conector_action != None:				
		menu_item.connect(conector_event,conector_action)
	menu_item.show()
	menu.append(menu_item)
	return menu_item

class CalendarIndicator():
	def __init__(self):
		if dbus.SessionBus().request_name("es.atareao.calendar-indicator") != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
			print "application already running"
			exit(0)
		self.indicator = appindicator.Indicator.new('Calendar-Indicator', 'Calendar-Indicator', appindicator.IndicatorCategory.APPLICATION_STATUS)
		print '12'
		#
		self.indicator.set_icon(comun.ICON_ENABLED)
		self.indicator.set_attention_icon(comun.ICON_DISABLED)
		#
		
		self.read_preferences()
		#
		self.events = []
		self.set_menu()
		GObject.timeout_add_seconds(60, self.work)
		

	def read_preferences(self):
		configuration = gkconfiguration.get_configuration()
		self.user = configuration['user']
		self.password = configuration['password']
		self.time = configuration['time']
		
		if self.user == None or self.password == None:
			p = Preferences()
			if p.run() == Gtk.ResponseType.ACCEPT:
				p.save_preferences()
			else:
				exit(1)
			p.destroy()
			self.user = configuration['user']
			self.password = configuration['password']
			self.time = configuration['time']
		error = True
		while error:
			try:
				self.gcal=GCal(self.user,self.password)
				error = False
			except Exception,e:
				print e
				error = True
				md = Gtk.MessageDialog(
					None,
					Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
					Gtk.MessageType.ERROR,
					Gtk.ButtonsType.OK_CANCEL,
					_('The email or/and the password are incorrect\nplease, try again?'))
				if md.run() == Gtk.ResponseType.CANCEL:
					exit(3)
				md.destroy()
				p = Preferences()
				if p.run() == Gtk.ResponseType.ACCEPT:
					p.save_preferences()
				else:
					exit(1)
				p.destroy()
				self.user = configuration['user']
				self.password = configuration['password']
				self.time = configuration['time']

	def work(self):
		if (time.time()-self.actualization_time) > self.time*60:
			while internet_on() == False:
				time.sleep(1)
			self.actualization_time = time.time()
			self.set_menu(check=True)
		return True
		
		

	def set_menu(self,check=False):
		self.menu = Gtk.Menu()
		#
		events2 = self.gcal.getFirstTenEventsOnDefaultCalendar()
		if check and len(self.events)>0:
			for event in events2:
				if not is_event_in_events(event,self.events):
					msg = _('New event:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					print msg
					self.notification = Notify.Notification ('Calendar Indicator',msg,comun.ICON_NEW_EVENT)
					self.notification.show()
			for event in self.events:
				if not is_event_in_events(event,events2):
					msg = _('Event finished:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					print msg
					self.notification = Notify.Notification ('Calendar Indicator',msg,comun.ICON_FINISHED_EVENT)
					self.notification.show()

		self.events = events2
		for event in self.events:
			add2menu(self.menu, text = (getTimeAndDate(event.when[0].start)+' - '+event.title.text))
		#
		add2menu(self.menu)
		self.menu_show_calendar = add2menu(self.menu, text = _('Show Calendar'), conector_event = 'activate',conector_action = self.menu_show_calendar_response)
		self.menu_preferences = add2menu(self.menu, text = _('Preferences'), conector_event = 'activate',conector_action = self.menu_preferences_response)
		add2menu(self.menu)
		menu_help = add2menu(self.menu, text =_('Help'))
		menu_help.set_submenu(self.get_help_menu())
		add2menu(self.menu)
		add2menu(self.menu, text = _('Exit'), conector_event = 'activate',conector_action = self.menu_exit_response)
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
			self.indicator.set_status (appindicator.IndicatorStatus.ACTIVE)
		else:
			print now.hour
			print com.hour
			print self.events[0].when[0].start
			self.indicator.set_status (appindicator.IndicatorStatus.ATTENTION)
		#
		self.menu.show()
		self.indicator.set_menu(self.menu)
		while Gtk.events_pending():
			Gtk.main_iteration()
		

	def get_help_menu(self):
		help_menu =Gtk.Menu()
		#		
		add2menu(help_menu,text = _('Web...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://launchpad.net/calendar-indicator'))
		add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://answers.launchpad.net/calendar-indicator'))
		add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://translations.launchpad.net/calendar-indicator'))
		add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://bugs.launchpad.net/calendar-indicator'))
		add2menu(help_menu)
		add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.menu_about_response)
		#
		help_menu.show()
		#
		return help_menu

	def menu_preferences_response(self,widget):
		self.menu_preferences.set_sensitive(False)
		p = Preferences()
		if p.run() == Gtk.ResponseType.ACCEPT:
			p.save_preferences()
		p.destroy()
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
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2011,2012\nLorenzo Carbonell')
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
		ad.set_logo(Gtk.gdk.pixbuf_new_from_file(comun.ICON))
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
	Notify.init("calendar-indicator")
	ci=CalendarIndicator()
	Gtk.main()

