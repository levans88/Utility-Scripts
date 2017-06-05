#!/usr/bin/env python

#  Helder Fraga aka Whise (c) helderfraga@gmail.com
#  Julien Lavergne (c) 2009 julien.lavergne@gmail.com
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

#-------------------------------------------
# NOTES
#-------------------------------------------
#
# Modified by Lenny Evans - lenny.evans3@gmail.com
# 	- Double-click on icons instead of single-click
#
# TODO:
# 	- Use system double-click sensitivity instead of defaulting to 400ms - LE
#

import time
import screenlets
from screenlets import Tooltip
from screenlets.options import StringOption, FontOption, BoolOption, IntOption, ColorOption, DirectoryOption, ListOption
from screenlets.utils import xdg_open,get_filename_on_drop
#from screenlets import DefaultMenuItem 
import cairo
import gtk
import pango
import urllib

try:
	import gnomedesktop
	GNOMEDESK = True
except:
	GNOMEDESK = False

try:
	import gnome.ui
	GNOMEUI = True
except:
	GNOMEUI = False
	
import os
import gobject
import gc

try:
	import gio
	
except:
	screenlets.show_message(None,_('You don\'t have GIO python bindings installed. \nYou need to install python-gobject >= 2.15 .'))
	sys.exit()


#use gettext for translation
import gettext

_ = screenlets.utils.get_translator(__file__)

def tdoc(obj):
	obj.__doc__ = _(obj.__doc__)
	return obj

@tdoc
class FolderViewScreenlet(screenlets.Screenlet):
	"""Display the content of a folder."""
	# default meta-info for Screenlets
	__name__ = 'FolderView'
	__version__ = '0.9.92'
	__author__ = 'Helder Fraga aka Whise'
	__desc__ = __doc__



	icon_size = 48
	rows = 5
	columns = 1
	pericons = 5
	frame_color = 0.1,0.1,0.1,0.5
	frame_color_selected = 0,0,0,0.5
	color_text_selected =(0, 0, 0, 0.6)
	color_text = 1,1,1,1
	color_title = 1,1,1,1
	banner_size = 0
	folder_path = os.path.join(os.path.expanduser("~"))
	folder_path_current = os.path.join(os.path.expanduser("~"))
	font = 'Sans 8'
	title_font = 'Sans 12'
	border_size = 1
	border_color=(1,1,1,0.3)
	shadow_size = 1
	shadow_color=(0,0,0,0.5)
	clicked = False
	rounda = 2
	roundb = 2
	sb_row = 5
	sb_column = 3
	icon_num = 0
	show_start = 0
	old_value = 0
	show_end = 16
	files_list_show = []
	fullscroll = 1
	full_path = False
	# internals
	__timeout = None
	exclude = ['Thumbs.db','desktop.ini','__MACOSX','._.DS_Store']
	expand_choices = 'horizontal','vertical'
	expand2 = _('Use a scrollbar')
	expand2_choices = _('Expand/Adjust to icons'),_('Use a scrollbar')
	expand = 'horizontal'
	showtip = False
	showthumb = True
	show_title = False
	files_list_show_reversed = []
	name = ''
	timer1 = None
	image_filename 	= ""
	show_back = False
	cp = ''
	showbyex = ''
	__drag_icon = None
	__drag_icon_mask = None
	__drag_sel = None
	__update_interval = 1 # every second
	click_count = 0
	click_time = 0
	show_line = 0
	use_desktop_file_name_field = 1

	# constructor
	def __init__(self, **keyword_args):
		screenlets.Screenlet.__init__(self, width=200, height=200,ask_on_option_override=False, drag_drop=True,resize_on_scroll= False, **keyword_args)
		#self.x = self.width
		#self.y = self.height
		# set theme
		self.apps_list = []
		self.__buffer_back = None
		self.__buffer_fore = None
		self.current_file = None
		self.theme_name = "default"
		#Init the theme to search for icons and default style
		self.icontheme = gtk.icon_theme_get_default()
		self.icontheme.connect("changed", self.icons_changed)
		#Default Options
		self.icon_size = 48
		self.columns = 2
		self.files_list_show = []
		self.timer = None

		
		self.folder_path_current = self.folder_path
		self.font = "Sans 8"
		self.title_font = "Sans 12"
		self.border_size_selected = 2

		self.cursor_position = [-1,-1]
		self.last_selected_element = [999,999]

		self.auto_update = False

		# add default menu items
		#self.add_menuitem("up_folder", _("Up"))


		#add custom option
		self.add_options_group(_('Folder'), _('Settings for the folder ...'))



		self.add_option(StringOption(_('Folder'), 'expand2', self.expand2,_('Expand Mode'), '',choices = self.expand2_choices))

		self.add_option(IntOption(_('Folder'),'banner_size',
						self.banner_size, _('Size of the Banner'),'', min=0, max=64536
						,hidden=True))

		self.add_option(DirectoryOption(_('Folder'), 'folder_path',
					self.folder_path, _('Folder path'), _('Default path to the folder'),
					))

		self.add_option(ListOption(_('Folder'), 'exclude', self.exclude,_('Exclude list'), '',))

		self.add_option(BoolOption(_('Folder'),'showtip', self.showtip, _('Display Tooltip'), '',))

		self.add_option(BoolOption(_('Folder'),'showthumb', self.showthumb, _('Show Thumbnails if available'), '',))

		self.add_option(StringOption(_('Folder'),'showbyex', self.showbyex, _('Show only by extension'), '',))

		self.add_option(BoolOption(_('Folder'),'show_title', self.show_title, _('Show Path in Title'), '',))

		self.add_option(BoolOption(_('Folder'),'full_path', self.full_path, _('Display full path name in banner'), '',))

		self.add_option(BoolOption(_('Folder'),'show_line', self.show_line, _('Underline Title'), '',))

		self.add_option(BoolOption(_('Folder'),'use_desktop_file_name_field', self.use_desktop_file_name_field, _('Use name field from .desktop file'), '',))

		self.add_options_group(_('Look'), _('Settings colors and fonts'))

		self.add_option(IntOption(_('Look'),'icon_size',
						self.icon_size, _('Icons Size'),'', min=0, max=64536
						))

		self.add_option(FontOption(_('Look'),'title_font', 
						self.title_font, _('Title Font'), '',))

		self.add_option(ColorOption(_('Look'),'color_title', 
						self.color_title, _('Title color'), '',))

		self.add_option(FontOption(_('Look'),'font', 
						self.font, _('Text Font'), '',))

		self.add_option(ColorOption(_('Look'),'color_text', 
						self.color_text, _('Text color'), '',))

		self.add_option(ColorOption(_('Look'),'frame_color', 
						self.frame_color, _('Background Color'), _('Frame color'),))

		self.add_option(IntOption(_('Look'),'rounda',
						self.rounda, _('Rounded Corner Angle'),'',min=0, max=20
						))
		self.add_option(ColorOption(_('Look'),'border_color', 
						self.border_color, _('Border color'), _('Color of the border')))

		self.add_option(IntOption(_('Look'),'border_size',
						self.border_size, _('Border Size'),'',min=0, max=4
						))
		self.add_option(ColorOption(_('Look'),'shadow_color', 
						self.shadow_color, _('Shadow Color'), _('Color of the shadow')))
		self.add_option(IntOption(_('Look'),'shadow_size',
						self.shadow_size, _('Shadow Size'),'',min=0, max=4
						))

		self.add_option(ColorOption(_('Look'),'frame_color_selected', 
						self.frame_color_selected, _('Selection color'), _('Frame color for selected background')))

		self.add_option(IntOption(_('Look'),'roundb',
						self.roundb, _('Selected Rounded Angle'),'',min=0, max=20
						))
		self.add_option(IntOption(_('Look'),'border_size_selected',
						self.border_size_selected, _('Selection Border Size'),'',min=0, max=4
						))
		self.add_option(ColorOption(_('Look'),'color_text_selected', 
						self.color_text_selected, _('Selection Text Color'), _('Color of the text when selected'),hidden=True))


		self.add_options_group(_('Background'), _('Settings colors and fonts'))

		self.add_option(BoolOption(_('Background'),'show_back', self.show_back, _('Show background image'), '',))
		self.add_option(StringOption(_('Background'), 'image_filename', self.image_filename, _('Background image'), _('Filename of image to be shown in background'))) 
		self.add_options_group(_('With Scrollbar'), _('Settings with scrollbars activated'))

		self.add_options_group(_('Without Scrollbar'), _('Settings without scrollbars activated'))

		self.add_option(IntOption(_('With Scrollbar'),'sb_row',
						self.sb_row, _('Icons per Column'),_('Maximum number of icons in a row'), min=1, max=64536
						))

		self.add_option(IntOption(_('With Scrollbar'),'sb_column',
						self.sb_column, _('Icons per Row'),_('Maximum number of icons in a column'), min=1, max=64536
						))

		self.add_option(StringOption(_('Without Scrollbar'), 'expand', self.expand,_('Expand Direction'), '',choices = self.expand_choices))

		self.add_option(IntOption(_('Without Scrollbar'),'pericons',
						self.pericons, _('Icons per Direction'),_('Number of icons in a row or columns, depends on horizontal/vertical'), min=1, max=64536
						))


		self.scrollbarbox = gtk.Fixed()
		self.adjust = gtk.Adjustment(0.0,0.0, 1.0, 1.0, 1.0, 1.0)
		self.scrollbar =  gtk.VScrollbar(self.adjust)
		self.window.add(self.scrollbarbox)
		self.window.connect("motion-notify-event",self.motion_notify_event)
		self.adjust.connect("value-changed", self.scroll_value_changed)
		self.scrollbar.connect("expose-event", self.sb_expose)
		self.window.connect("window_state_event",self.state_event)
		self.window.connect("drag-data-get", self.drag_data_get)
		targets = [('text/uri-list', 0, 0)]
		self.window.drag_source_set(gtk.gdk.BUTTON1_MASK,targets,gtk.gdk.ACTION_MOVE)
		# set as text-source
		self.window.drag_source_add_text_targets()
		#self.window.set_no_show_all(True)
		self.clipboard = gtk.Clipboard(selection='CLIPBOARD')
		#self.scrollbar.set_no_show_all(True)
		gc.collect()

	def state_event(self,widget,event):
		#if gtk.gdk.WINDOW_STATE_ABOVE in widget.window.get_state():
		pass#print widget.window.get_state()

	def get_selected_element(self, drag_direction=None):
		if self.expand2 == _('Use a scrollbar'):
			self.list =  self.files_list_show[self.show_start:self.show_end]
		else:
			self.list =  self.files_list_show

		if self.cursor_position != [-1,-1]:
			self.last_selected_element = self.cursor_position

		for elem in self.list:
			if drag_direction == "in" or drag_direction == None:
				if elem[2] == self.cursor_position:
					return elem
			elif drag_direction == "out":
				if elem[2] == self.last_selected_element:
					return elem
	
