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
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pytest

from tbtest import assets
from tbtest.console import LINUX_BANNER, XEN_BANNER, Console
from tbtest.qemu_vm import DEFAULT_SMP, QemuVm, unsupported_binary

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
_RUN_DIR_RE = re.compile(r"^(\d{4})-")
_MAX_RUN_NUMBER = 9999

# From the QEMU launch to the login prompt is about 80 s on an idle 8-core
# host. Boots overlap, so the allowance is for a full batch of them.
BOOT_TIMEOUT = 420.0

# Each guest's memory, matched to -m in tbtest.qemu_vm. dom0 boots in it,
# and it is what lets six boots share a 16 GB host.
GUEST_MEM_GIB = 2


@dataclass(frozen=True)
class Entry:
    """One GRUB entry: its title, which OS it boots and whether through a
    launch. `broken` names why it is not expected to boot on this release."""

    title: str
    os: str
    launch: bool
    broken: str | None = None

    @property
    def banner(self) -> str:
        return XEN_BANNER if self.os == "xen" else LINUX_BANNER


ENTRIES: dict[str, Entry] = {
    "xen_efi_launch": Entry("Boot Xen with TrenchBoot (EFI)", "xen", True),
    "xen_efi": Entry("Boot Xen normally (EFI)", "xen", False),
    "xen_mb2_launch": Entry(
        "Boot Xen with TrenchBoot (MB2)",
        "xen",
        True,
        broken="SKL ends with 'Bootloader shutdown EFI x64 boot services!' "
        "and nothing follows",
    ),
    "linux_launch": Entry(
        "Boot Linux with TrenchBoot",
        "linux",
        True,
        broken="panics: timer doesn't work through Interrupt-remapped IO-APIC",
    ),
    # Listed for the menu check and the warming boot, not booted by a test.
    # One control boot is enough and the Xen EFI one is it. The Linux
    # kernel booted directly never attaches the IDE disk here, so its
    # initramfs stops without a prompt.
    "xen_mb2": Entry("Boot Xen normally (MB2)", "xen", False),
    "linux": Entry("Boot Linux normally", "linux", False),
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


# A TPM 2.0 reports the DRTM PCRs, 17 to 22, as all ones from startup
# until a locality 4 start resets them to zero, which only a launch does.
PCR_ZERO = "0" * 64
PCR_ONES = "f" * 64


def _next_run_number() -> int:
    if not LOGS_DIR.exists():
        return 1
    numbers = [
        int(match.group(1))
        for path in LOGS_DIR.iterdir()
        if path.is_dir() and (match := _RUN_DIR_RE.match(path.name))
    ]
    return max(numbers, default=0) + 1


_run_log_dir: Path | None = None
_run_log_dir_lock = threading.Lock()


def _get_run_log_dir() -> Path:
    """Creates this run's log directory on first use, then reuses it."""
    global _run_log_dir
    with _run_log_dir_lock:
        if _run_log_dir is not None:
            return _run_log_dir
        number = _next_run_number()
        if number > _MAX_RUN_NUMBER:
            pytest.exit(
                f"logs/ has reached run {_MAX_RUN_NUMBER}, the 4-digit limit. "
                "Clean out old runs before testing again.",
                returncode=1,
            )
        now = datetime.now().astimezone()
        run_dir = LOGS_DIR / f"{number:04d}-{now.date().isoformat()}"
        run_dir.mkdir(parents=True)
        (run_dir / "timestamp.txt").write_text(now.isoformat() + "\n")
        _run_log_dir = run_dir
        return run_dir


_warm_lock = threading.Lock()


def warmed_firmware() -> Path:
    """The firmware after one boot to the GRUB menu, made on first use.

    Populating the variable store happens once, on an image that has never
    booted, so every boot after this one starts from a store that is there.
    """
    path = assets.warmed_firmware_path()
    with _warm_lock:
        if path.exists():
            return path
        scratch = path.with_suffix(".warming")
        log_dir = _get_run_log_dir() / "boot-warm-firmware"
        with QemuVm(
            log_dir,
            firmware=assets.FIRMWARE.fetch(),
            image=assets.unpacked_image(),
            save_firmware_to=scratch,
        ) as vm:
            # Let GRUB's own timeout boot the first entry: what matters is
            # that the firmware wrote its store and exited cleanly.
            Console(vm, BOOT_TIMEOUT).select_entry(ENTRIES["linux"].title)
        scratch.replace(path)
    return path


def _boot(name: str) -> Boot:
    entry = ENTRIES[name]
    log_dir = _get_run_log_dir() / f"boot-{name.replace('_', '-')}"
    boot = Boot(entry, log_dir)
    try:
        with QemuVm(
            log_dir, firmware=warmed_firmware(), image=assets.unpacked_image()
        ) as vm:
            console = Console(vm, BOOT_TIMEOUT)
            boot.titles = console.select_entry(entry.title)
            console.wait_for_login(entry.banner)
            console.login()
            assert vm.qmp is not None
            boot.record = vm.qmp.execute("query-amd-drtm")
            boot.pcrs = {i: console.pcr(i) for i in (16, 17, 18, 19)}
            if entry.os == "xen":
                boot.xen_log = console.run("xl dmesg | grep -i -E 'slaunch|drtm'")
            boot.dmesg = console.run("dmesg | grep -i -E 'slaunch|drtm'")
            boot.securityfs = console.run("ls /sys/kernel/security/slaunch 2>&1")
            boot.console = vm.capture
    except Exception as e:
        if entry.broken is None:
            raise
        boot.error = e
    return boot


_boot_pool: ThreadPoolExecutor | None = None
_boot_futures: dict[str, Future[Boot]] = {}


def _workers() -> int:
    """How many guests fit at once: by CPU at `-smp 2` and by free memory.

    Read at the time of the run, so a host booted with less runs fewer boots
    at a time rather than swapping.
    """
    by_cpu = (os.cpu_count() or 1) // DEFAULT_SMP
    available_gib = 0
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                available_gib = int(line.split()[1]) // (1 << 20)
    by_mem = available_gib // GUEST_MEM_GIB
    return max(1, min(by_cpu, by_mem))


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    """Starts every boot the collected tests need, before the first runs.

    Last of its hook, so `-k` and `-m` have already dropped what is not
    being run and its boots are never started.
    """
    if config.option.collectonly:
        return
    first_wanted: dict[str, int] = {}
    for index, item in enumerate(items):
        for name in getattr(item, "fixturenames", ()):
            if name in ENTRIES:
                first_wanted.setdefault(name, index)
    if not first_wanted:
        return
    # Ahead of the pool: one unpack and one warming boot, which the workers
    # would otherwise queue up behind.
    assets.unpacked_image()
    warmed_firmware()
    global _boot_pool
    _boot_pool = ThreadPoolExecutor(_workers(), thread_name_prefix="boot")
    for name in sorted(first_wanted, key=first_wanted.__getitem__):
        _boot_futures[name] = _boot_pool.submit(_boot, name)


def _booted(name: str) -> Boot:
    future = _boot_futures.get(name)
    return future.result() if future is not None else _boot(name)


def _entry_fixture(name: str):
    @pytest.fixture(scope="session", name=name)
    def wait_for_boot() -> Boot:
        boot = _booted(name)
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
linux = _entry_fixture("linux")


def broken(name: str):
    """Marks a test of an entry known not to boot: it must fail, so the day
    it passes is noticed."""
    reason = ENTRIES[name].broken
    assert reason is not None, f"{name} is not marked broken"
    return pytest.mark.xfail(reason=reason, strict=True)


_reports: list[pytest.TestReport] = []
_session_start = 0.0


def pytest_sessionstart(session: pytest.Session) -> None:
    global _session_start
    _session_start = time.monotonic()
    reason = unsupported_binary()
    if reason is not None:
        pytest.exit(
            f"This suite needs the QEMU drtm branch, see docs/testing.md: {reason}",
            returncode=1,
        )


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    _reports.append(report)


def _outcome_per_test() -> dict[str, tuple[str, float]]:
    collapsed: dict[str, tuple[str, float]] = {}
    for report in _reports:
        outcome, duration = collapsed.get(report.nodeid, ("passed", 0.0))
        if report.outcome != "passed":
            outcome = report.outcome
        collapsed[report.nodeid] = (outcome, duration + report.duration)
    return collapsed


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Writes `results.txt` beside the run's logs."""
    if _boot_pool is not None:
        _boot_pool.shutdown(wait=True, cancel_futures=True)
    if not _reports:
        return
    collapsed = _outcome_per_test()
    counts: dict[str, int] = {}
    for outcome, _ in collapsed.values():
        counts[outcome] = counts.get(outcome, 0) + 1
    summary = ", ".join(
        f"{count} {outcome}" for outcome, count in sorted(counts.items())
    )
    lines = [
        f"finished:    {datetime.now().astimezone().isoformat()}",
        f"exit status: {exitstatus}",
        f"summary:     {summary} in {time.monotonic() - _session_start:.1f}s",
        "",
    ]
    lines += [
        f"{outcome.upper():<7} {duration:7.1f}s  {nodeid}"
        for nodeid, (outcome, duration) in collapsed.items()
    ]
    failures = [report for report in _reports if report.failed]
    if failures:
        lines.append("")
        for report in failures:
            lines += [
                f"=== {report.nodeid} ({report.when}) ===",
                report.longreprtext,
                "",
            ]
    (_get_run_log_dir() / "results.txt").write_text("\n".join(lines) + "\n")
