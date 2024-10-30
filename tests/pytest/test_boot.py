# Copyright (C) 2024 Dream Chip Technologies
#
# SPDX-License-Identifier: BSD-2-Clause

"""boot flow tests"""

import logging
import pathlib
import re
import subprocess
import time
import typing

import pytest

from uart import Controller, Shell

baudrate = 115200

dev_bmc = "/dev/ttyUSB2"
dev_uboot = "/dev/ttyUSB1"

ssh_dut_dest = "root@192.168.1.2"
ssh_opts = [
    "-oStrictHostKeyChecking=no",
    "-oUserKnownHostsFile=/dev/null",
    ]

prompt_alcatraz = "alcatraz:~$"
prompt_bmc = "uart:~$"
prompt_uboot = "Zukimo#"
prompt_linux = "root@zukimo:~#"

def uart_cmd(sh, cmd, timeout_sec: int = None, check = True):
    if timeout_sec:
        out = sh.call(cmd, timeout_sec * 1000)
    else:
        out = sh.call(cmd)
    logging.info(out)
    if check:
        assert sh.prompt in out
    return out

def ssh(cmd: typing.Sequence[str]) -> subprocess.CompletedProcess:
    ssh_cmd = ["ssh", *ssh_opts, ssh_dut_dest, *cmd]
    return subprocess.run(ssh_cmd, check=False)


def scp_host2dut(path_host: str, path_dut: str):
    cmd = ["scp", *ssh_opts, path_host, f"{ssh_dut_dest}:{path_dut}"]
    _ = subprocess.run(cmd)


def scp_dut2host(path_dut: str, path_host: str):
    cmd = ["scp", *ssh_opts, f"{ssh_dut_dest}:{path_dut}", path_host]
    _ = subprocess.run(cmd)


def bmc_reset():
    with Controller(dev_bmc, baudrate) as uart:
        sh = Shell(uart, prompt_bmc)
        uart_cmd(sh, "misc version")

        uart_cmd(sh, "bc_gpio alc_reset 0 0")
        time.sleep(2)


def ping_host(sh_uboot: Shell):
    out = uart_cmd(sh_uboot, "ping ${serverip}", timeout_sec=10)
    assert ' is alive' in out


def check_firmware_ver(got: str):
    ver_file = pathlib.Path("firmware.ver")
    if not ver_file.exists():
        return
    with ver_file.open() as f:
        want = f.read()
    # do not compare line endings, exclude prompt line
    want_lines = want.split()
    got_lines = got.split()[:len(want_lines)]
    assert got_lines == want_lines

def test_update_uboot():
    """
    - reboot SoC by using the Board Controller
    - update the uboot image
    """

    bmc_reset()

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_uboot)

        uart_cmd(sh, "version")
        uart_cmd(sh, "env print")
        ping_host(sh)
        uart_cmd(sh, "run update_uboot", timeout_sec=60)

    bmc_reset()

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_uboot)

        uart_cmd(sh, "version")
        uart_cmd(sh, "env print")


def test_bootcmd_sdc():
    """
    - reboot SoC by using the Board Controller
    - update the sdcard via uboot
    - boot linux from sdcard
    """

    bmc_reset()

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_uboot)

        uart_cmd(sh, "version")
        ping_host(sh)
        uart_cmd(sh, "run update_dtb", timeout_sec=60)
        uart_cmd(sh, "run update_kernel", timeout_sec=60)
        uart_cmd(sh, "run update_rootfs", timeout_sec=60)
        uart_cmd(sh, "run update_squashfs", timeout_sec=600)
        uart_cmd(sh, "run bootcmd_sdc", check=False)

    time.sleep(45)

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_linux)

        out = uart_cmd(sh, "cat /etc/os-release")
        assert 'zukidemo' in out

        out = uart_cmd(sh, "cat /etc/firmware.ver")
        check_firmware_ver(out)


def test_bootcmd_nfs():
    """
    - reboot SoC by using the Board Controller
    - boot linux from nfs
    """

    systestxml = pathlib.Path("tests/pytest/system_test.xml")
    systestxml.unlink(missing_ok=True)

    bmc_reset()

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_uboot)

        uart_cmd(sh, "version")
        ping_host(sh)
        uart_cmd(sh, "run bootcmd_nfs", check=False)

    time.sleep(45)

    with Controller(dev_uboot, baudrate) as uart:
        sh = Shell(uart, prompt_linux)

        out = uart_cmd(sh, "")
        out = uart_cmd(sh, "")
        out = uart_cmd(sh, "cat /etc/os-release")
        assert 'zukidemo' in out

        out = uart_cmd(sh, "cat /etc/firmware.ver")
        check_firmware_ver(out)

        version = out.split()[0]
        is_release = re.match(r"\d+\.\d+\.\d+\.\d+", version)

    # run system tests on DUT and save results on host
    neg_pats = "*interactive*"
    if not is_release:
        neg_pats += ":*release_version_valid"
    ssh(["/usr/bin/system_test", "--gtest_output=xml:/tmp/", f"--gtest_filter=-{neg_pats}"])
    scp_dut2host("/tmp/system_test.xml", str(systestxml))
