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

# Arrays of paths for installing
DFLT_INSTALL_PATHS=("${DEFAULT_INSTALL_PREFIX_DIR}/bin" "${DEFAULT_INSTALL_PREFIX_DIR}/cross/bin")
ALT_INSTALL_PATHS=("${ALT_INSTALL_PREFIX_DIR}/bin" "${ALT_INSTALL_PREFIX_DIR}/cross/bin")
#echo ${DFLT_INSTALL_PATHS[@]}
#echo ${ALT_INSTALL_PATHS[@]}

declare -A test_installed_params

test_installed () {
  #echo test_installed: $@

  app=$1
  test_installed_params["getVersion"]="${THIS_DIR}/$1_install.py"
  test_installed_params["versionParam"]="--version"

  for param in "$@"; do
    #echo $param

    # param should be "name=value" split at the '='
    # and store in nameValueArray
    IFS='=' read -a nameValueArray <<< $param

    # Store the name and value into the test_installed_params dictionary
    test_installed_params["${nameValueArray[0]}"]=${nameValueArray[1]}
  done

  # Capture all of which's output so as to not spew console
  whichOutput=$(which ${app} 2>&1)
  whichExitCode=$?
  #echo whichExitCode=$whichExitCode
  #echo whichOutput=$whichOutput
  #echo PATH=$PATH

  # Check if ${app{ installed at all
  [[ ${whichExitCode} != 0 ]] && \
    echo ${app} not installed && exit 1

  # It was but is it in the expected directories
  whichDir=$(dirname ${whichOutput})
  OK=0
  for install_path in ${INSTALL_PATHS[@]}; do
    [[ "${whichDir}" == *"${install_path}"* ]] && OK=1
  done
  [[ ${OK} == 0 ]] && echo ${app} not installed in ${DFLT_INSTALL_PATHS[@]} && exit 1

  # Test if ${app} actual version is the expected version
  actualVer=$(${app} ${test_installed_params["versionParam"]} 2>&1)
  expectedVer=$(${test_installed_params["getVersion"]} printVer 2>&1)
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
  echo "Usage: $0 <full> | <quick>"
  echo "  full: does several installs and tests the results"
  echo "  quick: assumes previously installed and runs tests"
  exit 0
}

# If no parameters display help
if [[ $# == 0 ]]; then
  help
fi


INSTALL_PATHS=${DFLT_INSTALL_PATHS}
export PATH=${INSTALL_PATHS}:${ORG_PATH}

if [[ $1 == "quick" ]]; then
  test_all
  exit 0
fi

if [[ $1 == "full" ]]; then
  echo "test.sh: full install all"
  ${THIS_DIR}/install.py all

  # Test that everything was installed
  echo "test.sh: test_all"
  test_all

  # Test individual building and forced installation.
  # This is only a subset as it's already taking about
  # 30 minutes.
  echo "test.sh: install ninja meson --forceInstall"
  ${THIS_DIR}/install.py ninja meson --forceInstall
  which ninja
  ninja --version
  which meson
  meson -v

  # Test all again still using the DFLT_INSTALL_PATHS
  echo "test.sh: test_all after install ninja meson"
  test_all

  # Test we can install on the ALT prefixes without forceInstall
  echo "test.sh: install to ALT location without forceInstall"
  rm -rf ${ALT_CODE_PREFIX_DIR}
  rm -rf ${ALT_INSTALL_PREFIX_DIR}
  ${THIS_DIR}/install.py all --codePrefixDir ${ALT_CODE_PREFIX_DIR} --installPrefixDir ${ALT_INSTALL_PREFIX_DIR}

  # Test all on the ALT paths
  echo "test.sh: test_all ALT location"
  INSTALL_PATHS=${ALT_INSTALL_PATHS}
  export PATH=${INSTALL_PATHS}:${ORG_PATH}
  test_all
else
  help
fi
