# Vendor Install Tools

[![Build Status](https://travis-ci.org/winksaville/vendor-install-tools.svg?branch=NiklasRosenstein)](https://travis-ci.org/winksaville/vendor-install-tools)

This repository contains scripts to install the following packages
as a cross-compiling toolset.

- binutils
- [craftr](https://github.com/craftr-build/craftr)
- gcc
- [meson](https://github.com/mesonbuild/meson)
- [ninja](https://github.com/ninja-build/ninja)
- qemu

__Command Line Interface__

```
usage: install [-h] {gcc,craftr,ninja,meson,qemu,binutils,all} ...

positional arguments:
  {gcc,craftr,ninja,meson,qemu,binutils,all}
  options               Additional options to be passed to the installers,
                        must be prefixed with --. Standard options are
                        --prefix=~/opt, --temp=~/temp, --force-install=false
                        and --dry=false. You can specify an option for a
                        specific installer by prefixing the tool name like
                        --gcc:version=5.2.0 .

optional arguments:
  -h, --help            show this help message and exit
```