#-------------------------------------------
# CLIPBOARD METHODS
#-------------------------------------------

	def clipboardGet(self, clipboard, selection_data, info,data):
		#selection_data.set( "text/uri-list", 8, tempImgUri )
		
		selection_data.set('x-special/gnome-copied-files', 8,'copy\n' + self.cp)
		#selection_data.set('text/uri-list', 8,self.cp)



	def _clipboardClearFuncCb( self, clipboard, tempImgPath):
		pass

#-------------------------------------------
# DRAG N DROP METHODS
#-------------------------------------------

	def create_drag_icon (self, drag_direction):
		"""Create drag_icon and drag_mask for drag-operation."""
		elem = self.get_selected_element(drag_direction)
		
		if elem:
			self.__drag_icon = gtk.gdk.pixbuf_new_from_file_at_size(self.generate_icon_names(elem),int(self.icon_size*self.scale), int(self.icon_size*self.scale))
			self.__drag_sel = elem
	
	def drag_end(self, widget, drag_context):
		# call user-defined handler
		self.__drag_icon = None
		self.on_mouse_leave(1)
	
	def drag_begin(self, widget, drag_context):
		if self.cursor_position != [-1,-1]:
			drag_direction = "in"
			self.create_drag_icon(drag_direction)
			if self.__drag_icon:
				self.window.drag_source_set_icon_pixbuf(self.__drag_icon)

		if self.cursor_position == [-1,-1]:
			drag_direction = "out"
			self.create_drag_icon(drag_direction)
			if self.__drag_icon:
				self.window.drag_source_set_icon_pixbuf(self.__drag_icon)


	def drag_data_get (self, widget, drag_context, selection_data, info, timestamp):
		uri_list = 'file://'+ (self.__drag_sel[0].get_path())
		selection_data.set(selection_data.target, 8,uri_list)

	def on_drop (self, x, y, sel_data, timestamp):
		filename = ''
		filename = get_filename_on_drop(sel_data)
		for f in filename:
			if f != '':
				os.system('mv ' + f + ' ' + chr(34) + self.folder_path_current + chr(34) + ' &')

