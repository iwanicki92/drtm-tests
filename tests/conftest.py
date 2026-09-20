# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Boots each GRUB entry of the image once per session and hands tests what
the boot left behind: the launch record, the PCRs and the OS's own view.

A boot takes a minute or two, so tests never boot QEMU themselves. They
take an entry's fixture, a `Boot`, and assert on its fields. Collection
starts every boot the run needs, as many at a time as the CPUs and the
memory allow, so a fixture is usually just waiting on a boot in flight.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from drtmtest import machine, trenchboot
from drtmtest.console import LINUX_BANNER, XEN_BANNER, Console
from drtmtest.dasharo import FIRMWARE, warmed_firmware
from drtmtest.qemu_vm import QemuVm
from drtmtest.session import BootSession

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

# From the QEMU launch to the login prompt is about 80 s on an idle 8-core
# host. Boots overlap, so the allowance is for a full batch of them.
BOOT_TIMEOUT = 420.0

# Each guest's memory, matched to -m in drtmtest.machine. dom0 boots in it,
# and it is what lets six boots share a 16 GB host.
GUEST_MEM_GIB = 2


@dataclass(frozen=True)
class Entry:
    """One GRUB entry: its title, which OS it boots, whether through a
    launch, and under which firmware. `broken` names why it is not expected
    to boot on the pinned releases."""

    title: str
    os: str
    launch: bool
    firmware: str = "dasharo"
    broken: str | None = None

    @property
    def expected_broken(self) -> bool:
        """Whether this run's image is one the entry is known not to boot
        on: the pinned releases. A local build is usually there to test
        a fix, so nothing is expected broken on it."""
        return self.broken is not None and trenchboot.release() is not None

    @property
    def banner(self) -> str:
        return XEN_BANNER if self.os == "xen" else LINUX_BANNER


ENTRIES: dict[str, Entry] = {
    "xen_efi_launch": Entry("Boot Xen with TrenchBoot (EFI)", "xen", True),
    "xen_efi": Entry("Boot Xen normally (EFI)", "xen", False),
    # The MB2 entries are legacy boots: under UEFI the launch runs SKL and
    # then stops, so they boot through SeaBIOS, the way a BIOS board would.
    "xen_mb2_launch": Entry(
        "Boot Xen with TrenchBoot (MB2)", "xen", True, firmware="seabios"
    ),
    # The releases' GRUB reads the kernel's MLE header from the wrong offset
    # in its EFI SKINIT setup, so SKL enters the kernel at startup_32, not
    # sl_stub_entry. The kernel never learns of the launch, never executes
    # STGI, and with GIF still clear its timer check panics. The legacy
    # path below boots, and so does a build with the GRUB fix.
    "linux_launch": Entry(
        "Boot Linux with TrenchBoot",
        "linux",
        True,
        broken="panics in check_timer: SKL entered startup_32, GIF never set",
    ),
    "linux_legacy_launch": Entry(
        "Boot Linux with TrenchBoot", "linux", True, firmware="seabios"
    ),
    # Booted as the Linux control and the warming boot. A kernel booted
    # directly is what an IOMMU passing DMA through breaks, Xen's dom0 not.
    "linux": Entry("Boot Linux normally", "linux", False),
    # Listed for the menu check, not booted by a test: its EFI twin is the
    # Xen control.
    "xen_mb2": Entry("Boot Xen normally (MB2)", "xen", False, firmware="seabios"),
}


@dataclass
class Boot:
    """What one boot left behind, gathered before the VM is torn down.

    `error` holds why a boot known to be broken did not get there, and is
    `None` for one that reached the shell.
    """

    entry: Entry
    log_dir: Path
    titles: list[str] = field(default_factory=list)
    record: dict = field(default_factory=dict)
    pcrs: dict[int, str] = field(default_factory=dict)
    xen_log: str = ""
    dmesg: str = ""
    securityfs: str = ""
    console: str = ""
    error: Exception | None = None

    @property
    def xen_lines(self) -> str:
        """What the hypervisor printed on the serial console, the lines
        tagged "(XEN)", with or without a timestamp after the tag."""
        return "\n".join(
            line for line in self.console.splitlines() if line.startswith("(XEN)")
        )


# A TPM 2.0 reports the DRTM PCRs, 17 to 22, as all ones from startup
# until a locality 4 start resets them to zero, which only a launch does.
PCR_ZERO = "0" * 64
PCR_ONES = "f" * 64

# The PSP DRTM service answers a launch that fails after SKINIT by capping
# PCR 18 to 20 with one all-ones extend, and the DLME may still boot. This
# is SHA-256(32 zero bytes || 32 0xff bytes), what such a PCR then reads.
PCR_CAPPED = "bba91ca85dc914b2ec3efb9e16e7267bf9193b14350d20fba8a8b406730ae30a"


