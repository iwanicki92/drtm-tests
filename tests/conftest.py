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
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from drtmtest import bundle, grubcfg, machine, matrix, qemu_vm, trenchboot
from drtmtest.console import LINUX_BANNER, XEN_BANNER, Console, hex_dump
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

# Everything a boot takes from the environment is read here, at import on
# the main thread, and handed to the boot, the environment its processes
# run in included. The boots run on the pool's threads while the unit
# tests run on this one, and those patch the environment: a boot that read
# it at that moment booted a TPM with the test's banks, and a child of one
# that read it on its way to exec failed with EFAULT. The image is the
# exception, unpacked by `_prepare`.

# Whether the boots get the Secure Processor's DRTM service, and whether
# the image's SKL is expected to use it: `None`, "on" or "classic".
PSP = machine.psp_mode()

# The QEMU binary, the accelerator, the TPM's banks and swtpm's log level.
SETTINGS = qemu_vm.Settings.from_environment()

# The banks the fresh TPM state of every boot has PCRs in.
BANKS = SETTINGS.banks

# What `DRTM_QEMU_ARGS` appends to every boot.
EXTRA_ARGS = machine.extra_args()

# The image every boot runs, set by `_prepare` before the pool starts.
_IMAGE: Path | None = None


def _image() -> Path:
    assert _IMAGE is not None, "the image is unpacked by _prepare, ahead of the pool"
    return _IMAGE


# The upstream releases' SKL declares SHA-1 and SHA-256 in its log
# whatever the TPM has, and their Xen's legacy path copies the multiboot
# information's digests for those two banks alone.
OTHER_BANKS = trenchboot.upstream() and BANKS != qemu_vm.PCR_BANKS
MORE_BANKS = trenchboot.upstream() and bool(set(BANKS) - set(qemu_vm.PCR_BANKS))


