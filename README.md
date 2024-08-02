# Zukimo BSP

This is the documentation and overview of the Zukimo BSP project.
The yocto used is based on `nanbield`.


[TOC]


## Repository structure

Git submodules are mounted below `repos/`.  The directory `layers/` contains
symlinks to the needed meta layers provided by those repositories so that the
bitbake environment always uses the correct version-controlled layers.

After cloning this top repository, populate the `repos` directory:
```
git submodule update --init --recursive
```


## Prerequisites

To build and use the BSP, some [preparations](doc/PREREQUISITES.md) must be made.


## Prepare Yocto workspace

To setup a workspace for the first time the setup script must be sourced with
machine and optional build folder, e.g. one folder for each machine.

```
source setup-env --machine zukimo  # implies default build folder "build"
source setup-env --machine zukimo build-zukimo  # example for non-default folder
```

After the workspace is initialized the images can be built as layed out in the
next chapter.

Everytime a new shell is opened in the workspace it needs to be initialized to
the build folder.
```
source setup-env  # if the folder is "build"
source setup-env build-zukimo  # if the folder is "build-zukimo"
```

## Build

Build only the base image:
```
bitbake zukimo-image-base
```

Do a full build and update TFTP and NFS folders:
```
make build images tftp nfs
```

This will update the images in
- `images/${MACHINE}`
- the TFTP folder
- the NFS folder

Find the raw results in `build*/tmp/deploy/images/*`:
- U-Boot: `u-boot.bin`
- Kernel: `Image`
- Device-tree: `devicetree/*.dtb`
- Initrd: `*-initramfs-*.cpio.xz.u-boot`
- Rootfs: `*rootfs.tar.gz`

For debugging purposes ELF binaries with symbol information can be found:
- U-Boot: `build*/tmp/work/*-oe-linux/u-boot/*/build/u-boot`
- Kernel: `build*/tmp/work/*-oe-linux/linux-yocto/*/linux-*-standard-build/vmlinux`


## Work with modules and update recipes

To work in modules checked out by recipes and change them it is best to use the
bitbake `devtool`.  With this it is very easy to get the sources from the recipe,
test and modify them, create a patch file and update the recipe.  The following
gives a rough idea how `devtool` can be used.

All sources modified by `devtool` will be checked out to
`build/workspace/sources/`.

Once set into the modified state bitbake will start to
compile the source from this location instead of the spilled location in `tmp`.

By resetting the module, `devtool` will remove the
`build/workspace/sources/<recipe-name>` folder, and bitbake will continue to
build the recipe inside the `build/tmp` location.

Usecase: Checkout a module in our layer, change, update recipe, reset.
```
devtool modify kernel-module-dct-isp-main
bitbake kernel-module-dct-isp-main

# Commit the change after testing (update-recipe will add the change as patch
# file to the recipe).
devtool update-recipe kernel-module-dct-isp-main
devtool reset kernel-module-dct-isp-main
```

Same usecase for a recipe in another layer.
```
devtool modify gstreamer1.0-plugins-good
bitbake gstreamer1.0-plugins-good

# Commit and reset after testing
devtool update-recipe -a meta-multimedia gstreamer1.0-plugins-good
devtool reset gstreamer1.0-plugins-good
```


## Prepare SD card

- Format your SD card to FAT32
- Copy the following files onto it:
  - `dtb.bin`
  - `image.bin`
  - `rootfs.bin`
  - `squashfs.bin`
  - `boot.bin`


## Use u-boot

U-boot allows the user to adjust boot settings or update the SD card via TFTP.

Stop the autoboot by pressing any key.

`printenv` gives you an overview of the default settings, which can be changed
using `editenv`.

### Update all from u-boot

- `run update_all`

### Update kernel from u-boot

- `run update_kernel`

### Update u-boot from u-boot

- `run update_uboot`

### Update rootfs from u-boot

- `run update_rootfs`

### Update dtb from u-boot

- `run update_dtb`

### Update squashfs from u-boot

- `run update_squashfs`

### Change environment variable inside u-boot

To change the boot medium from SD card to (for example) NFS, stop in u-boot and
change the variable `bootcmd` to one of:
- `bootcmd_nfs`
- `bootcmd_sdc`
- `bootcmd_tftp`

```
editenv bootcmd
saveenv
```

## Build SDK

For the application development it might be easier to compile the sources with
a SDK. To initially build the SDK itself, run
```
bitbake zukimo-image-base -c populate_sdk
```

## Helpfull Yocto commands

List all recipes with "i2c" in their name:
```
bitbake-layers show-recipes '*i2c*'
```

Get a list of all packages that an image contains:
```
bitbake -g zukimo-image-base && cat pn-buildlist | grep -ve "native" | sort | uniq
```

Inspect environment variables used to build a target:
```
bitbake zukimo-image-base -e
```

Build dependency graph (generated `task-depends.dot` can be opened in text viewer, too):
```
bitbake -g zukimo-image-base -u taskexp
```


## Debugging

The BSP supports [Linux-aware debugging](doc/DEBUG.md) with Trace32.


## Camera

The camera bringup is explained in an [own document](doc/CAMERA.md).


## FAQ

There are [frequently asked questions](doc/FAQ.md) and answers.


## References

- [Yocto requirements](https://docs.yoctoproject.org/4.0.5/ref-manual/system-requirements.html?highlight=requirements)
