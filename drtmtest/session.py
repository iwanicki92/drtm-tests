# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""A pytest plugin that boots ahead of the tests: every boot the collected
tests need is started in a pool at collection, each run gets a numbered
log directory, and `results.txt` in it says how the run went.
"""

import os
import re
import threading
import time
from collections.abc import Callable, Collection
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import pytest

_RUN_DIR_RE = re.compile(r"^(\d{4})-")
_MAX_RUN_NUMBER = 9999


def cpu_workers() -> int:
    """One boot per core: overlapping past the core count measured slower."""
    return os.cpu_count() or 1


class BootSession[T]:
    """Boots shared by a session, one per name, overlapping in a pool.

    `boot(name, log_dir)` runs one and returns what its fixture hands the
    tests. `names` are the fixture names that stand for a boot, which is
    how collection knows which to start. `prepare(names)` runs before the
    pool, for the one build or unpack every boot would otherwise queue up
    behind. `workers` is the pool size, or how to compute it at run time.
    `check()` returns why this QEMU cannot run the suite, which ends the
    session before anything boots, and `header()` adds lines to
    `results.txt`.

    Register it from `conftest.py`:

        def pytest_configure(config):
            config.pluginmanager.register(SESSION)

    and have each boot fixture return `SESSION.booted(name)`.
    """

    def __init__(
        self,
        logs_dir: Path,
        boot: Callable[[str, Path], T],
        names: Collection[str],
        workers: int | Callable[[], int] = cpu_workers,
        prepare: Callable[[list[str]], None] | None = None,
        check: Callable[[], str | None] | None = None,
        header: Callable[[], list[str]] | None = None,
    ):
        self.logs_dir = Path(logs_dir)
        self._boot = boot
        self.names = names
        self._workers = workers
        self._prepare = prepare
        self._check = check
        self._header = header
        self._run_log_dir: Path | None = None
        self._run_log_dir_lock = threading.Lock()
        self._pool: ThreadPoolExecutor | None = None
        self._futures: dict[str, Future[T]] = {}
        self._reports: list[pytest.TestReport] = []
        self._started = 0.0

    def _next_run_number(self) -> int:
        if not self.logs_dir.exists():
            return 1
        numbers = [
            int(match.group(1))
            for path in self.logs_dir.iterdir()
            if path.is_dir() and (match := _RUN_DIR_RE.match(path.name))
        ]
        return max(numbers, default=0) + 1

    def run_log_dir(self) -> Path:
        """This run's log directory, created on first use.

        Locked because concurrent boots reach it from their own threads,
        and two of them numbering the run at once would make two.
        """
        with self._run_log_dir_lock:
            if self._run_log_dir is not None:
                return self._run_log_dir
            number = self._next_run_number()
            if number > _MAX_RUN_NUMBER:
                pytest.exit(
                    f"{self.logs_dir} has reached run {_MAX_RUN_NUMBER}, the "
                    "4-digit limit. Clean out old runs before testing again.",
                    returncode=1,
                )
            now = datetime.now().astimezone()
            run_dir = self.logs_dir / f"{number:04d}-{now.date().isoformat()}"
            run_dir.mkdir(parents=True)
            (run_dir / "timestamp.txt").write_text(now.isoformat() + "\n")
            self._run_log_dir = run_dir
            return run_dir

    def boot_log_dir(self, name: str) -> Path:
        """`default_boot` writes to `boot-default`, so a log directory
        names the boot that produced it."""
        stem = name.removesuffix("_boot").replace("_", "-")
        return self.run_log_dir() / f"boot-{stem}"

    def _run(self, name: str) -> T:
        return self._boot(name, self.boot_log_dir(name))

    def booted(self, name: str) -> T:
        """What `name`'s boot produced, waiting for it to finish.

        Collection submits every boot the run needs, so this usually just
        takes the result. A boot reached some other way still runs here
        rather than failing.
        """
        future = self._futures.get(name)
        return future.result() if future is not None else self._run(name)

    def pytest_sessionstart(self, session: pytest.Session) -> None:
        self._started = time.monotonic()
        reason = self._check() if self._check is not None else None
        if reason is not None:
            pytest.exit(reason, returncode=1)

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(
        self, config: pytest.Config, items: list[pytest.Item]
    ) -> None:
        """Starts every boot the collected tests need, before the first runs.

        Only what was collected is submitted, so running one test boots
        once, and in the order the tests ask for them, so the pool works on
        what is wanted first. Last of its hook, so `-k` and `-m` have
        already dropped what is not being run and its boots never start.
        """
        if config.option.collectonly:
            return
        first_wanted: dict[str, int] = {}
        for index, item in enumerate(items):
            for name in getattr(item, "fixturenames", ()):
                if name in self.names:
                    first_wanted.setdefault(name, index)
        if not first_wanted:
            return
        wanted = sorted(first_wanted, key=first_wanted.__getitem__)
        if self._prepare is not None:
            self._prepare(wanted)
        workers = self._workers if isinstance(self._workers, int) else self._workers()
        self._pool = ThreadPoolExecutor(workers, thread_name_prefix="boot")
        for name in wanted:
            self._futures[name] = self._pool.submit(self._run, name)

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        self._reports.append(report)

    def _outcome_per_test(self) -> dict[str, tuple[str, float]]:
        """One outcome and duration per test, summed over its phases.

        A boot fixture's cost lands in setup and its teardown in the last
        test's teardown, so counting only `call` would report 0.0s for
        every test. A non-passing phase decides the outcome.
        """
        collapsed: dict[str, tuple[str, float]] = {}
        for report in self._reports:
            outcome, duration = collapsed.get(report.nodeid, ("passed", 0.0))
            if report.outcome != "passed":
                outcome = report.outcome
            collapsed[report.nodeid] = (outcome, duration + report.duration)
        return collapsed

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        """Writes `results.txt` beside the run's logs, so a log directory
        records what was being tested and how it went."""
        if self._pool is not None:
            # Drops boots nothing ever waited for, which is what -x leaves
            # queued. One already running still has to finish.
            self._pool.shutdown(wait=True, cancel_futures=True)
        if not self._reports:
            return
        collapsed = self._outcome_per_test()
        counts: dict[str, int] = {}
        for outcome, _ in collapsed.values():
            counts[outcome] = counts.get(outcome, 0) + 1
        summary = ", ".join(
            f"{count} {outcome}" for outcome, count in sorted(counts.items())
        )
        lines = [f"finished:    {datetime.now().astimezone().isoformat()}"]
        if self._header is not None:
            lines += self._header()
        lines += [
            f"exit status: {exitstatus}",
            f"summary:     {summary} in {time.monotonic() - self._started:.1f}s",
            "",
        ]
        lines += [
            f"{outcome.upper():<7} {duration:7.1f}s  {nodeid}"
            for nodeid, (outcome, duration) in collapsed.items()
        ]
        failures = [report for report in self._reports if report.failed]
        if failures:
            lines.append("")
            for report in failures:
                lines += [
                    f"=== {report.nodeid} ({report.when}) ===",
                    report.longreprtext,
                    "",
                ]
        (self.run_log_dir() / "results.txt").write_text("\n".join(lines) + "\n")
