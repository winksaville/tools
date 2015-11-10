#!/usr/bin/env python3

# Copyright 2015 wink saville
#
# licensed under the apache license, version 2.0 (the "license");
# you may not use this file except in compliance with the license.
# you may obtain a copy of the license at
#
#     http://www.apache.org/licenses/license-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the license is distributed on an "as is" basis,
# without warranties or conditions of any kind, either express or implied.
# see the license for the specific language governing permissions and
# limitations under the license.

# Install all of the vendor tools

import parseinstallargs
import ninja_install
import meson_install
import binutils_install

import argparse
import sys
import os
import subprocess
import argparse

#CODE_PREFIX_DIR='~/tmp'
#INSTALL_PREFIX_DIR='~/opt'

#class InstallArgs:
#    def __init__(self, defaultSrcPrefixDir, defaultInstallPrefixDir):
#        parser = argparse.ArgumentParser()
#
#        dflt=os.path.abspath(os.path.expanduser(defaultSrcPrefixDir))
#        parser.add_argument('--codePrefixDir',
#                help='Source prefix dir (default: {})'.format(dflt),
#                nargs='?',
#                default=dflt)
#
#        dflt=os.path.abspath(os.path.expanduser(defaultInstallPrefixDir))
#        parser.add_argument('--installPrefixDir',
#                help='Install prefix dir (default: {})'.format(dflt),
#                nargs='?',
#                default=dflt)
#
#        self.o = parser.parse_args()

args = parseinstallargs.InstallArgs('all')

#THIS_DIR=os.path.abspath(os.path.dirname(sys.argv[0]))
#CODE_PREFIX_DIR=args.codePrefixDir
#INSTALL_PREFIX_DIR=args.installPrefixDir
#INSTALL_PREFIX_CROSS_DIR=os.path.join(args.installPrefixDir, 'cross')

#print('THIS_DIR =', THIS_DIR)
#print('CODE_PREFIX_DIR =', CODE_PREFIX_DIR)
#print('INSTALL_PREFIX_DIR =', INSTALL_PREFIX_DIR)
#print('INSTALL_PREFIX_CROSS_DIR =', INSTALL_PREFIX_CROSS_DIR)

if len(args.apps) == 0:
    argparse.ArgumentParser.print_help()
    sys.exit(0)

if 'all' in args.apps:
    args.apps = ['ninja', 'meson', 'binutils']

# Install the apps
for app in args.apps:
    if app == 'ninja':
        installer = ninja_install.Installer()
        installer.install()
    elif app == 'meson':
        installer = meson_install.Installer()
        installer.install()
    elif app == 'binutils':
        installer = binutils_install.Installer()
        installer.install()
    else:
        print('Unknow app:', app)
        sys.exit(1)

#subprocess.check_call('{0}/ninja-install.py --codePrefixDir {1}/ninja --installPrefixDir {2}'
#        .format(THIS_DIR, CODE_PREFIX_DIR, INSTALL_PREFIX_DIR),
#        shell=True)
#subprocess.check_call('{0}/binutils-install.py --codePrefixDir {1}/binutils --installPrefixDir {2}'
#        .format(THIS_DIR, CODE_PREFIX_DIR, INSTALL_PREFIX_CROSS_DIR),
#        shell=True)
#subprocess.check_call('{0}/gcc-install.py --codePrefixDir {1}/gcc --installPrefixDir {2}'
#        .format(THIS_DIR, CODE_PREFIX_DIR, INSTALL_PREFIX_CROSS_DIR),
#        shell=True)
#subprocess.check_call('{0}/qemu-install.py --codePrefixDir {1}/qemu --installPrefixDir {2}'
#        .format(THIS_DIR, CODE_PREFIX_DIR, INSTALL_PREFIX_DIR),
#        shell=True)