#-------------------------------------------
# TOOLTIPS METHODS
#-------------------------------------------

	def hide_tip(self):
		if self.showtip:
			self.hide_tooltip()
			if self.timer:
				gobject.source_remove(self.timer)
				self.timer = None


	def show_tip(self):
		if self.showtip:
			self.timer = gobject.timeout_add(2000, self.show_tips)


	def show_tips(self):
		if self.clicked: return
		elem = self.get_selected_element()	
		if elem:				
			self.path = str(elem[0].get_path())
			if os.path.isfile(elem[0].get_path()):
				self.txt = str(elem[1].get_name()) + '\n\n'+ _('Location: ') + self.path+ '\n' + _('Size: ') + str(float(elem[1].get_size())/(1024*1024))[0:4]+ ' Mbytes\n' + _('Type: ') + str(elem[1].get_content_type())
			else:
				self.txt = str(elem[1].get_name()) + '\n\n'+ _('Location: ') + self.path.replace(str(elem[1].get_name()),'')+ _('\nContent: \n') 
				for z in os.listdir(self.path)[0:10]:
					self.txt = self.txt + z + '\n'
				self.txt = self.txt + '...'
			self.show_tooltip(str(self.txt),self.x+self.mousex+10,self.y+self.mousey+10)
			if self.timer:
				gobject.source_remove(self.timer)
				self.timer = None
		

	def show_tooltip (self,text,tooltipx,tooltipy):
	        """Show tooltip window at current mouse position."""
		if self.tooltip == None:
      			self.tooltip = Tooltip(300, 400)
			self.tooltip.window.set_opacity(0.8)		
			self.tooltip.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
			self.window.set_tooltip_window(self.tooltip.window)
       		self.tooltip.text = text
       		self.tooltip.x    = tooltipx
       		self.tooltip.y    = tooltipy
		self.tooltip.window.show()


	def hide_tooltip (self):
	        """hide tooltip window"""
		if self.tooltip != None:
			self.tooltip.hide()
			self.tooltip = None	


#-------------------------------------------
# SCROLLBARS METHODS
#-------------------------------------------

	def sb_expose(self,widget,event):
		if self.fullscroll <= 1: 
			widget.hide()


	def scroll_value_changed(self,widget):

		self.value = self.adjust.get_value()
		if len(str(self.value)) < 8:
			self.adjust.set_value(int(self.value))
			self.show_start = int(self.value * self.sb_row* self.sb_column)
			self.show_end = int(self.value * self.sb_row* self.sb_column + (self.sb_row* self.sb_column))
			if self.show_end > self.icon_num: self.show_end = self.icon_num
			
			
			self.redraw_foreground()
			self.update()
		
		else: self.adjust.set_value(0.0000000000000) #MORE ZEROS SEEMS TO WORK LOL



	def on_scroll_up (self):
		if self.expand2 == _('Use a scrollbar') and int(self.value)-1 >= 0:
			self.adjust.set_value(int(self.value)-1)

	def on_scroll_down (self):
		if self.expand2 == _('Use a scrollbar') and int(self.value)+1 < self.fullscroll :
			self.adjust.set_value(int(self.value)+1)

	def update_scrollbar(self):

		self.fullscroll = round(((self.icon_num/self.sb_row) +1) / self.sb_column)
		try:
			if self.fullscroll/((float(self.icon_num)/float(self.sb_row)) / self.sb_column) < 1:
				self.fullscroll = self.fullscroll +1
		except: self.fullscroll = 1
		self.increment = 1
		if self.fullscroll <= 1: 
			self.hide_scrollbar()

		else:
			self.adjust.set_upper(self.fullscroll)
			self.show_scrollbar()
			self.scrollbarbox.move(self.scrollbar,int((self.width-self.border_size-self.shadow_size)*self.scale)-24 , int((self.banner_size+9)*self.scale))
			self.scrollbar.set_size_request(-1,int((self.height-self.banner_size*2)*self.scale))
		self.value = self.adjust.get_value()
		if len(str(self.value)) < 8:
			self.adjust.set_value(int(self.value))
			self.show_start = int(self.value * self.sb_row* self.sb_column)
			self.show_end = int(self.value * self.sb_row* self.sb_column + (self.sb_row* self.sb_column))
			if self.show_end > self.icon_num: self.show_end = self.icon_num
	

	
	def show_scrollbar(self):
		if str(self.scrollbar.flags()).find('GTK_MAPPED') == -1:

			self.scrollbarbox.put(self.scrollbar,0,0)
			
			self.scrollbar.set_size_request(-1,int((self.height-self.banner_size*2)*self.scale))
			self.scrollbarbox.show()
			self.scrollbar.show()
			self.width = int(((self.icon_size * 2 * self.rows) + ((self.border_size+self.shadow_size)*2)+15 ) + 24/self.scale)


	def hide_scrollbar(self):

		self.scrollbar.hide()
		self.width = int(((self.icon_size * 2 * self.rows) + ((self.border_size+self.shadow_size)*2)+15 ))
		#self.width = int(self.icon_size * 2 * self.rows + (self.border_size+self.shadow_size)*2+10)
		#self.width = int((self.icon_size * 2 * self.rows) +10 + (self.border_size+self.shadow_size)*2)
		self.init_buffers()
		self.redraw_background()
		self.redraw_foreground()
		self.update()
		self.scrollbar.hide()

#-------------------------------------------
# SAVE THEME METHODS
#-------------------------------------------


	def show_edit_dialog(self):
		# create dialog
		dialog = gtk.Dialog(_("Theme name to save?"), self.window)
		dialog.resize(300, 100)
		dialog.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK, 
			gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		entrybox = gtk.Entry()
		entrybox.set_text(str(_('New theme name...')))
		dialog.vbox.add(entrybox)
		entrybox.show()	
		# run dialog
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			try:
				os.mkdir(os.environ['HOME'] + '/.screenlets/FolderView/themes/' + entrybox.get_text())
			except:
				screenlets.show_message(None,_('Theme not created'))
			f = open(os.environ['HOME'] + '/.screenlets/FolderView/themes/' + entrybox.get_text() + '/theme.conf' , 'w')
			if f:
				f.write('[Theme]' + '\n')
				f.write('name	= ' + entrybox.get_text() +'\n')
				f.write('author	= ' + os.environ['USER'] +'\n')
				f.write('versio = ' + '1.0' + '\n')
				f.write('info	= ' + 'Created automaticly' + '\n')
				f.write('[Options]' + '\n')
				f.write('shadow_color=' + str(self.shadow_color).replace('[','(').replace(']',')') + '\n')
				f.write('pericons=' + str(self.pericons) + '\n')
				f.write('height=' + str(self.height) + '\n')
				f.write('font=' +  str(self.font) + '\n')
				f.write('title_font=' + str(self.title_font) + '\n')
				f.write('frame_color=' + str(self.frame_color).replace('[','(').replace(']',')') + '\n')
				f.write('width=' + str(self.width) + '\n')
				f.write('border_color=' + str(self.border_color).replace('[','(').replace(']',')') + '\n')
				f.write('show_title=' + str(self.show_title) + '\n')
				f.write('show_line=' + str(self.show_line) + '\n')
				f.write('use_desktop_file_name_field=' + str(self.use_desktop_file_name_field) + '\n')
				f.write('expand=' + str(self.expand) +'\n')
				f.write('banner_size=' + str(self.banner_size) + '\n')

				f.write('border_size_selected=' + str(self.border_size_selected) + '\n')
				f.write('frame_color_selected=' + str(self.frame_color_selected).replace('[','(').replace(']',')') + '\n')
				f.write('shadow_size=' + str(self.shadow_size) + '\n')
				f.write('border_size=' + str(self.border_size) + '\n')

				f.write('rounda=' + str(self.rounda) + '\n')
				f.write('color_text=' + str(self.color_text).replace('[','(').replace(']',')') + '\n')
				f.write('color_title=' + str(self.color_title).replace('[','(').replace(']',')') + '\n')
				f.write('icon_size=' + str(self.icon_size) + '\n')
				f.write('full_path=' + str(self.full_path) + '\n')

				f.close()
				screenlets.show_message(None,_('Theme saved in ~/.screenlets/FolderView/themes'))
		dialog.hide()
		

