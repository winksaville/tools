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

import argparse
import multiprocessing
import os
import shutil
import subprocess
import sys
import traceback

DEFAULT_VER='5.3.0'
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
#ISL_URL  = 'ftp://gcc.gnu.org/pub/gcc/infrastructure/isl-0.14.tar.bz2'

class Installer:
    '''Installer'''

    def __init__(self, defaultVer=DEFAULT_VER, defaultCodePrefixDir=None,
            defaultInstallPrefixDir=None, defaultForceInstall=None,
            defaultCrossDir=DEFAULT_CROSS_DIR, defaultTarget=None,
            extraFlags=None):
        '''See parseinstallargs for defaults prefixes'''
        if extraFlags is None:
            extraFlags = ''
        self.extraFlags = extraFlags
        self.args = parseinstallargs.InstallArgs(APP, defaultVer, defaultCodePrefixDir,
                defaultInstallPrefixDir, defaultForceInstall, defaultCrossDir, defaultTarget)

    def parseUnknownArgs(self):
        #print('self.args.unknownArgs =', self.args.unknownArgs)
        parser = argparse.ArgumentParser()

        parser.add_argument('--extraGccConfigFlags', default=[],
                action='append',
                help='Extra flags to pass to gcc configure, multiple allowed')
        (self.extraArgs, unknownArgs) = parser.parse_known_args(self.args.unknownArgs)


    def runCmd(self, cmd, shell=True, verbose=False):
        print('gcc_install.py: cwd={} cmd={}'.format(os.getcwd(), cmd))
        if verbose:
            output=None
        else:
            output=subprocess.DEVNULL
        subprocess.run(cmd, shell=shell, stdout=output)

    def makePrerequisiteLibrary(self, envVars, libSrcPath, installPrefixDir):
        '''Makes a library using native gcc installing in installPrefixDir'''
        print('makePrerequisiteLibrary:', libSrcPath)
        cwd = os.getcwd()
        os.chdir(libSrcPath)
        self.runCmd('{} ./configure --prefix={}'.format(envVars, installPrefixDir))
        self.runCmd('{} make -j {}'.format(envVars, multiprocessing.cpu_count()))
        self.runCmd('{} make install'.format(envVars))
        os.chdir(cwd)
        print('makePrerequisiteLibrary: COMPLETED', libSrcPath)

    def install(self):
        dst_dir = os.path.join(self.args.installPrefixDir, 'bin')
        os.makedirs(dst_dir, exist_ok=True)
        retval = 0

        self.parseUnknownArgs()

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
            #isl does't compile and its optional so don't add
            #isl_path = os.path.join(code_dir, 'isl')
            #print('gcc_install: isl_path=', isl_path)
            gcc_path = os.path.join(code_dir, 'gcc')
            print('gcc_install: gcc_path=', gcc_path)

            #envVars = ('LDFLAGS=-L/home/wink/opt/lib' +
            #          ' CPPFLAGS=-I/home/wink/opt/include')
            envVars = ''

            # If desired make false when testing so we don't download.
            if True:
                if self.args.forceInstall:
                    shutil.rmtree(gmp_path, ignore_errors=True)
                    shutil.rmtree(mpfr_path, ignore_errors=True)
                    shutil.rmtree(mpc_path, ignore_errors=True)
                    #shutil.rmtree(isl_path, ignore_errors=True)
                    shutil.rmtree(gcc_path, ignore_errors=True)

                utils.wget_extract(GMP_URL, dst_path=gmp_path)
                utils.wget_extract(MPFR_URL, dst_path=mpfr_path)
                utils.wget_extract(MPC_URL, dst_path=mpc_path)
                #utils.wget_extract(ISL_URL, dst_path=isl_path)
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

            # Make the prerequisites (isl is optional)
            #self.makePrerequisiteLibrary(envVars, isl_path, os.path.dirname(self.args.installPrefixDir))

            # Make the prerequisites (Not needed if I install existing versions??)
            #self.makePrerequisiteLibrary(envVars, gmp_path, os.path.dirname(self.args.installPrefixDir))
            #self.makePrerequisiteLibrary(envVars, mpfr_path, os.path.dirname(self.args.installPrefixDir))
            #self.makePrerequisiteLibrary(envVars, mpc_path, os.path.dirname(self.args.installPrefixDir))

            # Create the build directory and cd into it
            os.chdir(gcc_path)
            os.makedirs('build', exist_ok=True)
            os.chdir('build')

            # ls the directory with gcc, gmp, mpfr and mpc for debug purposes
            #utils.bash('ls -al {}'.format(os.path.dirname(self.args.codePrefixDir)))

            cmd = ('{env}' +
                   ' ../configure --prefix={prefix}' +
                   ' --with-gmp={gmp}' +
                   ' --with-gmp-include={gmp}' +
                   ' --with-mpfr={mpfr}' +
                   ' --with-mpfr-include={mpfr}/src' +
                   ' --with-mpc={mpc}' +
                   ' --with-mpc-include={mpc}/src' +
                   #' --with-isl={isl}' +
                   #' --with-isl-include={isl}/include' +
                   ' --disable-nls ' +
                   ' --enable-languages=c,c++' +
                   ' --disable-multilib' +
                   ' --without-headers').format(
                           env=envVars, prefix=self.args.installPrefixDir, gmp=gmp_path, mpfr=mpfr_path,
                           mpc=mpc_path) #, isl=isl_path)
            if self.args.target != '':
                cmd += ' --target={}'.format(self.args.target)

            # Add extraFlags added on the command line
            for extraFlag in self.extraArgs.extraGccConfigFlags:
                cmd += ' {}'.format(extraFlag)

            # Add extraFlags passed to the constructor
            for extraFlag in self.extraFlags:
                cmd += ' {}'.format(extraFlag)
            self.runCmd(cmd)

            cpu_count = multiprocessing.cpu_count()
            cci = os.environ.get('CIRCLECI')
            if cci != None and cci == 'true':
                cpu_count = 4;

            self.runCmd('{env} make all-gcc -j {c}'
                    .format(env=envVars, c=cpu_count), verbose=True)

            self.runCmd('{env} make install-gcc'
                    .format(env=envVars))

            self.runCmd('{env} make all-target-libgcc -j {c}'
                    .format(env=envVars, c=cpu_count))

            self.runCmd('{env} make install-target-libgcc'
                    .format(env=envVars))

        return 0

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'printVer':
        print(DEFAULT_VER)
    else:
        installer = Installer()
        installer.install()
