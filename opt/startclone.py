#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__="hechao"
__date__ ="$2012-7-2 17:13:31$"

import gtk
import os
import re
import time
from threading import Thread
from subprocess import Popen, PIPE
import gettext
gettext.bindtextdomain('startclone', './po')
gettext.textdomain('startclone')
def _(s):
    return gettext.gettext(s)

from widgets import *
from syscall import *

class StartClone(BaseFunc):
    def __init__(self):
        gtk.gdk.threads_init()

        #gtk.rc_parse("res/gtkrc")

        window = InitWindow()
        mainbox = gtk.VBox()
        self.framebox = gtk.VBox()

        # loge
        logobox = LogoBox()
        mainbox.pack_start(logobox, False)

        # 主页
        self.mainpage = MainPage(self)
        # 备份
        self.clonepage = ClonePage(self)
        # 还原
        self.restorepage = RestorePage(self)

        # 添加首页
        self.framebox.pack_start(self.mainpage, False)
        mainbox.pack_start(self.framebox, False)

        window.add(mainbox)
        window.show_all()
        gtk.main()


class InitWindow(gtk.Window):
    '''init'''
    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title(_("系统备份/还原"))
        gtk.window_set_default_icon_from_file("res/icon.png")
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_border_width(2)
	#self.set_decorated(False)
	self.set_resizable(False)

        #pixbuf = gtk.gdk.pixbuf_new_from_file("res/back.png")
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#8795a0"))
	self.set_size_request(800, 600)

        #self.connect("expose_event", self.expose, pixbuf)
        self.connect("destroy", self.destroy)

    def destroy(self, widget):
        gtk.widget_pop_colormap()
	gtk.main_quit()

    def expose(self, widget, event, pixbuf):
        w, h = widget.allocation.width, widget.allocation.height
        cr = widget.window.cairo_create()
	cr.set_source_pixbuf(pixbuf.scale_simple(w, h, gtk.gdk.INTERP_BILINEAR), 0, 0)
        cr.paint()
        widget.queue_draw()

        if widget.get_child() != None:
	    widget.propagate_expose(widget.get_child(), event)
        return True


class LogoBox(gtk.EventBox, BaseFunc):
    '''init'''
    def __init__(self):
        gtk.EventBox.__init__(self)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ededed"))
        '''logo'''
        logo = gtk.image_new_from_file("res/top.png")
        align = self.define_align(logo)
        align.set_padding(20, 20, 20, 0)
        self.add(align)


class MainPage(gtk.VBox, BaseFunc):
    '''init'''
    def __init__(self, base):
        gtk.VBox.__init__(self)
        self.base = base

        '''提示语'''
        self.label_des = gtk.Label()
        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("欢迎使用此U盘还原/备份系统，它能快速还原/备份您的硬盘分区！"))
        align = self.define_align(self.label_des)
        align.set_padding(20, 20, 20, 0)
        self.pack_start(align, False)

        ebox = gtk.EventBox()
        ebox.set_size_request(800, 350)
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.pack_start(ebox)

        '''功能项'''
        funcbox = gtk.HBox()
        align = self.define_align(funcbox, 0.5, 0.5)
        #align.set_padding(100, 100, 73, 0)
        ebox.add(align)

        # 备份入口
        self.clone_button = self.draw_button("res/clone_n.png", "res/clone_h.png", "res/clone_p.png")
        self.clone_button.connect("clicked", self.clone_click)
        self.clone_button.connect("enter-notify-event", self.enter, \
        _("此备份功能支持备份Linux/Window/MacOS系统的硬盘分区，压缩方式支持pxz(多线程版xz)、gzip、lzma。"))
	self.clone_button.connect("leave-notify-event", self.leave)
        funcbox.pack_start(self.clone_button, False, False, 30)

        # 还原入口
        self.restore_button = self.draw_button("res/restore_n.png", "res/restore_h.png", "res/restore_p.png")
        self.restore_button.connect("clicked", self.restore_click)
        self.restore_button.connect("enter-notify-event", self.enter, \
        _("此还原功能能够快速还原您的系统或硬盘数据，并且能还原到不同的存储设备上。"))
	self.restore_button.connect("leave-notify-event", self.leave)
        funcbox.pack_start(self.restore_button, False, False, 30)

        # 关机/重启
        powerbox = self.power_halt()
        self.pack_start(powerbox, False)

        self.show_all()

    def enter(self, widget, event, text):
        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" % text)

    def leave(self, widget, event):
        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("欢迎使用此U盘还原/备份系统，它能快速还原/备份您的硬盘分区！"))

    def clone_click(self, widget):
        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        self.base.framebox.pack_start(self.base.clonepage, False)

    def restore_click(self, widget):
        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        self.base.framebox.pack_start(self.base.restorepage, False)

    def power_halt(self):
        ebox = gtk.EventBox()
        ebox.set_size_request(-1, 80)
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#8795a0"))

        hbox = gtk.HBox()
        # 关机
        self.halt_button = self.draw_button("res/halt_n.png", "res/halt_h.png", "res/halt_p.png")
        self.halt_button.connect("clicked", self.on_click, "poweroff", _("您确定要关闭计算机吗？"))
        hbox.pack_end(self.halt_button, False, False, 10)

        #重启
        self.reboot_button = self.draw_button("res/reboot_n.png", "res/reboot_h.png", "res/reboot_p.png")
        self.reboot_button.connect("clicked", self.on_click, "reboot", _("您确定要重启计算机吗？"))
        hbox.pack_end(self.reboot_button, False)

        align = self.define_align(hbox, 1, 0.5)
        ebox.add(align)
        return ebox


    def on_click(self, widget, cmd, text):
        ret = self.show_dialog(text)
        if ret:
            os.system(cmd)