#-------------------------------------------
# GET FILE LIST METHODS
#-------------------------------------------

	def populate_list(self, path):
		# Generate the list of GFile and GFileInfos
		# Used when creating a new FolderView	

		parent = gio.File(path)
		self.files_list_show = []
		self.icon_num = 0
		ldir = os.listdir(path)
		ldir.sort(key=str.upper)
		for elem in ldir:
			
			if os.path.isdir(path + '/' + elem):
				Gfile = gio.File(os.path.join(path,elem))
				tuble = [Gfile, Gfile.query_info("standard::*"), []]
				name = tuble[1].get_name()
				if not tuble[1].get_is_hidden() and not tuble[1].get_is_backup():
					if tuble not in self.files_list_show:
						if name not in self.exclude:
							if self.showbyex != '':
								if name.endswith(self.showbyex): 
									self.files_list_show.append(tuble)
									self.icon_num =  self.icon_num +1
							else:
								self.files_list_show.append(tuble)
								self.icon_num =  self.icon_num +1
				
				tuble = False
				Gfile = False
		for elem in ldir:
			
			if not os.path.isdir(path + '/' + elem):
				Gfile = gio.File(os.path.join(path,elem))
				tuble = [Gfile, Gfile.query_info("standard::*"), []]
				name = tuble[1].get_name()
				if not tuble[1].get_is_hidden() and not tuble[1].get_is_backup() and not name.lower().endswith('lnk'):
					if tuble not in self.files_list_show:
						if name not in self.exclude:
							if self.showbyex != '':
								if name.endswith(self.showbyex): 
									self.files_list_show.append(tuble)
									self.icon_num =  self.icon_num +1
							else:
								self.files_list_show.append(tuble)
								self.icon_num =  self.icon_num +1

				
				tuble = False
				Gfile = False		
		parent = False

		#list_files.sort(key=str.lower)
		if self.expand == 'horizontal':
			if self.expand2 == _('Use a scrollbar'):
				self.rows = self.sb_row #self.pericons
				self.columns = self.sb_column #int(self.icon_num)/int(self.pericons)
			else:
				self.rows = self.pericons
				self.columns = int(self.icon_num)/int(self.pericons)
				self.columns = int(round(self.columns + 0.5))
				if int((self.columns-1) * self.pericons) == self.icon_num:
					self.columns = self.columns -1	
		else:
			if self.expand2 == _('Use a scrollbar'):
				self.rows = self.sb_row #self.pericons
				self.columns = self.sb_column #int(self.icon_num)/int(self.pericons)
			else:

				self.columns = self.pericons
				self.rows = int(self.icon_num)/int(self.pericons)
				self.rows = int(round(self.rows + 0.5))
				if int((self.columns) * (self.rows-1)) == self.icon_num:
					self.rows = self.rows -1

		if self.expand2 == _('Use a scrollbar'):
			self.width = int((self.icon_size * 2 * self.rows + ((self.border_size+self.shadow_size)*2)+15 ) + 24/self.scale)
		else:
			self.width = int(((self.icon_size * 2 * self.rows) + ((self.border_size+self.shadow_size)*2)+15 ))
		self.height = int(self.icon_size * 2 * self.columns + self.banner_size + (self.border_size+self.shadow_size)*2+15)

		x = 0
		gc.collect()
	
#-------------------------------------------
# DESKTOP FILES METHODS
#-------------------------------------------

	def gnomedesk_get(self,path):
		f = open(path, "r")

		# Removed former sizehint of 2000 bytes as it was failing to read full .desktop files
		# containing many "Comment" lines (ex: mate-system-monitor > 14000 bytes). 
		tmp = f.readlines()
		
		f.close()
		ico = ''
		exe = ''
		found_name = False;
		found_exe = False;

		for line in tmp:
			if line.startswith('Icon='):
				ico = line.replace('Icon=','').replace('\n','')

			elif line.startswith('Exec='):
				if found_exe == False:
					found_exe = True;
					exe = line.replace('Exec=','').replace('\n','')

			elif line.startswith('Name='):
				if found_name == False:
					found_name = True;
					name = line.replace('Name=','').replace('\n','')			

		return ico,exe,name

	def gnomedesk_get_name(self,path):
		return self.gnomedesk_get(path)[2]

	def gnomedesk_get_icon(self,path):
		return self.gnomedesk_get(path)[0]

	def gnomedesk_get_exe(self,path):
		return self.gnomedesk_get(path)[1]

