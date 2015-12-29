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

APP = 'qemu-system-arm'
GIT_URL = 'git://git.qemu.org/qemu.git'

def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')
  dst_bin = os.path.join(dst_dir, APP)

  try:
    output = installlib.run_piped([dst_bin, '--version']).stdout
  except OSError:
    output = None
  if output and settings['version'] in output:
    print('{0} {1} already installed'.format(APP, settings['version']))
    if not settings['force_install']:
      return

  print('installing {0} {1} ...'.format(APP, settings['version']))
  if output:
    print('note: existing installation of {0} will be overwritten'.format(APP, settings['version']))

  code_dir = os.path.join(settings['temp'], APP)
  branch = 'v{0}'.format(settings['co_version'])
  shutil.rmtree(code_dir, ignore_errors=True)
  installlib.git_clone(GIT_URL, code_dir, branch=branch, depth=5, recursive=False)
  os.chdir(code_dir)
  installlib.git('submodule', 'update', '--init', 'dtc')

  installlib.makedirs('build')
  os.chdir('build')
  installlib.run(['../configure', '--prefix={0}'.format(settings['prefix']),
    '--target-list=arm-softmmu,arm-linux-user', '--python=python2'])
  installlib.run(['make', '-j', str(cpu_count())])
  installlib.run(['make', 'install'])

if __name__ == '__main__':
  main()
