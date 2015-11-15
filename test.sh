#!/usr/bin/env bash

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
# Install everything at the defaults


# Save current path and get the directory this file is in
ORG_PATH=$PATH
THIS_DIR=$(realpath $(dirname $0))

# Must match pareseisntallargs.py
DEFAULT_CODE_PREFIX_DIR=$HOME/tmp
DEFAULT_INSTALL_PREFIX_DIR=$HOME/opt
ALT_CODE_PREFIX_DIR=$HOME/tmpx
ALT_INSTALL_PREFIX_DIR=$HOME/optx

# Default install paths, we expect the executables
# to be installed in these paths
DFLT_INSTALL_PATHS=("${DEFAULT_INSTALL_PREFIX_DIR}/bin" "${DEFAULT_INSTALL_PREFIX_DIR}/cross/bin")
ALT_INSTALL_PATHS=("${ALT_INSTALL_PREFIX_DIR}/bin" "${ALT_INSTALL_PREFIX_DIR}/cross/bin")

add_install_paths_to_org_path () {
  declare -a ary1=("${!1}")
  export INSTALL_PATHS="${ary1[@]}"
  for install_path in "${ary1[@]}"; do
    export PATH=${install_path}:${PATH}
  done
}

# First parameter is the name of the app
#
# Second parameter is the is passed to the app to get its version
#
# Third parameter is the is code to get the expected version
test_installed () {
  app=$1
  versionParam=$2
  getExpectedVer=$3

  # Check if ${app} installed at all, capturing all of
  # which's output so as to not spew console
  whichOutput=$(which ${app} 2>&1)
  whichExitCode=$?
  [[ ${whichExitCode} != 0 ]] && echo ${app} not installed && exit 1

  # It is but is it in the expected directories ${INSTALL_PATHS} which
  # is a bash associative array and in the loop below we check it.
  whichDir=$(dirname ${whichOutput})
  OK=0
  for install_path in ${INSTALL_PATHS[@]}; do
    [[ "${whichDir}" == *"${install_path}"* ]] && OK=1
  done
  [[ ${OK} == 0 ]] && echo ${app} not installed in ${INSTALL_PATHS[@]} && exit 1

  # Now get the expected version
  expectedVer=$(${getExpectedVer} 2>&1)

  # Next get the actual version
  actualVer=$(${app} ${versionParam} 2>&1)

  # Finally verify the expectedVer is contained in the actualVer output
  [[ ${actualVer} != *"${expectedVer}"* ]] && \
    printf "$1 BAD version reported:\n-----\n${actualVer}\n-----\nBut expected ${expectedVer}\n" && exit 1

  echo $1 OK
}


test_all () {
  test_installed ninja "--version" "${THIS_DIR}/ninja_install.py printVer"
  test_installed meson "-v" "${THIS_DIR}/meson_install.py printVer"
  test_installed arm-eabi-ld "--version" "${THIS_DIR}/binutils_install.py printVer"
  test_installed arm-eabi-gdb "--version" "${THIS_DIR}/binutils_install.py printGdbVer"
  test_installed arm-eabi-gcc "--version" "${THIS_DIR}/gcc_install.py printVer"
  test_installed x86_64-pc-linux-ld "--version" "${THIS_DIR}/binutils_install.py printVer"
  test_installed x86_64-pc-linux-gdb "--version" "${THIS_DIR}/binutils_install.py printGdbVer"
  test_installed x86_64-pc-linux-gcc "--version" "${THIS_DIR}/gcc_install.py printVer"
  test_installed qemu-system-arm "--version" "${THIS_DIR}/qemu_install.py printVer"
}

help () {
  echo "Usage: $0 <full> | <quick> [install_prefix_dir]"
  echo "  full: does several installs and tests the results"
  echo "  quick: assumes previously installed and runs tests"
  echo "  install_prefix_dir: Optional paths to look for installed"
  echo "                      files. (default: ~/opt)"
  exit 0
}

# If no parameters display help
if [[ $# == 0 ]]; then
  help
fi

if [[ "$2" != "" ]]; then
  # User has supplied a default install prefix dir
  DEFAULT_INSTALL_PREFIX_DIR=$2
fi

# Add DFLT_INSTALL_PATHS to the orginal path
add_install_paths_to_org_path DFLT_INSTALL_PATHS[@]

if [[ $1 == "quick" ]]; then
  test_all
  exit 0
fi

if [[ $1 == "alt" ]]; then
  add_install_paths_to_org_path ALT_INSTALL_PATHS[@]
  test_all
  exit 0
fi

if [[ $1 == "full" ]]; then
  echo "test.sh: install all"
  ${THIS_DIR}/install.py all
  [[ $? != 0 ]] && echo "Error installing" && exit 1

  # Test that everything was installed
  echo "test.sh: test_all full"
  test_all

  # Test individual building and forced installation.
  # This is only a subset as it's already taking about
  # 30 minutes.
  echo "test.sh: install ninja meson --forceInstall"
  ${THIS_DIR}/install.py ninja meson --forceInstall
  [[ $? != 0 ]] && echo "Error forceInstall" && exit 1

  # Test all again still using the DFLT_INSTALL_PATHS
  echo "test.sh: test_all after install ninja meson"
  test_all

  # Test we can install on the ALT prefixes without forceInstall
  echo "test.sh: install to ALT location without forceInstall"
  rm -rf ${ALT_CODE_PREFIX_DIR}
  rm -rf ${ALT_INSTALL_PREFIX_DIR}
  ${THIS_DIR}/install.py all --codePrefixDir ${ALT_CODE_PREFIX_DIR} --installPrefixDir ${ALT_INSTALL_PREFIX_DIR}
  [[ $? != 0 ]] && echo "Error alternate install" && exit 1

  # Test all on the ALT paths
  add_install_paths_to_org_path ALT_INSTALL_PATHS[@]
  test_all
else
  help
fi
