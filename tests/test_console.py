# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Reading a hex dump off the console Xen shares with dom0."""

import pytest

from drtmtest.console import hex_dump

# What v0.5.3-rc1 spliced into the event log dump: the hypervisor's uart
# watchdog fires on the very traffic the dump makes.
UART_WARNING = (
    "(XEN) [  108.008517] uart interrupt taking more than 4ms, switched to polling"
)


def test_a_dump_is_the_bytes_it_spells():
    assert hex_dump("00ff10") == b"\x00\xff\x10"


def test_the_newlines_a_long_dump_wraps_at_are_ignored():
    assert hex_dump("00ff\n1020\n") == b"\x00\xff\x10\x20"


def test_a_hypervisor_line_spliced_into_a_dump_is_dropped():
    assert hex_dump(f"00ff{UART_WARNING}\n1020") == b"\x00\xff\x10\x20"


def test_a_dump_that_is_not_hex_still_raises():
    with pytest.raises(ValueError):
        hex_dump("what happened")
