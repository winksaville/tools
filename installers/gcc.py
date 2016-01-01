# Copyright (C) 2016 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function
import os, sys
import shutil
import installlib

try:
  from multiprocessing import cpu_count
except ImportError:
  cpu_count = lambda: 1

GCC_URL  = 'http://ftp.gnu.org/gnu/gcc/gcc-{0}/gcc-{0}.tar.bz2'
GMP_URL  = 'http://ftp.gnu.org/gnu/gmp/gmp-{0}.tar.xz'
MPFR_URL = 'http://ftp.gnu.org/gnu/mpfr/mpfr-{0}.tar.xz'
MPC_URL  = 'http://ftp.gnu.org/gnu/mpc/mpc-{0}.tar.gz'

def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')
  tmp_dir = os.path.join(settings['temp'], 'gcc')
  download_dir = os.path.join(settings['temp'], '_download')
  if settings['target']:
    tmp_dir += '-' + settings['target']

  gcc_path = os.path.join(tmp_dir, 'gcc')
  gmp_path = os.path.join(tmp_dir, 'gmp')
  mpfr_path = os.path.join(tmp_dir, 'mpfr')
  mpc_path = os.path.join(tmp_dir, 'mpc')

  try:
    if settings['target']:
      app = settings['target'] + '-gcc'
    else:
      app = 'gcc'
    app = os.path.join(dst_dir, app)
    output = installlib.run_piped([app, '--version']).stdout
  except OSError as exc:
    output = None
  if output and settings['version'] in output:
    print('gcc {0} already installed'.format(settings['version']))
    if not settings['force_install']:
      return

  print('installing gcc {0} ...'.format(settings['version']))
  if output:
    print('existing installation of gcc will be overwritten')

  if settings['dry']:
    return

  shutil.rmtree(tmp_dir, ignore_errors=True)

  url = GCC_URL.format(settings['version'])
  installlib.download_extract(url, gcc_path, temp=download_dir, strip_components=1)

  url = GMP_URL.format(settings['gmp_version'])
  installlib.download_extract(url, gmp_path, temp=download_dir, strip_components=1)

  url = MPFR_URL.format(settings['mpfr_version'])
  installlib.download_extract(url, mpfr_path, temp=download_dir, strip_components=1)

  url = MPC_URL.format(settings['mpc_version'])
  installlib.download_extract(url, mpc_path, temp=download_dir, strip_components=1)

  os.chdir(gcc_path)
  installlib.makedirs('build')
  os.chdir('build')

  command = ['../configure', '--prefix=' + settings['prefix'],
    '--with-gmp=' + gmp_path, '--with-gmp-include=' + gmp_path,
    '--with-mpfr=' + mpfr_path, '--with-mpfr-include=' + mpfr_path + '/src',
    '--with-mpc=' + mpc_path, '--with-mpc-include=' + mpc_path + '/src',
    # '--with-ils' + ils_path, '--with-ils-include=' + ils + '/src',
    '--disable-nls', '--disable-multilib', '--enable-languages=c,c++',
    '--without-headers']
  if settings['target']:
    command += ['--target=' + settings['target']]

  settings.setdefault('silent', False)
  options = {'print_cmd': True}
  if settings['silent']:
    print('note: peforming silent installation of GCC')
    options['devnull'] = True

  installlib.run(command, **options)
  installlib.run(['make', 'all-gcc', '-j', str(cpu_count())], **options)
  installlib.run(['make', 'install-gcc'], **options)
  installlib.run(['make', 'all-target-libgcc', '-j', str(cpu_count())], **options)
  installlib.run(['make', 'install-target-libgcc'], **options)

if __name__ == '__main__':
  main()
