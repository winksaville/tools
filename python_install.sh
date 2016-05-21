#!/bin/bash
# Install Python 3.5.1 to ${HOME}/opt/Python-3.5.1/bin/
#
# FORCE : Use TRUE to force the installation
# REQUESTED_PYTHON_VER : 3.5.1
# SRC_PREFIX_DIR : ${HOME}/opt/src
# INSTALL_PREFIX_DIR : ${HOME}/opt
#
# You can pass the environment variable by preceeding the command with the command
# so to force compiliation:
#   FORCE=TRUE ./python_install.sh
#
# or to compile 3.5.0
#   REQUESTED_PYTHON_VER=3.5.0 ./python_install.sh
#
# or to compile 3.5.0 to ${HOME}/srouces/ and ${HOME}/install/
#   REQUESTED_PYTHON_VER=3.5.0 SRC_PREFIX_DIR=${HOME}/sources INSTALL_PREFIX_DIR=${HOME}/install ./python_install.sh

[ "${REQUESTED_PYTHON_VER}" == "" ] && REQUESTED_PYTHON_VER="3.5.1"
#echo REQUESTED_PYTHON_VER=${REQUESTED_PYTHON_VER}

VERSION="$(python3 --version)"
#echo VERSION=${VERSION}

versionarray=(${VERSION})
#echo versionarray[0]=${versionarray[0]}
#echo versionarray[1]=${versionarray[1]}

[ "${SRC_PREFIX_DIR}" == "" ] && SRC_PREFIX_DIR=${HOME}/opt/src
#echo SRC_PREFIX_DIR=${SRC_PREFIX_DIR}
[ "${INSTALL_PREFIX_DIR}" == "" ] && INSTALL_PREFIX_DIR=${HOME}/opt
#echo INSTALL_PREFIX_DIR=${INSTALL_PREFIX_DIR}

if [[ "${REQUESTED_PYTHON_VER}" != "${versionarray[1]}" ]] || [[ "${FORCE}" == "TRUE" ]]; then
  name=Python-${REQUESTED_PYTHON_VER}
  mkdir -p ${SRC_PREFIX_DIR}
  mkdir -p ${INSTALL_PREFIX_DIR}/${name}
  wget https://www.python.org/ftp/python/${REQUESTED_PYTHON_VER}/${name}.tgz
  tar -xf ${name}.tgz -C ${SRC_PREFIX_DIR}
  cd ${SRC_PREFIX_DIR}/${name}/
  ./configure --prefix=${INSTALL_PREFIX_DIR}/${name}
  make
  #make test
  make install
else
  echo Python version is \"${VERSION}\"
fi
