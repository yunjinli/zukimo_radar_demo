# Copyright (C) 2024 Dream Chip Technologies
#
# SPDX-License-Identifier: BSD-2-Clause

import logging
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        help="Watch live progress, short for --log-cli-level=INFO",
    )

def pytest_configure(config):
    config.option.xmlpath = __file__ + f"/../report-zukimo.xml"
    config.inicfg["junit_family"] = "xunit1"
    config.inicfg["junit_logging"] = "all"
    config.inicfg["junit_suite_name"] = f"pytest-zukimo"
    config.inicfg["log_cli"] = True
    config.inicfg["log_cli_level"] = "WARN"
    if config.option.live:
        config.inicfg["log_cli_level"] = "INFO"
    config.inicfg["log_cli_format"] = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s"
    config.inicfg["log_cli_date_format"] = "%Y-%m-%d %H:%M:%S"
    config.inicfg["log_file"] = __file__ + f"/../test.log"
    config.inicfg["log_file_level"] = "INFO"
    config.inicfg["log_file_format"] = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s"
    config.inicfg["log_file_date_format"] = "%Y-%m-%d %H:%M:%S"
