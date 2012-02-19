#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
#
__author__='atareao'
__date__ ='$19/02/2012'
#
#
# Copyright (C) 2012 Lorenzo Carbonell
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

#install gir1.2-gnomekeyring-1.0
from gi.repository import GnomeKeyring, GLib
import ConfigParser
import comun
import os

config_dir = os.path.join(os.path.expanduser('~'),'.config')
config_app_dir = os.path.join(config_dir, comun.APP)
config_file = os.path.join(config_app_dir, comun.APPCONF)

DEFAULTS = {'user':'', 
			'password':'********',
			'time':'5',
			'theme':'light',
			'keyring':GnomeKeyring.get_default_keyring_sync()[1]}

class Configuration(object):
	
	def __init__(self):
		self.config = ConfigParser.RawConfigParser()
		self.conf = DEFAULTS
		if not os.path.exists(config_file):
			self.create()
			self.save()
		self.read()
	'''
	####################################################################
	Keyring Functions
	####################################################################
	'''
	def _get_item(self, keyring, name):
		for id in GnomeKeyring.list_item_ids_sync(keyring)[1]:
			item = GnomeKeyring.item_get_info_sync(keyring, id)[1]
			if item.get_display_name() == name:
				return id,item
		return None

	def _set_password(self, keyring, name, password):
		item = self._get_item(keyring, name)
		if item:
			id,item = item
			info = GnomeKeyring.item_get_info_sync(keyring, id)[1]
			info.set_secret(password)
			GnomeKeyring.item_set_info_sync(keyring,id, info)
		else:
			GnomeKeyring.item_create_sync(keyring, GnomeKeyring.ItemType.GENERIC_SECRET, name, GLib.Array(), password, False)	

	def _get_password(self, keyring, name):
		for id in GnomeKeyring.list_item_ids_sync(keyring)[1]:
			item = GnomeKeyring.item_get_info_sync(keyring, id)[1]
			if item.get_display_name() == name:
				return item.get_secret()
		return None

	'''
	####################################################################
	Config Functions
	####################################################################
	'''
		 
	def _get(self,key):
		try:
			value = self.config.get('Configuration',key)
		except ConfigParser.NoOptionError:
			value = DEFAULTS[key]
		if value == 'None':
			value = None
		return value
		
	def set(self, key, value):
		if key in self.conf.keys():
			self.conf[key] = value
			
	def get(self,key):
		if key in self.conf.keys():
			return self.conf[key]
		return None

	'''
	####################################################################
	Operations
	####################################################################
	'''
	def read(self):
		self.config.read(config_file)
		for key in self.conf.keys():
			self.conf[key] =  self._get(key)
		self.conf['password'] = self._get_password(self.conf['keyring'],comun.APP)
		

	def create(self):
		if not self.config.has_section('Configuration'):
			self.config.add_section('Configuration')
		self.set_defaults()
	
	def set_defaults(self):
		self.conf = {}
		for key in DEFAULTS.keys():
			self.conf[key] = DEFAULTS[key]
		self.password = ''

	def save(self):
		for key in self.conf.keys():
			if key == 'password':
				self._set_password(self.conf['keyring'], comun.APP, self.conf['password'])
				self.config.set('Configuration', 'password', '********')
			else:
				self.config.set('Configuration', key, self.conf[key])
		if not os.path.exists(config_app_dir):
			os.makedirs(config_app_dir)
		self.config.write(open(config_file, 'w'))
		

if __name__=='__main__':
	configuration = Configuration()
	#configuration.set('password','armadillo')
	#configuration.save()
	print '############################################################'
	print configuration.get('password')
