# Copyright (C) 2022 Dream Chip Technologies
#
# SPDX-License-Identifier: BSD-2-Clause

import contextlib
import serial
import time
import logging
from datetime import datetime, timedelta


class Controller:
    def __init__(self, dev: str, baudrate: int):
        self._dev = dev
        self._baudrate = baudrate
        self._serial = None

    def __enter__(self):
        self._serial = serial.Serial(self._dev, self._baudrate, timeout=0.5)
        self._serial.flushOutput()
        self._serial.flushInput()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._serial is not None
        self._serial.close()
        self._serial = None

    def read(self, size: int = 1):
        assert self._serial is not None
        return self._serial.read(size)

    def read_all(self):
        assert self._serial is not None
        return self._serial.read(self._serial.in_waiting or 1)

    def write(self, data: bytes):
        assert self._serial is not None
        return self._serial.write(data)

    def getc(self, size, timeout=1):
        return self._serial.read(size) or None

    def putc(self, data, timeout=1):
        return self._serial.write(data)

    @contextlib.contextmanager
    def timeout(self, timeout_s: float):
        assert self._serial is not None
        old_timeout = self._serial.timeout
        self._serial.timeout = timeout_s
        yield old_timeout
        self._serial.timeout = old_timeout

    def shell(self, prompt: str):
        return Shell(self, prompt)


class Shell:
    def __init__(self, ctl: Controller, prompt: str):
        self._ctl = ctl
        self.prompt = prompt
        # read away potential boot messages and prompt
        self.call("\n")
        while self._ctl.read(1024):
            pass

    def call(self, cmd: str, timedelta_ms: int = None):
        """Send cmd to UART shell, return its output

        Note: The call will take at least timeout_s seconds.
        """
        _cmd = f"{cmd}\r\n".encode()

        logging.info(cmd)

        if timedelta_ms is None:
            timedelta_ms = 1000
        timeout = timedelta(milliseconds=timedelta_ms)

        out = bytes()
        self._ctl.write(_cmd)
        deadline = datetime.now() + timeout
        while True:
            out += self._ctl.read_all()
            if datetime.now() > deadline:
                break
            delta = min(timeout / 20, deadline - datetime.now())
            time.sleep(delta.total_seconds())

        if out.startswith(_cmd):
            out = out[len(_cmd) :]
        return out.decode()
