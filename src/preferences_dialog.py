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

from gi.repository import Gtk, Gdk
import os
import shutil
import locale
import gettext
from configurator import Configuration
from googlecalendarapi import GoogleCalendar
from logindialog import LoginDialog
import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


class Preferences(Gtk.Dialog):
	def __init__(self,googlecalendar = None):
		self.googlecalendar = googlecalendar
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
		notebook.append_page(frame2,tab_label = Gtk.Label(_('Colors')))
		vbox2 = Gtk.VBox()
		frame2.add(vbox2)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		vbox2.pack_start(scrolledwindow,True,True,0)
		self.store = Gtk.ListStore(str, str,str)
		self.treeview = Gtk.TreeView(self.store)
		self.treeview.connect('cursor-changed',self.on_cursor_changed)
		column1 = Gtk.TreeViewColumn(_('Calendar'),  Gtk.CellRendererText(), text=0)
		self.treeview.append_column(column1)
		column2 = Gtk.TreeViewColumn(_('Color'),  Gtk.CellRendererText(), background=1)
		self.treeview.append_column(column2)
		scrolledwindow.add(self.treeview)
		#
		frame3 = Gtk.Frame()
		notebook.append_page(frame3,tab_label = Gtk.Label(_('Options')))
		table3 = Gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table3.set_border_width(5)
		table3.set_col_spacings(5)
		table3.set_row_spacings(5)
		frame3.add(table3)
		#
		label21 = Gtk.Label(_('Time between autommatic syncronizations (hours)')+':')
		label21.set_alignment(0,.5)
		table3.attach(label21,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.spin3 = Gtk.SpinButton()
		self.spin3.set_range(12,120)
		self.spin3.set_increments(12,24)
		table3.attach(self.spin3,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label22 = Gtk.Label(_('Autostart')+':')
		label22.set_alignment(0,.5)
		table3.attach(label22,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch4 = Gtk.Switch()		
		table3.attach(self.switch4,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label23 = Gtk.Label(_('Theme light')+':')
		label23.set_alignment(0,.5)
		table3.attach(label23,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.switch5 = Gtk.Switch()		
		table3.attach(self.switch5,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.load_preferences()
		#
		self.show_all()
	def on_cursor_changed(self,widget):
		selection = self.treeview.get_selection()
		if selection is not None:
			model,aiter = selection.get_selected()
			print(model[aiter][0],model[aiter][1],model[aiter][2])			
			colordialog = Gtk.ColorSelectionDialog("Select color")
			colordialog.get_color_selection().set_current_color(Gdk.color_parse(model[aiter][1]))
			if colordialog.run() == Gtk.ResponseType.OK:
				color = colordialog.get_color_selection().get_current_color().to_string()
				print(color)
				model[aiter][1] = color
			colordialog.destroy()
	def on_switch1_changed(self,widget,data):
		if self.switch1.get_active():
			if os.path.exists(comun.TOKEN_FILE):
				os.remove(comun.TOKEN_FILE)
		else:
			googlecalendar = GoogleCalendar(token_file = comun.TOKEN_FILE)
			if googlecalendar.do_refresh_authorization() is None:
				authorize_url = googlecalendar.get_authorize_url()
				ld = LoginDialog(authorize_url)
				ld.run()
				googlecalendar.get_authorization(ld.code)
				ld.destroy()				
				if googlecalendar.do_refresh_authorization() is None:
					md = Gtk.MessageDialog(	parent = self,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You have to authorize Calendar-Indicator to use it, do you want to authorize?'))
					if md.run() == Gtk.ResponseType.CANCEL:
						exit(3)				
				else:
					if googlecalendar.do_refresh_authorization() is None:
						exit(3)
			self.switch1.set_active(True)
			self.liststore.clear()
			self.liststore.append([_('All'),None])
			for calendar in googlecalendar.get_calendars():
				self.liststore.append([calendar['summary'],calendar['id']])
			self.entry2.set_active(0)
		
	def load_preferences(self):
		self.switch1.set_active(os.path.exists(comun.TOKEN_FILE))
		configuration = Configuration()
		time = configuration.get('time')
		theme = configuration.get('theme')
		calendar_id = configuration.get('calendar_id')
		self.spin3.set_value(time)
		if os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")):
			self.switch4.set_active(True)
		if theme == 'light':
			self.switch5.set_active(True)
		else:
			self.switch5.set_active(False)
		if os.path.exists(comun.TOKEN_FILE):
			if self.googlecalendar is not None:
				calendars = self.googlecalendar.calendars.values()
			else:
				gca = GoogleCalendar(token_file = comun.TOKEN_FILE)
				calendars = gca.get_calendars().values()
			self.liststore.clear()
			self.store.clear()
			self.liststore.append([_('All'),None])			
			for calendar in calendars:
				self.liststore.append([calendar['summary'],calendar['id']])
				if configuration.has(calendar['id']):
					color = configuration.get(calendar['id'])
				else:
					color = '#EEEEEE'
				self.store.append([calendar['summary'],color,calendar['id']])
			if calendar_id is None:
				self.entry2.set_active(0)
			else:
				for i,item in enumerate(self.liststore):
					if calendar_id == item[1]:
						self.entry2.set_active(i)
						return
	
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
			aiter = self.store.get_iter_first()
			while(aiter is not None):
				configuration.set(self.store.get_value(aiter,2),self.store.get_value(aiter,1))
				aiter = self.store.iter_next(aiter)
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
		
