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

import utils
import parseinstallargs

import subprocess
import sys
import os
import traceback
import shutil

DEFAULT_CROSS_DIR='x-tools'
GCC_VER='5.2.0'
BINU_VER='2.25.1'
DEFAULT_VER=GCC_VER
AN_APP='gcc'

class Builder:
    '''Buidler for x86_64-unknown-elf-xxx.'''

    def __init__(self, defaultVer=DEFAULT_VER, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None,
            defaultCrossDir=DEFAULT_CROSS_DIR, defaultTarget=None,
            extraFlags=None):
        '''See parseinstallargs for defaults prefixes'''
        if extraFlags is None:
            extraFlags = ''
        self.extraFlags = extraFlags
        app = AN_APP
        self.args = parseinstallargs.InstallArgs(app, defaultVer,
                defaultCodePrefixDir,
                defaultInstallPrefixDir,
                defaultForceInstall, defaultCrossDir, defaultTarget)


    def build(self):
        if self.args.target is None:
            print('No default target expecting something like "x86_64-unknown-elf"')
            return 1
        print('ct_ng_build: self.args.installPrefixDir={}'
                .format(self.args.installPrefixDir))
        print('ct_ng_build: self.args.crossDir={}'.format(self.args.crossDir))
        print('ct_ng_build: self.args.target={}'.format(self.args.target))

        self.args.installPrefixDir = '{}/{}'.format(
                self.args.installPrefixDir, self.args.target)
        print('ct_ng_build: installPrefixDir={}'.format(self.args.installPrefixDir))
        dst_dir = os.path.join(self.args.installPrefixDir, 'bin')
        print('ct_ng_build: dst_dir={}'.format(dst_dir))
        os.makedirs(dst_dir, exist_ok=True)
        retval = 0

        self.args.app = '{}-{}'.format(self.args.target, self.args.app)
        print('ct_ng_build: self.args.app={}'.format(self.args.app))

        try:
            dst = os.path.join(dst_dir, self.args.app)
            output = subprocess.check_output([dst, '--version'],
                    stderr=subprocess.STDOUT)
            if output is None:
                output = b''
        except BaseException as err:
            output = b''

        if not self.args.forceInstall and bytes(self.args.ver, 'utf-8') in output:
            print('{app} {ver} is already installed'
                    .format(app=self.args.app, ver=self.args.ver))
        else:
            print('compiling {app} {ver}'
                    .format(app=self.args.app, ver=self.args.ver))
            code_dir = os.path.join(self.args.codePrefixDir,
                    '{}/{}'.format(self.args.crossDir, self.args.target))
            print('ct_ng_build: code_dir={}'.format(code_dir))
            if self.args.forceInstall:
                shutil.rmtree(code_dir, ignore_errors=True)
            os.makedirs(code_dir)

            shutil.copy2('./config.{}'.format(self.args.target),
                '{}/.config'.format(code_dir))
            os.chdir(code_dir)

            # Builds and isntall app's
            subprocess.check_call(['ct-ng', 'build'])

        return retval

if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == 'printBinuVer':
            print(BINU_VER)
        elif sys.argv[1] == 'printGccVer':
            print(GCC_VER)
        else:
            print("WAIT '{}' is bad parameter to ct_ng_runner.py".format(sys.argv[1]))
    else:
        builder = Builder()
        builder.build()
