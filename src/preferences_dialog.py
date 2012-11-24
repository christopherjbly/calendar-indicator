#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$19/02/2012$'
#
#
# Copyright (C) 2011,2012 Lorenzo Carbonell
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

from gi.repository import Gtk
import os
import shutil
import locale
import gettext
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


class Preferences(Gtk.Dialog):
	def __init__(self):
		title = comun.APPNAME + ' | '+_('Preferences')
		Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_size_request(180, 170)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Login')))
		#
		table1 = Gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label11 = Gtk.Label(_('Allow access to Google Calendar')+':')
		label11.set_alignment(0,.5)
		table1.attach(label11,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch1 = Gtk.Switch()
		self.switch1.connect('button-press-event',self.on_switch1_changed)
		self.switch1.connect('activate',self.on_switch1_changed)
		table1.attach(self.switch1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label12 = Gtk.Label(_('Calendar')+':')
		label12.set_alignment(0,.5)
		table1.attach(label12,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.liststore = Gtk.ListStore(str,str)
		self.entry2 = Gtk.ComboBox.new_with_model(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		self.entry2.pack_start(renderer_text, True)
		self.entry2.add_attribute(renderer_text, "text", 0)
		self.entry2.set_active(0)
		table1.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		
		#
		frame2 = Gtk.Frame()
		notebook.append_page(frame2,tab_label = Gtk.Label(_('Options')))
		table2 = Gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table2.set_border_width(5)
		table2.set_col_spacings(5)
		table2.set_row_spacings(5)
		frame2.add(table2)
		#
		label21 = Gtk.Label(_('Time between updates')+':')
		label21.set_alignment(0,.5)
		table2.attach(label21,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.spin3 = Gtk.SpinButton()
		self.spin3.set_range(5,100)
		self.spin3.set_increments(5,10)
		table2.attach(self.spin3,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label22 = Gtk.Label(_('Autostart')+':')
		label22.set_alignment(0,.5)
		table2.attach(label22,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch4 = Gtk.Switch()		
		table2.attach(self.switch4,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label23 = Gtk.Label(_('Theme light')+':')
		label23.set_alignment(0,.5)
		table2.attach(label23,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch5 = Gtk.Switch()		
		table2.attach(self.switch5,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.load_preferences()
		#
		self.show_all()
	def on_switch1_changed(self,widget,data):
		if self.switch1.get_active():
			if os.path.exists(comun.TOKEN_FILE):
				os.remove(comun.TOKEN_FILE)
				exit(0)
		gca = GCAService()
		if gca:
			self.switch1.set_active(False)
			for calendar in gca.get_calendars():
				self.liststore.append([calendar['summary'],calendar['id']])
			self.entry2.set_active(0)
		
	def load_preferences(self):
		self.switch1.set_active(os.path.exists(comun.TOKEN_FILE))
		configuration = Configuration()
		time = configuration.get('time')
		theme = configuration.get('theme')
		calendar_id = configuration.get('calendar_id')
		print(calendar_id)
		self.spin3.set_value(time)
		if os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")):
			self.switch4.set_active(True)
		if theme == 'light':
			self.switch5.set_active(True)
		else:
			self.switch5.set_active(False)
		if os.path.exists(comun.TOKEN_FILE):
			gca = GoogleCalendar(token_file = comun.TOKEN_FILE)
			if gca:
				for calendar in gca.get_calendars():
					self.liststore.append([calendar['summary'],calendar['id']])
				if len(calendar_id)>0:
					for i,item in enumerate(self.liststore):
						if calendar_id == item[1]:
							self.entry2.set_active(i)
							return
				self.entry2.set_active(0)
			
	
	def save_preferences(self):
		if os.path.exists(comun.TOKEN_FILE):
			configuration = Configuration()
			tree_iter = self.entry2.get_active_iter()
			if tree_iter != None:
				model = self.entry2.get_model()
				calendar_id = model[tree_iter][1]	
			configuration.set('calendar_id',calendar_id)
			configuration.set('first-time',False)
			configuration.set('time',self.spin3.get_value())
			if self.switch5.get_active():
				configuration.set('theme','light')
			else:
				configuration.set('theme','dark')
			configuration.save()
			filestart = os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")
			if self.switch4.get_active():
				if not os.path.exists(filestart):
					if not os.path.exists(os.path.dirname(filestart)):
						os.makedirs(os.path.dirname(filestart))
					shutil.copyfile('/usr/share/calendar-indicator/calendar-indicator-autostart.desktop',filestart)
			else:		
				if os.path.exists(filestart):
					os.remove(filestart)		

	def close_application(self,widget):
		self.ok = False
	

if __name__ == "__main__":
	p = Preferences()
	if p.run() == Gtk.ResponseType.ACCEPT:
		p.save_preferences()
	p.destroy()
	exit(0)
		
