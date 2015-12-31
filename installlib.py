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
import posixpath
import re
import runpy
import subprocess
import tempfile
import traceback
import tarfile
import zipfile

from subprocess import STDOUT, PIPE

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
  @property
  def output(self):
    return self.stdout
  def check_returncode(self):
    if self.returncode != 0:
      raise CalledProcessError(self.returncode, self.args, self.stdout, self.stderr)

def run(command, **kwargs):
  devnull = kwargs.pop('devnull', False)
  piped = kwargs.pop('piped', False)
  merge_pipes = kwargs.pop('merge_pipes', True)
  if piped:
    if devnull:
      raise TypeError('conflicting arguments piped and devnull')
    if not kwargs.get('stdout'):
      kwargs['stdout'] = subprocess.PIPE
    if not kwargs.get('stderr'):
      if merge_pipes:
        kwargs['stderr'] = subprocess.STDOUT
      else:
        kwargs['stderr'] = subprocess.STDERR
  elif devnull:
    if hasattr(subprocess, 'DEVNULL'):
      dev = subprocess.DEVNULL
    else:
      dev = open(os.devnull, 'wb')
      kwargs['close_fds'] = True
    kwargs['stdout'] = dev
    kwargs['stderr'] = dev

  encoding = kwargs.pop('encoding', sys.getdefaultencoding())
  check = kwargs.pop('check', True)
  print_cmd = kwargs.pop('print_cmd', False)
  if kwargs.get('shell') and not isinstance(command, str):
    command = quote_args(command)

  if print_cmd:
    if isinstance(command, str):
      print('$', command)
    else:
      print('$', quote_args(command))

  process = subprocess.Popen(command, **kwargs)
  stdout, stderr = process.communicate()
  if encoding:
    if stdout:
      stdout = stdout.decode(encoding)
    if stderr:
      stderr = stderr.decode(encoding)
  result = CompletedProcess(command, process.returncode, stdout, stderr)
  if check:
    result.check_returncode()
  return result

def run_piped(command, **kwargs):
  kwargs.setdefault('merge_pipes', True)
  return run(command, piped=True, **kwargs)

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

def download_extract(url, directory, temp=None, strip_components=0):
  ''' Downloads the file at the specified *url* using wget and
  extracts its contents using tar, stripping the number of specified
  components. '''

  makedirs(directory)
  if temp is not None:
    makedirs(temp)
    basename = posixpath.basename(url)
    temp_fn = os.path.join(temp, basename)
  else:
    fd, temp_fn = tempfile.mkstemp()
    os.close(fd)

  try:
    if not temp or not os.path.isfile(temp_fn):
      print("  Downloading", url)
      try:
        cmd = ['wget', '--timeout=20', '-qO-', url, safe('>'), temp_fn]
        if wget_version() >= '1.16.1':
          # Are there older versions that support this option?
          cmd.insert(4, '--show-progress')
        run(cmd, shell=True)
      except BaseException as exc:
        # We delete the file if anything happened while downloading it.
        os.remove(temp_fn)
        raise
    else:
      print("  Already downloaded", basename)
    print("  Extracting to", directory)
    run(['tar', '-xf', temp_fn, '--strip-components=%d' % strip_components, '-C', directory])
  finally:
    if not temp and os.path.isfile(temp_fn):
      # Only delete the downloaded file if its a "system" temporary file
      # and was not downloaded to an explicit temporary directory.
      os.remove(temp_fn)

def wget_version():
  ''' Returns the version number of WGet. '''

  if not hasattr(wget_version, '_version'):
    output = run(['wget', '-V'], piped=True).output
    version = re.search('WGet\s+([\d\.]+)', output, re.I)
    if not version:
      raise RuntimeError('could not determine WGet version')
    wget_version._version = version.group(1)
  return wget_version._version

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

def register(name, script, deps=(), default_install=True, **settings):
  ''' Register an installer script. '''

  installers[name] = {
    'script': script, 'settings': settings,
    'deps': deps, 'default_install': default_install,
  }

class InstallSession(object):

  def __init__(self):
    self.options = {}
    self.tool_options = {}
    self.installed = set()

  def install(self, name, required_by=None):
    if name in self.installed:
      return

    try:
      installer = installers[name]
    except KeyError:
      message = 'no installer for {name!r} '
      if required_by:
        message += '(required by {req!r}) '
      message += 'available'
      raise ValueError(message.format(name=name, req=required_by))

    settings = installer['settings'].copy()
    settings.update(self.options)
    settings.update(self.tool_options.get(name, {}))

    self.installed.add(name)
    for dep in installer['deps']:
      self.install(dep, name)

    if settings.get('dry', False):
      print('note: dry installation of', name)

    try:
      runpy.run_path(installer['script'], {'settings': settings}, run_name='__main__')
    except SystemExit as exc:
      raise
    except BaseException as exc:
      traceback.print_exc()
      print('error installing {0}. quit'.format(name))
      raise SystemExit(1)

# ============================================================================
# ============================================================================

import argparse

def main():
  choices = list(installers.keys())
  choices.append('all')

  parser = argparse.ArgumentParser()
  parser.add_argument('targets', nargs='+', choices=choices, metavar='TOOL')
  parser.add_argument('options', nargs='...', help=''
    'Additional options to be passed to the installers, must be '
    'prefixed with --. Standard options are --prefix=~/opt, --temp=~/temp, '
    '--force-install=false and --dry=false. You can specify an option for a '
    'specific installer by prefixing the tool name like --gcc:version=5.2.0 .')

  args = parser.parse_args()
  cwd = os.getcwd()

  # Parse additional options.
  session = InstallSession()
  for option in args.options:
    if not option.startswith('--'):
      parser.error('additional options must start with --')
    key, sep, value = option[2:].partition('=')
    if not key:
      parser.error('invalid option {0!r}'.format(option))
    if not sep:
      value = True
    elif value.lower() == 'true':
      value = True
    elif value.lower() == 'false':
      value = False
    if ':' in key:
      tool_name, _, sub_key = key.partition(':')
      if not sub_key:
        parser.error('invalid option {0!r}'.format(option))
      if tool_name not in choices:
        parser.error('unknown tool {0!r} in option {1!r}'.format(tool_name, option))
      sub_key = sub_key.replace('-', '_')
      session.tool_options.setdefault(tool_name, {})[sub_key] = value
    else:
      key = key.replace('-', '_')
      session.options[key] = value

  session.options.setdefault('prefix', os.path.expanduser('~/opt'))
  session.options.setdefault('temp', os.path.expanduser('~/tmp'))
  session.options.setdefault('force_install', False)
  session.options.setdefault('dry', False)

  if args.targets == ['all']:
    tools = sorted(x[0] for x in installers.items() if x[1]['default_install'])
  else:
    tools = args.targets
  for name in tools:
    session.install(name)
    os.chdir(cwd)
