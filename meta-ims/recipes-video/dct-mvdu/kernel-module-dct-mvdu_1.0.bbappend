FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://0001-Enabled-picture-in-picture.patch;patchdir=.."
SRC_URI += "file://0002-Fix-wrong-pixel-format.patch;patchdir=.."

