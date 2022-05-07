#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import platform
import subprocess
import json

#set(PROJECT_NAME "weather") from CMakeList
program_name = "weather"

#--------------------------------------------------utilities
def get_cpu_cores_count():
    return os.cpu_count()

def check_if_app_exists(app):
    ver_result = subprocess.run([app, '--version'])
    if ver_result.returncode:
        print("ERROR: ", app, " doesn't installed!")
        sys.exit(1)

def download_and_extract(url_str, dir_path, file_name):
    ar_ext = ".tar.gz"
    out_path = os.path.join(dir_path, file_name)
    ar_path = out_path + ar_ext
    if (not os.path.exists(ar_path)):
        print("DOWNLOAD: " + ar_path)
        subprocess.run(["curl", '-L', url_str, '--output', ar_path])

    if (not os.path.exists(out_path)):
        print("EXTRACT: " + ar_path)
        shutil.unpack_archive(filename=ar_path, extract_dir=dir_path, format="gztar")

def get_cmake_target():
    target = 'install'
    if (platform.system() == "Windows"):
        target = 'INSTALL'
    return target

#--------------------------------------------------prepare
check_if_app_exists("perl")
check_if_app_exists("curl")
check_if_app_exists("cmake")

ROOT_DIR = os.path.realpath(os.path.dirname(__file__))
CMAKE_GENERATOR="Unix Makefiles"
LIBSSL = "libressl-3.4.3"
LIBCURL = "curl-7.82.0"
LIBJSON_VER = "1.9.5"
LIBJSON = "jsoncpp-" + LIBJSON_VER
LIBZLIB = "zlib-1.2.12"
LIBGLFW = "glfw-3.3.7"
#---------------------------------------------------
LIBS = os.path.join(ROOT_DIR, "libs")
DEST = os.path.join(ROOT_DIR, "build")
LIBSBUILD=os.path.join(DEST, "libs")

if (not os.path.exists(LIBS)):
    os.mkdir(LIBS)
    os.mkdir(os.path.join(LIBS, "include"))
    os.mkdir(os.path.join(LIBS, "lib"))

if (not os.path.exists(DEST)):
    os.mkdir(DEST)

SSL_LIB_FILE = os.path.join(LIBS,"lib", "libssl")
CURL_LIB_FILE = os.path.join(LIBS,"lib" , "libcurl")
JSON_LIB_FILE = os.path.join(LIBS,"lib", "libjsoncpp")
Z_LIB_FILE = os.path.join(LIBS,"lib", "libz")
GLFW_LIB_FILE = os.path.join(LIBS,"lib", "libglfw")

SOSUFFIX = "so"
ASUFFIX = "a"
if (platform.system() == "Windows"):
    CMAKE_GENERATOR="Visual Studio 16 2019"
    SOSUFFIX="dll"
    ASUFFIX="lib"
    Z_LIB_FILE=os.path.join(LIBS,"lib","zlibstatic")
    JSON_LIB_FILE = os.path.join(LIBS,"lib", "jsoncpp")
    GLFW_LIB_FILE = os.path.join(LIBS,"lib", "glfw3")

if (platform.system() == "Darwin"):
    SOSUFFIX="dylib"

SSL_LIB_FILE += "." + ASUFFIX
CURL_LIB_FILE += "." + ASUFFIX
JSON_LIB_FILE += "." + ASUFFIX
Z_LIB_FILE += "." + ASUFFIX
GLFW_LIB_FILE += "." + ASUFFIX

if (not os.path.exists(LIBSBUILD)): 
    os.mkdir(LIBSBUILD)

TGZ=".tar.gz"
#--------------------------------------------------download libs
download_and_extract('http://www.zlib.net/' + LIBZLIB + TGZ, LIBSBUILD, LIBZLIB)
download_and_extract('https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/' + LIBSSL + TGZ, LIBSBUILD, LIBSSL)
download_and_extract('https://curl.se/download/' + LIBCURL + TGZ, LIBSBUILD, LIBCURL)
download_and_extract('https://github.com/open-source-parsers/jsoncpp/archive/refs/tags/' + LIBJSON_VER + TGZ, LIBSBUILD, LIBJSON)
download_and_extract('https://codeload.github.com/glfw/glfw/tar.gz/3.3.7', LIBSBUILD, LIBGLFW)

