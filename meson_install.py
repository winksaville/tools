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

import glob
import subprocess
import sys
import os
import traceback
import shutil

APP='meson'
URL='https://github.com/mesonbuild/meson.git'
DEFAULT_VER='0.32.0'
CHECKOUT=DEFAULT_VER
#CHECKOUT='master'

def rmfile(file_name):
    try:
      os.remove(file_name)
    except OSError:
        pass

class Installer:
    '''Installer for meson.'''

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
            dst = os.path.join(dst_dir, self.args.app)
            output = subprocess.check_output([dst, '-v'],
                    stderr=subprocess.STDOUT)
            if output is None:
                output = b''
        except BaseException as err:
            output = b''

        if not self.args.forceInstall and bytes(self.args.ver, 'utf-8') in output:
            print('{app} {ver} is already installed'
                    .format(app=self.args.app, ver=self.args.ver))
        else:
            print('installing {app} {ver}'
                    .format(app=self.args.app, ver=self.args.ver))

            # Install using pip3
            subprocess.check_call('pip3 install --prefix {prefix} --upgrade {app}=={ver}'
                .format(prefix=self.args.installPrefixDir, app=self.args.app, ver=self.args.ver), shell=True)

            # Add symlink between the 'script.py' and 'bin'
            meson_script = os.path.join(self.args.installPrefixDir,'bin/meson.py')
            mesonconf_script = os.path.join(self.args.installPrefixDir,'bin/mesonconf.py')
            mesonintrospect_script = os.path.join(self.args.installPrefixDir,'bin/mesonintrospect.py')
            wraptool_script = os.path.join(self.args.installPrefixDir,'bin/wraptool.py')

            meson_bin = os.path.join(self.args.installPrefixDir,'bin/meson')
            mesonconf_bin = os.path.join(self.args.installPrefixDir,'bin/mesonconf')
            mesonintrospect_bin = os.path.join(self.args.installPrefixDir,'bin/mesonintrospect')
            wraptool_bin = os.path.join(self.args.installPrefixDir,'bin/wraptool')


            rmfile(meson_bin)
            rmfile(mesonconf_bin)
            rmfile(mesonintrospect_bin)
            rmfile(wraptool_bin)

            os.symlink(meson_script, meson_bin)
            os.symlink(mesonconf_script, mesonconf_bin)
            os.symlink(mesonintrospect_script, mesonintrospect_bin)
            os.symlink(wraptool_script, wraptool_bin)

            # Tell the user to update PYTHONPATH
            python_path = glob.glob(os.path.join(self.args.installPrefixDir, 'lib/python*'))
            if len(python_path) == 1:
                site_packages = os.path.join(python_path[0], 'site-packages')
                if not os.path.exists(site_packages):
                    print('PYTHONPATH needed and expecting it to be \'{}\', but it does not exist')
                else:
                    print('Add the prefix directory, {prefix} to PYTHONPATH.')
                    print('For instance add the following to .bashrc:'
                            .format(prefix=self.args.installPrefixDir))
                    print('  export PYTHONPATH={}:$PYTHONPATH'
                            .format(site_packages))
            else:
                print('PYTHONPATH needed but there are more than one \'python*\' directories: {}'
                        .format(python_path))

        return retval 

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'printVer':
        print(DEFAULT_VER)
    else:
        installer = Installer()
        installer.install()
