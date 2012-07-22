#! /usr/bin/python
# -*- coding: utf-8 -*-
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
from gi.repository import GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Notify

import urllib2
import time
import dbus
import locale
import gettext
import datetime
import webbrowser
from calendardialog import CalendarDialog
import gdata.client
#
import comun
from configurator import Configuration
from gkeyring import MyGnomeKeyring, NoPasswordFound, GnomeKeyringLocked
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
		self.notification = Notify.Notification.new('','', None)
		self.read_preferences()
		#
		self.events = []
		self.create_menu()
		self.update_menu()
		self.actualization_time = 0
		GLib.timeout_add_seconds(60, self.work)

	def read_preferences(self):
		configuration = Configuration()
		self.time = configuration.get('time')
		self.theme = configuration.get('theme')
		user = self.get_user()
		password = self.get_password()
		incorrect = True
		while incorrect:
			try:
				self.gcal=GCal(user,password)				
				incorrect = False
			except gdata.client.BadAuthentication, e2:
				md = Gtk.MessageDialog(	parent = None,
										flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
										type = Gtk.MessageType.ERROR,
										buttons = Gtk.ButtonsType.OK_CANCEL,
										message_format = _('The email or/and the password are incorrect\nplease, try again?'))
				if md.run() != Gtk.ResponseType.OK:
					exit(3)
				md.destroy()
				p = Preferences()
				if p.run() != Gtk.ResponseType.ACCEPT:
					exit(1)
				p.save_preferences()
				p.destroy()
				user = self.get_user()
				password = self.get_password()
			except urllib2.URLError,e:
				md = Gtk.MessageDialog(	parent = None,
										flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
										type = Gtk.MessageType.ERROR,
										buttons = Gtk.ButtonsType.OK_CANCEL,
										message_format = _('There is no connection\ntry again?'))
				if md.run() == Gtk.ResponseType.CANCEL:
					exit(3)
				md.destroy()					

	def work(self):
		if (time.time()-self.actualization_time) > self.time*60:
			while internet_on() == False:
				time.sleep(1)
			self.actualization_time = time.time()
			self.update_menu(check=True)
		return True

	def create_menu(self):
		self.menu = Gtk.Menu()
		self.menu_events = []
		for i in range(10):
			menu_event = add2menu(self.menu, text = '')
			menu_event.set_visible(False)
			self.menu_events.append(menu_event)
		add2menu(self.menu)
		self.menu_refresh = add2menu(self.menu, text = _('Refresh'), conector_event = 'activate',conector_action = self.on_menu_refresh)
		self.menu_show_calendar = add2menu(self.menu, text = _('Show Calendar'), conector_event = 'activate',conector_action = self.menu_show_calendar_response)
		self.menu_preferences = add2menu(self.menu, text = _('Preferences'), conector_event = 'activate',conector_action = self.menu_preferences_response)
		add2menu(self.menu)
		menu_help = add2menu(self.menu, text =_('Help'))
		menu_help.set_submenu(self.get_help_menu())
		add2menu(self.menu)
		add2menu(self.menu, text = _('Exit'), conector_event = 'activate',conector_action = self.menu_exit_response)
		self.menu.show()
		self.indicator.set_menu(self.menu)		
				
	def update_menu(self,check=False):
		#
		now = datetime.datetime.now()
		normal_icon = os.path.join(comun.ICONDIR,'%s-%s-normal.svg'%(now.day,self.theme))
		starred_icon = os.path.join(comun.ICONDIR,'%s-%s-starred.svg'%(now.day,self.theme))
		#
		self.indicator.set_icon(normal_icon)
		self.indicator.set_attention_icon(starred_icon)		
		#
		events2 = self.gcal.getFirstTenEventsOnDefaultCalendar()
		if check and len(self.events)>0:
			for event in events2:
				if not is_event_in_events(event,self.events):
					msg = _('New event:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					self.notification.update('Calendar Indicator',msg,comun.ICON_NEW_EVENT)
					self.notification.show()
			for event in self.events:
				if not is_event_in_events(event,events2):
					msg = _('Event finished:')+'\n'
					msg += getTimeAndDate(event.when[0].start)+' - '+event.title.text
					self.notification.update('Calendar Indicator',msg,comun.ICON_FINISHED_EVENT)
					self.notification.show()
		self.events = events2
		#for menu_event in self.menu_events:
		#	menu_event.set_visible(False)
		for i,event in enumerate(self.events):
			self.menu_events[i].set_label(getTimeAndDate(event.when[0].start)+' - '+event.title.text)
			self.menu_events[i].set_visible(True)
		for i in range(len(self.events),10):
			self.menu_events[i].set_visible(True)
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
			self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
		else:
			self.indicator.set_status(appindicator.IndicatorStatus.ATTENTION)
			self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
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
		self.menu_about = add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.menu_about_response)
		#
		help_menu.show()
		#
		return help_menu

	def menu_preferences_response(self,widget):
		self.menu_preferences.set_sensitive(False)
		p1 = Preferences()
		if p1.run() == Gtk.ResponseType.ACCEPT:
			p1.save_preferences()			
			p1.destroy()
			error = True
			while error:
				try:
					configuration = Configuration()
					self.gcal=GCal(configuration.get('user'), configuration.get('password'))
					self.time = configuration.get('time')
					self.theme = configuration.get('theme')
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
		else:
			p1.destroy()
		self.menu_preferences.set_sensitive(True)
					
	def menu_show_calendar_response(self,widget):
		self.menu_show_calendar.set_sensitive(False)
		cd = CalendarDialog('Calendar',parent = None, googlecalendar = self.gcal)
		cd.run()
		cd.destroy()
		self.menu_show_calendar.set_sensitive(True)

	def on_menu_refresh(self,widget):
		self.update_menu(check=True)
	
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
		ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		ad.set_program_name(comun.APPNAME)
		ad.run()
		ad.destroy()
		self.menu_about.set_sensitive(True)
		
	def get_password(self):
		gk = MyGnomeKeyring(comun.APP)
		incorrect = True
		while incorrect:
			try:
				password = gk.get('password')
				incorrect  = False
			except NoPasswordFound,e:
				print e
				p = Preferences(self)
				if p.run() != Gtk.ResponseType.ACCEPT:
					exit(1)
				p.save_preferences()
				p.destroy()
			except GnomeKeyringLocked,e:
				print e
				md = Gtk.MessageDialog(	parent = self,
										flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
										type = Gtk.MessageType.ERROR,
										buttons = Gtk.ButtonsType.OK_CANCEL,
										message_format = _('You must unlock the Gnome Keyring. Try again?'))
				if md.run() != Gtk.ResponseType.OK:
					exit(3)
				md.destroy()
			except Exception,e:
				print e
		return password
		
	def get_user(self):
		conf = Configuration()
		user = conf.get('user')
		while user == None or user == '':
			p = Preferences(self)
			if p.run() != Gtk.ResponseType.ACCEPT:
				exit(1)
			p.save_preferences()
			p.destroy()
			conf = Configuration()
			user = conf.get('user')
		return user
		
if __name__ == "__main__":
	Notify.init("calendar-indicator")
	ci=CalendarIndicator()
	Gtk.main()