#--------------------------------------------------build libs
#--------------------------------------------------zlib
sources_dir = os.path.join(LIBSBUILD, LIBZLIB)
if (os.path.exists(sources_dir)):
    if (not os.path.exists(os.path.join(LIBS, Z_LIB_FILE))):
        print("BUILD: " + Z_LIB_FILE)
        build_dir = sources_dir + "_build"
        if (not os.path.exists(build_dir)):
            os.mkdir(build_dir)

        subprocess.run(['cmake',
            '-G', CMAKE_GENERATOR,
            '-S', sources_dir,
            '-B', build_dir,
            '-DCMAKE_INSTALL_PREFIX=' + LIBS])
        subprocess.run(['cmake',
            '--build', build_dir,
            '--config', 'Release',
            '--target', get_cmake_target(),
            '-j{}'.format(get_cpu_cores_count())])

        if (platform.system() == "Windows"):
            shutil.move(os.path.join(build_dir, 'zconf.h'), os.path.join(LIBS, "include", 'zconf.h'))
            shutil.move(os.path.join(build_dir, 'Release', 'zlibstatic.lib'), os.path.join(LIBS, "lib", 'zlibstatic.lib'))
##--------------------------------------------------openssl
sources_dir = os.path.join(LIBSBUILD, LIBSSL)
if (os.path.exists(sources_dir)):
    if (not os.path.exists(os.path.join(LIBS, SSL_LIB_FILE))):
        print("BUILD: " + SSL_LIB_FILE)
        build_dir = sources_dir + "_build"
        ssl_prefs_dir = os.path.join(LIBS, 'sslprefs')
        if (not os.path.exists(build_dir)):
            os.mkdir(build_dir)
        if (not os.path.exists(ssl_prefs_dir)):
            os.mkdir(ssl_prefs_dir)

        if (platform.system() == "Windows"):
            #read settings
            rc_settings_path = os.path.join(ROOT_DIR, "rc", "settings.json")
            with open(rc_settings_path, "r") as read_file:
                rc_settings = json.load(read_file)
            if (rc_settings):
                rc_settings["cert_path"] = os.path.join(ROOT_DIR, ssl_prefs_dir, "cert.pem")
                with open(rc_settings_path, "w") as write_file:
                    json.dump(rc_settings, write_file)

        subprocess.run(['cmake',
            '-G', CMAKE_GENERATOR,
            '-S', sources_dir,
            '-B', build_dir,
            '-DCMAKE_INSTALL_PREFIX=' + LIBS,
            '-DOPENSSLDIR=' + ssl_prefs_dir,
            '-DENABLE_ASM=OFF',
            '-DLIBRESSL_APPS=ON',
            '-DLIBRESSL_TESTS=ON'])
        subprocess.run(['cmake',
            '--build', build_dir,
            '--config', 'Release',
            '--target', get_cmake_target(),
            '-j{}'.format(get_cpu_cores_count())])

        if (platform.system() == "Windows"):
            shutil.move(os.path.join(LIBS, 'lib', 'ssl-50.lib'), os.path.join(LIBS, 'lib', 'libssl.lib'))
            shutil.move(os.path.join(LIBS, 'lib', 'crypto-47.lib'), os.path.join(LIBS, 'lib', 'libcrypto.lib'))
            shutil.move(os.path.join(LIBS, 'lib', 'tls-22.lib'), os.path.join(LIBS, 'lib', 'libtls.lib'))