@dataclass(frozen=True)
class Entry:
    """One GRUB entry: its title, which OS it boots, whether through a
    launch, and under which firmware. `broken` names why it is not expected
    to boot on the upstream releases. An entry with a `parameter` is not
    picked from the menu but typed at GRUB's shell: the titled entry's
    commands, read off the image, with the parameter on the kernel's
    line, so every image has it."""

    title: str
    os: str
    launch: bool
    firmware: str = "dasharo"
    broken: str | None = None
    parameter: str | None = None

    @property
    def broken_reason(self) -> str | None:
        """Why this session is not expected to boot the entry, or `None`
        when it should. The upstream releases carry known breakage, while
        the fork's image carries the fixes and a local build is usually
        there to test one, so nothing is expected broken on those. An image
        without legacy boot code cannot boot the SeaBIOS entries. Under the
        service with a classic SKL the TPM localities the SKL and the OS
        extend through stay locked, since only the service's LAUNCH would
        open them: Xen boots on with its extends failing, and Linux
        panics on its own, in `slaunch_pcr_extend`. Linux also resets on
        a log whose banks are not the TPM's, which the upstream SKL
        writes under any other banks."""
        if self.firmware == "seabios" and not trenchboot.legacy_bootable():
            return (
                "the image has no legacy boot code, its wic carries the EFI boot alone"
            )
        if PSP == "classic" and self.launch and self.os == "linux":
            return (
                "classic SKL: the kernel's extend fails at a locked locality, it panics"
            )
        if self.broken is not None and trenchboot.upstream():
            return self.broken
        if OTHER_BANKS and self.launch and self.os == "linux":
            return "the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has"
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
    # The upstream releases' GRUB reads the kernel's MLE header from the
    # wrong offset in its EFI SKINIT setup, so SKL enters the kernel at
    # startup_32, not sl_stub_entry. The kernel never learns of the
    # launch, never executes STGI, and with GIF still clear its timer
    # check panics. The legacy path below boots, and so does a build with
    # the GRUB fix.
    "linux_launch": Entry(
        "Boot Linux with TrenchBoot",
        "linux",
        True,
        broken="panics in check_timer: SKL entered startup_32, GIF never set",
    ),
    "linux_legacy_launch": Entry(
        "Boot Linux with TrenchBoot", "linux", True, firmware="seabios"
    ),
    # The legacy Linux launch with one more kernel parameter, typed at
    # GRUB's shell. The SKL measures the command line into PCR 18, so this
    # launch must differ from the plain one there and nowhere else.
    "linux_alt_launch": Entry(
        "Boot Linux with TrenchBoot",
        "linux",
        True,
        firmware="seabios",
        parameter="drtmtest=alt",
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

    `pcrs` are the SHA-256 PCRs 17 to 22, `bank_pcrs` the same in every
    bank the TPM has, by bank in the TPM's order. `eventlog` is the DRTM
    event log as dumped from the guest, `slb` the SLB of the SKL the image
    booted, the header's length worth of it, what SKINIT measures, and
    `slb_length` that length, all gathered on launches only. `iommu` is
    what the OS says of its IOMMU: Xen's `virt_caps`, or the kernel's
    iommu class and groups. `cmdline` is Linux's `/proc/cmdline`.
    """

    entry: Entry
    log_dir: Path
    titles: list[str] = field(default_factory=list)
    record: dict = field(default_factory=dict)
    pcrs: dict[int, str] = field(default_factory=dict)
    bank_pcrs: dict[str, dict[int, str]] = field(default_factory=dict)
    xen_log: str = ""
    dmesg: str = ""
    securityfs: str = ""
    console: str = ""
    eventlog: bytes = b""
    slb: bytes = b""
    slb_length: int = 0
    iommu: str = ""
    cmdline: str = ""
    error: Exception | None = None

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
            machine.options(_image(), extra=EXTRA_ARGS),
            firmware=FIRMWARE.fetch(trenchboot.CACHE_DIR),
            tpm="tis",
            save_firmware_to=scratch,
            settings=SETTINGS,
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
    the prompt does not land on the line. A Xen that printed no range
    took no launch it could use, and the tests on the log fail on the
    empty log this returns."""
    if entry.os == "linux":
        source = "/sys/kernel/security/slaunch/eventlog"
        out = console.run(f"xxd -p {source} | tr -d '\\n'; echo")
    else:
        match = _XEN_EVENT_LOG_RE.search(capture)
        if match is None:
            return b""
        base, end = (int(x, 16) for x in match.groups())
        if base % 4096 or (end - base) % 4096:
            raise RuntimeError(f"event log range {match.group(0)!r} is not in pages")
        out = console.run(
            f"dd if=/dev/mem bs=4096 skip={base // 4096} count={(end - base) // 4096}"
            " 2>/dev/null | xxd -p | tr -d '\\n'; echo"
        )
    try:
        return hex_dump(out)
    except ValueError:
        raise RuntimeError(f"the event log dump is not hex: {out[:200]!r}") from None


def _slb(console: Console) -> tuple[int, bytes]:
    """The SLB header's length field and that many bytes of the SKL the
    image booted, what SKINIT measures. An image with both builds boots
    the AMDSL one under the service."""
    skl = "/boot/skl-amdsl.bin" if PSP == "on" else "/boot/skl.bin"
    header = console.run(f"xxd -p -s 2 -l 2 {skl}")
    length = int.from_bytes(hex_dump(header), "little")
    out = console.run(f"xxd -p -l {length} {skl} | tr -d '\\n'; echo")
    try:
        return length, hex_dump(out)
    except ValueError:
        raise RuntimeError(f"the SLB dump is not hex: {out[:200]!r}") from None


def _boot(name: str, log_dir: Path) -> Boot:
    entry = ENTRIES[name]
    boot = Boot(entry, log_dir)
    dasharo = entry.firmware == "dasharo"
    xen = entry.os == "xen"
    try:
        with QemuVm(
            log_dir,
            machine.options(_image(), psp=PSP is not None, extra=EXTRA_ARGS),
            firmware=_warmed_firmware() if dasharo else None,
            tpm="tis",
            settings=SETTINGS,
        ) as vm:
            console = Console(vm, BOOT_TIMEOUT)
            if entry.parameter is None:
                boot.titles = console.select_entry(entry.title, boot_prompt=dasharo)
            else:
                commands = grubcfg.commands(
                    _image(), entry.title, entry.parameter, env=SETTINGS.environment
                )
                (log_dir / "grub-commands.txt").write_text("\n".join(commands) + "\n")
                boot.titles = console.type_entry(commands, boot_prompt=dasharo)
            console.wait_for_login(entry.banner)
            console.login()
            # The kernel's console messages otherwise land in the middle
            # of a command's output, a 64 KiB hex dump among them.
            console.run("dmesg -n 1")
            assert vm.qmp is not None
            boot.record = vm.qmp.execute("query-amd-drtm")
            boot.pcrs = console.pcrs(list(range(17, 23)))
            boot.bank_pcrs = {
                bank: console.pcrs(list(range(17, 23)), bank)
                for bank in console.pcr_banks()
            }
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
                boot.slb_length, boot.slb = _slb(console)
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
    global _IMAGE
    _IMAGE = trenchboot.unpacked_image()
    if any(ENTRIES[name].firmware == "dasharo" for name in names):
        _warmed_firmware()


def _check() -> str | None:
    reason = machine.unsupported_binary()
    if reason is not None:
        return f"This suite needs the QEMU drtm branch, see docs/testing.md: {reason}"
    if shutil.which("mtype") is None:
        return "This suite needs mtools on PATH, it reads grub.cfg off the image"
    return None


def _first_line(*command: str) -> str | None:
    """What a command prints first, `None` when it is not there or fails."""
    try:
        out = subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.splitlines()[0] if out.returncode == 0 and out.stdout else None


def _details() -> dict:
    """What `results.json` records of the session: the image, the matrix
    configuration if the environment is one, the QEMU and swtpm in use,
    the commit under test and the entries the tests take."""
    qemu = Path(SETTINGS.binary)
    return {
        "release": trenchboot.release(),
        "image": trenchboot.description(),
        "configuration": matrix.current(),
        "psp": PSP,
        "banks": list(BANKS),
        "qemu": _first_line(str(qemu), "--version"),
        "qemu_bundle": bundle.TAG if bundle.is_bundled(qemu) else None,
        "swtpm": _first_line("swtpm", "--version"),
        "commit": _first_line("git", "-C", str(LOGS_DIR.parent), "rev-parse", "HEAD"),
        "entries": {
            name: {"title": entry.title, "firmware": entry.firmware}
            for name, entry in ENTRIES.items()
        },
    }


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
        f"banks:       {','.join(BANKS)}",
    ],
    details=_details,
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
linux_alt_launch = _entry_fixture("linux_alt_launch")
linux = _entry_fixture("linux")