#-------------------------------------------
# FILE INFO METHODS
#-------------------------------------------

	def generate_icon_names(self, tuble):
		''' 	Generate a list of icons names from a [GFile, GFileInfo, [x,y]]
		'''

		self.info = tuble[1]
		#print gio.desktop_app_info_new_from_filename (tuble[0].get_path())
		self.Gicon = self.info.get_icon()
		self.uri = tuble[0].get_path()
		self.icon_names = self.Gicon.get_names()
      		
		if self.showthumb:
      			
			self.info = tuble[0].query_info(gio.FILE_ATTRIBUTE_THUMBNAIL_PATH, gio.FILE_QUERY_INFO_NONE)
			thumbfile = self.info.get_attribute_as_string(gio.FILE_ATTRIBUTE_THUMBNAIL_PATH)
			if thumbfile:
				path = thumbfile.replace('file://','')
				if os.path.exists(path): return path
			#if GNOMEUI:
			#	icon, isthumbnail = self.thumbnailer.CheckWorkList(tuble[0].get_uri())
			#	if not icon:
			#		self.thumbnailer.AddToWorkList(tuble[0].get_uri(), tuble[1].get_content_type())
			#	else:
			#		if isthumbnail:
			#			return icon


		#icon = (self.thumbnailer.Process(tuble[0].get_uri(), tuble[1].get_content_type())).replace('file://','')
		#return icon

		if str(self.uri).lower().endswith('.desktop'):

			if GNOMEDESK:
				self.ico = gnomedesktop.item_new_from_file(self.uri, gnomedesktop.LOAD_ONLY_IF_EXISTS).get_string(gnomedesktop.KEY_ICON)

			else:
				self.ico = self.gnomedesk_get_icon(self.uri)
			if self.ico != None:
				if os.path.isfile(self.ico):
					return self.ico
				else:
					
					self.ico = self.ico.replace('.png','').replace('.svg','').replace('.xpm','')
				self.icon = self.icontheme.lookup_icon(self.ico,self.icon_size,self.icon_size)
				if self.icon:
					return self.icon.get_filename()	
		else:
			self.iconinfo = self.icontheme.choose_icon(self.icon_names, self.icon_size,gtk.ICON_LOOKUP_USE_BUILTIN);
			if self.iconinfo:
				return self.iconinfo.get_filename()		
			for x in range(0,len(self.icon_names)-1):
				xx = len(self.icon_names)-1-x
				if self.icontheme.has_icon(self.icon_names[xx]):
					return self.icon_names[xx]
		return 'gtk-execute'
	

	def icons_changed(self, event):
		self.redraw_foreground()
		self.update()


	def generate_file_name(self, tuble):
		'''	Generate the name of a file from a (GFile, GFileInfo)
		'''
		info = tuble[1].get_name()

		if info.lower().endswith('.desktop'):
			if self.use_desktop_file_name_field == True:
				info = self.gnomedesk_get_name(tuble[0].get_path())
				#info[:info.lower().find('.desktop')]
			else:
				info = info.split(".")[0]
		return info


	def set_path_to_parent(self):
		if self.folder_path_current is not bool:
			self.folder_path_current = os.path.split(self.folder_path_current)[0]
			self.update_path()

	def monitor_path(self, path):
		''' 	Monitor the path for modified files/directory
		''' 	
		if self.current_file:
			self.current_file.disconnect_by_func(self.monitor_callback)

		self.current_file = gio.File(self.folder_path_current).monitor_directory()
		self.current_file.connect("changed", self.monitor_callback)
		

	def monitor_callback(self, monitor, Gfile, event, data=None):
		try:
			tuble = [Gfile, Gfile.query_info("standard::*"), []]
		except:
			self.update_path()
			#self.populate_list(self.folder_path_current)
			if self.expand2 == _('Use a scrollbar'):
				self.update_scrollbar()	
			self.init_buffers()
			self.redraw_background()
			self.redraw_foreground()
			self.update()
			if self.expand2 == _('Use a scrollbar'):
				self.update_scrollbar()	

			return True
		if not tuble[1].get_is_hidden() and not tuble[1].get_is_backup():
			self.update_path()
			#self.populate_list(self.folder_path_current)
			if self.expand2 == _('Use a scrollbar'):
				self.update_scrollbar()	
			self.init_buffers()
			self.redraw_background()
			self.redraw_foreground()
			self.update()
			if self.expand2 == _('Use a scrollbar'):
				self.update_scrollbar()	

		#self.show_notification("Changes !")
		return True


	def update_path_from_settings(self):
		self.folder_path_current = self.folder_path
		self.monitor = self.monitor_path(self.folder_path_current)
		self.update_path()
		self.init_buffers()
		self.redraw_background()
		self.redraw_foreground()


	def update_path(self):
		''' Update path from settings
		'''
		
		if self.folder_path_current is not bool:
			try:
				self.populate_list(self.folder_path_current)
			except:
				self.populate_list(os.path.join(os.path.expanduser("~")))
			self.monitor = self.monitor_path(self.folder_path_current)		
			
	
		self.update()
		gc.collect()


#-------------------------------------------
# MOUSE CLICKS METHODS
#-------------------------------------------

	def click_callback(self):
		# Callback when click
		elem = self.get_selected_element()
		if elem:
			if str(elem[0].get_path()).lower().endswith('.desktop'):
				uri = elem[0].get_path()
				if GNOMEDESK:
					item = gnomedesktop.item_new_from_file(uri, gnomedesktop.LOAD_ONLY_IF_EXISTS)
					run = item.get_string(gnomedesktop.KEY_EXEC)
				else:
					run = self.gnomedesk_get_exe(uri)
				os.system(run + ' &')
			else:
				xdg_open(chr(34) + elem[0].get_path() + chr(34))
			return



	def right_click_callback(self):
		self.menu = gtk.Menu()
		elem = self.get_selected_element()
		if elem:
			apps = gio.app_info_get_all_for_type(elem[1].get_content_type())
			self.apps_list = []
			self.apps_execs =  {}
			for app in apps:
				self.apps_list.append(app.get_name())
				self.apps_execs[app.get_name()] = app.get_executable() + ' ' + '"' +elem[0].get_path() + '"'
			
			self.add_submenuitem(_("Open with"),_("Open with"),self.apps_list)
			self.add_submenuitem(_("Actions"), _("Actions"),[_('Copy'),_('Paste'),_('Delete')])
			self.cp = "file://" +  elem[0].get_path()
		self.add_menuitem("export", _("Save Theme"))
		self.add_default_menuitems()



	def on_mouse_down(self, event):
		# Called when a buttonpress-event occured in Screenlet's window. 
		# Returning True causes the event to be not further propagated.
		self.set_current_cursor(event,self.window) 
		if event.type == gtk.gdk.BUTTON_PRESS:
			if event.button == 1:	# Left click
				if self.lock_position:	# If screenlet window is locked...
					
					# If screenlet window click count is 1, get elapsed time between now and
					# the first click. If it's less than 400 millis, increment, else reset...
					if self.click_count == 1:
						elapsed = (time.time() - self.click_time)

						if elapsed < .4:
							self.click_count += 1
							self.clicked = True
						else:
							self.click_count = 0
							self.clicked = False

					# If screenlet window click count is 0, increment and get the time...
					if self.click_count == 0:
						self.click_count += 1
						self.click_time = time.time();
				#else:
					#self.click_callback
					#self.update_scrollbar()
					#self.clicked = False
					#return False
	
			elif event.button == 3:
				self.clicked = True
				self.right_click_callback()

		elif event.type == gtk.gdk._2BUTTON_PRESS:
			elem = self.get_selected_element()

			if not elem and self.mousey < self.banner_size:
				os.system('xdg-open ' +chr(34) +self.folder_path_current + chr(34))



	def on_mouse_up(self, event):
		self.set_current_cursor(event,self.window) 
		if event.type == gtk.gdk.BUTTON_RELEASE:
			if event.button == 1:
				if self.lock_position:	# If screenlet window is locked...
					# If clicked twice, accept double-click as complete, do the callback
					# and reset status and count...
					if self.click_count == 2:
						self.click_callback()
						self.click_count = 0
						#self.update_scrollbar()
						self.clicked = False
						return False
				#else:
					#self.clicked = True

			elif event.button == 3:
				self.clicked = True
				self.right_click_callback()

		elif event.type == gtk.gdk._2BUTTON_PRESS:
			
			elem = self.get_selected_element()
			if not elem:
				os.system('xdg-open ' +chr(34) +self.folder_path_current + chr(34))
				


