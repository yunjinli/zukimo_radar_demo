# Copyright (C) 2023 Dream Chip Technologies
#
# SPDX-License-Identifier: BSD-2-Clause

TOP_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
TFTP_DIR := "/srv/tftp/${MACHINE}"
NFS_DIR := /export/${MACHINE}-rfs
SHELL := /bin/bash
PKG := u-boot

.PHONY: _default update build images clean tftp
.PHONY: dt_pcie_rc dt_pcie_ep

_default: help

-include ${TOP_DIR}/ci/validate.mk
-include ${TOP_DIR}/ci/branch.mk
-include ${TOP_DIR}/ci/hooks.mk
-include ${TOP_DIR}/ci/main.mk
-include ${TOP_DIR}/ci/setup.mk

ifndef MACHINE
$(info "MACHINE must be defined, assure setup-env is sourced.")
$(info "  source ./setup-env <BUILDDIR>")
$(info "  source ./setup-env --machine <MACHINE> <BUILDDIR>")
$(error )
endif

ifndef BUILDDIR
$(info "BUILDDIR must be defined, assure setup-env is sourced.")
$(info "  source ./setup-env <BUILDDIR>")
$(info "  source ./setup-env --machine <MACHINE> <BUILDDIR>")
$(error )
endif

TARGET := \
	zukimo-image-base \
	zukimo-image-minimal-initramfs \
	device-tree \
	u-boot \
	u-boot-scr

IMG_SRC := \
	Image \
	boot.scr \
	zukimo-image-minimal-initramfs-${MACHINE}.cpio.xz.u-boot \
	zukimo-image-base-${MACHINE}.rootfs.tar.gz \
	zukimo-image-base-${MACHINE}.rootfs.squashfs \
	devicetree/${MACHINE}.dtb \
	devicetree/${MACHINE}_pcie_rc.dtb \
	devicetree/${MACHINE}_pcie_ep.dtb \
	u-boot.bin \

IMG_DEST := \
	image.bin \
	boot.scr \
	rootfs.bin \
	rootfs.tar.gz \
	squashfs.bin \
	dtb.bin \
	dtb_pcie_rc.bin \
	dtb_pcie_ep.bin \
	uboot.bin

IMG_SEQ=$(shell seq $(words $(IMG_SRC)))

# Derive version string from current branch and CI build number.
# release/0.1.2   --> 0.1.2.B
# main            --> main-0.0.0.B
# feature/abc     --> feature_abc-0.0.0.B
# [detached HEAD] --> DETACHED-0.0.0.B

_VER_BUILD := 0
ifeq (${CI},true)
_VER_BUILD := ${BUILD_NUMBER}
_VER_BRANCH := ${BRANCH_NAME}
else
_VER_BRANCH := $(shell git branch --show-current)
endif

ifeq (,${_VER_BRANCH})
_VER_BRANCH := DETACHED
endif

_VER_RELEASE := $(_VER_BRANCH:release/%=%)
ifeq (${_VER_RELEASE},${_VER_BRANCH})
_VER_RELEASE := $(subst /,_,${_VER_BRANCH})-0.0.0
endif

export RELEASE_VERSION_HPC_SYSTEM = ${_VER_RELEASE}.${_VER_BUILD}
export RELEASE_GITHASH_HPC_SYSTEM = $(shell git describe --match=NEVERMATCH --always --abbrev=0 --dirty)
BB_ENV_PASSTHROUGH_ADDITIONS := ${BB_ENV_PASSTHROUGH_ADDITIONS} RELEASE_VERSION_HPC_SYSTEM RELEASE_GITHASH_HPC_SYSTEM
export BB_ENV_PASSTHROUGH_ADDITIONS

define newline


endef

build:
	@## build yocto images
	bitbake ${TARGET}

images:
	@## backup build artifacts to images folder
	mkdir -p ${TOP_DIR}/images/${MACHINE}
	rm -Rf ${TOP_DIR}/images/${MACHINE}/*
	$(foreach ii,${IMG_SEQ},\
		cp -Lf ${BUILDDIR}/tmp/deploy/images/${MACHINE}/$(word $(ii), $(IMG_SRC)) \
			${TOP_DIR}/images/${MACHINE}/$(word $(ii), $(IMG_DEST)) $(newline) \
	)
	rm -f ${TOP_DIR}/firmware.ver
	cp ${BUILDDIR}/tmp/work/zukimo-oe-linux/zukimo-image-base/1.0/rootfs/etc/firmware.ver \
		${TOP_DIR}/firmware.ver

tftp:
	@## backup build artifacts to TFTP folder
	mkdir -p ${TFTP_DIR}
	$(foreach ii,${IMG_SEQ}, \
		cp -Lf ${BUILDDIR}/tmp/deploy/images/${MACHINE}/$(word $(ii), $(IMG_SRC)) \
		${TFTP_DIR}/$(word $(ii), $(IMG_DEST)) $(newline) \
	)

dt_pcie_rc: tftp
	@## backup build artifacts to TFTP folder using PCIe_RC device tree
	cp -Lf ${BUILDDIR}/tmp/deploy/images/${MACHINE}/devicetree/${MACHINE}_pcie_rc.dtb ${TFTP_DIR}/dtb.bin

dt_pcie_ep: tftp
	@## backup build artifacts to TFTP folder using PCIe_EP device tree
	cp -Lf ${BUILDDIR}/tmp/deploy/images/${MACHINE}/devicetree/${MACHINE}_pcie_ep.dtb ${TFTP_DIR}/dtb.bin

nfs: images
	@## unpack full rootfs to NFS folder
	sudo rm -Rf ${NFS_DIR}
	sudo mkdir -p ${NFS_DIR}
	sudo tar --same-owner -pxzf ${TOP_DIR}/images/${MACHINE}/rootfs.tar.gz -C ${NFS_DIR}

clean:
	@## remove build artifacts
	rm -Rf ${BUILDDIR}

clean-package:
	@## clean package
	source ./setup-env --machine ${MACHINE} ${BUILDDIR} \
		&& bitbake -f -c clean ${PKG}

rebuild-package:
	@## rebuild package
	source ./setup-env --machine ${MACHINE} ${BUILDDIR} \
		&& bitbake -f -c configure ${PKG} \
		&& bitbake -f -c compile ${PKG} \
		&& bitbake -f -c install ${PKG}

reconfigure-package:
	@## rebuild package
	source ./setup-env --machine ${MACHINE} ${BUILDDIR} \
		&& bitbake -f -c configure ${PKG} \
		&& bitbake -f -c compile ${PKG} \
		&& bitbake -f -c deploy ${PKG}

.PHONY: _help_nop
_help_nop:

.PHONY: help
help:
	@## show help for targets with a recipe that starts with "@## "
	@printf "%-20s  %s\n" "TARGET" "DESCRIPTION"
	@make -f $(firstword $(MAKEFILE_LIST)) -p --no-print-directory _help_nop | awk -F: ' \
			/^[^#\t].*:/                    { target = $$1 } \
			/^\t@## / && target~"^[^$$]+$$" { printf "%-20s  %s\n", target, substr($$0,6); \
							  target = "" } \
		' | LC_COLLATE=C sort
