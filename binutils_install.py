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
import shutil
import multiprocessing

APP='binutils-gdb'
URL = 'git://sourceware.org/git/binutils-gdb.git'
DEFAULT_VER='2.25.1'
AN_APP='ld'
TARGET='arm-eabi'
TARGET_DASH='-'

class Installer:
    '''Installer'''

    def __init__(self, defaultVer=DEFAULT_VER, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None):
        '''See parseinstallargs for defaults prefixes'''
        self.args = parseinstallargs.InstallArgs(APP, defaultVer, defaultCodePrefixDir,
                defaultInstallPrefixDir, defaultForceInstall)

    def install(self):
        dst_dir = os.path.join(self.args.installPrefixDir, 'bin')
        os.makedirs(dst_dir, exist_ok=True)
        retval = 0

        try:
            dst = os.path.join(dst_dir, '{target}{target_dash}{an_app}'
                    .format(target=TARGET, target_dash=TARGET_DASH, an_app=AN_APP))
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
            code_dir = os.path.join(self.args.codePrefixDir, self.args.app)
            if self.args.forceInstall:
                shutil.rmtree(code_dir, ignore_errors=True)
            os.makedirs(code_dir)

            utils.git('clone', [URL, code_dir])
            os.chdir(code_dir)
            version = self.args.ver.replace('.','_')
            utils.git('checkout', ['binutils-{}'.format(version)])
            os.mkdir('build')
            os.chdir('build')

            utils.bash('../configure --prefix={0} --target={1} --disable-nls'
                    .format(self.args.installPrefixDir, TARGET))
            utils.bash('make all -j {}'.format(multiprocessing.cpu_count()))
            utils.bash('make install')

        return retval

if __name__ == '__main__':

    installer = Installer()
    installer.install()