#-------------------------------------------
# OTHER SCREENLETS METHODS
#-------------------------------------------


	def on_init(self):
		#self.add_menuitem('copy', _('Copy'))
		#self.add_menuitem('paste', _('Paste'))
		#self.add_menuitem('delete', _('Delete'))
		#self.add_menuitem('rename', _('Rename'))
		#if GNOMEUI and self.showthumb:
		#	self.thumbnailer = thumbnailengine(self.icon_size)
		#	self.thumbnailer.connect("worklist-finished", lambda m: self.icons_changed(0))
		#self.window.window.set_keep_above(0)

		# Timeout formerly 1000, not seeing any consequences but leaving a note in case - LE
		gobject.timeout_add(0, self.finish)


	def finish(self):
		self.window.set_keep_below(1)
		self.add_menuitem("export", _("Save Theme"))
		self.add_default_menuitems()
		self.update_path_from_settings()
		if self.expand2 == _('Use a scrollbar'):
			self.update_scrollbar()
			self.scrollbar.show()
			self.value = self.adjust.get_value()
			self.redraw_background()
			self.redraw_foreground()
			self.update()
			self.scrollbar.modify_bg(gtk.STATE_NORMAL,  gtk.gdk.Color(self.frame_color[0]*65535,self.frame_color[1]*65535,self.frame_color[2]*65535,0)) # cor da barra maior
			self.scrollbar.modify_bg(gtk.STATE_SELECTED,  gtk.gdk.Color(self.color_title[0]*65535,self.color_title[1]*65535,self.color_title[2]*65535,0)) # cor da barra menor
			self.scrollbar.modify_bg(gtk.STATE_PRELIGHT,  gtk.gdk.Color(self.color_title[0]*65535,self.color_title[1]*65535,self.color_title[2]*65535,0)) # cor da seta a funcionar
			self.scrollbar.modify_bg(gtk.STATE_ACTIVE,  gtk.gdk.Color(self.color_title[0]*65535,self.color_title[1]*65535,self.color_title[2]*65535,0)) # cor da seta a funcionar
			self.scrollbar.modify_bg(gtk.STATE_INSENSITIVE,  gtk.gdk.Color(self.frame_color[0]*65535,self.frame_color[1]*65535,self.frame_color[2]*65535,0)) # cor da seta a nao funcionar
			self.scrollbar.modify_fg(gtk.STATE_NORMAL,  gtk.gdk.Color(self.color_title[0]*65535,self.color_title[1]*65535,self.color_title[2]*65535,0)) 
		
		# Automatically redraw after init (remove requirement for mouse over to finish drawing)
		self.redraw_canvas()
		
		return False
		


	def draw_text(self, ctx, text, x, y,  font, size, width, allignment=pango.ALIGN_LEFT,alignment=None,justify = False,weight = 0, ellipsize = pango.ELLIPSIZE_NONE,title=False):
		"""Draws text"""
		ctx.save()
		ctx.translate(x+1, y+1)
		if self.p_layout == None :
	
			self.p_layout = ctx.create_layout()
		else:
			
			ctx.update_layout(self.p_layout)
		if self.p_fdesc == None:self.p_fdesc = pango.FontDescription()
		else: pass
		self.p_fdesc.set_family(pango.FontDescription(font).get_family())
		self.p_fdesc.set_size(size * pango.SCALE)
		self.p_fdesc.set_weight(weight)
		self.p_fdesc.set_style(pango.FontDescription(font).get_style())
		self.p_layout.set_font_description(pango.FontDescription(font))
		#self.p_layout.set_font_description(self.font)
		self.p_layout.set_width(width * pango.SCALE)
		self.p_layout.set_alignment(allignment)
		if alignment != None:self.p_layout.set_alignment(alignment)
		self.p_layout.set_justify(justify)
		self.p_layout.set_wrap(pango.WRAP_WORD_CHAR)
		#self.p_layout.set_ellipsize(ellipsize)
		#self.p_layout.set_height(20)#doesnt work in pygtk yet, check latter
		self.p_layout.set_ellipsize(pango.ELLIPSIZE_NONE)

		
		if title == True:
	
			if self.banner_size != self.p_layout.get_size()[1]/pango.SCALE + 10 :
				self.banner_size = self.p_layout.get_size()[1]/pango.SCALE + 10 

		
		#print self.p_layout.get_text(),self.p_layout.get_size()[0]/pango.SCALE
		self.p_layout.set_markup(text)
		#Workarround for non set_height
			
		if self.p_layout.get_line(2):
			while True: 
				if self.p_layout.get_line(2):
					text = text[:-1]
					self.p_layout.set_markup(text)
				else:
					text = text[:-3] + '...'
					self.p_layout.set_markup(text)
					break
		#print self.p_layout.get_pixel_size()[1]*self.scale , ((self.icon_size * 1.8)-(self.icon_size * 1.2+1))*self.scale
		if self.p_layout.get_pixel_size()[1]*self.scale > ((self.icon_size * 1.8)-(self.icon_size * 1.2+1))*self.scale:
			self.p_layout.set_ellipsize(ellipsize)

		ctx.set_source_rgba(1-self.color_text[0],1-self.color_text[1],1-self.color_text[2],0.5)
		ctx.show_layout(self.p_layout)
		try:
			ctx.set_source_rgba(*self.color_text)
		
			ctx.translate(-1, -1)
			ctx.show_layout(self.p_layout)
			ctx.restore()
		except:pass



	def __setattr__(self, name, value):
		# call Screenlet.__setattr__ in baseclass (ESSENTIAL!!!!)
		if (name == 'folder_path' and value == False): 
			pass
		elif (name == 'banner_size' and value == self.banner_size): 
			pass
		else:
			screenlets.Screenlet.__setattr__(self, name, value)

		if self.has_started:

			if name in  ['folder_path','expand','pericons','showbyex','banner_size','sb_row','sb_column','show_title','show_line','showbyex','use_desktop_file_name_field']:
				self.update_path_from_settings()
				if self.expand2 == _('Use a scrollbar'):
					self.update_scrollbar()	

			if name in ['border_color','rounda','image_filename','show_back', 'shadow_color','frame_color','title_font','color_title']:
				self.redraw_background()
				self.update()

			if name in ['icon_size','color_text','font']:
				self.redraw_foreground()
				self.update()

			if name in ['roundb','frame_color_selected','border_size_selected','shadow_size','border_size']:
				self.redraw_background()
				self.redraw_foreground()
				self.update()

			if name == 'expand2':
				if not value == _('Use a scrollbar'):
					self.hide_scrollbar()
				
				self.update_path_from_settings()
				self.init_buffers()
				self.redraw_background()
				self.redraw_foreground()
				self.update()
				if value == _('Use a scrollbar'):
					self.update_scrollbar()	


		if name == 'show_title' and value == False: self.banner_size = 0



	def get_style_color(self):
		''' 	Get default color for background
			#TODO Use this
		'''
		style = gtk.Style().bg[gtk.STATE_NORMAL]
		return style


	def on_menuitem_select(self, id):
		"""handle MenuItem-events in right-click menu"""
		if id == _('Copy'):
			self.clipboard.clear()
			self.clipboard.set_with_data( [('x-special/gnome-copied-files', 0, 0),('text/uri-list',0,0)],self.clipboardGet, self._clipboardClearFuncCb, self.cp)
			
		elif id == _('Delete'):
			if screenlets.show_question(self,_("Delete ") + self.cp + ' ?'):os.system('rm -rf ' + chr(34) + self.cp.replace('file://','') + chr(34))
		elif id == _('Paste'):
			files = self.clipboard.wait_for_text().split('\n')
			for f in files:
				if os.path.exists(str(f).replace('file://','')):
					os.system('cp ' + chr(34) + str(f).replace('file://','') + chr(34)+ ' ' + chr(34) + self.folder_path_current+ chr(34))

		elif id=="export":
			self.show_edit_dialog()

		if id in self.apps_list:
			os.system(self.apps_execs[id]+ ' &')
		self.clicked = False
		self.on_mouse_leave(0)


	def update(self):

		self.redraw_canvas()
		
		return True # keep on running this event

	def on_mouse_enter (self, event):
		self.clicked = False
		self.redraw_canvas()
		self.show_tip()


	def on_mouse_leave (self, event):
		"""Called when the mouse leaves the Screenlet's window."""

		if not self.clicked:

			self.cursor_position = [-1,-1]
			self.redraw_canvas()
			self.hide_tip()#self.timer1 = gobject.timeout_add(2000, self.hide_tip)

	def motion_notify_event(self, widget, event):
		"""Called when the mouse moves in the Screenlet's window."""
		#if event.window == self.ww:
		before_cursor = self.cursor_position
		self.set_current_cursor(event,widget)
		if before_cursor <> self.cursor_position:
			self.hide_tip()
			self.show_tip()
			self.update()


	def set_current_cursor(self, event,widget):
		self.mousex,self.mousey = widget.get_pointer()
		self.cursor_position= [int(self.mousex / self.scale), int(self.mousey / self.scale)]
		if self.cursor_position[1] < self.banner_size:
			self.cursor_position = [-1,-1]
		else:
			self.cursor_position  = [int(self.cursor_position[0]-self.border_size - self.shadow_size-5) / int((self.icon_size * 2)), 
				int(self.cursor_position[1]-self.banner_size-self.border_size - self.shadow_size-5) / int( int((self.icon_size*2 )))]
			

	def get_x(self, situation):
		return situation[2][0] * self.icon_size * 2

	def get_y(self,situation):
		return situation[2][1] * self.icon_size * 2 + self.banner_size

	def init_buffers (self):
		"""(Re-)Create back-/foreground buffers"""
		if self.width >0:
			if self.expand2 == _('Use a scrollbar'):self.scrollbar.hide()
			self.__buffer_back = gtk.gdk.Pixmap(self.window.window, 
				int(self.width * self.scale), int(self.height * self.scale), -1)
			self.__buffer_fore = gtk.gdk.Pixmap(self.window.window, 
				int(self.width * self.scale), int(self.height * self.scale), -1)
			if self.expand2 == _('Use a scrollbar'):self.scrollbar.show()
		else: print _('SHIT')


	def on_load_theme (self): 
		"""A Callback to do special actions when the theme gets reloaded.
		(called AFTER loading theme and BEFORE redrawing shape/canvas)"""

		if self.has_started:
			self.init_buffers()
			self.redraw_background()
			self.redraw_foreground()		

	def on_scale (self):
		"""Called when the scale-attribute changes."""
		if self.has_started:
			self.init_buffers()
			self.redraw_foreground()
			self.redraw_background()

		if self.expand2 == _('Use a scrollbar'):
			self.width = int((self.icon_size * 2 * self.rows + ((self.border_size+self.shadow_size)*2)+15 ) + 24/self.scale)
			self.update_scrollbar()

	def redraw_background(self):
		# create context
		self.ctx_back = self.__buffer_back.cairo_create()

		# clear context
		self.clear_cairo_context(self.ctx_back)

		# compose background
		self.ctx_back.set_operator(cairo.OPERATOR_OVER)
		self.ctx_back.scale(self.scale, self.scale)
		self.ctx_back.set_source_rgba(*self.frame_color)

		# Determine title/path to show: full, truncated, or none
		if self.show_title == True:
			if self.full_path == True:
				bt = str(self.folder_path_current)
			else:
				bt = str(self.folder_path_current).split('/')[len(str(self.folder_path_current).split('/'))-1]
		else:
			bt = ""

		if self.show_back and self.image_filename != "":
			self.draw_scaled_image(self.ctx_back,0 ,0, urllib.unquote(self.image_filename.replace('file://','')), self.width-10+self.shadow_size, self.height-10+self.shadow_size)	
		else:
			self.ctx_back.set_source_rgba(*self.frame_color)
			self.draw_rectangle_advanced (self.ctx_back, 0, 0, self.width-(self.border_size + self.shadow_size)*2, self.height-(self.border_size + self.shadow_size)*2,
			rounded_angles=(self.rounda,self.rounda,self.rounda,self.rounda), fill=True, border_size=self.border_size, border_color=(self.border_color[0],self.border_color[1],self.border_color[2],self.border_color[3]),
			shadow_size=self.shadow_size, shadow_color=(self.shadow_color[0],self.shadow_color[1],self.shadow_color[2],self.shadow_color[3]))
			self.ctx_back.set_source_rgba(1-self.color_title[0],1-self.color_title[1],1-self.color_title[2],0.3)
			
			if self.show_line and bt != "":
				self.draw_line(self.ctx_back,10,self.banner_size +2 ,self.width-30,0,line_width = 1,close=False,preserve=False)
			
			self.ctx_back.set_source_rgba(*self.color_title)
			
			# If title or path string isn't empty, draw it, and optionally underline it... 
			if bt != "":
				self.draw_text(self.ctx_back, bt, 			# self.ctx_back, texte
					10, 			# x
					10,			# y
					self.title_font, 				# font
					int(self.banner_size * 0.4) , int(self.width-10) ,		# size, width
					alignment=pango.ALIGN_LEFT, ellipsize=pango.ELLIPSIZE_END,title=True)
			
				if self.show_line:
					self.draw_line(self.ctx_back,10,self.banner_size +2 ,self.width-30,0,line_width = 1,close=False,preserve=False)


	def redraw_foreground(self):
		#self.ctx_fore.translate(self.border_size + self.shadow_size,5)
		# create context from fg-buffer
		
		self.ctx_fore = self.__buffer_fore.cairo_create()
		self.clear_cairo_context(self.ctx_fore)
		self.ctx_fore.scale(self.scale, self.scale)
			#Draw the icon
		self.ctx_fore.set_source_rgba(*self.frame_color)
		self.ctx_fore.translate(self.border_size + self.shadow_size+7,self.border_size + self.shadow_size+5)
		self.x_position = self.y_position = 0
		self.list = self.files_list_show
		if self.expand2 == _('Use a scrollbar'):
			self.list =  self.files_list_show[self.show_start:self.show_end]

		for elem in self.list:
			if self.expand == 'horizontal':
				#Update the position of the file
				elem[2] = [self.x_position, self.y_position]
	
				if self.x_position == self.rows-1:# If we are at the end of the row, 
								# jump to the next row
	
					self.x_position = int(0)
					self.y_position = int(self.y_position) + 1
	
				else: 
					self.x_position = int(self.x_position) + 1
			else:
				#Update the position of the file

				elem[2] = [self.x_position, self.y_position]
				if self.y_position == self.columns -1:# If we are at the end of the row, 
								# jump to the next row
	
					self.x_position = int(self.x_position) + 1
					self.y_position = int(0)
	
				else: 
					self.y_position = int(self.y_position) + 1
			ico = self.generate_icon_names(elem)
			if ico is not None and os.path.isfile(ico):
			#if ico.lower().endswith('png') or ico.lower().endswith('svg') or ico.lower().endswith('xpm'):#xpm",
				w,h = self.get_image_size(ico)
				if int(w) != int(h):
					if int(w) != self.icon_size and int(h) != self.icon_size:
						if  (w*self.icon_size)/h > (self.icon_size * 1.8*self.scale +3):
							wi = self.icon_size * 1.8*self.scale +3-5
						else:
							wi = (w*self.icon_size)/h
						self.draw_scaled_image(self.ctx_fore, 						# self.ctx_fore
							self.get_x(elem) + (self.icon_size + (self.icon_size-wi))* 0.5 ,	# x
							self.get_y(elem) + self.icon_size  * 0.2,ico,int(wi),self.icon_size)	
				else:
					if int(w) != self.icon_size and int(h) != self.icon_size:
						self.draw_scaled_image(self.ctx_fore, 						# self.ctx_fore
							self.get_x(elem) + self.icon_size * 0.5 ,	# x
							self.get_y(elem) + self.icon_size * 0.2,ico,self.icon_size,self.icon_size)	
	
					else:
						self.draw_image(self.ctx_fore, 						# self.ctx_fore
							self.get_x(elem) + self.icon_size * 0.5 ,	# x
							self.get_y(elem) + self.icon_size * 0.2,ico)				
			else:
				try:
					self.draw_icon(self.ctx_fore, 						# self.ctx_fore
						self.get_x(elem) + self.icon_size * 0.5 ,	# x
						self.get_y(elem) + self.icon_size * 0.2,		# y
						ico, 			# icon name
						self.icon_size, self.icon_size)	
				except:
					self.draw_icon(self.ctx_fore, 						# self.ctx_fore
						self.get_x(elem) + self.icon_size * 0.5 ,	# x
						self.get_y(elem) + self.icon_size * 0.2,		# y
						gtk.STOCK_MISSING_IMAGE, 			# icon name
						self.icon_size, self.icon_size)	

			#Draw the text
			self.ctx_fore.set_source_rgba(*self.color_text)
			self.draw_text(self.ctx_fore, self.generate_file_name(elem), 		# self.ctx_fore, texte
				self.get_x(elem)+3, 			# x
				self.get_y(elem) + self.icon_size * 1.2+5,			# y
				self.font, 				# font
				int(self.icon_size * 0.18), int(self.icon_size * 2)-6 ,		# size, width
				alignment=pango.ALIGN_CENTER, ellipsize=pango.ELLIPSIZE_END)


	def on_draw(self, ctx):

		ctx.save()
		if self.__buffer_back:
			ctx.set_operator(cairo.OPERATOR_OVER)
			ctx.set_source_pixmap(self.__buffer_back, 0, 0)
			ctx.paint()


		#ctx.translate(((self.border_size + self.shadow_size)*2)*self.scale,(self.border_size + self.shadow_size+5)*self.scale)
		ctx.set_source_rgba(*self.frame_color_selected)
		
		elem = self.get_selected_element()
		if elem:
			self.draw_rectangle_advanced(ctx,			# ctx
				(self.get_x(elem)+self.border_size + self.shadow_size+5)*self.scale ,		# x
				(self.get_y(elem)+self.border_size + self.shadow_size+5)*self.scale ,		# y
				self.icon_size * 2 *self.scale , self.icon_size * 1.9 *self.scale ,		# width, height
				rounded_angles=(self.roundb,self.roundb,self.roundb,self.roundb), fill=True,
				border_size=self.border_size_selected, border_color=(self.color_text[0],self.color_text[1],self.color_text[2],0.5))

			
		if self.__buffer_fore:
			ctx.set_operator(cairo.OPERATOR_OVER)
			ctx.set_source_pixmap(self.__buffer_fore, 0, 0)
			ctx.paint()

		ctx.restore()
		gc.collect()

	def on_draw_shape(self, ctx):
		ctx.scale(self.scale, self.scale)
		ctx.set_source_rgba(0, 0, 0, 1)
 		ctx.rectangle(0, 0, self.width, self.height)
		ctx.fill()

