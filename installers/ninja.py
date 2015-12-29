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

GIT_URL = 'https://github.com/martine/ninja.git'

def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')
  dst_bin = os.path.join(dst_dir, 'ninja')

  # Check if ninja is already installed, and if it has the version we want.
  try:
    output = installlib.run_piped([dst_bin, '--version'], check=False).stdout
  except OSError:
    output = None
  if output and output.startswith(settings['version']):
    print('ninja {0} already installed'.format(settings['version']))
    if not settings['force_install']:
      return

  print('installing ninja {0} ...'.format(settings['version']))
  if output:
    print('note: existing installation of ninja will be overwritten')

  code_dir = os.path.join(settings['temp'], 'ninja')
  branch = 'v{0}'.format(settings['version'])
  shutil.rmtree(code_dir, ignore_errors=True)
  installlib.makedirs(code_dir)
  installlib.git_clone(GIT_URL, code_dir, branch=branch, depth=5)
  os.chdir(code_dir)

  # Compile ninja
  installlib.run(['./configure.py', '--bootstrap'])

  # Copy the ninja executable to the bin directory.
  installlib.makedirs(dst_dir)
  shutil.rmtree(dst_bin, ignore_errors=True)
  shutil.copy2('ninja', dst_bin)

if __name__ == '__main__':
  main()
