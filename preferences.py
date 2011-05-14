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

import gtk
import os
import shutil
import locale
import gettext
from configurator import GConf
from encoderapi import Encoder
import comun

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


class Preferences(gtk.Dialog):
	def __init__(self):
		self.ok = False
		#
		title = comun.APPNAME + ' | '+_('Preferences')
		gtk.Dialog.__init__(self, title,None,gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.set_size_request(450, 175)
		self.set_resizable(False)
		#self.set_icon(gtk.gdk.pixbuf_new_from_file(comun.ICON))		
		self.connect('destroy', self.close_application)
		#
		vbox0 = gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = gtk.Notebook()
		vbox0.add(notebook)
		#
		frame1 = gtk.Frame()
		notebook.append_page(frame1,tab_label = gtk.Label(_('Login')))
		#
		table1 = gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label11 = gtk.Label(_('User')+':')
		label11.set_alignment(0,.5)
		table1.attach(label11,0,1,0,1, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		label12 = gtk.Label(_('Password')+':')
		label12.set_alignment(0,.5)
		table1.attach(label12,0,1,1,2, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		self.entry1 = gtk.Entry()
		self.entry1.set_width_chars(40)
		table1.attach(self.entry1,1,2,0,1, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
		#
		self.entry2 = gtk.Entry()
		self.entry2.set_visibility(False)
		self.entry2.set_width_chars(40)
		table1.attach(self.entry2,1,2,1,2, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
		#
		frame2 = gtk.Frame()
		notebook.append_page(frame2,tab_label = gtk.Label(_('Options')))
		table2 = gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table2.set_border_width(5)
		table2.set_col_spacings(5)
		table2.set_row_spacings(5)
		frame2.add(table2)
		#
		label21 = gtk.Label(_('Time between updates')+':')
		label21.set_alignment(0,.5)
		table2.attach(label21,0,1,0,1, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		self.spin3 = gtk.SpinButton()
		self.spin3.set_range(1,100)
		self.spin3.set_increments(1,10)
		table2.attach(self.spin3,1,2,0,1, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
		#
		label22 = gtk.Label(_('Autostart')+':')
		label22.set_alignment(0,.5)
		table2.attach(label22,0,1,1,2, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		self.checkbox4 = gtk.CheckButton()
		table2.attach(self.checkbox4,1,2,1,2, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
		#
		self.load_preferences()
		#
		self.show_all()
		#
		if self.run() == gtk.RESPONSE_ACCEPT:
			self.ok = True
			self.save_preferences()
		self.destroy()

	def load_preferences(self):
		encoder = Encoder()
		self.user = self.load_key('user',encoder.encode(''))
		self.password = self.load_key('password',encoder.encode(''))
		self.time = self.load_key('time',5)
		#
		self.entry1.set_text(encoder.decode(self.user))
		self.entry2.set_text(encoder.decode(self.password))
		self.spin3.set_value(self.time)
		if os.path.exists(os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator.py.desktop")):
			self.checkbox4.set_active(True)
		
		
	def load_key(self,key,defecto):
		gconfi = GConf()
		PATH = '/apps/remember-me/options/'+key
		try:
			valor = gconfi.get_key(PATH)
			return valor
		except ValueError:
			gconfi.set_key(PATH,defecto)
		return defecto
		
	def save_preferences(self):
		gconfi = GConf()
		encoder = Encoder()
		gconfi.set_key('/apps/remember-me/options/user',encoder.encode(self.entry1.get_text()))
		gconfi.set_key('/apps/remember-me/options/password',encoder.encode(self.entry2.get_text()))
		gconfi.set_key('/apps/remember-me/options/time',self.spin3.get_value())
		filestart = os.path.join(os.getenv("HOME"),".config/autostart/calendar-indicator.py.desktop")
		if self.checkbox4.get_active():
			if not os.path.exists(filestart):
				shutil.copy('/usr/share/calendar-indicator/calendar-indicator.py.desktop', filestart)
		else:		
			if os.path.exists(filestart):
				os.remove(filestart)

	def close_application(self,widget):
		self.ok = False
	

if __name__ == "__main__":
	p = Preferences()
	exit(0)
		