##--------------------------------------------------curl
sources_dir = os.path.join(LIBSBUILD, LIBCURL)
if (os.path.exists(sources_dir)):
    if (not os.path.exists(os.path.join(LIBS, CURL_LIB_FILE))):
        print("BUILD: " + CURL_LIB_FILE)
        build_dir = sources_dir + "_build"
        if (not os.path.exists(build_dir)):
            os.mkdir(build_dir)

        subprocess.run(['cmake',
            '-G', CMAKE_GENERATOR,
            '-S', sources_dir,
            '-B', build_dir,
            '-DCURL_USE_OPENSSL=ON',
            '-DOPENSSL_ROOT_DIR=' + LIBS,
            '-DOPENSSL_USE_STATIC_LIBS=ON',
            '-DCMAKE_INSTALL_PREFIX=' + LIBS,
            '-DCMAKE_BUILD_TYPE=release',
            '-DBUILD_SHARED_LIBS=OFF',
            '-DBUILD_CURL_EXE=OFF',
            '-DCURL_DISABLE_LDAP=ON',
            '-DCURL_DISABLE_LDAPS=ON',
            '-DCURL_DISABLE_TESTS=ON',
            '-DCURL_DISABLE_RTSP=ON'])
        subprocess.run(['cmake',
            '--build', build_dir,
            '--config', 'Release',
            '--target', get_cmake_target(),
            '-j{}'.format(get_cpu_cores_count())])
##--------------------------------------------------jsoncpp
sources_dir = os.path.join(LIBSBUILD, LIBJSON)
if (os.path.exists(sources_dir)):
    if (not os.path.exists(os.path.join(LIBS, JSON_LIB_FILE))):
        print("BUILD: " + JSON_LIB_FILE)
        build_dir = sources_dir + "_build"
        if (not os.path.exists(build_dir)):
            os.mkdir(build_dir)

        subprocess.run(['cmake', 
            '-G', CMAKE_GENERATOR,
            '-S', sources_dir,
            '-B', build_dir,
            '-DCMAKE_INSTALL_PREFIX=' + LIBS,
            '-DCMAKE_BUILD_TYPE=release',
            '-DBUILD_STATIC_LIBS=ON',
            '-DBUILD_SHARED_LIBS=OFF',
            '-DCMAKE_INSTALL_INCLUDEDIR=include'])
        subprocess.run(['cmake',
            '--build', build_dir,
            '--config', 'Release',
            '--target', get_cmake_target(),
            '-j{}'.format(get_cpu_cores_count())])
##--------------------------------------------------GLFW
sources_dir = os.path.join(LIBSBUILD, LIBGLFW)
if (os.path.exists(sources_dir)):
    if (not os.path.exists(os.path.join(LIBS, GLFW_LIB_FILE))):
        print("BUILD: " + GLFW_LIB_FILE)
        build_dir = sources_dir + "_build"
        if (not os.path.exists(build_dir)):
            os.mkdir(build_dir)

        subprocess.run(['cmake', 
            '-G', CMAKE_GENERATOR,
            '-S', sources_dir,
            '-B', build_dir,
            '-DCMAKE_INSTALL_PREFIX=' + LIBS,
            '-DCMAKE_BUILD_TYPE=release',
            '-DGLFW_BUILD_EXAMPLES=OFF',
            '-DGLFW_BUILD_TESTS=OFF',
            '-DGLFW_BUILD_DOCS=OFF'])
        subprocess.run(['cmake',
            '--build', build_dir,
            '--config', 'Release',
            '--target', get_cmake_target(),
            '-j{}'.format(get_cpu_cores_count())])
##--------------------------------------------------build project
proj_build=os.path.join(DEST, 'project')
if (not os.path.exists(proj_build)):
    os.mkdir(proj_build)

print("BUILD: generate project for " + CMAKE_GENERATOR)
subprocess.run(['cmake',
    '-G', CMAKE_GENERATOR,
    '-S', ROOT_DIR,
    '-B', proj_build,
    '-DCMAKE_BUILD_TYPE=release'])
print("BUILD: build executable with cmake...")
subprocess.run(['cmake',
    '--build', proj_build,
    '--config','Release',
    '-j{}'.format(get_cpu_cores_count())])

print('path to project: ' + proj_build)

if (platform.system() == "Windows"):
    program_name = "project1.exe"
shutil.move(os.path.join(proj_build, program_name), os.path.join(ROOT_DIR, program_name))

print('done')

sys.exit(0)