def _warmed_firmware() -> Path:
    """The firmware after one boot to the GRUB menu, made on first use."""

    def boot(scratch: Path) -> None:
        log_dir = SESSION.run_log_dir() / "boot-warm-firmware"
        with QemuVm(
            log_dir,
            machine.options(trenchboot.unpacked_image()),
            firmware=FIRMWARE.fetch(trenchboot.CACHE_DIR),
            tpm="tis",
            save_firmware_to=scratch,
        ) as vm:
            # Let GRUB's own timeout boot the first entry: what matters is
            # that the firmware wrote its store and exited cleanly.
            Console(vm, BOOT_TIMEOUT).select_entry(ENTRIES["linux"].title)

    return warmed_firmware(trenchboot.CACHE_DIR, boot)


def _boot(name: str, log_dir: Path) -> Boot:
    entry = ENTRIES[name]
    boot = Boot(entry, log_dir)
    dasharo = entry.firmware == "dasharo"
    try:
        with QemuVm(
            log_dir,
            machine.options(trenchboot.unpacked_image()),
            firmware=_warmed_firmware() if dasharo else None,
            tpm="tis",
        ) as vm:
            console = Console(vm, BOOT_TIMEOUT)
            boot.titles = console.select_entry(entry.title, boot_prompt=dasharo)
            console.wait_for_login(entry.banner)
            console.login()
            assert vm.qmp is not None
            boot.record = vm.qmp.execute("query-amd-drtm")
            boot.pcrs = console.pcrs(list(range(17, 23)))
            if entry.os == "xen":
                # For the log only: the console ring can lose early lines,
                # so tests read Xen's lines off the serial capture instead.
                boot.xen_log = console.run("xl dmesg | grep -i -E 'slaunch|drtm'")
            boot.dmesg = console.run("dmesg | grep -i -E 'slaunch|slmodule|drtm'")
            boot.securityfs = console.run("ls /sys/kernel/security/slaunch 2>&1")
            boot.console = vm.capture
    except Exception as e:
        if not entry.expected_broken:
            raise
        boot.error = e
    return boot


def _workers() -> int:
    """How many guests fit at once: by CPU at `-smp 2` and by free memory.

    Read at the time of the run, so a host booted with less runs fewer boots
    at a time rather than swapping.
    """
    by_cpu = (os.cpu_count() or 1) // machine.DEFAULT_SMP
    available_gib = 0
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                available_gib = int(line.split()[1]) // (1 << 20)
    by_mem = available_gib // GUEST_MEM_GIB
    return max(1, min(by_cpu, by_mem))


def _prepare(names: list[str]) -> None:
    """One unpack and one warming boot, ahead of the pool."""
    trenchboot.unpacked_image()
    if any(ENTRIES[name].firmware == "dasharo" for name in names):
        _warmed_firmware()


def _check() -> str | None:
    reason = machine.unsupported_binary()
    if reason is None:
        return None
    return f"This suite needs the QEMU drtm branch, see docs/testing.md: {reason}"


SESSION = BootSession(
    LOGS_DIR,
    _boot,
    ENTRIES.keys(),
    workers=_workers,
    prepare=_prepare,
    check=_check,
    header=lambda: [f"image:       {trenchboot.description()}"],
)


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(SESSION)


def _entry_fixture(name: str):
    @pytest.fixture(scope="session", name=name)
    def wait_for_boot() -> Boot:
        boot = SESSION.booted(name)
        if boot.error is not None:
            pytest.fail(f"{boot.entry.title!r} did not reach the shell: {boot.error}")
        return boot

    wait_for_boot.__doc__ = f"One boot of {ENTRIES[name].title!r}."
    return wait_for_boot


xen_efi_launch = _entry_fixture("xen_efi_launch")
xen_efi = _entry_fixture("xen_efi")
xen_mb2_launch = _entry_fixture("xen_mb2_launch")
xen_mb2 = _entry_fixture("xen_mb2")
linux_launch = _entry_fixture("linux_launch")
linux_legacy_launch = _entry_fixture("linux_legacy_launch")
linux = _entry_fixture("linux")


def broken(name: str):
    """Marks a test of an entry known not to boot on the releases: there it
    must fail, so the day it passes is noticed. On a local image the mark
    is inert and the test has to pass."""
    entry = ENTRIES[name]
    assert entry.broken is not None, f"{name} is not marked broken"
    return pytest.mark.xfail(entry.expected_broken, reason=entry.broken, strict=True)
