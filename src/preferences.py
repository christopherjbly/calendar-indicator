#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# preferences.py
#
# Copyright (C) 2012
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
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
import locale
import gettext
import com
import shutil
from gi.repository import Gio
from configurator import Configurator

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(com.APP, com.LANGDIR)
gettext.textdomain(com.APP)
_ = gettext.gettext

YVIEWER = ['yviewer','/usr/bin/yviewer','/usr/bin/yviewer "%s"']
VLC = ['vlc','/usr/bin/vlc','/usr/bin/vlc --one-instance "%s"']
MINITUBE = ['minitube','/usr/bin/minitube','/usr/bin/minitube "%s"']
BROWSER = ['browser','browser','"%s"']

class Preferences():
	def __init__(self):
		self.configurator = Configurator(com.KEY)
		self.viewer = 'yviewer'
		self.vlc = Gio.File.new_for_path(VLC[1])
		self.minitube = Gio.File.new_for_path(MINITUBE[1])
		self.yviewer = Gio.File.new_for_path(YVIEWER[1])

	def read(self):
		self.viewer = self.configurator.get('viewer')
		
	def save(self):
		self.configurator.set('viewer',self.viewer)
	
	def get_active_viewer(self):
		self.read()
		if self.viewer == 'yviewer':
			if self.yviewer.query_exists(None):
				return YVIEWER
			else:
				return BROWSER
		elif self.viewer == 'vlc':
			if self.vlc.query_exists(None):
				return VLC
			else:
				return BROWSER
		elif self.viewer == 'minitube':
			if self.minitube.query_exists(None):
				return MINITUBE
			else:
				return BROWSER
		return BROWSER

		
	def set_default(self):
		self.viewer = 'yviewer'
		self.save()
		
if __name__ == "__main__":
	pf = Preferences()
	pf.read()
	print pf.viewer
	exit(0)