class ClonePage(gtk.VBox, BaseFunc):
    '''init'''
    def __init__(self, base):
        gtk.VBox.__init__(self)
        self.base = base

        '''提示'''
        self.label_des = gtk.Label()
        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("准备备份您的分区..."))
        align = self.define_align(self.label_des)
        align.set_padding(20, 20, 20, 0)
        self.pack_start(align, False)

        self.ebox = gtk.EventBox()
        self.ebox.set_size_request(800, 350)
        self.ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.pack_start(self.ebox)

        #partbox = gtk.VBox(False, 8)
        table = gtk.Table(4, 2)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        self.onepad = self.define_align(table, 0.5, 0.5)
        self.ebox.add(self.onepad)

        box_bar = gtk.VBox()
        #进度条
        self.progressbar = gtk.ProgressBar()
	self.progressbar.set_size_request(500, 30)
        box_bar.pack_start(self.progressbar)
        #进度条下的描述
        self.label_bar = gtk.Label()
        box_bar.pack_start(self.label_bar)
        self.twopad = self.define_align(box_bar, 0.5, 0.5)
        #self.ebox.add(self.align_bar)

        self.part_dict = get_parted()
        self.save_part = []
       
        # 目标分区
        self.combo_target = gtk.combo_box_new_text()
        self.target_add_row(table, 0, _("备份分区"))
        self.combo_target.set_active(0)
        self.combo_target.connect("changed", self.on_target_change)
        '''
        self.combo_target = gtk.combo_box_new_text()
        hbox = self.set_target()
        self.combo_target.set_active(0)
        partbox.pack_start(hbox)
        '''
        # 存储分区
        self.combo_save = gtk.combo_box_new_text()
        self.save_add_row(table, 1, _("保存分区"))
        self.combo_save.set_active(0)
        self.combo_save.connect("changed", self.on_save_change)

        # 压缩类型
        self.xz_dict = {0:(_("使用pigz压缩"), "pigz"), 1:(_("使用pxz压缩"), "pxz"), \
        2:(_("使用lzma压缩"), "lzma"), 3:(_("使用lzop压缩"), "lzop")}
        self.combo_xz = gtk.combo_box_new_text()
        self.xz_add_row(table, 2, _("压缩类型"))
        self.combo_xz.set_active(0)

        # 文件名
        self.entry_name = gtk.Entry()
        self.entry_name.set_text(time.strftime('%Y-%m-%d-%H', time.localtime(time.time())))
        self.name_add_row(table, 3, _("存储目录"))

        # 后退/备份
        back_box = self.back_clone()
        self.pack_start(back_box, False)

        self.show_all()

    def target_add_row(self, table, row, label_text):
        label = gtk.Label(label_text)
        label.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
        label.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" % label_text)
        table.attach(label, 0, 1, row, row + 1, 0, 0, 0, 0)

        for key in self.part_dict:
            info = _("总容量:") + self.part_dict[key][1] + " " + _("分区格式:") + self.part_dict[key][2]
            self.combo_target.append_text(self.part_dict[key][0] + "(%s)" %(info))
        table.attach(self.combo_target, 1, 2, row, row + 1, gtk.EXPAND | gtk.FILL, 0, 0, 0)

    def save_add_row(self, table, row, label_text):
        label = gtk.Label(label_text)
        label.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" % label_text)
        table.attach(label, 0, 1, row, row + 1)

        ac = self.combo_target.get_active()
        for key in self.part_dict:
            if ac == key:
                continue
            info = _("总容量:") + self.part_dict[key][1] + " " + _("分区格式:") + self.part_dict[key][2]
            self.combo_save.append_text(self.part_dict[key][0] + "(%s)" %(info))
            self.save_part.append(self.part_dict[key][0])
        table.attach(self.combo_save, 1, 2, row, row + 1)

    def xz_add_row(self, table, row, label_text):
        label = gtk.Label(label_text)
        label.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" % label_text)
        table.attach(label, 0, 1, row, row + 1)

        for key in self.xz_dict:
            self.combo_xz.append_text(self.xz_dict[key][0])
        table.attach(self.combo_xz, 1, 2, row, row + 1)

    def name_add_row(self, table, row, label_text):
        label = gtk.Label(label_text)
        label.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" % label_text)
        table.attach(label, 0, 1, row, row + 1)
        table.attach(self.entry_name, 1, 2, row, row + 1)

    def on_target_change(self, widget):
        ac = widget.get_active()
        self.combo_save.get_model().clear()
        self.save_part = []
        
        for key in self.part_dict:
            if ac == key:
                continue
            info = _("总容量:") + self.part_dict[key][1] + " " + _("分区格式:") + self.part_dict[key][2]
            self.combo_save.append_text(self.part_dict[key][0] + "(%s)" %(info))
            self.save_part.append(self.part_dict[key][0])
        self.combo_save.set_active(0)
        print self.part_dict[ac]

    def on_save_change(self, widget):
        #o = self.combo_save.get_active()
        #print self.save_part[o]
        pass

    def back_clone(self):
        ebox = gtk.EventBox()
        ebox.set_size_request(-1, 80)
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#8795a0"))

        hbox = gtk.HBox()
        # 备份
        self.clone_button = self.draw_button("res/backup_n.png", "res/backup_h.png", "res/backup_p.png", "res/backup_i.png")
        self.clone_button.connect("clicked", self.on_clone)
        hbox.pack_end(self.clone_button, False, False, 10)

        # 返回
        self.back_button = self.draw_button("res/back_n.png", "res/back_h.png", "res/back_p.png", "res/back_i.png")
        self.back_button.connect("clicked", self.on_back)
        hbox.pack_end(self.back_button, False)

        align = self.define_align(hbox, 1, 0.5)
        ebox.add(align)
        return ebox

    def on_back(self, widget):
        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        self.base.framebox.pack_start(self.base.mainpage, False)
        #....
        self.clone_button.set_sensitive(True)
        self.back_button.set_sensitive(True)
        self.progressbar.set_fraction(0)
        self.progressbar.set_text('')
        self.label_bar.set_text('')
        self.ebox.remove(self.ebox.get_child())
        self.ebox.add(self.onepad)

    def on_clone(self, widget):
        # 获取cmd信息
        cmd = self.get_clone_cmd()
        if not cmd:
            return False

        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("系统备份中，请稍候..."))

        c_thread = RunThread(cmd)
        c_thread.progress = self.progress
        c_thread.start()

        #禁用按钮
        self.clone_button.set_sensitive(False)
        self.back_button.set_sensitive(False)

        self.ebox.remove(self.ebox.get_child())
        self.ebox.add(self.twopad)
        self.show_all()

    def get_clone_cmd(self):
        i = self.combo_target.get_active()
        o = self.combo_save.get_active()
        if i < 0 or o < 0:
            print "请选择分区！"
            return False
        dir_name = self.entry_name.get_text()
        if not dir_name:
            print "请输入目录名！"
        dir_name = "".join(dir_name.split())
        i_dev = self.part_dict[i][0]
        name = i_dev.split("/")[2]
        x = self.combo_xz.get_active()
        x_comp = self.xz_dict[x][1]
        if x_comp == "pigz":
            name = name + ".img.gz"
        elif x_comp == "pxz":
            name = name + ".img.xz"
        elif x_comp == "lzma":
            name = name + ".img.lzma"
        elif x_comp == "lzop":
            name = name + ".img.lzo"

        fstype = self.part_dict[i][2]
        o_dev = self.save_part[o]
        print i, i_dev, o, o_dev
        o_path = mount_dev(o_dev)
        #创建存储目录
        os.system("mkdir -p %s" %(o_path+"/"+dir_name))
        umount_dev(i_dev)
        o_path = o_path+"/"+dir_name

        cmd = "partclone.%s -L /tmp/startclone.log -c -C -s %s -O - | %s -3 > %s/%s" \
        %(fstype, i_dev, x_comp, o_path, name)
        print cmd
        #写入设置文件
        echo_config(x_comp, name, fstype, i_dev, o_path)
        return cmd

    def progress(self, cmd):
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        while True:
            info = p.stderr.readline()
            if p.poll() != None:
                break
            tmp = re.findall("Elapsed:\s*([0-9:]*), Remaining:\s*([0-9:]*), Completed:\s*([0-9.]*)%, (.*),", info)
            if tmp:
                complete = float(tmp[0][2])/100
                txt = _("已用时间:") + tmp[0][0] + ", " + _("剩余时间:") + tmp[0][1] + ", " + _("速率:") + tmp[0][3]
                self.progressbar.set_text(tmp[0][2]+"%")
                self.progressbar.set_fraction(complete)
                self.label_bar.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" %txt)
        if p.poll() == 0:
		#备份完成
		self.progressbar.set_text(_("备份已完成！"))
	else:
		self.label_bar.set_markup("<span color='red' font_desc='11'>%s</span>" \
            %_("备份失败，请重试！"))
        self.back_button.set_sensitive(True)

