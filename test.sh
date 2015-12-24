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
DFLT_INSTALL_PATHS=("${DEFAULT_INSTALL_PREFIX_DIR}/bin"
  "${DEFAULT_INSTALL_PREFIX_DIR}/cross/bin"
  "${DEFAULT_INSTALL_PREFIX_DIR}/x-tools/x86_64-unknown-elf/bin"
  "${DEFAULT_INSTALL_PREFIX_DIR}/x-tools/i386-unknown-elf/bin"
  "${DEFAULT_INSTALL_PREFIX_DIR}/x-tools/arm-unknown-eabi/bin")

ALT_INSTALL_PATHS=("${ALT_INSTALL_PREFIX_DIR}/bin"
  "${ALT_INSTALL_PREFIX_DIR}/cross/bin"
  "${ALT_INSTALL_PREFIX_DIR}/x-tools/x86_64-unknown-elf/bin"
  "${ALT_INSTALL_PREFIX_DIR}/x-tools/i386-unknown-elf/bin"
  "${ALT_INSTALL_PREFIX_DIR}/x-tools/arm-unknown-eabi/bin")

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
  test_installed ct-ng "version" "${THIS_DIR}/crosstool_ng_install.py printVer"
  #test_installed arm-eabi-ld "--version" "${THIS_DIR}/binutils_install.py printVer"
  #test_installed arm-eabi-gdb "--version" "${THIS_DIR}/binutils_install.py printGdbVer"
  #test_installed arm-eabi-gcc "--version" "${THIS_DIR}/gcc_install.py printVer"
  test_installed x86_64-unknown-elf-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
  test_installed x86_64-unknown-elf-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
  test_installed i386-unknown-elf-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
  test_installed i386-unknown-elf-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
  test_installed arm-unknown-eabi-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
  test_installed arm-unknown-eabi-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
  test_installed qemu-system-arm "--version" "${THIS_DIR}/qemu_install.py printVer"
}


install_all () {
  echo "test.sh: install all"
  ${THIS_DIR}/install.py all
  [[ $? != 0 ]] && echo "Error installing" && exit 1

  # Test that everything was installed
  echo "test.sh: test_all full"
  test_all
}

force_install () {
  # Test individual building and forced installation.
  # This is only a subset as it's already taking about
  # 30 minutes.
  echo "test.sh: install ninja meson --forceInstall"
  ${THIS_DIR}/install.py ninja meson --forceInstall
  [[ $? != 0 ]] && echo "Error forceInstall" && exit 1

  # Test ninja and meson again
  test_installed ninja "--version" "${THIS_DIR}/ninja_install.py printVer"
  test_installed meson "-v" "${THIS_DIR}/meson_install.py printVer"
}

alt_install() {
  # Test we can install on the ALT prefixes without forceInstall
  echo "test.sh: install to ALT location without forceInstall"
  rm -rf ${ALT_CODE_PREFIX_DIR}
  rm -rf ${ALT_INSTALL_PREFIX_DIR}
  ${THIS_DIR}/install.py all --codePrefixDir ${ALT_CODE_PREFIX_DIR} --installPrefixDir ${ALT_INSTALL_PREFIX_DIR}
  [[ $? != 0 ]] && echo "Error alternate install" && exit 1

  # Test all on the ALT paths
  add_install_paths_to_org_path ALT_INSTALL_PATHS[@]
  test_all
}

full_install() {
  install_all
  force_install
  alt_install
}

help () {
  echo "Usage: $0 <parameters> [install_prefix_dir]"
  echo "Parameters:"
  echo "  app: ninja | meson | ct-ng"
  #echo "       arm-eabi-gdb | arm-eabi-ld | arm-eabi-gcc"
  echo "       x86_64-unknown-elf-ld | x86_64-unknown-elf-gcc"
  echo "       i386-unknown-elf-ld | i386-unknown-elf-gcc"
  echo "       arm-unknown-eabi-ld | arm-unknown-eabi-gcc"
  echo "       qemu-system-arm"
  echo "  quick: assumes previously installed and runs tests"
  echo "  install_all: install all"
  echo "  force_install: force install ninja and meson"
  echo "  alt_install: reinstall all at an alternate code"
  echo "               and install prefix directories"
  echo "  full: install_all, force_install and alt_install"
  echo ""
  echo "Optional parameters"
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

case $1 in
"quick")
  test_all
  ;;
"install_all")
  install_all
  ;;
"force_install")
  force_install
  ;;
"alt_install")
  alt_install
  ;;
"full")
  full_install
  ;;
"ninja")
  test_installed ninja "--version" "${THIS_DIR}/ninja_install.py printVer"
  ;;
"meson")
  test_installed meson "-v" "${THIS_DIR}/meson_install.py printVer"
  ;;
"ct-ng")
  test_installed ct-ng "version" "${THIS_DIR}/crosstool_ng_install.py printVer"
  ;;
"arm-eabi-ld")
  test_installed arm-eabi-ld "--version" "${THIS_DIR}/binutils_install.py printVer"
  ;;
"arm-eabi-gdb")
  test_installed arm-eabi-gdb "--version" "${THIS_DIR}/binutils_install.py printGdbVer"
  ;;
"arm-eabi-gcc")
  test_installed arm-eabi-gcc "--version" "${THIS_DIR}/gcc_install.py printVer"
  ;;
"qemu-system-arm")
  test_installed qemu-system-arm "--version" "${THIS_DIR}/qemu_install.py printVer"
  ;;
"x86_64-unknown-elf-ld")
   test_installed x86_64-unknown-elf-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
   ;;
"x86_64-unknown-elf-gcc")
   test_installed x86_64-unknown-elf-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
   ;;
"i386-unknown-elf-ld")
   test_installed i386-unknown-elf-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
   ;;
"i386-unknown-elf-gcc")
   test_installed i386-unknown-elf-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
   ;;
"arm-unknown-eabi-ld")
   test_installed arm-unknown-eabi-ld "--version" "${THIS_DIR}/ct_ng_runner.py printBinuVer"
   ;;
"i386-unknown-elf-gcc")
   test_installed arm-unknown-eabi-gcc "--version" "${THIS_DIR}/ct_ng_runner.py printGccVer"
   ;;
*)
  help
  ;;
esac
