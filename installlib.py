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
''' Base library for installers. Compatible with Python 2 and 3. '''

from __future__ import print_function
import os
import sys
import runpy
import subprocess
import tempfile
import tarfile
import zipfile

string_type = (str if sys.version_info[0] == 3 else basestring)

try:
  from shlex import quote as _quote
except ImportError:
  from pipes import quote as _quote

try:
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen

# ============================================================================
# A re-implementation of Python 3.5's subprocess.run() interface.
# The only difference is that run() will always check the returncode
# by default.
# ============================================================================

class CalledProcessError(OSError):
  def __init__(self, returncode, cmd, output=None, stderr=None):
    self.returncode = returncode
    self.cmd = cmd
    self.output = output
    self.stderr = stderr
  def __str__(self):
    fmt = 'Command {0!r} exited with non-zero exit status {1}'
    return fmt.format(self.cmd, self.returncode)
  @property
  def stdout(self):
    return self.output
  @stdout.setter
  def stdout(self, value):
    self.output = value

class CompletedProcess(object):
  def __init__(self, args, returncode, stdout=None, stderr=None):
    super(CompletedProcess, self).__init__()
    self.args = args
    self.returncode = returncode
    self.stdout = stdout
    self.stderr = stderr
  def __repr__(self):
    parts = [('args', self.args), ('returncode', self.returncode)]
    if self.stdout is not None:
      parts.append(('stdout', self.stdout))
    if self.stderr is not None:
      parts.append(('stderr', self.stderr))
    content = ', '.join('{0}={1!r}'.format(*x) for x in parts)
    return 'CompletedProcess({0})'.format(content)
  def check_returncode(self):
    if self.returncode != 0:
      raise CalledProcessError(self.returncode, self.args, self.stdout, self.stderr)

def run(command, *args, **kwargs):
  encoding = kwargs.pop('encoding', sys.getdefaultencoding())
  check = kwargs.pop('check', True)
  if kwargs.get('shell') and not isinstance(command, str):
    command = quote_args(command)
  process = subprocess.Popen(command, *args, **kwargs)
  stdout, stderr = process.communicate()
  if encoding:
    if stdout:
      stdout = stdout.decode(encoding)
    if stderr:
      stderr = stdout.decode(encoding)
  result = CompletedProcess(command, process.returncode, stdout, stderr)
  if check:
    result.check_returncode()
  return result

def run_piped(command, *args, **kwargs):
  merge = kwargs.pop('merge', True)
  stderr = subprocess.STDOUT if merge else subprocess.PIPE
  return run(command, *args, stdout=subprocess.PIPE, stderr=stderr, **kwargs)

def run_in_venv(venv_path, command, *args, **kwargs):
  if isinstance(command, string_type):
    command = [command]
  if os.name == 'nt':
    activate = os.path.join(venv_path, 'Scripts', 'activate.bat')
    command = quote(activate) + ' & ' + quote_args(command)
  else:
    activate = os.path.join(venv_path, 'bin', 'activate')
    command = '. ' + quote(activate) + ' ; ' + quote_args(command)
  if not os.path.isfile(activate):
    raise ValueError('virtualenv does not exist or is invalid', venv_path)
  return run(command, *args, shell=True, **kwargs)

def quote(arg):
  if isinstance(arg, safe):
    return str(arg)
  return _quote(arg)

def quote_args(args):
  return ' '.join(map(quote, args))

class safe(object):
  def __init__(self, string):
    self.string = string
  def __str__(self):
    return self.string

# ============================================================================
# ============================================================================

def git(*args, **kwargs):
  ''' Simple wrapper for calling git. '''

  command = ['git']
  command += args
  return run(command, **kwargs)

def git_clone(url, directory=None, branch=None, depth=None, recursive=True, **kwargs):
  ''' Clone a git repository at *url* to the specified *directory*.
  With *branch*, you can specify the branch or git tag to clone from.
  The *depth* specifies the number of commits to download. '''

  command = ['git', 'clone', url]
  command += [directory] if directory else []
  command += ['--branch', branch] if branch else []
  command += ['--depth', str(depth)] if depth else []
  command += ['--recursive'] if recursive else []
  return run(command, **kwargs)

def download_extract(url, directory, strip_components=0):
  ''' Downloads the file at the specified *url* using wget and
  extracts its contents using tar, stripping the number of specified
  components. '''

  makedirs(directory)
  with tempfile.NamedTemporaryFile(delete=False) as dst:
    dst.close()
    try:
      print("  Downloading", url)
      run(['wget', '--timeout=20', '-qO-', url, safe('>'), dst.name], shell=True)
      print("  Extracting to", directory)
      run(['tar', '-xf', dst.name, '--strip-components=%d' % strip_components,
        '-C', directory])
    finally:
      os.remove(dst.name)

def ensure_venv(directory, python_bin='python'):
  ''' Ensures that a virtual environment at *directory* exists. If it
  does not, it will be created with the specified *python_bin*. '''

  if not os.path.isdir(directory):
    return run(['virtualenv', '--python', python_bin, directory])
  return None

def makedirs(dirname):
  if not os.path.isdir(dirname):
    os.makedirs(dirname)

# ============================================================================
# ============================================================================

installers = {}

def register(name, script, deps=(), **settings):
  ''' Register an installer script. '''

  installers[name] = {
    'script': script, 'settings': settings,
    'deps': deps, 'installed': False
  }

def install(name, required_by=None, **override_settings):
  try:
    installer = installers[name]
  except KeyError:
    message = 'no installer for {name!r} '
    if required_by:
      message += '(required by {req!r}) '
    message += 'available'
    raise ValueError(message.format(name=name, req=required_by))

  if installer['installed']:
    return
  installer['installed'] = True
  for dep in installer['deps']:
    install(dep, name)
  settings  = installer['settings'].copy()
  settings.update(override_settings)
  runpy.run_path(installer['script'], {'settings': settings}, run_name='__main__')

# ============================================================================
# ============================================================================

import argparse

def main():
  choices = list(installers.keys())
  choices.append('all')

  parser = argparse.ArgumentParser()
  parser.add_argument('target', choices=choices)
  parser.add_argument('--prefix', default='~/opt')
  parser.add_argument('--temp', default='~/tmp')
  parser.add_argument('--force', action='store_true')
  args = parser.parse_args()
  args.prefix = os.path.abspath(os.path.expanduser(args.prefix))
  args.temp = os.path.abspath(os.path.expanduser(args.temp))
  cwd = os.getcwd()

  settings = {'prefix': args.prefix, 'temp': args.temp, 'force_install': args.force}
  if args.target == 'all':
    for name in sorted(installers):
      install(name, **settings)
      os.chdir(cwd)
  else:
    install(args.target, **settings)
