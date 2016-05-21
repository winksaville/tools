# Install gcc/g++ 5 because options -Wpednatic and -std
# are not in older compilers and they generate unknown
# command line option errors. The update-alternatives
# makes the compilers the default.
[ "${GCC_VERSION}" == "" ] && GCC_VERSION=6

###
# get_version
#
# @param $1 = app
#
# @out_variable = ver_triple
##
get_ver () {
  #echo get_ver $1
  local CUR_VER="$($1 --version)"
  #echo "CUR_VER=${CUR_VER}"
  local cur_ver_array=(${CUR_VER})
  #echo "cur_ver_array=${cur_ver_array[@]}"
  #echo "cur_ver_array[0]=${cur_ver_array[0]}"
  #echo "cur_ver_array[1]=${cur_ver_array[1]}"
  #echo "cur_ver_array[2]=${cur_ver_array[2]}"
  
  # Split version on '.' and from the version triple
  local SAVE_IFS=$IFS
  IFS='.'; ver_triple=(${cur_ver_array[2]})
  IFS=$SAVE_IFS
}

get_ver gcc
#echo "ver_triple=${ver_triple[@]}"
gcc_ver=${ver_triple[0]}
echo "gcc_ver=${gcc_ver}"
get_ver g++
#echo "ver_triple=${ver_triple[@]}"
gpp_ver=${ver_triple[0]}
echo "g++_ver=${gpp_ver}"

if [ "${gcc_ver}" != "${GCC_VERSION}" ] || [ "${gpp_ver}" != "${GCC_VERSION}" ] ; then
  echo "add-apt-repository" ;
  sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
  sudo apt-get update
else
  echo "Skipping gcc/g++ install, versions are ${GCC_VERSION}"
fi

[ "${gcc_ver}" != "${GCC_VERSION}" ] && \
  echo "install gcc" && \
  sudo apt-get install gcc-${GCC_VERSION} && \
  sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${GCC_VERSION} 100

[ "${gpp_ver}" != "${GCC_VERSION}" ] && \
  echo "install g++" && \
  sudo apt-get install g++-${GCC_VERSION} && \
  sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-${GCC_VERSION} 100

