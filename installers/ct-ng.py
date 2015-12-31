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

GIT_URL = 'https://github.com/crosstool-ng/crosstool-ng.git'


def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')
  code_dir = os.path.join(settings['temp'], 'crosstool-ng')

  try:
    app = os.path.join(dst_dir, 'ct-ng')
    output = installlib.run_piped([app, 'version']).output
  except OSError as exc:
    output = None

  if output and settings['version'] in output:
    print('crosstools-ng {0} already installed'.format(settings['version']))
    if not settings['force_install']:
      return

  print('installing crosstools-ng {0} ...'.format(settings['version']))
  if output:
    print('note: existing installation of crosstools-ng will be overwritten')

  shutil.rmtree(code_dir, ignore_errors=True)
  branch = 'crosstool-ng-' + settings['version']
  installlib.git_clone(GIT_URL, code_dir, branch=branch, depth=5)

  os.chdir(code_dir)
  installlib.run(['./bootstrap'])
  installlib.run(['./configure', '--prefix=' + settings['prefix']])
  installlib.run(['make'])
  installlib.run(['make', 'install'])


if __name__ == '__main__':
  main()
