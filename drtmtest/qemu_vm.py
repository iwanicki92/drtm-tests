# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""One QEMU process with its serial console on a socket, QMP beside it and
an swtpm behind it when asked for. What it boots is the caller's options.
"""

import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from collections.abc import Iterable, Mapping
from pathlib import Path

from drtmtest.qmp_client import QmpClient

# Starting paused and quitting takes well under a second.
_PROBE_TIMEOUT = 30.0

# The longest a boot stays silent: GRUB loading Xen, the kernel and the
# initrd over IDE is about 10 s idle, and a loaded host stretches it.
IDLE_TIMEOUT = 90.0


def binary() -> str:
    """Which `qemu-system-x86_64` to run, honouring `DRTM_QEMU_BINARY`.

    A path, or a name to find on `PATH`. Only a QEMU carrying the `drtm`
    branch runs SKINIT and the devices these suites boot on, which is why
    this exists.
    """
    return os.environ.get("DRTM_QEMU_BINARY", "qemu-system-x86_64")


def use_kvm() -> bool:
    """Whether to run under KVM, honouring `DRTM_QEMU_ACCEL`.

    `tcg` is the default: it is the only accelerator that runs SKINIT, and
    a guest with `smm=on` measured slower under KVM on every machine tried,
    about 2x on a nested-virtualisation host. `kvm` forces KVM and `auto`
    picks it whenever `/dev/kvm` is usable.
    """
    accel = os.environ.get("DRTM_QEMU_ACCEL", "tcg").lower()
    if accel == "tcg":
        return False
    if accel == "kvm":
        return True
    if accel != "auto":
        raise ValueError(
            f"DRTM_QEMU_ACCEL must be 'auto', 'kvm' or 'tcg', got {accel!r}"
        )
    return os.access("/dev/kvm", os.R_OK | os.W_OK)


def unsupported_binary(
    options: Iterable[str], rejects: Mapping[str, str] | None = None
) -> str | None:
    """Why the QEMU in use cannot run a suite, or `None` if it can.

    Starts it paused with `options`, the arguments only our build accepts,
    and quits. Upstream refuses most of them outright. `rejects` maps a
    substring of a clean probe's stderr to the reason to report, for the
    ones upstream drops with a warning instead.
    """
    args = [
        binary(),
        "-accel",
        "tcg",
        "-nodefaults",
        "-display",
        "none",
        "-S",
        "-monitor",
        "stdio",
        *options,
    ]
    try:
        probe = subprocess.run(
            args,
            input="quit\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=_PROBE_TIMEOUT,
        )
    except FileNotFoundError:
        return f"{binary()} was not found"
    except subprocess.TimeoutExpired:
        return f"{binary()} did not quit within {_PROBE_TIMEOUT:.0f}s"
    if probe.returncode != 0:
        lines = probe.stderr.strip().splitlines()
        return lines[-1] if lines else f"it exited with {probe.returncode}"
    for needle, reason in (rejects or {}).items():
        if needle in probe.stderr:
            return reason
    return None


def tpm_args(sock: str, kind: str = "tis") -> list[str]:
    """An swtpm on `sock` as a TPM 2.0 behind the `tis` or `crb` frontend.

    QEMU's `emulator` backend drives swtpm over its control channel, so one
    socket serves both.
    """
    if kind not in ("tis", "crb"):
        raise ValueError(f"tpm must be 'tis' or 'crb', got {kind!r}")
    return [
        "-chardev",
        f"socket,id=chrtpm,path={sock}",
        "-tpmdev",
        "emulator,id=tpm0,chardev=chrtpm",
        "-device",
        f"tpm-{kind},tpmdev=tpm0",
    ]


def pflash_args(firmware: Path) -> list[str]:
    """`firmware` as the flash, variable store included, so hand it a copy."""
    return ["-drive", f"if=pflash,format=raw,file={firmware}"]


def qmp_args(sock: str) -> list[str]:
    return ["-qmp", f"unix:{sock},server,nowait"]


# The PCR banks a fresh TPM state gets. swtpm allocates every bank libtpms
# has, and a Linux launch then fails its late PCR extend: the SKL event log
# carries one digest per bank below, and the kernel hands the TPM exactly
# those, which a TPM with more banks active refuses. A discrete TPM ships
# with these two.
PCR_BANKS: tuple[str, ...] = ("sha1", "sha256")


def pcr_banks() -> tuple[str, ...]:
    """The banks a boot's fresh TPM state gets: what `DRTM_PCR_BANKS`
    lists, comma separated, else `PCR_BANKS`. The SKL declares the TPM's
    banks in its event log and fills the ones it cannot hash for with a
    placeholder, and Linux refuses a log that does not match the TPM, so
    other sets are for exercising that."""
    value = os.environ.get("DRTM_PCR_BANKS", "").strip().lower()
    if not value:
        return PCR_BANKS
    return tuple(bank.strip() for bank in value.split(",") if bank.strip())


_STATE_FILE = "tpm2-00.permall"


def _wait_for_socket(process: subprocess.Popen, sock: str, what: str) -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if Path(sock).exists():
            return
        if process.poll() is not None:
            raise RuntimeError(
                f"swtpm exited with {process.returncode} before creating its {what}"
            )
        time.sleep(0.05)
    process.kill()
    raise TimeoutError(f"swtpm never created its {what} at {sock}")


def allocate_pcr_banks(state_dir: Path, banks: Iterable[str], log_f) -> None:
    """Writes a TPM 2.0 state into `state_dir` with only `banks` active,
    through `swtpm_setup`, replacing any state already there."""
    state_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "swtpm_setup",
            "--tpm2",
            "--tpmstate",
            str(state_dir),
            "--pcr-banks",
            ",".join(banks),
            "--overwrite",
        ],
        stdout=log_f,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if not (state_dir / _STATE_FILE).exists():
        raise RuntimeError(f"swtpm_setup wrote no {_STATE_FILE} into {state_dir}")


def start_swtpm(
    state_dir: Path,
    sock: str,
    log_f,
    banks: Iterable[str] | None = None,
) -> subprocess.Popen:
    """Starts a TPM 2.0 emulator on a Unix socket and waits for the socket.

    `state_dir` gets a fresh state with `banks` active first, what
    `pcr_banks()` says when that is None.

    Errors go to stderr regardless of `--log`, so a log holding only
    `swtpm_setup`'s lines means a clean run. `DRTM_SWTPM_LOG_LEVEL` adds
    debug tracing: level 5 and above enables libtpms logging, 20 dumps every
    command.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    allocate_pcr_banks(state_dir, banks if banks is not None else pcr_banks(), log_f)
    args = [
        "swtpm",
        "socket",
        "--tpm2",
        "--tpmstate",
        f"dir={state_dir}",
        "--ctrl",
        f"type=unixio,path={sock}",
    ]
    level = os.environ.get("DRTM_SWTPM_LOG_LEVEL")
    if level:
        args += ["--log", f"fd=1,level={level}"]
    process = subprocess.Popen(args, stdout=log_f, stderr=subprocess.STDOUT)
    _wait_for_socket(process, sock, "control socket")
    return process


