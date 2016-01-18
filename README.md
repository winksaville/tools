# Vendor install tools

This has scripts for installing third party vendor tools
such as binutils, gcc, ninja and qemu. This initial set
are used to create cross compiling tools.

To install the tools run:
```
vendor-install-tools/install.py all
```
You can also install individual tools, see the positional parameters in the help:
```
$ ./install.py --help
usage: install.py [-h] [--forceInstall] [--codePrefixDir [CODEPREFIXDIR]]
                  [--installPrefixDir [INSTALLPREFIXDIR]]
                  [--crossDir [CROSSDIR]] [--ver [VER]] [--gitver [GITVER]]
                  [--target [TARGET]]
                  [apps [apps ...]]

positional arguments:
  apps                  Apps to install, "all" or one or more in the list:
                        ['ninja', 'meson', 'ct-ng',
                         'gcc-x86_64', 'gcc-i386','gcc-arm',
                         'qemu-system-arm']

optional arguments:
  -h, --help            show this help message and exit
  --forceInstall        force install (default: False)
  --codePrefixDir [CODEPREFIXDIR]
                        Code prefix for creating the binaries (default:
                        /home/wink/tmp)
  --installPrefixDir [INSTALLPREFIXDIR]
                        Install prefix directory for the binaries (default:
                        /home/wink/opt)
  --crossDir [CROSSDIR]
                        cross directory (default: )
  --ver [VER]           version to install (default: )
  --gitver [GITVER]     version to checkout from git (default: )
  --target [TARGET]     Target to compile (default: )
```
