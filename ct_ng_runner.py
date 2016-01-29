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
GCC_VER='5.3.0'
GCC_X86_64_VER='5.3.1-wink-intr-attr-2'
X86_64_TARGET='x86_64-unknown-elf'
BINU_VER='2.25.1'
DEFAULT_VER=GCC_VER
AN_APP='gcc'
GCC_GIT_REPO_URL = 'https://github.com/winksaville/gcc.git'
CHECKOUT_LABEL='wink-intr-attr'

class Builder:
    '''Buidler for ct-ng builds'''

    def __init__(self, defaultVer=DEFAULT_VER, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None,
            defaultCrossDir=DEFAULT_CROSS_DIR, defaultTarget=None,
            extraFlags=None):
        '''See parseinstallargs for defaults prefixes'''
        if extraFlags is None:
            extraFlags = ''
        self.extraFlags = extraFlags
        app = AN_APP
        if (defaultVer is DEFAULT_VER) and (defaultTarget == X86_64_TARGET):
            defaultVer=GCC_X86_64_VER
        self.args = parseinstallargs.InstallArgs(app, defaultVer,
                defaultCodePrefixDir,
                defaultInstallPrefixDir,
                defaultForceInstall, defaultCrossDir, defaultTarget)


    def build(self):
        if self.args.target is None:
            print('No default target expecting something like "x86_64-unknown-elf"')
            return 1

        self.args.installPrefixDir = '{}/{}'.format(
                self.args.installPrefixDir, self.args.target)
        dst_dir = os.path.join(self.args.installPrefixDir, 'bin')
        os.makedirs(dst_dir, exist_ok=True)
        retval = 0

        self.args.app = '{}-{}'.format(self.args.target, self.args.app)

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
            if self.args.forceInstall:
                shutil.rmtree(code_dir, ignore_errors=True)
            os.makedirs(code_dir)

            if self.args.target == X86_64_TARGET:
                # Get gcc from git which supports attribute(interrupt)
                # gcc_path must match GCC_CUSTOM_LOCATION in config.x86_64-unknown-elf
                gcc_path = os.path.expanduser(os.path.join('~/prgs', 'ct-ng-gcc'))
                shutil.rmtree(gcc_path, ignore_errors=True)
                print('gcc_install: gcc_path=', gcc_path)
                utils.git('clone', [GCC_GIT_REPO_URL, gcc_path, '--depth', '1', '--single-branch',
                    '--branch', CHECKOUT_LABEL])
                os.chdir(gcc_path)
                
            thisDir = os.path.dirname(os.path.realpath(__file__))
            src = os.path.abspath('{}/config.{}'.format(thisDir, self.args.target))
            dst = os.path.abspath('{}/.config'.format(code_dir))
            print('config src=', src)
            print('config dst=', dst)
            shutil.copy2(src, dst)
            os.chdir(code_dir)

            # Build and install app's
            subprocess.check_call(['ct-ng', 'build.4'])

        return retval

if __name__ == '__main__':

    if len(sys.argv) == 2:
        if sys.argv[1] == 'printBinuVer':
            print(BINU_VER)
        elif sys.argv[1] == 'printGccVer':
            print(GCC_VER)
        elif sys.argv[1] == 'printGccX86_64_Ver':
            print(GCC_X86_64_VER)
        else:
            print("WAIT '{}' is bad parameter to ct_ng_runner.py".format(sys.argv[1]))
    else:
        builder = Builder()
        builder.build()