def expects_boot(name: str):
    """Marks a test that needs its entry to boot. Where this session is
    known not to boot the entry, the test must fail, so the day it passes
    is noticed. Everywhere else the mark is inert and the test has to
    pass."""
    reason = ENTRIES[name].broken_reason
    return pytest.mark.xfail(reason is not None, reason=reason or "", strict=True)


def expects_open_localities():
    """Marks a test on what the launch extended: under the service with a
    classic SKL nothing issues its LAUNCH, the localities stay locked,
    every extend fails and the PCRs stay as SKINIT left them, so the
    test must fail. The boot itself goes on, on Xen."""
    return pytest.mark.xfail(
        PSP == "classic",
        reason="classic SKL: no LAUNCH, so the PSP's locality locks stay on the TPM",
        strict=True,
    )


def expects_skls_banks():
    """Marks a test on the banks the log declares: the upstream SKL
    declares SHA-1 and SHA-256 whatever the TPM has, so on those releases
    the test must fail under any other banks."""
    return pytest.mark.xfail(
        OTHER_BANKS,
        reason="the upstream SKL logs SHA-1 and SHA-256 whatever the TPM has",
        strict=True,
    )


def expects_xens_mbi_digest():
    """Marks the MB2 replay: the upstream Xen's early code copies the
    multiboot information's digests the TPM returns until one the log
    does not declare, and the upstream log declares SHA-1 and SHA-256,
    so in a bank beyond those the PCR 18 record has no digest and the
    replay misses. With fewer banks every digest is copied."""
    return pytest.mark.xfail(
        MORE_BANKS,
        reason="the upstream Xen copies the MBI's digests for SHA-1 and SHA-256 alone",
        strict=True,
    )
