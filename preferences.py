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
		self.set_default_size(50, 250)
		self.set_resizable(False)
		self.set_icon(gtk.gdk.pixbuf_new_from_file(comun.ICON))		
		self.connect('destroy', self.close_application)
		#
		vbox0 = gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = gtk.Notebook()
		vbox0.add(notebook)
		#
		frame0 = gtk.Frame()
		notebook.append_page(frame0,tab_label = gtk.Label(_('Login')))
		#
		table = gtk.Table(rows = 2, columns = 2, homogeneous = False)
		table.set_border_width(5)
		table.set_col_spacings(5)
		table.set_row_spacings(5)
		frame0.add(table)
		#
		label11 = gtk.Label(_('User')+':')
		label11.set_alignment(0,.5)
		table.attach(label11,0,1,0,1, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		label12 = gtk.Label(_('Password')+':')
		label12.set_alignment(0,.5)
		table.attach(label12,0,1,1,2, xoptions = gtk.FILL, yoptions = gtk.SHRINK)
		#
		self.entry1 = gtk.Entry()
		self.entry1.set_width_chars(50)
		table.attach(self.entry1,1,2,0,1, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
		#
		self.entry2 = gtk.Entry()
		self.entry2.set_visibility(False)
		self.entry2.set_width_chars(50)
		table.attach(self.entry2,1,2,1,2, xoptions = gtk.EXPAND, yoptions = gtk.SHRINK)
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
		#
		self.entry1.set_text(encoder.decode(self.user))
		self.entry2.set_text(encoder.decode(self.password))
		
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

	def close_application(self,widget):
		self.ok = False
	

if __name__ == "__main__":
	p = Preferences()
	exit(0)
		
