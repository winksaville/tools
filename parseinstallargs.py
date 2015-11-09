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

import argparse
import os

DEFAULT_CODE_PREFIX_DIR = '~/tmp'
DEFAULT_INSTALL_PREFIX_DIR = '~/opt'

class InstallArgs:
    def __init__(self, app, defaultVer=None, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None):
        parser = argparse.ArgumentParser()

        self.app = app

        parser.add_argument('apps', default=[], nargs='*',
                help='List of applicatons')

        if defaultForceInstall is None:
            defaultForceInstall = False
        parser.add_argument('--forceInstall',
                help='force install (default: {})'.format(defaultForceInstall),
                action='store_true',
                default=defaultForceInstall)

        if defaultCodePrefixDir is None:
            defaultCodePrefixDir=os.path.abspath(
                    os.path.expanduser(DEFAULT_CODE_PREFIX_DIR))
        parser.add_argument('--codePrefixDir',
                help='Code prefix for creating the binaries (default: {})'
                        .format(defaultCodePrefixDir),
                nargs='?',
                default=defaultCodePrefixDir)

        if defaultInstallPrefixDir is None:
            defaultInstallPrefixDir=os.path.abspath(
                    os.path.expanduser(DEFAULT_INSTALL_PREFIX_DIR))
        parser.add_argument('--installPrefixDir',
                help='Install prefix directory for the binaries (default: {})'
                        .format(defaultInstallPrefixDir),
                nargs='?',
                default=defaultInstallPrefixDir)

        if defaultVer is None:
            defaultVer = ''
        parser.add_argument('--ver',
                help='version to install (default: {})'.format(defaultVer),
                nargs='?',
                default=defaultVer);

        # Add parser to InstallArgs namespace
        parser.parse_args(namespace=self)

        # Be sure the prefix directory paths are expanded and absolute
        self.codePrefixDir = os.path.abspath(os.path.expanduser(self.codePrefixDir))
        self.installPrefixDir = os.path.abspath(os.path.expanduser(self.installPrefixDir))

