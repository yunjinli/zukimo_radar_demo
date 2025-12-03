LICENSE = "GPL-2.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-2.0-only;md5=801f80980d171dd6425610833a22dbe6"

inherit module

SRC_URI = "${GITSRC_SPA_ML_DRIVER}"
SRCREV = "${GITREV_SPA_ML_DRIVER}"

S = "${WORKDIR}/git"

EXTRA_OEMAKE += "O=${STAGING_KERNEL_BUILDDIR} EXTRA_INC=-I${STAGING_KERNEL_BUILDDIR}/include/dct"

DEPENDS = "kernel-module-dct-ipc"

RDEPENDS:${PN} += "kernel-module-dct-ipc kernel-module-dct-ipc-clk"
RPROVIDES:${PN} += "kernel-module-npu"

# Assure to get access to the kernel headers
do_configure[depends] += "virtual/kernel:do_shared_workdir"