class RunThread(Thread):
    def __init__(self, cmd):
        Thread.__init__(self)
        self.setDaemon(True)

        self.cmd = cmd

    def progress(self, cmd):
        pass

    def run(self):
        self.progress(self.cmd)



class RestorePage(gtk.VBox, BaseFunc):
    def __init__(self, base):
        gtk.VBox.__init__(self)
        self.base = base

        '''提示'''
        self.label_des = gtk.Label()
        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("准备还原您的分区，请指定要还原的镜像目录。"))
        align = self.define_align(self.label_des)
        align.set_padding(20, 20, 20, 0)
        self.pack_start(align, False)

        self.ebox = gtk.EventBox()
        self.ebox.set_size_request(800, 350)
        self.ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.pack_start(self.ebox)

        #选择存储目录
        vbox = gtk.VBox(False, 6)
        hbox = gtk.HBox(False, 10)
        self.entry_restore = gtk.Entry()
        self.entry_restore.set_size_request(400, 30)
        hbox.pack_start(self.entry_restore)

        #按钮
        self.button_browse = gtk.Button(_("浏览..."))
        self.button_browse.connect("clicked", self.on_open)
        hbox.pack_start(self.button_browse)
        #...
        vbox.pack_start(hbox)
        self.tip_label = gtk.Label()
        vbox.pack_start(self.tip_label)

        self.onepad = self.define_align(vbox, 0.5, 0.5)
        self.ebox.add(self.onepad)

        box_bar = gtk.VBox()
        #进度条
        self.progressbar = gtk.ProgressBar()
	self.progressbar.set_size_request(500, 30)
        box_bar.pack_start(self.progressbar)
        #进度条下的描述
        self.label_bar = gtk.Label()
        box_bar.pack_start(self.label_bar)
        self.twopad = self.define_align(box_bar, 0.5, 0.5)

        # 后退/备份
        back_box = self.back_restore()
        self.pack_start(back_box, False)

        self.show_all()

    def on_open(self, widget):
        dialog = gtk.FileChooserDialog(_("还原分区"), None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK,  gtk.RESPONSE_OK))
        res = dialog.run()
        if res == gtk.RESPONSE_OK:
            self.entry_restore.set_text(dialog.get_filename().rstrip('/') + '/')
        dialog.destroy()

    def back_restore(self):
        ebox = gtk.EventBox()
        ebox.set_size_request(-1, 80)
        ebox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#8795a0"))

        hbox = gtk.HBox()
        # 还原
        self.restore_button = self.draw_button("res/recover_n.png", "res/recover_h.png", "res/recover_p.png", "res/recover_i.png")
        self.restore_button.connect("clicked", self.on_restore)
        hbox.pack_end(self.restore_button, False, False, 10)

        # 返回
        self.back_button = self.draw_button("res/back_n.png", "res/back_h.png", "res/back_p.png", "res/back_i.png")
        self.back_button.connect("clicked", self.on_back)
        hbox.pack_end(self.back_button, False)

        align = self.define_align(hbox, 1, 0.5)
        ebox.add(align)
        return ebox

    def on_back(self, widget):
        self.base.framebox.foreach(lambda widget: self.base.framebox.remove(widget))
        self.base.framebox.pack_start(self.base.mainpage, False)
        #....
        self.restore_button.set_sensitive(True)
        self.back_button.set_sensitive(True)
        self.progressbar.set_fraction(0)
        self.progressbar.set_text('')
        self.label_bar.set_text('')
        self.ebox.remove(self.ebox.get_child())
        self.ebox.add(self.onepad)

    def on_restore(self, widget):
        # 获取路径
        o_path = self.entry_restore.get_text()
        config = o_path + "startclone.info"
        if not os.path.isfile(config):
            self.tip_label.set_markup("<span color='red' font_desc='11'>%s</span>" \
            %_("没有备份镜像，请重新选择！"))
            return False
        else:
            self.tip_label.set_markup('')

        # 获取命令
        cmd = self.get_restore_cmd(o_path, config)
        print cmd
        if not cmd:
            self.tip_label.set_markup("<span color='red' font_desc='11'>%s</span>" \
            %_("没有备份镜像，请重新选择！"))
            return False

        self.label_des.set_markup("<span foreground='#ffffff' font_desc='11'>%s</span>" \
        % _("系统还原中，请稍候..."))

        c_thread = RunThread(cmd)
        c_thread.progress = self.progress
        c_thread.start()

        #禁用按钮
        self.restore_button.set_sensitive(False)
        self.back_button.set_sensitive(False)

        self.ebox.remove(self.ebox.get_child())
        self.ebox.add(self.twopad)
        self.show_all()

    def progress(self, cmd):
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        while True:
            info = p.stderr.readline()
            if p.poll() != None:
                break
            tmp = re.findall("Elapsed:\s*([0-9:]*), Remaining:\s*([0-9:]*), Completed:\s*([0-9.]*)%, (.*),", info)
            if tmp:
                complete = float(tmp[0][2])/100
                txt = _("已用时间:") + tmp[0][0] + ", " + _("剩余时间:") + tmp[0][1] + ", " + _("速率:") + tmp[0][3]
                self.progressbar.set_text(tmp[0][2]+"%")
                self.progressbar.set_fraction(complete)
                self.label_bar.set_markup("<span foreground='#000000' font_desc='11'>%s</span>" %txt)
        if p.poll() == 0:
		#还原完成
		self.progressbar.set_text(_("还原已完成！"))
	else:
		self.label_bar.set_markup("<span color='red' font_desc='11'>%s</span>" \
            %_("还原失败，请重试！"))
        self.back_button.set_sensitive(True)

    def get_restore_cmd(self, o_path, config):
        fp = open(config, 'r')
        info = fp.readline()
        fp.close()
        if info:
            info = info.split()
            if len(info) == 4:
                x_comp = info[0]
                print x_comp
                i_img = o_path + info[1]
                print i_img
                if not os.path.isfile(i_img):
                    return False
                fstype = info[2]
                o_dev = info[3]
                umount_dev(o_dev)
                cmd = "%s -d -c %s | partclone.%s -r -C -s - -O %s" %(x_comp, i_img, fstype, o_dev)
                return cmd
        return False


if __name__ == "__main__":
    StartClone()


