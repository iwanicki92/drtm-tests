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
import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from drtmtest import machine, trenchboot
from drtmtest.console import LINUX_BANNER, XEN_BANNER, Console
from drtmtest.dasharo import FIRMWARE, warmed_firmware
from drtmtest.eventlog import Event, parse
from drtmtest.qemu_vm import QemuVm
from drtmtest.session import BootSession

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

# From the QEMU launch to the login prompt is about 80 s on an idle 8-core
# host. Boots overlap, so the allowance is for a full batch of them.
BOOT_TIMEOUT = 420.0

# Each guest's memory, matched to -m in drtmtest.machine. dom0 boots in it,
# and it is what lets six boots share a 16 GB host.
GUEST_MEM_GIB = 2

# Whether the boots get the Secure Processor's DRTM service, and whether
# the image's SKL is expected to use it: `None`, "on" or "classic".
PSP = machine.psp_mode()


@dataclass(frozen=True)
class Entry:
    """One GRUB entry: its title, which OS it boots, whether through a
    launch, and under which firmware. `broken` names why it is not expected
    to boot on the pinned releases. An `optional` entry is one only some
    images carry, and its tests skip where the menu lacks it."""

    title: str
    os: str
    launch: bool
    firmware: str = "dasharo"
    broken: str | None = None
    optional: bool = False

    @property
    def broken_reason(self) -> str | None:
        """Why this session is not expected to boot the entry, or `None`
        when it should. The pinned releases carry known breakage, and a
        local build is usually there to test a fix, so nothing is expected
        broken on one. An image without legacy boot code cannot boot the
        SeaBIOS entries. Under the service with a classic SKL every launch
        is expected to fail: neither its GRUB nor the SKL talks to the
        service, so the TPM localities the SKL and the OS extend through
        stay locked, and only the service's LAUNCH would open them."""
        if self.firmware == "seabios" and not trenchboot.legacy_bootable():
            return (
                "the image has no legacy boot code, its wic carries the EFI boot alone"
            )
        if PSP == "classic" and self.launch:
            return "classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM"
        if self.broken is not None and trenchboot.release() is not None:
            return self.broken
        return None

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
    # The Linux launch with one more kernel parameter, which the fork's
    # images carry and the releases do not. The SKL measures the command
    # line into PCR 18, so this launch must differ from the plain one
    # there and nowhere else.
    "linux_alt_launch": Entry(
        "Boot Linux with TrenchBoot (alt)",
        "linux",
        True,
        firmware="seabios",
        optional=True,
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
    `None` for one that reached the shell. `skipped` says why an optional
    entry was not booted at all.

    `eventlog` is the DRTM event log as dumped from the guest, `slb_length`
    and `slb_sha256` the SLB header's length and the digest of that many
    bytes of the SKL the image booted, both gathered on launches only.
    `iommu` is what the OS says of its IOMMU: Xen's `virt_caps`, or the
    kernel's iommu class and groups. `cmdline` is Linux's `/proc/cmdline`.
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
    eventlog: bytes = b""
    slb_length: int = 0
    slb_sha256: str = ""
    iommu: str = ""
    cmdline: str = ""
    error: Exception | None = None
    skipped: str | None = None

    @property
    def events(self) -> list[Event]:
        """The event log's events, none when nothing was dumped."""
        return parse(self.eventlog) if self.eventlog else []

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


# Where Xen reserved the SKL's event log, as v0.5.2 prints the range,
# "(base - end)", and the v4 patchset does, "[base, end)".
_XEN_EVENT_LOG_RE = re.compile(
    r"SLAUNCH: reserving event log [\[(]\s*(0x[0-9a-fA-F]+)\s*[-,]\s*(0x[0-9a-fA-F]+)"
)


def _event_log(console: Console, entry: Entry, capture: str) -> bytes:
    """The DRTM event log as hex off the console: Linux exposes it in
    securityfs, dom0 reads Xen's reserved range out of `/dev/mem`. The
    hex comes as one line, so the newline after it is the dump's own and
    the prompt does not land on the line."""
    if entry.os == "linux":
        source = "/sys/kernel/security/slaunch/eventlog"
        out = console.run(f"xxd -p {source} | tr -d '\\n'; echo")
    else:
        match = _XEN_EVENT_LOG_RE.search(capture)
        if match is None:
            raise RuntimeError("Xen printed no event log range")
        base, end = (int(x, 16) for x in match.groups())
        if base % 4096 or (end - base) % 4096:
            raise RuntimeError(f"event log range {match.group(0)!r} is not in pages")
        out = console.run(
            f"dd if=/dev/mem bs=4096 skip={base // 4096} count={(end - base) // 4096}"
            " 2>/dev/null | xxd -p | tr -d '\\n'; echo"
        )
    try:
        return bytes.fromhex(out)
    except ValueError:
        raise RuntimeError(f"the event log dump is not hex: {out[:200]!r}") from None


def _slb(console: Console) -> tuple[int, str]:
    """The SLB header's length field and the SHA-256 of that many bytes of
    the SKL the image booted, what SKINIT measures. An image with both
    builds boots the AMDSL one under the service."""
    skl = "/boot/skl-amdsl.bin" if PSP == "on" else "/boot/skl.bin"
    header = console.run(f"xxd -p -s 2 -l 2 {skl}")
    length = int.from_bytes(bytes.fromhex(header), "little")
    # BusyBox head has no -c, dd reads the same bytes.
    digest = console.run(f"dd if={skl} bs={length} count=1 2>/dev/null | sha256sum")
    return length, digest.split()[0]


def _boot(name: str, log_dir: Path) -> Boot:
    entry = ENTRIES[name]
    boot = Boot(entry, log_dir)
    dasharo = entry.firmware == "dasharo"
    xen = entry.os == "xen"
    try:
        with QemuVm(
            log_dir,
            machine.options(trenchboot.unpacked_image(), psp=PSP is not None),
            firmware=_warmed_firmware() if dasharo else None,
            tpm="tis",
        ) as vm:
            console = Console(vm, BOOT_TIMEOUT)
            try:
                boot.titles = console.select_entry(entry.title, boot_prompt=dasharo)
            except LookupError as e:
                if not entry.optional:
                    raise
                boot.skipped = str(e)
                return boot
            console.wait_for_login(entry.banner)
            console.login()
            # The kernel's console messages otherwise land in the middle
            # of a command's output, a 64 KiB hex dump among them.
            console.run("dmesg -n 1")
            assert vm.qmp is not None
            boot.record = vm.qmp.execute("query-amd-drtm")
            boot.pcrs = console.pcrs(list(range(17, 23)))
            if xen:
                # For the log only: the console ring can lose early lines,
                # so tests read Xen's lines off the serial capture instead.
                boot.xen_log = console.run("xl dmesg | grep -i -E 'slaunch|drtm'")
                boot.iommu = console.run("xl info | grep virt_caps")
            else:
                boot.iommu = console.run("ls /sys/class/iommu /sys/kernel/iommu_groups")
                boot.cmdline = console.run("cat /proc/cmdline")
            boot.dmesg = console.run("dmesg | grep -i -E 'slaunch|slmodule|drtm'")
            boot.securityfs = console.run("ls /sys/kernel/security/slaunch 2>&1")
            if entry.launch:
                boot.eventlog = _event_log(console, entry, vm.capture)
                boot.slb_length, boot.slb_sha256 = _slb(console)
            boot.console = vm.capture
    except Exception as e:
        if entry.broken_reason is None:
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
    header=lambda: [
        f"image:       {trenchboot.description()}",
        f"psp:         {PSP or 'off'}",
    ],
)


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(SESSION)


def _entry_fixture(name: str):
    @pytest.fixture(scope="session", name=name)
    def wait_for_boot() -> Boot:
        boot = SESSION.booted(name)
        if boot.skipped is not None:
            pytest.skip(boot.skipped)
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
linux_alt_launch = _entry_fixture("linux_alt_launch")
linux = _entry_fixture("linux")


def expects_boot(name: str):
    """Marks a test that needs its entry to boot. Where this session is
    known not to boot the entry, the test must fail, so the day it passes
    is noticed. Everywhere else the mark is inert and the test has to
    pass."""
    reason = ENTRIES[name].broken_reason
    return pytest.mark.xfail(reason is not None, reason=reason or "", strict=True)


# The SKL's log has the SKL's extends. Under the service the PSP extends
# PCR 17 and 18 too, at its LAUNCH and at the SKL's request, and logs
# them in a log of its own that nothing fetches, so the replay of the
# SKL's log alone cannot reach the PCRs. Strict, so an image that merges
# the two logs is noticed.
replays_without_psp = pytest.mark.xfail(
    PSP == "on",
    reason="the PSP's extends are in its own log, which the SKL's does not carry",
    strict=True,
)
