#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$06-jun-2010 12:34:44$'
#
# <one line to give the program's name and a brief idea of what it does.>
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

from gi.repository import Gtk
import os
import shutil
import locale
import gettext
import gkconfiguration
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
		#self.set_icon_from_file(comun.ICON)
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
		label11 = Gtk.Label(_('User')+':')
		label11.set_alignment(0,.5)
		table1.attach(label11,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label12 = Gtk.Label(_('Password')+':')
		label12.set_alignment(0,.5)
		table1.attach(label12,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_width_chars(30)
		table1.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry2 = Gtk.Entry()
		self.entry2.set_visibility(False)
		self.entry2.set_width_chars(30)
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
		self.load_preferences()
		#
		self.show_all()

	def load_preferences(self):
		configuration = gkconfiguration.get_configuration()
		self.user = configuration['user']
		self.password = configuration['password']
		self.time = configuration['time']
		#
		self.entry1.set_text(self.user)
		self.entry2.set_text(self.password)
		self.spin3.set_value(int(float(self.time)))
		if not os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator-autostart.desktop")):
			self.switch4.set_active(True)
	
	def save_preferences(self):
		gkconfiguration.set_configuration(self.entry1.get_text(),self.entry2.get_text(),str(self.spin3.get_value()))
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
		
