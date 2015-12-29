# Vendor Install Tools

This repository contains scripts to install the following packages
as a cross-compiling toolset.

- binutils
- gcc
- meson
- ninja
- qemu

__Command Line Interface___

```
usage: install [-h] {ninja,gcc,meson,qemu,binutils,all} ...

positional arguments:
  {ninja,gcc,meson,qemu,binutils,all}
  options               Additional options to be passed to the installers,
                        must be prefixed with --. Standard options are
                        --prefix=~/opt, --temp=~/temp, --force-install=false
                        and --dry=false. You can specify an option for a
                        specific installer by prefixing the tool name like
                        --gcc:version=5.2.0 .

optional arguments:
  -h, --help            show this help message and exit
```
