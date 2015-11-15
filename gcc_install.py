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
import traceback

DEFAULT_VER='5.2.0'
APP='gcc'
AN_APP='gcc'
DEFAULT_CROSS_DIR='cross'
TARGET='arm-eabi'
CHECKOUT_LABEL='gcc_{}_release'.format(DEFAULT_VER.replace('.','_'))
GCC_GIT_REPO_URL = 'https://github.com/gcc-mirror/gcc.git'
#GCC_GIT_REPO_URL = 'https://github.com/winksaville/gcc-5.2.0.git' # My debug version
GCC_URL  = 'http://ftp.gnu.org/gnu/gcc/gcc-{0}/gcc-{0}.tar.bz2'
GMP_URL  = 'http://ftp.gnu.org/gnu/gmp/gmp-6.0.0a.tar.xz'
MPFR_URL = 'http://ftp.gnu.org/gnu/mpfr/mpfr-3.1.3.tar.xz'
MPC_URL  = 'http://ftp.gnu.org/gnu/mpc/mpc-1.0.3.tar.gz'

class Installer:
    '''Installer'''

    def __init__(self, defaultVer=DEFAULT_VER, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None,
            defaultCrossDir=DEFAULT_CROSS_DIR, defaultTarget=None):
        '''See parseinstallargs for defaults prefixes'''
        self.args = parseinstallargs.InstallArgs(APP, defaultVer, defaultCodePrefixDir,
                defaultInstallPrefixDir, defaultForceInstall, defaultCrossDir, defaultTarget)


    def install(self):
        dst_dir = os.path.join(self.args.installPrefixDir, 'bin')
        os.makedirs(dst_dir, exist_ok=True)
        retval = 0

        try:
            theApp = AN_APP
            if self.args.target != '':
                theApp = '{}-{}'.format(self.args.target, theApp)

            theApp = os.path.join(dst_dir, theApp)
            output = subprocess.check_output([theApp, '--version'],
                    stderr=subprocess.STDOUT)
            if output is None:
                output = b''
        except BaseException as err:
            output = b''

        if not self.args.forceInstall and bytes(self.args.ver, 'utf-8') in output:
            print('{app} {ver} is already installed'
                    .format(app=self.args.app, ver=self.args.ver))
        else:
            code_dir = self.args.codePrefixDir
            if self.args.target != '':
                code_dir = os.path.join(code_dir, self.args.target)
            gmp_path = os.path.join(code_dir, 'gmp')
            print('gcc_install: gmp_path=', gmp_path)
            mpfr_path = os.path.join(code_dir, 'mpfr')
            print('gcc_install: mpfr_path=', mpfr_path)
            mpc_path = os.path.join(code_dir, 'mpc')
            print('gcc_install: mpc_path=', mpc_path)
            gcc_path = os.path.join(code_dir, 'gcc')
            print('gcc_install: gcc_path=', gcc_path)

            if self.args.forceInstall:
                shutil.rmtree(gmp_path, ignore_errors=True)
                shutil.rmtree(mpfr_path, ignore_errors=True)
                shutil.rmtree(mpc_path, ignore_errors=True)
                shutil.rmtree(gcc_path, ignore_errors=True)

            utils.wget_extract(GMP_URL, dst_path=gmp_path)
            utils.wget_extract(MPFR_URL, dst_path=mpfr_path)
            utils.wget_extract(MPC_URL, dst_path=mpc_path)
            if True:
                # Use wget as its faster
                utils.wget_extract(GCC_URL.format(self.args.ver), dst_path=gcc_path)
                os.chdir(gcc_path)
            else:
                # Use git, but its slower
                os.makedirs(self.args.codePrefixDir, exist_ok=True)
                utils.git('clone', [GCC_GIT_REPO_URL, gcc_path])
                os.chdir(gcc_path)
                utils.git('checkout', [CHECKOUT_LABEL])

            # Create the build directory and cd into it
            os.mkdir('build')
            os.chdir('build')

            # ls the directory with gcc, gmp, mpfr and mpc for debug purposes
            #utils.bash('ls -al {}'.format(os.path.dirname(self.args.codePrefixDir)))

            configureCmd = ('../configure --prefix={0}' +
                   ' --with-gmp={gmp}' +
                   ' --with-gmp-include={gmp}' +
                   ' --with-mpfr={mpfr}' +
                   ' --with-mpfr-include={mpfr}/src' +
                   ' --with-mpc={mpc}' +
                   ' --with-mpc-include={mpc}/src' +
                   ' --disable-nls ' +
                   ' --enable-languages=c,c++' +
                   ' --disable-multilib' +
                   ' --without-headers').format(
                           self.args.installPrefixDir, gmp=gmp_path, mpfr=mpfr_path, mpc=mpc_path)
            if self.args.target != '':
                configureCmd += ' --target={}'.format(self.args.target)

            subprocess.run(configureCmd, shell=True)
            subprocess.run('make all-gcc -j {}'.format(multiprocessing.cpu_count()),
                    shell=True,
                    stdout=subprocess.DEVNULL) # Too much logging overflows 4MB travis-ci log limit
            subprocess.run('make install-gcc', shell=True)
            subprocess.run('make all-target-libgcc -j {}'.format(multiprocessing.cpu_count()),
                    shell=True,
                    stdout=subprocess.DEVNULL) # Too much logging overflows 4MB travis-ci log limit
            subprocess.run('make install-target-libgcc', shell=True)

        return 0

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'printVer':
        print(DEFAULT_VER)
    else:
        installer = Installer()
        installer.install()
