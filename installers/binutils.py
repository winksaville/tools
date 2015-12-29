# Copyright (C) 2015 Niklas Rosenstein
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

import os
import shutil
import installlib

try:
  from multiprocessing import cpu_count
except ImportError:
  cpu_count = lambda: 1

APP = 'binutils'
APP_VERSION_BIN = 'ld'
GIT_URL = 'git://sourceware.org/git/binutils-gdb.git'

def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')

  try:
    app = APP_VERSION_BIN
    if settings['target']:
      app = settings['target'] + '-' + app
    app = os.path.join(dst_dir, app)
    output = installlib.run_piped([app, '--version']).stdout
  except OSError:
    output = None
  if output and settings['version'] in output:
    print('{0} {1} already installed'.format(APP, settings['version']))
    if not settings['force_install']:
      return

  print('installing {0} {1} ...'.format(APP, settings['version']))
  if output:
    print('note: existing installation of {1} {0} will be removed'.format(APP, settings['version']))

  if settings['dry']:
    return

  code_dir = os.path.join(settings['temp'], APP)
  branch = 'binutils-{0}'.format(settings['version'].replace('.', '_'))
  shutil.rmtree(code_dir, ignore_errors=True)
  installlib.git_clone(GIT_URL, code_dir, branch=branch, depth=5)
  os.chdir(code_dir)

  installlib.makedirs('build')
  os.chdir('build')

  config_cmd = ['../configure', '--prefix={0}'.format(settings['prefix']), '--disable-nls']
  if settings['target']:
    config_cmd += ['--target={0}'.format(settings['target'])]
  installlib.run(config_cmd)  # xxx: too much logging output for Travis CI?
  installlib.run(['make', 'all', '-j', str(cpu_count())])
  installlib.run(['make', 'install'])

if __name__ == '__main__':
  main()
