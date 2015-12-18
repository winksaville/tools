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

all_apps = ['ninja', 'meson', 'binutils-i586-elf', 'binutils-arm-eabi', 'gcc-i586-elf',
        'gcc-arm-eabi', 'qemu-system-arm']

args = parseinstallargs.InstallArgs('all', apps=all_apps)

if len(args.apps) == 0:
    args.print_help()
    sys.exit(0)

if 'all' in args.apps:
    args.apps = all_apps

# Install the apps
for app in args.apps:
    if app == 'ninja':
        installer = ninja_install.Installer()
        installer.install()
    elif app == 'meson':
        installer = meson_install.Installer()
        installer.install()
    elif app == 'binutils-arm-eabi':
        installer = binutils_install.Installer(defaultTarget='arm-eabi')
        installer.install()
    elif app == 'binutils-i586-elf':
        installer = binutils_install.Installer(defaultTarget='i586-elf')
        installer.install()
    elif app == 'binutils-x86_64':
        installer = binutils_install.Installer(defaultTarget='x86_64-pc-linux')
        installer.install()
    elif app == 'gcc-arm-eabi':
        installer = gcc_install.Installer(defaultTarget='arm-eabi')
        installer.install()
    elif app == 'gcc-i586-elf':
        installer = gcc_install.Installer(defaultTarget='i586-elf')
        installer.install()
    elif app == 'gcc-x86_64':
        print('gcc-x86_64 ******* NOT YET WORKING ********')
        installer = gcc_install.Installer(defaultTarget='x86_64-pc-linux',
                extraFlags=[
                    '--enable-threads=posix',
                    '--enable-libmpx',
                    '--enable-__cxa_atexit',
                    '--disable-libunwind-exceptions',
                    '--enable-clocale=gnu',
                    '--disable-libstdcxx-pch',
                    '--disable-libssp',
                    '--enable-gnu-unique-object',
                    '--enable-linker-build-id',
                    '--enable-lto',
                    '--enable-plugin',
                    '--enable-install-libiberty',
                    '--with-linker-hash-style=gnu',
                    '--enable-gnu-indirect-function',
                    '--disable-multilib',
                    '--disable-werror',
                    '--enable-checking=release',
                    '--with-default-libstdcxx-abi=gcc4-compatible',
                ])
        installer.install()
    elif app == 'qemu-system-arm':
        installer = qemu_install.Installer()
        installer.install()
    else:
        print('Unknown app:', app)
        sys.exit(1)
