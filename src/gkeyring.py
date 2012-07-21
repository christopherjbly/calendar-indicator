#! /usr/bin/python
# -*- coding: utf-8 -*-
#
__author__='atareao'
__date__ ='$29/04/2012'
#
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

from gi.repository import GnomeKeyring, GLib
import ctypes
import exceptions
libc = ctypes.CDLL("libc.so.6")


def mlock(var):
    if var:
      libc.mlock(var, len(var))

def munlock(var):
    if var:
      libc.munlock(var, len(var))
class NoPasswordFound(Exception):
	def __str__(self):
		return 'No password found'
class GnomeKeyringLocked(Exception):
	def __str__(self):
		return 'Gnome Keyring Locked'

class MyGnomeKeyring():
	
	def __init__(self,key):
		self.key = key
		
	def _set_value_to_gnomekeyring(self, name, value):
		"""Store a value in the keyring."""
		attributes = GnomeKeyring.Attribute.list_new()
		GnomeKeyring.Attribute.list_append_string(attributes, 'id', str(name))
		keyring = GnomeKeyring.get_default_keyring_sync()[1]
		value = GnomeKeyring.item_create_sync(keyring, GnomeKeyring.ItemType.GENERIC_SECRET,"%s preferences" % (self.key),attributes, str(value), True)
		return value[1]
		
	def _get_value_from_gnomekeyring(self, name):
		"""Get a locked secret for threaded/multiprocessing use."""
		value = ""
		attrlist = GnomeKeyring.Attribute.list_new()
		GnomeKeyring.Attribute.list_append_string(attrlist, 'id', str(name))
		result, found = GnomeKeyring.find_items_sync(GnomeKeyring.ItemType.GENERIC_SECRET,attrlist)
		if result == GnomeKeyring.Result.OK:
			value = found[0].secret
			mlock(value)
			return value
		elif result == GnomeKeyring.Result.NO_MATCH:
			raise(NoPasswordFound())
		raise(GnomeKeyringLocked())
	
	def get(self,key):
		return self._get_value_from_gnomekeyring('%s %s'%(self.key,key))
		
	def set(self,key,value):
		return self._set_value_to_gnomekeyring('%s %s'%(self.key,key),value)
		
	def get_password(self):
		return self.get('password')
		
	def set_password(self,password):
		return self.set('password',password)

if __name__ == '__main__':
	gk = MyGnomeKeyring()
	print gk.set_password('prueba')
	print gk.set('ril_password','alfa')
	print gk.get_password()	
	print gk.get('ril_password')
