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

# Install all or a specific set of the vendor tools

import parseinstallargs
import ninja_install
import meson_install
import binutils_install
import gcc_install
import qemu_install

import argparse
import sys
import os
import subprocess
import argparse

all_apps = ['ninja', 'meson', 'binutils', 'gcc', 'qemu']

args = parseinstallargs.InstallArgs('all', apps=all_apps)

if len(args.apps) == 0:
    args.print_help()
    sys.exit(0)

if 'all' in args.apps:
    args.apps = all_apps

# Install the apps
print('install.py: args.apps =', args.apps)
for app in args.apps:
    print('install.py: app =', app)
    if app == 'ninja':
        installer = ninja_install.Installer()
        installer.install()
    elif app == 'meson':
        installer = meson_install.Installer()
        installer.install()
    elif app == 'binutils':
        installer = binutils_install.Installer()
        installer.install()
    elif app == 'gcc':
        installer = gcc_install.Installer()
        installer.install()
    elif app == 'qemu':
        installer = qemu_install.Installer()
        installer.install()
    else:
        print('Unknown app:', app)
        sys.exit(1)