def _short_socket_path(prefix: str) -> str:
    # AF_UNIX paths are capped at about 108 bytes, so sockets cannot live
    # under a long per-boot log directory. Reserve a short unique name and
    # hand the daemon the bare path, which it creates itself.
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".sock")
    os.close(fd)
    os.unlink(path)
    return path


def _free_tcp_port() -> int:
    # Free again between here and QEMU binding it, so two boots starting at
    # once could in principle pick the same one. Not seen in practice.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QemuExited(RuntimeError):
    """QEMU went away while the console was being waited on."""


class GuestPanicked(RuntimeError):
    """The VM stopped as panicked: a strict-mode rule or the guest itself."""


class GuestHung(RuntimeError):
    """The console went silent for longer than a boot ever pauses."""


class QemuVm:
    """Runs one QEMU as a `with` block.

    `options` is the machine, CPU, memory and devices: everything but what
    the harness adds, which is the accelerator, the flash, the TPM, the
    serial console, QMP, the pause on a panic and the log file. `log_dir`
    receives the process's own output (`qemu-stderr.log`), its `-D` log
    (`qemu.log`), the swtpm log and the raw serial capture (`serial.log`),
    written as they arrive so they are useful even if the boot times out.

    The serial console is read by a background thread for the life of the
    block, and `expect` waits on it from a cursor that advances with every
    match, so one prompt seen twice is two matches.

    `firmware` is the flash image to boot, copied per boot so the guest's
    writes to its variable store land on the copy, or `None` for QEMU's own
    SeaBIOS. `save_firmware_to` keeps that copy after a clean exit, which
    is how a warmed image is made. `tpm` attaches an swtpm-backed TPM 2.0
    as `tis` or `crb`, or nothing when `None`.
    """

    def __init__(
        self,
        log_dir: Path,
        options: Iterable[str],
        firmware: Path | None = None,
        tpm: str | None = None,
        save_firmware_to: Path | None = None,
    ):
        if tpm is not None:
            tpm_args("", tpm)
        self.log_dir = Path(log_dir)
        self.options = list(options)
        self.firmware = Path(firmware) if firmware is not None else None
        self.tpm = tpm
        self.save_firmware_to = save_firmware_to
        self.qmp: QmpClient | None = None
        self._workdir: str | None = None
        self._firmware_copy: Path | None = None
        self._process: subprocess.Popen | None = None
        self._swtpm: subprocess.Popen | None = None
        self._swtpm_sock: str | None = None
        self._qmp_sock: str | None = None
        self._serial_sock: socket.socket | None = None
        self._files: list = []
        self._serial_buf = bytearray()
        self._serial_lock = threading.Lock()
        self._cursor = 0
        self._reader: threading.Thread | None = None
        self._stop = threading.Event()
        self._last_status_check = 0.0

    def __enter__(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._workdir = tempfile.mkdtemp(prefix="drtmtest-")
        serial_log = open(self.log_dir / "serial.log", "wb")
        qemu_out = open(self.log_dir / "qemu-stderr.log", "wb")
        self._files = [serial_log, qemu_out]
        self._serial_log = serial_log

        args = [
            binary(),
            "-accel",
            "kvm" if use_kvm() else "tcg",
            "-display",
            "none",
            # A panic leaves the VM stopped rather than exiting, so the run
            # state names it and QMP still answers about the machine.
            "-action",
            "panic=pause",
            "-D",
            str(self.log_dir / "qemu.log"),
            *self.options,
        ]
        if self.firmware is not None:
            # The variable store lives in this image, so each boot gets a copy.
            firmware = Path(self._workdir) / "firmware.rom"
            shutil.copy(self.firmware, firmware)
            self._firmware_copy = firmware
            args += pflash_args(firmware)
        if self.tpm is not None:
            swtpm_log = open(self.log_dir / "swtpm.log", "wb")
            self._files.append(swtpm_log)
            self._swtpm_sock = _short_socket_path("drtmtest-swtpm-")
            self._swtpm = start_swtpm(
                Path(self._workdir) / "swtpm-state", self._swtpm_sock, swtpm_log
            )
            args += tpm_args(self._swtpm_sock, self.tpm)
        self._qmp_sock = _short_socket_path("drtmtest-qmp-")
        args += qmp_args(self._qmp_sock)
        serial_port = _free_tcp_port()
        # `server` without `nowait`: QEMU holds the guest until the console
        # is connected, so the first bytes out are never lost.
        args += ["-serial", f"tcp:127.0.0.1:{serial_port},server"]
        (self.log_dir / "qemu-args.txt").write_text("\n".join(args) + "\n")
        self._process = subprocess.Popen(
            args, stdout=qemu_out, stderr=subprocess.STDOUT
        )
        self.qmp = QmpClient(self._qmp_sock)
        self._serial_sock = self._connect_serial(serial_port)
        self._serial_sock.settimeout(0.2)
        self._reader = threading.Thread(target=self._read_serial, daemon=True)
        self._reader.start()
        return self

    def wait_for_qmp(self, timeout: float = 5.0) -> QmpClient:
        """The QMP client once QEMU has opened its socket.

        For a boot started with `-S`, which has to be poked over QMP before
        the console prints anything.
        """
        assert self._qmp_sock is not None and self.qmp is not None
        deadline = time.monotonic() + timeout
        while not os.path.exists(self._qmp_sock):
            if time.monotonic() >= deadline:
                raise TimeoutError("QEMU never created its QMP socket")
            time.sleep(0.05)
        return self.qmp

    def _connect_serial(self, port: int, timeout: float = 10.0) -> socket.socket:
        deadline = time.monotonic() + timeout
        last: Exception | None = None
        while time.monotonic() < deadline:
            if self._process is not None and self._process.poll() is not None:
                raise QemuExited(self._exit_reason())
            try:
                return socket.create_connection(("127.0.0.1", port), timeout=1)
            except ConnectionRefusedError as e:
                last = e
                time.sleep(0.1)
        raise TimeoutError(f"QEMU never opened its serial port: {last}")

    def _read_serial(self) -> None:
        assert self._serial_sock is not None
        while not self._stop.is_set():
            try:
                chunk = self._serial_sock.recv(65536)
            except TimeoutError:
                continue
            except OSError:
                break
            if not chunk:
                break
            with self._serial_lock:
                # `__exit__` closes the log under this lock, so a reader that
                # outlived the join must not write to it.
                if self._stop.is_set():
                    break
                self._serial_log.write(chunk)
                self._serial_log.flush()
                self._serial_buf.extend(chunk)

    @property
    def capture(self) -> str:
        """Everything the guest has printed so far."""
        with self._serial_lock:
            return bytes(self._serial_buf).decode("utf-8", "replace")

    def send(self, data: bytes) -> None:
        assert self._serial_sock is not None
        self._serial_sock.sendall(data)

    def _exit_reason(self) -> str:
        assert self._process is not None
        tail = ""
        stderr = self.log_dir / "qemu-stderr.log"
        if stderr.exists():
            tail = stderr.read_text(errors="replace").strip().splitlines()[-3:]
            tail = "\n".join(tail)
        return f"QEMU exited with {self._process.returncode}\n{tail}"

    def _check_alive(self) -> None:
        """Raises if QEMU is gone or the VM stopped as panicked.

        A panic pauses the VM, which leaves the process running and the
        console silent, so the run state is what says it happened. Polled
        at most once a second.
        """
        assert self._process is not None
        if self._process.poll() is not None:
            raise QemuExited(self._exit_reason())
        now = time.monotonic()
        if now - self._last_status_check < 1.0:
            return
        self._last_status_check = now
        assert self.qmp is not None
        try:
            status = self.qmp.execute("query-status")
        except OSError:
            return
        if status.get("status") == "guest-panicked":
            raise GuestPanicked(
                f"the VM stopped as panicked, see {self.log_dir / 'qemu.log'}"
            )

    def expect(
        self,
        needle: str,
        timeout: float,
        failures: Iterable[str] = (),
        answers: Mapping[str, bytes] | None = None,
        idle: float = IDLE_TIMEOUT,
    ) -> str:
        """Waits for `needle` after the cursor and returns the text up to it.

        `failures` are patterns that end the wait at once with an error,
        such as a kernel panic. `answers` map a prompt to what to send when
        it appears, once per appearance, for prompts that hold the boot.
        `idle` is how long the console may stay silent: a guest that hangs
        prints nothing, and that is reported well before `timeout`.
        """
        needle_b = needle.encode()
        failure_b = [f.encode() for f in failures]
        answered = {k.encode(): self._cursor for k in (answers or {})}
        now = time.monotonic()
        deadline = now + timeout
        last_seen = now
        seen = 0
        while True:
            with self._serial_lock:
                buf = bytes(self._serial_buf[self._cursor :])
            if len(buf) != seen:
                seen = len(buf)
                last_seen = time.monotonic()
            elif time.monotonic() - last_seen >= idle:
                raise GuestHung(
                    f"nothing on the console for {idle:.0f}s while waiting for "
                    f"{needle!r}. Read since the last match:\n{buf.decode('utf-8', 'replace')}"
                )
            at = buf.find(needle_b)
            if at >= 0:
                end = at + len(needle_b)
                self._cursor += end
                return buf[:end].decode("utf-8", "replace")
            for f in failure_b:
                if f in buf:
                    raise GuestPanicked(
                        f"{f.decode()!r} on the console while waiting for {needle!r}"
                    )
            for prompt, after in answered.items():
                at = buf.find(prompt, after - self._cursor)
                if at >= 0:
                    assert answers is not None
                    self.send(answers[prompt.decode()])
                    answered[prompt] = self._cursor + at + len(prompt)
            self._check_alive()
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"no {needle!r} on the console within {timeout:.0f}s. "
                    f"Read since the last match:\n{buf.decode('utf-8', 'replace')}"
                )
            time.sleep(0.05)

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop.set()
        if self._serial_sock is not None:
            self._serial_sock.close()
        if self._reader is not None:
            self._reader.join(timeout=5)
        for process in (self._process, self._swtpm):
            # QEMU first, so it never sees its TPM backend vanish.
            if process is None:
                continue
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        for sock in (self._swtpm_sock, self._qmp_sock):
            if sock is not None:
                Path(sock).unlink(missing_ok=True)
        # After QEMU is down, so the pflash writes have landed, and only on
        # a clean exit: a boot that failed is not one to cache.
        if (
            self.save_firmware_to is not None
            and exc_type is None
            and self._firmware_copy is not None
        ):
            shutil.copy(self._firmware_copy, self.save_firmware_to)
        if self._workdir is not None:
            shutil.rmtree(self._workdir, ignore_errors=True)
        with self._serial_lock:
            for f in self._files:
                f.close()
        return False
