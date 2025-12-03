do_install:append() {
    ln -sf libpython3.11.so.1.0 ${D}${libdir}/libpython3.11.so
}

FILES_${PN} += "${libdir}/libpython3.11.so"