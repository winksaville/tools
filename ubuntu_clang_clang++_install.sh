# Install clang & clang++
[ "${CLANG_VERSION}" == "" ] && CLANG_VERSION=3.8

###
# get_version
#
# @param $1 = app
#
# @out_variable = version
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
  #echo "cur_ver_array[3]=${cur_ver_array[3]}"

  # Split version on '.' and from the version triple
  local SAVE_IFS=$IFS
  local SPLIT_DOT=""
  IFS='.'; SPLIT_DOT=(${cur_ver_array[2]})
  version="${SPLIT_DOT[0]}.${SPLIT_DOT[1]}"
  IFS=$SAVE_IFS
}

get_ver clang
#echo "version="${version}"
clang_ver=${version}
echo "clang_ver=${clang_ver}"
get_ver clang++
#echo "version="${version}"
clangpp_ver=${version}
echo "clangpp_ver=${clangpp_ver}"

if [ "${clang_ver}" != "${CLANG_VERSION}" ] || [ "${clangpp_ver}" != "${CLANG_VERSION}" ] ; then
  echo "add llvm-toolchain to srouces.list" ;
  sudo sh -c 'echo "deb http://llvm.org/apt/trusty/ llvm-toolchain-trusty-${CLANG_VERSION} main" >> /etc/apt/sources.list'
  sudo apt-get update
else
  echo "Skipping clang/glang++ install, versions are ${CLANG_VERSION}"
fi

[ "${clang_ver}" != "${CLANG_VERSION}" ] && \
  echo "install clang" && \
  sudo apt-get install clang-${CLANG_VERSION} && \
  sudo update-alternatives --install /usr/bin/clang clang /usr/bin/clang-${GCC_VERSION} 100

[ "${clangpp_ver}" != "${CLANG_VERSION}" ] && \
  echo "install clang++" && \
  sudo apt-get install clang++-${CLANG_VERSION} && \
  sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-${GCC_VERSION} 100

