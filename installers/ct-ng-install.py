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
#
# Options:
# - target (required)
# - no_menuconfig (optional, False)
# - reconfig (optional, False)

import os
import installlib
import shutil


def main():
  target = settings.get('target')
  if not target:
    print('error: ct-ng-install:target not specified.')
    return 1

  # xxx: check if the toolset is already installed!

  no_menuconfig = settings.get('no_menuconfig', False)
  reconfig = settings.get('reconfig', False)
  dst_dir = os.path.join(settings['prefix'], 'cross', target)
  cfg_file = os.path.join(dst_dir, '.config')
  if not os.path.exists(cfg_file) or reconfig:
    if no_menuconfig:
      print('error: configuration file {0!r} does not exist'.format(config_file))
      return 1
    # xxx: should we always flush the original configuration?
    shutil.rmtree(dst_dir, ignore_errors=True)
    installlib.makedirs(dst_dir)
    installlib.run(['ct-ng', 'menuconfig'], stderr=installlib.PIPE, cwd=dst_dir)
    if not os.path.isfile(cfg_file):
      print('error: ct-ng menuconfig did not save a .config file')
      return 1

  print('installing {0} with crosstool-ng to {1!r}'.format(target, dst_dir))
  os.chdir(dst_dir)
  installlib.run(['ct-ng', 'build.4'])


if __name__ == '__main__':
  main()
