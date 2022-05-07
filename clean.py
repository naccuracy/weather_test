#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import shutil

def rm_rf_if_exists(dir):
    if (os.path.exists(dir)):
        shutil.rmtree(dir)

root_dir = os.path.realpath(os.path.dirname(__file__))
#---------------------------------------------------
LIBS=os.path.join(root_dir, "libs")
DEST=os.path.join(root_dir, "build")
LIBSBUILD=os.path.join(DEST, "libs")
LIBSSL=os.path.join(LIBSBUILD, "libressl-3.4.3")
LIBCURL=os.path.join(LIBSBUILD,"curl-7.82.0")
LIBJSON=os.path.join(LIBSBUILD,"jsoncpp-1.9.5")
LIBZLIB=os.path.join(LIBSBUILD,"zlib-1.2.12")
LIBGLFW=os.path.join(LIBSBUILD,"glfw-3.3.7")

rm_rf_if_exists(LIBS)
rm_rf_if_exists(os.path.join(DEST, "project"))
rm_rf_if_exists(LIBSSL)
rm_rf_if_exists(LIBSSL + "_build")
rm_rf_if_exists(LIBCURL)
rm_rf_if_exists(LIBCURL + "_build")
rm_rf_if_exists(LIBJSON)
rm_rf_if_exists(LIBJSON + "_build")
rm_rf_if_exists(LIBZLIB)
rm_rf_if_exists(LIBZLIB + "_build")
rm_rf_if_exists(LIBGLFW)
rm_rf_if_exists(LIBGLFW + "_build")

print("done")
