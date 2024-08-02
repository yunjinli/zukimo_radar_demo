# FAQ

## Build kernel modules

In order to speed up the turnaround times during development of kernel modules
it is possible to build them via SDK in a standalone fashion. For these kind
of builds some boundary conditions must be met.


### Setup environment

An SDK must be [built](../README.md#build-sdk) and installed.

Source the sdk, checkout the module and set the environment variables.
- `KERNEL_SRC`            - always needed to get access to linux headers
- `KBUILD_EXTRA_SYMBOLS`  - nedded when module depends on other out of tree module
- `EXTRA_INC`             - nedded when module depends on other out of tree module

```sh
. /opt/yocto/zukidemo/0.0.1/environment-setup-cortexa65ae-oe-linux
git clone <url-of-isp-main-driver-repo>
cd <clone-dir>/linux
export KERNEL_SRC=/opt/yocto/zukidemo/0.0.1/sysroots/cortexa65ae-oe-linux/usr/src/kernel
export KBUILD_EXTRA_SYMBOLS=${PROJECT}/build/tmp/work/${MACHINE}-oe-linux/kernel-module-dct-isp-main/1.0/recipe-sysroot/usr/include/kernel-module-dct-irc5/Module.symvers
export EXTRA_INC=-I${PROJECT}/build/tmp/work-shared/${MACHINE}/kernel-build-artifacts/include/dct
make
```

To quickly deploy the kernel module, copy it to the board via scp and directly reload the module:

```sh
scp *.ko root@192.168.1.2:/lib/modules/6.1.57-yocto-standard/extra/
ssh -t root@192.168.1.2 "rmmod isp_main; modprobe isp_main.ko;"
```
