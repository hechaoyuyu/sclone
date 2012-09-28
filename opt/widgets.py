# -*- coding:utf-8 -*-
__author__="hechao"
__date__ ="$2012-7-3 10:13:19$"

import gtk
import gettext
gettext.bindtextdomain('startclone', './po')
gettext.textdomain('startclone')
def _(s):
    return gettext.gettext(s)


class BaseFunc:
    '''all fucntion'''
    def define_align(self, widget, xa=0.0, ya=0.0, xc=0.0, yc=0.0):
        # gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
        align = gtk.Alignment(xa, ya, xc, yc)
        align.add(widget)
        return align

    def draw_button(self, n_bg, h_bg, p_bg, i_bg=None):
        n_pixbuf, h_pixbuf, p_pixbuf = self.set_pixbuf(n_bg, h_bg, p_bg)
        button = gtk.Button()
        button.set_size_request(n_pixbuf.get_width(), n_pixbuf.get_height())
        i_pixbuf = None
        if i_bg:
            i_pixbuf = gtk.gdk.pixbuf_new_from_file(i_bg)

	button.connect("expose_event", self.expose_button, n_pixbuf, h_pixbuf, p_pixbuf, i_pixbuf)
        return button

    def set_pixbuf(self, n, h, p):
        n_pixbuf = gtk.gdk.pixbuf_new_from_file(n)
        h_pixbuf = gtk.gdk.pixbuf_new_from_file(h)
        p_pixbuf = gtk.gdk.pixbuf_new_from_file(p)
        return n_pixbuf, h_pixbuf, p_pixbuf

    def expose_button(self, widget, event, n_pixbuf, h_pixbuf, p_pixbuf, pixbuf = None):
        if widget.state == gtk.STATE_NORMAL:
            pixbuf = n_pixbuf
	elif widget.state == gtk.STATE_PRELIGHT:
            pixbuf = h_pixbuf
	elif widget.state == gtk.STATE_ACTIVE:
	    pixbuf = p_pixbuf

	cr = widget.window.cairo_create()
	x, y = widget.allocation.x, widget.allocation.y
	if pixbuf != None:
	    cr.set_source_pixbuf(pixbuf, x, y)
	    cr.paint()

        if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)

	return True

    def show_dialog(self, message, title='startclone'):
	md = gtk.MessageDialog(None, type=gtk.MESSAGE_QUESTION,
			buttons=gtk.BUTTONS_YES_NO)
        md.set_keep_above(True)
	md.set_title(title)
	md.set_markup(message)
	response = md.run()
	md.destroy()
        
	if response == gtk.RESPONSE_YES:
		return True
	return False

