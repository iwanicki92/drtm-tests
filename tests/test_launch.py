# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""What every launch has to leave on either vendor: the OS at its shell
with the DRTM PCRs extended in every bank, every CPU the machine has up,
and no error the suite does not expect."""

import re
from fnmatch import fnmatch

import pytest
from conftest import (
    ENTRIES,
    VENDOR,
    Boot,
    expects_boot,
    expects_every_cpu,
    expects_open_localities,
)

from drtmtest import machine, trenchboot
from drtmtest.console import strip_ansi

# Every entry this session boots, and the launches among them.
BOOTED = [
    name
    for name, entry in ENTRIES.items()
    if name != "xen_mb2" and (VENDOR == "amd" or not entry.amd_only)
]
LAUNCHES = [name for name in BOOTED if ENTRIES[name].launch]

# How many CPUs the OS brought up: Xen counts its own, with or without a
# timestamp after its tag, and Linux its own.
_XEN_CPUS = re.compile(r"^\(XEN\)(?: \[[^]]*\])? Brought up (\d+) CPUs", re.MULTILINE)
_LINUX_CPUS = re.compile(r"\] smp: Brought up \d+ nodes?, (\d+) CPUs?")

_PANIC = re.compile(r"Kernel panic - not syncing|Panic on CPU \d+")

# GRUB's errors the boots print: every EFI boot the first, and on Intel
# the second as GRUB tries the SKL as SINIT ACM before the firmware's.
_GRUB_EXPECTED = {
    "amd": {"error: no such device: ()/EFI/BOOT/grub.cfg."},
    "intel": {
        "error: no such device: ()/EFI/BOOT/grub.cfg.",
        "error: it does not look like SINIT ACM.",
    },
}
# The upstream releases load the ACMs they ship for real chipsets too,
# which GRUB rejects as SKL on AMD and as not this platform's on Intel.
_GRUB_UPSTREAM = {
    "amd": {"error: SKL module isn't correct."},
    "intel": {"error: SINIT ACM does not match platform."},
}

# What the session traces into qemu.log beside the guest errors, and the
# traces among them that say the launch or the guest went wrong.
_TRACES = machine.INTEL_TRACES if VENDOR == "intel" else machine.LAUNCH_TRACES
_ERROR_TRACES = {
    "amd": {"amd_drtm_guest_error", "amd_psp_drtm_launch_failed"},
    "intel": {
        "txt_senter_errorcode",
        "txt_reset_request",
        "txt_drtm_tpm_error",
        "txt_dmar_rejected",
        "txt_wakeup_rejected",
        "txt_monitor_wake_ignored",
        "getsec_smxe_off",
        "getsec_cpl",
        "getsec_unimpl",
        "getsec_senter_no_chipset",
    },
}


def _params(names: list[str], *marks, cpus: bool = False) -> list:
    return [
        pytest.param(
            name,
            marks=[
                expects_boot(name),
                *marks,
                *([expects_every_cpu(name)] if cpus else []),
            ],
        )
        for name in names
    ]


def cpus_up(boot: Boot) -> int | None:
    """How many CPUs the OS says it brought up, `None` if it never said."""
    pattern = _XEN_CPUS if boot.entry.os == "xen" else _LINUX_CPUS
    found = pattern.findall(strip_ansi(boot.console))
    return int(found[-1]) if found else None


def unexpected_errors(boot: Boot) -> list[str]:
    """Panics, GRUB errors nothing expects, and the lines of `qemu.log`
    that are error traces or none of the session's traces, which leaves
    QEMU's guest errors."""
    grub = _GRUB_EXPECTED[VENDOR]
    if trenchboot.upstream():
        grub = grub | _GRUB_UPSTREAM[VENDOR]
    console = strip_ansi(boot.console).replace("\r", "")
    errors = [m.group(0) for m in _PANIC.finditer(console)]
    errors += [
        line.strip()
        for line in console.splitlines()
        if line.strip().startswith("error: ") and line.strip() not in grub
    ]
    for line in boot.qemu_log.splitlines():
        trace = line.split()[0] if line.strip() else None
        if trace is not None and (
            trace in _ERROR_TRACES[VENDOR]
            or not any(fnmatch(trace, pattern) for pattern in _TRACES)
        ):
            errors.append(line)
    return errors


@pytest.mark.parametrize("name", _params(LAUNCHES, expects_open_localities()))
def test_launch_extends_the_drtm_pcrs(name: str, request: pytest.FixtureRequest):
    """The launch reached the shell and reset and extended PCR 17 and 18
    in every bank. A launch that failed and fell back to a normal boot
    leaves them all ones, a bank it never extended all zeros."""
    boot: Boot = request.getfixturevalue(name)
    assert boot.bank_pcrs, "no PCRs were read"
    for bank, pcrs in boot.bank_pcrs.items():
        for index in (17, 18):
            assert set(pcrs[index]) not in ({"0"}, {"f"}), (bank, pcrs)


@pytest.mark.parametrize("name", _params(LAUNCHES, cpus=True))
def test_launch_brings_every_cpu_up(name: str, request: pytest.FixtureRequest):
    """The OS woke every AP the launch left asleep."""
    boot: Boot = request.getfixturevalue(name)
    assert cpus_up(boot) == boot.smp, boot.console[-2000:]


@pytest.mark.parametrize("name", _params(BOOTED, cpus=True))
def test_boot_shows_no_unexpected_errors(name: str, request: pytest.FixtureRequest):
    boot: Boot = request.getfixturevalue(name)
    assert unexpected_errors(boot) == []