class thumbnailengine(gobject.GObject):
	__gsignals__ = {"thumbnail-finished" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [gobject.TYPE_STRING]),
					"worklist-finished" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

	def __init__(self,icon_size):
		gobject.GObject.__init__(self)
		self.icon_size = icon_size
		self.thumbFactory = gnome.ui.ThumbnailFactory(gnome.ui.THUMBNAIL_SIZE_LARGE)
		self.WorkList = []
		self.DoneList = []
		self.stockimage = gtk.STOCK_MISSING_IMAGE 
		self.Timer = None
		
	def lookup(self, uri):
		icon = self.thumbFactory.lookup(uri,0)
		if not icon:
			icon = gtk.STOCK_MISSING_IMAGE
		return icon
			
	def Process(self,uri,mime_type):
		# Check availability of thumbnail and create one if necessary
		if self.thumbFactory.can_thumbnail(uri,mime_type, 0):
			# Check for existing thumbnail
			thumbnail = self.thumbFactory.lookup(uri, 0)
			if not thumbnail:
				thumbnail = self.thumbFactory.generate_thumbnail(uri, mime_type)
				if thumbnail != None:
					self.thumbFactory.save_thumbnail(thumbnail, uri, 0)
			icon = uri
		else:
			icon = gtk.STOCK_MISSING_IMAGE
		return icon
		
	def ProcessWorkList(self):
		processitem = self.WorkList.pop(0)
		image = self.Process(*processitem)
		if isinstance(image, str):
			if image.startswith("file://"):
				image = self.lookup(image)
				isthumbnail = True
			else:
				isthumbnail = False
		self.DoneList.append([processitem[0], image, isthumbnail])
		self.emit("thumbnail-finished", processitem[0])
		if self.WorkList == []:
			self.emit("worklist-finished")
			self.Timer = None
			return False
		else:
			return True	
	
				
	def CheckWorkList(self,uri):
		for item in self.DoneList:
			if item[0] == uri:
				return item[1], item[2]
		return None, False

	def AddToWorkList(self, uri, mime_type):
		if self.WorkList.count([uri, mime_type]):
			return
		self.WorkList.append([uri,mime_type])
		if not self.Timer:
			self.Timer = gobject.timeout_add(50, self.ProcessWorkList)




# If the program is run directly or passed as an argument to the python
# interpreter then create a Screenlet instance and show it
if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(FolderViewScreenlet)
