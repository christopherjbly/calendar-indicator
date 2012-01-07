#! /usr/bin/python
# -*- coding: iso-8859-1 -*-
#
__author__='atareao'
__date__ ='$09/07/2011'
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
import gnomekeyring


# attributes to detect gnome-encfs items in keyring
ATTR = {'application': 'calendar-indicator' }
KEYRING = gnomekeyring.get_default_keyring_sync()
ITYPE = gnomekeyring.ITEM_GENERIC_SECRET

def int2bool(value):
	if value == 0:
		return False
	return True

def get_items():
	try:
		items = gnomekeyring.find_items_sync(ITYPE, ATTR)
	except gnomekeyring.NoMatchError:
		items = []
	return items

def exists_configuration():
	if len(get_items())>0:
		return True
	return False
	
def get_configuration():
	items = get_items()
	if len(items)>0:
		item = items[0]
		configuration = {\
		'user':item.attributes['user'],\
		'password':item.secret,\
		'time':item.attributes['time']}	
		return configuration
	return None

def set_configuration(user,password,time):
	items = get_items()
	attributes = ATTR.copy()
	attributes['user'] = user
	attributes['password'] = password
	attributes['time'] = time
	if len(items) == 0:
		name = 'Calendar-Indicator configuration'
		gnomekeyring.item_create_sync(KEYRING, ITYPE, name, attributes, password, False)	
	else:
		item = items[0]
		gnomekeyring.item_set_attributes_sync(KEYRING, item.item_id, attributes)
		info = gnomekeyring.item_get_info_sync(KEYRING, item.item_id)
		info.set_secret(password)
		gnomekeyring.item_set_info_sync(KEYRING, item.item_id, info)

if __name__=='__main__':
	set_configuration('user','password','5')
	print get_configuration()
