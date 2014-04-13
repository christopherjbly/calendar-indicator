#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import GdkPixbuf
import cairo
import datetime
import os
import math
import comun
from configurator import Configuration
from comun import _

		
class Widget(Gtk.Window):
	__gsignals__ = {
        'pinit' : (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,(bool,)),
        }
	
	def __init__(self,indicator=None,widgetnumber=1,weather=None):
		Gtk.Window.__init__(self)
		self.set_default_size(5, 5)		
		self.set_icon_from_file(comun.ICON)		
		self.set_decorated(False)
		self.set_border_width(0)		
		self.screen = self.get_screen()
		self.visual = self.screen.get_rgba_visual()
		if self.visual != None and self.screen.is_composited():
			self.set_visual(self.visual)		
		self.set_app_paintable(True)
		self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
		self.connect('draw', self.on_expose, None)
		#self.connect('destroy', self.save_preferences, None)
		self.connect("button-press-event", self.click)
		self.connect("button-release-event", self.release)
		self.connect("motion-notify-event", self.mousemove)				
		vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL,0)		
		self.add(vbox)
		hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,0)
		vbox.pack_start(hbox,False,False,10)
		button = Gtk.Button()
		button.connect('clicked',self.on_button_clicked)
		hbox.pack_start(button,False,False,10)		
		self.pin = Gtk.Image()
		button.add(self.pin)
		button.set_name('pin')
		#
		self.drag = False
		self.drag_x = 0
		self.drag_y = 0		
		self.filename = None
		self.temperature = None
		self.location = None
		self.parse_time = False		
		self.widgetnumber = widgetnumber
		self.indicator = indicator
		self.weather_data = weather		
		self.load_preferences()
		self.read_widgetfile()
		ans = self.read_main_data()
		if ans is not None:
			self.set_size_request( ans[0], ans[1])
		self.parse_data()
		#
		style_provider = Gtk.CssProvider()
		css = """
			#pin{
				opacity:0.05;
				border-image: none;
				background-image: none;
				background-color: rgba(0, 0, 0, 0);
				border-radius: 0px;
			}
			#pin:hover {
				transition: 1000ms linear;
				opacity:1.0;
				border-image: none;
				background-image: none;
				background-color: rgba(0, 0, 0, 0);
				border-radius: 0px;
			}
		"""
		style_provider.load_from_data(css.encode('UTF-8'))
		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(), 
			style_provider,     
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)		
		#
		self.show_all()

	def read_widgetfile(self):		
		if os.path.exists(os.path.join(self.skin,'skin')):
			f = open(os.path.join(self.skin,'skin'))
			self.widgetdata = f.read()
			f.close()
			if self.widgetdata.find('$HOUR$')>-1 or self.widgetdata.find('$MINUTES$')>-1:
				self.parse_time = True
			else:
				self.parse_time = False
		else:
			self.skin = None
			self.widgetdata = None
			
	def set_weather(self,weather):
		self.weather_data = weather
		self.parse_data()
		self.queue_draw()
	def set_location(self,location):
		self.location = location
		self.parse_data()
		self.queue_draw()
		
	def set_datetime(self,utcnow):
		self.datetime = utcnow
		if self.parse_time:
			self.parse_data()
			self.queue_draw()
		
	def set_hideindicator(self,hideindicator):
		self.hideindicator = hideindicator
		if hideindicator:
			if self.indicator.get_status() == appindicator.IndicatorStatus.PASSIVE:
				self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
			else:
				self.indicator.set_status(appindicator.IndicatorStatus.PASSIVE)
				
	def set_keep_above(self,keep_above):
		self.is_above = keep_above
		if keep_above:			
			self.set_type_hint(Gdk.WindowTypeHint.DOCK)
			self.pin.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(comun.IMAGESDIR,'pinin.svg'),36,72,1))
		else:
			self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
			self.pin.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(comun.IMAGESDIR,'pinup.svg'),36,36,1))
		self.hide()
		self.show()
		
	def load_preferences(self):
		pass
		'''
		configuration = Configuration()		
		self.a24h = configuration.get('24h')
		if self.widgetnumber == 1:
			x = configuration.get('wp1-x')
			y = configuration.get('wp1-y')
			self.location = configuration.get('location')
			self.showwidget = configuration.get('widget1')
			self.hideindicator = configuration.get('onwidget1hide')
			self.set_keep_above(configuration.get('onwidget1top'))
			self.set_skip_taskbar_hint(not configuration.get('showintaskbar1'))
			self.set_skip_taskbar_hint(True)
			self.skin = configuration.get('skin1')
		else:
			x = configuration.get('wp2-x')
			y = configuration.get('wp2-y')
			self.location = configuration.get('location2')
			self.showwidget = configuration.get('widget2')
			self.hideindicator = configuration.get('onwidget2hide')
			self.set_keep_above(configuration.get('onwidget2top'))
			self.set_skip_taskbar_hint(not configuration.get('showintaskbar2'))
			self.skin = configuration.get('skin2')		
		self.move(x,y)
		'''
		
	def show_in_taskbar(self,show_in_taskbar):
		self.set_skip_taskbar_hint(not show_in_taskbar) # Not show in taskbar

	def save_preferences(self):
		configuration = Configuration()
		x,y = self.get_position()
		if self.widgetnumber == 1:
			configuration.set('wp1-x',x)
			configuration.set('wp1-y',y)
			configuration.set('onwidget1top',self.is_above)
		else:
			configuration.set('wp2-x',x)
			configuration.set('wp2-y',y)
			configuration.set('onwidget2top',self.is_above)
		configuration.save()
	def on_button_clicked(self,widget):
		self.emit('pinit',not self.is_above)
	def click(self, widget, event):
		self.drag =  True
		self.oldx, self.oldy = event.x,event.y
		pointer,self.drag_x,self.drag_y,mods = self.get_screen().get_root_window().get_pointer()
		if self.hideindicator:
			if self.indicator.get_status() == appindicator.IndicatorStatus.PASSIVE:
				self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
			else:
				self.indicator.set_status(appindicator.IndicatorStatus.PASSIVE)
		
	def release(self, widget, event):
		self.drag =  False

	def mousemove(self,widget,event):
		pointer,x,y,mods = self.get_screen().get_root_window().get_pointer()
		if self.drag:
			pointer,x,y,mods = self.get_screen().get_root_window().get_pointer()
			wpx,wpy = self.get_position()
			if not(self.drag_x == 0 or self.drag_y == 0):
				self.move(wpx+int(x-self.drag_x)+int(event.x-self.oldx),wpy+int(y-self.drag_y)+int(event.y-self.oldy))
				self.save_preferences()
			self.drag_x,self.drag_y = x,y

	def on_expose(self, widget, cr, data):
		cr.save()
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.rectangle(0.0, 0.0, *widget.get_size())
		cr.fill()
		cr.restore()
		#
		if self.surface is not None:
			cr.save()
			cr.set_source_surface(self.surface)
			cr.paint()
			cr.restore()

	def read_main_data(self):
		if self.widgetdata is not None:
			row = self.widgetdata.split('\n')[0].split('|')
			if row[0] == 'MAIN':
				atype, title, width, height = row
				width = int(width)
				height = int(height)
				return width,height
		return None
		
	def parse_data(self):
		if self.skin is not None and os.path.exists(os.path.join(self.skin,'skin')):
			maindir = self.skin
			ans = self.read_main_data()
			if ans is not None and self.weather_data is not None:
				mainsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, ans[0], ans[1])
				cr = cairo.Context(mainsurface)
				try:
					for index,line in enumerate(self.widgetdata.split('\n')):
						row = line.split('|')
						cr.save()
						if row is not None and len(row)>1:
							if row[0] == 'CLOCK':
								print(row)
								atype, minutesorhours, fileimage, x, y, width, height, xpos, ypos = row
								fileimage = os.path.join(maindir,fileimage)
								x = float(x)
								y = float(y)
								width = float(width)
								height = float(height)
								surface = get_surface_from_file(fileimage)
								print(surface.get_width(),surface.get_height())
								if surface is not None:
									s_width = surface.get_width()
									s_height = surface.get_height()
									if xpos == 'CENTER':
										x = x-width/2.0
									elif xpos == 'RIGHT':
										x = x-width
									if ypos == 'CENTER':
										y = y-height/2.0
									elif ypos == 'BOTTOM':
										y = y-height
									now = self.datetime + datetime.timedelta(hours=float(self.weather_data['current_conditions']['rawOffset']))
									atime = float(now.hour) + float(now.minute)/60.0
									hours = atime
									if not self.a24h and hours>12:
										hours -= 12.0
									minutes = (atime -int(atime))*60.0
									cr.translate(x,y)
									cr.scale(width/s_width,height/s_height)
									if minutesorhours == '$HOUR$':
										cr.rotate(2.0*math.pi/12.0*hours-math.pi/2.0)
									elif minutesorhours == '$MINUTES$':
										cr.rotate(2.0*math.pi/60.0*minutes-math.pi/2.0)
									cr.set_source_surface(surface)
									cr.paint()								
							elif row[0] == 'IMAGE':
								atype, fileimage, x, y, width, height, xpos, ypos = row
								if self.weather_data is not None:
									if fileimage == '$CONDITION$':
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['current_conditions']['condition_image'])								
									elif fileimage == '$MOONPHASE$':
										fileimage = os.path.join(comun.IMAGESDIR,self.weather_data['current_conditions']['moon_icon'])
									elif fileimage == '$WIND$':
										fileimage = os.path.join(comun.IMAGESDIR,self.weather_data['current_conditions']['wind_icon'])
									elif fileimage == '$CONDITION_01$' and len(self.weather_data['forecasts'])>0: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][0]['condition_image'])
									elif fileimage == '$CONDITION_02$' and len(self.weather_data['forecasts'])>1: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][1]['condition_image'])
									elif fileimage == '$CONDITION_03$' and len(self.weather_data['forecasts'])>2: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][2]['condition_image'])
									elif fileimage == '$CONDITION_04$' and len(self.weather_data['forecasts'])>3: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][3]['condition_image'])
									elif fileimage == '$CONDITION_05$' and len(self.weather_data['forecasts'])>4: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][4]['condition_image'])
									elif fileimage == '$MOONPHASE_01$' and len(self.weather_data['forecasts'])>0: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][0]['moon_phase'])
									elif fileimage == '$MOONPHASE_02$' and len(self.weather_data['forecasts'])>1: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][1]['moon_phase'])
									elif fileimage == '$MOONPHASE_03$' and len(self.weather_data['forecasts'])>2: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][2]['moon_phase'])
									elif fileimage == '$MOONPHASE_04$' and len(self.weather_data['forecasts'])>3: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][3]['moon_phase'])
									elif fileimage == '$MOONPHASE_05$' and len(self.weather_data['forecasts'])>4: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][4]['moon_phase'])
									elif fileimage == '$WIND_01$' and len(self.weather_data['forecasts'])>0: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][0]['wind_icon'])
									elif fileimage == '$WIND_02$' and len(self.weather_data['forecasts'])>1: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][1]['wind_icon'])
									elif fileimage == '$WIND_03$' and len(self.weather_data['forecasts'])>2: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][2]['wind_icon'])
									elif fileimage == '$WIND_04$' and len(self.weather_data['forecasts'])>3: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][3]['wind_icon'])
									elif fileimage == '$WIND_05$' and len(self.weather_data['forecasts'])>4: 
										fileimage = os.path.join(comun.WIMAGESDIR,self.weather_data['forecasts'][4]['wind_icon'])
									else:
										fileimage = os.path.join(maindir,fileimage)
								else:
									fileimage = os.path.join(maindir,fileimage)
								x = float(x)
								y = float(y)
								width = float(width)
								height = float(height)
								surface = get_surface_from_file(fileimage)
								if surface is not None:
									s_width = surface.get_width()
									s_height = surface.get_height()
									if xpos == 'CENTER':
										x = x-width/2.0
									elif xpos == 'RIGHT':
										x = x-width
									if ypos == 'CENTER':
										y = y-height/2.0
									elif ypos == 'BOTTOM':
										y = y-height							
									cr.translate(x,y)
									cr.scale(width/s_width,height/s_height)
									cr.set_source_surface(surface)
									cr.paint()
							elif row[0] == 'TEXT':
								atype, text, x, y, font, size, color, xpos, ypos = row
								x = float(x)
								y = float(y)
								size = int(size)
								r,g,b,a = color.split(',')
								cr.set_source_rgba(float(r),float(g),float(b),float(a))
								cr.select_font_face(font)
								cr.set_font_size(size)
								if self.parse_time:								
									now = self.datetime + datetime.timedelta(hours=float(self.weather_data['current_conditions']['rawOffset']))
									hours = now.hour
									if not self.a24h:
										if hours>12:
											hours -= 12
										if hours < 1:
											hours += 12
									hours = str(hours)
									hours = '0'*(2-len(hours))+hours
									minutes = str(now.minute)
									minutes = '0'*(2-len(minutes))+minutes									
									if text.find('$HOUR$')>-1:
										text = text.replace('$HOUR$',hours)
									if text.find('$MINUTES$')>-1:
										text = text.replace('$MINUTES$',minutes)
								if text.find('$WEEKDAY$')>-1:
									text = text.replace('$WEEKDAY$',now.strftime('%A'))							
								if text.find('$DAY$')>-1:
									text = text.replace('$DAY$',now.strftime('%d'))							
								if text.find('$MONTH$')>-1:
									text = text.replace('$MONTH$',now.strftime('%m'))							
								if text.find('$MONTHNAME$')>-1:
									text = text.replace('$MONTHNAME$',now.strftime('%B'))							
								if text.find('$YEAR$')>-1:
									text = text.replace('$YEAR$',now.strftime('%Y'))
								if text.find('$LOCATION$')>-1 and self.location is not None:
									text = text.replace('$LOCATION$',self.location)
								if self.weather_data is not None:
									if text.find('$TEMPERATURE$')>-1:
										text = text.replace('$TEMPERATURE$','{0}{1:c}'.format(self.weather_data['current_conditions']['temperature'],176))
									if text.find('$MAX_TEMPERATURE$')>-1:
										text = text.replace('$MAX_TEMPERATURE$','{0}{1:c}'.format(self.weather_data['forecasts'][0]['high'],176))
									if text.find('$MIN_TEMPERATURE$')>-1:
										text = text.replace('$MIN_TEMPERATURE$','{0}{1:c}'.format(self.weather_data['forecasts'][0]['low'],176))
									if text.find('$HUMIDITY$')>-1:
										text = text.replace('$HUMIDITY$',self.weather_data['current_conditions']['humidity'])
									if text.find('$PRESSURE$')>-1:
										text = text.replace('$PRESSURE$',self.weather_data['current_conditions']['pressure'])
									if text.find('$WIND$')>-1:
										text = text.replace('$WIND$',self.weather_data['current_conditions']['wind_condition'])
									if text.find('$CONDITION$')>-1:
										text = text.replace('$CONDITION$',self.weather_data['current_conditions']['condition_text'])
									if len(self.weather_data['forecasts'])>0:
										if text.find('$MAX_TEMPERATURE_01$')>-1:
											text = text.replace('$MAX_TEMPERATURE_01$',self.weather_data['forecasts'][0]['high'])
										if text.find('$MIN_TEMPERATURE_01$')>-1:
											text = text.replace('$MIN_TEMPERATURE_01$',self.weather_data['forecasts'][0]['low'])
										if text.find('$CONDITION_01$')>-1:
											text = text.replace('$CONDITION_01$',self.weather_data['forecasts'][0]['condition_text'])
										if text.find('$DAY_OF_WEEK_01$')>-1:
											text = text.replace('$DAY_OF_WEEK_01$',self.weather_data['forecasts'][0]['day_of_week'])
									if len(self.weather_data['forecasts'])>1:
										if text.find('$MAX_TEMPERATURE_02$')>-1:
											text = text.replace('$MAX_TEMPERATURE_02$',self.weather_data['forecasts'][1]['high'])
										if text.find('$MIN_TEMPERATURE_02$')>-1:
											text = text.replace('$MIN_TEMPERATURE_02$',self.weather_data['forecasts'][1]['low'])
										if text.find('$CONDITION_02$')>-1:
											text = text.replace('$CONDITION_02$',self.weather_data['forecasts'][1]['condition_text'])
										if text.find('$DAY_OF_WEEK_02$')>-1:
											text = text.replace('$DAY_OF_WEEK_02$',self.weather_data['forecasts'][1]['day_of_week'])
									if len(self.weather_data['forecasts'])>2:
										if text.find('$MAX_TEMPERATURE_03$')>-1:
											text = text.replace('$MAX_TEMPERATURE_03$',self.weather_data['forecasts'][2]['high'])
										if text.find('$MIN_TEMPERATURE_03$')>-1:
											text = text.replace('$MIN_TEMPERATURE_03$',self.weather_data['forecasts'][2]['low'])
										if text.find('$CONDITION_03$')>-1:
											text = text.replace('$CONDITION_03$',self.weather_data['forecasts'][2]['condition_text'])
										if text.find('$DAY_OF_WEEK_03$')>-1:
											text = text.replace('$DAY_OF_WEEK_03$',self.weather_data['forecasts'][2]['day_of_week'])
									if len(self.weather_data['forecasts'])>3:
										if text.find('$MAX_TEMPERATURE_04$')>-1:
											text = text.replace('$MAX_TEMPERATURE_04$',self.weather_data['forecasts'][3]['high'])
										if text.find('$MIN_TEMPERATURE_04$')>-1:
											text = text.replace('$MIN_TEMPERATURE_04$',self.weather_data['forecasts'][3]['low'])
										if text.find('$CONDITION_04$')>-1:
											text = text.replace('$CONDITION_04$',self.weather_data['forecasts'][3]['condition_text'])
										if text.find('$DAY_OF_WEEK_04$')>-1:
											text = text.replace('$DAY_OF_WEEK_04$',self.weather_data['forecasts'][3]['day_of_week'])
									if len(self.weather_data['forecasts'])>4:
										if text.find('$MAX_TEMPERATURE_05$')>-1:
											text = text.replace('$MAX_TEMPERATURE_05$',self.weather_data['forecasts'][4]['high'])
										if text.find('$MIN_TEMPERATURE_05$')>-1:
											text = text.replace('$MIN_TEMPERATURE_05$',self.weather_data['forecasts'][4]['low'])
										if text.find('$CONDITION_05$')>-1:
											text = text.replace('$CONDITION_05$',self.weather_data['forecasts'][4]['condition_text'])
										if text.find('$DAY_OF_WEEK_05$')>-1:
											text = text.replace('$DAY_OF_WEEK_05$',self.weather_data['forecasts'][4]['day_of_week'])
										
								x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(text)
								if xpos == 'CENTER':
									x = x-width/2.0
								elif xpos == 'RIGHT':
									x = x-width
								if ypos == 'CENTER':
									y = y+height/2.0
								elif ypos == 'TOP':
									y = y+height
								cr.move_to(x,y)
								cr.show_text(text)							
						cr.restore()
					self.surface =  mainsurface
					return
				except Exception as e:
					print('Parsing data error: %s'%e)
		self.surface = None
		
def get_surface_from_file(filename):
	if os.path.exists(filename):
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
		if pixbuf:		
			surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
			context = cairo.Context(surface)
			Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
			context.paint()
			return surface
	return None
	

if __name__ == "__main__":
	ss =Widget()
	ss.show()
	Gtk.main()
	exit(0)
