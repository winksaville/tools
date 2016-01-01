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

import os
import installlib
import shutil
import stat
import re

GIT_URL = 'https://github.com/craftr-build/craftr.git'


def main():
  dst_dir = os.path.join(settings['prefix'], 'bin')
  code_dir = os.path.join(settings['prefix'], 'share', 'craftr')
  venv_dir = os.path.join(settings['prefix'], 'venv3')

  try:
    app = os.path.join(dst_dir, 'craftr')
    output = installlib.run([app, '-V'], piped=True).output
    version = re.search('Craftr\s+([\d\w\.\-]+)', output, re.I).group(1)
  except OSError as exc:
    version = None

  if version and version >= settings['min_version']:
    print("craftr {0} already installed".format(version))
    if not settings['force_install']:
      return
  elif version:
    print("craftr {0} already installed but doesn't match the minimum "
      "version required {1}".format(settings['min_version']))

  print("installing craftr {0} ...".format(settings['version']))
  if version:
    print("note: the existing installation of craftr {0} will be overwritten".format(version))

  shutil.rmtree(code_dir, ignore_errors=True)
  installlib.git_clone(GIT_URL, code_dir, branch=settings['version'], depth=5)
  os.chdir(code_dir)

  installlib.ensure_venv(venv_dir, 'python3')
  installlib.run_in_venv(venv_dir, ['pip', 'install', '-e', '.', '--upgrade'])

  # Create a script that runs craftr in the virtualenv.
  script_fn = os.path.join(dst_dir, 'craftr')
  script_src = (
    '#!/bin/bash\n'
    'VENV_DIR={venv}\n'
    'source "$VENV_DIR/bin/activate"\n'
    'craftr $*\n'
  ).format(venv=installlib.quote(venv_dir))
  with open(script_fn, 'w') as fp:
    fp.write(script_src)
  st = os.stat(script_fn)
  os.chmod(script_fn, st.st_mode | stat.S_IEXEC)


if __name__ == '__main__':
  main()
