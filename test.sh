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


test_installed () {
  # Declare in local scope
  declare -A params

  app=$1
  params[getVersion]="${THIS_DIR}/$1_install.py"
  params[versionParam]="--version"

  for param in "$@"; do
    #echo param=$param

    # param should be "name=value" split at the '='
    # and store in nameValueArray
    IFS="=" read -a nameValueArray <<< "$param"
    #echo nameValueArray[0]=${nameValueArray[0]}
    #echo nameValueArray[1]=${nameValueArray[1]}

    # Store the name and value into the params dictionary
    params[${nameValueArray[0]}]=${nameValueArray[1]}
    #echo params keys="${!params[@]}"
    #echo params values="${params[@]}"
  done

  # Capture all of which's output so as to not spew console
  whichOutput=$(which ${app} 2>&1)
  whichExitCode=$?
  #echo whichExitCode=$whichExitCode
  #echo whichOutput=$whichOutput
  #echo PATH=$PATH

  # Check if ${app{ installed at all
  [[ ${whichExitCode} != 0 ]] && echo ${app} not installed && exit 1

  # It was but is it in the expected directories
  whichDir=$(dirname ${whichOutput})
  OK=0
  for install_path in ${INSTALL_PATHS[@]}; do
    [[ "${whichDir}" == *"${install_path}"* ]] && OK=1
  done
  [[ ${OK} == 0 ]] && echo ${app} not installed in ${INSTALL_PATHS[@]} && exit 1

  # Test if ${app} actual version is the expected version
  actualVer=$(${app} ${params[versionParam]} 2>&1)
  expectedVer=$(${params[getVersion]} printVer 2>&1)
  [[ ${actualVer} != *"${expectedVer}"* ]] && \
    echo ${app} is ${actualVer} expected ${expectedVer} && exit 1

  echo ${app} OK
}

test_all () {
  test_installed ninja
  test_installed meson versionParam=-v
  test_installed arm-eabi-ld getVersion=${THIS_DIR}/binutils_install.py
  test_installed qemu-system-arm getVersion=${THIS_DIR}/qemu_install.py

  #TODO: gcc is not the same version as binutils, need a fix
  #test_installed arm-eabi-gcc getVersion=${THIS_DIR}/binutils_install.py
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

DFLT_INSTALL_PATHS=("${DEFAULT_INSTALL_PREFIX_DIR}/bin" "${DEFAULT_INSTALL_PREFIX_DIR}/cross/bin")
ALT_INSTALL_PATHS=("${ALT_INSTALL_PREFIX_DIR}/bin" "${ALT_INSTALL_PREFIX_DIR}/cross/bin")

# Add DFLT's to PATH
INSTALL_PATHS="${DFLT_INSTALL_PATHS[@]}"
export PATH=${INSTALL_PATHS}:${ORG_PATH}

if [[ $1 == "quick" ]]; then
  test_all
  exit 0
fi

if [[ $1 == "full" ]]; then
  ${THIS_DIR}/install.py all
  [[ $? != 0 ]] && echo "Error installing" && exit 1

  # Test that everything was installed
  echo "test.sh: test_all"
  test_all

  # Test individual building and forced installation.
  # This is only a subset as it's already taking about
  # 30 minutes.
  echo "test.sh: install ninja meson --forceInstall"
  ${THIS_DIR}/install.py ninja meson --forceInstall
  [[ $? != 0 ]] && echo "Error forceInstall" && exit 1

  # Test all again still using the INSTALL_PATHS
  echo "test.sh: test_all after install ninja meson"
  test_all

  # Test we can install on the ALT prefixes without forceInstall
  echo "test.sh: install to ALT location without forceInstall"
  rm -rf ${ALT_CODE_PREFIX_DIR}
  rm -rf ${ALT_INSTALL_PREFIX_DIR}
  ${THIS_DIR}/install.py all --codePrefixDir ${ALT_CODE_PREFIX_DIR} --installPrefixDir ${ALT_INSTALL_PREFIX_DIR}
  [[ $? != 0 ]] && echo "Error alternate install" && exit 1

  # Test all on the ALT paths
  echo "test.sh: test_all ALT location"
  INSTALL_PATHS=${ALT_INSTALL_PATHS}
  export PATH=${INSTALL_PATHS}:${ORG_PATH}
  test_all
else
  help
fi
