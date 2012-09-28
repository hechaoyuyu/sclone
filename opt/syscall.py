#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "hechao"
__date__ = "$2012-7-10 10:33:34$"

import os
import re
import sys
import commands

def get_output(cmd):
    status, output = commands.getstatusoutput(cmd)
    if status: raise
    return output

def get_size(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def get_parted():
    ret = {}
    try:
        hds = get_output('echo /dev/sd[a-z]').split()
        k = 0
        for hd in hds:
            info = get_output('parted -s %s unit B p' % hd)
            parts = re.findall("[1-9]{1,2} (?!.*extended).*", info)
            for part in parts:
                part = part.split()
                ret[k] = hd + part[0], get_size(part[3][0:-1]), part[5]
                k += 1
    except:
        print >> sys.stderr, "Command failed: parted"
    return ret

def is_mount(path, dev):
    if os.path.ismount(path):
        return True
    if not os.path.isdir(path):
        os.mkdir(path)
    try:
        info = get_output('mount | grep %s' %dev).split()
        if not os.system('mount --bind %s %s' %(info[2], path)):
            return True
    except:
        if not os.system('mount %s %s' %(dev, path)):
            return True
    return False

def mount_dev(dev):
    path = ''
    try:
        info = get_output('blkid %s' %dev)
        tmp = re.findall("UUID=\"(.*)\" TYPE", info)
        print tmp
        if tmp:
            if is_mount("/media/" + tmp[0], dev):
                path = "/media/" + tmp[0]
    except:
        print >> sys.stderr, "Command failed: blkid"
    return path

def umount_dev(dev):
    try:
        if not os.system("mount | grep %s" %dev):
            os.system("umount %s" %dev)
    except:
        print >> sys.stderr, "Command failed: umount"

def echo_config(x_comp, name, fstype, i_dev, o_path):
    try:
        os.system("echo %s %s %s %s > %s/startclone.info" %(x_comp, name, fstype, i_dev, o_path))
    except:
        print >> sys.stderr, "Command failed: echo"
