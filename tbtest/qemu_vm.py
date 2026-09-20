# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""One QEMU process booting the image on the AMD launch machine, with an
swtpm behind it, its serial console on a socket and QMP beside it.
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

from tbtest.qmp_client import QmpClient

# A model with the SKINIT feature. Under `amd-drtm=on` the machine turns
# the feature on for any model, but Genoa is what the image was built for.
DEFAULT_CPU = "EPYC-Genoa"
DEFAULT_SMP = 2
DEFAULT_MEM = "2G"

# What the launch devices log when asked to, into qemu.log.
LAUNCH_TRACES = (
    "amd_drtm_*",
    "amd_nb_*",
    "x86_skinit",
    "x86_vm_cr_write",
    "x86_sipi_after_launch",
    "x86_init_held",
    "x86_init_redirected",
)

# Starting paused and quitting takes well under a second.
_PROBE_TIMEOUT = 30.0

# The longest a boot stays silent: GRUB loading Xen, the kernel and the
# initrd over IDE is about 10 s idle, and a loaded host stretches it.
IDLE_TIMEOUT = 90.0


def binary() -> str:
    """Which `qemu-system-x86_64` to run, honouring `DRTM_QEMU_BINARY`.

    A path, or a name to find on `PATH`. Only a QEMU carrying the `drtm`
    branch runs SKINIT, which is why this exists.
    """
    return os.environ.get("DRTM_QEMU_BINARY", "qemu-system-x86_64")


def use_kvm() -> bool:
    """Whether to pass `-enable-kvm`, honouring `DRTM_QEMU_ACCEL`.

    `tcg` is the default and the only accelerator that runs SKINIT. `kvm`
    forces KVM and `auto` picks it whenever `/dev/kvm` is usable, kept for
    booting the normal entries faster.
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


def unsupported_binary() -> str | None:
    """Why the QEMU in use cannot boot this image, or `None` if it can.

    Starts it paused on the launch machine. Upstream refuses the option.
    """
    args = [
        binary(),
        "-machine",
        "q35,amd-drtm=on",
        "-accel",
        "tcg",
        "-nodefaults",
        "-display",
        "none",
        "-S",
        "-monitor",
        "stdio",
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
    return None


def qemu_args(
    firmware: Path | None,
    image: Path,
    swtpm_sock: str,
    qmp_sock: str,
    cpu: str = DEFAULT_CPU,
    smp: int = DEFAULT_SMP,
    mem: str = DEFAULT_MEM,
    strict: bool = True,
    snapshot: bool = True,
    log_file: Path | None = None,
) -> list[str]:
    """The command line every boot shares, without a serial console.

    `firmware` is the flash image to boot, or `None` for QEMU's own SeaBIOS,
    the legacy path the image's MBR also supports. `strict` makes the
    platform device stop the VM on a broken launch rule, so a wrong launch
    is a panic the harness sees rather than a line in the log.
    """
    args = [
        binary(),
        "-machine",
        "q35,smm=on,amd-drtm=on",
        "-accel",
        "kvm" if use_kvm() else "tcg",
        "-cpu",
        cpu,
        "-smp",
        str(smp),
        "-m",
        mem,
        "-global",
        f"amd-drtm-platform.strict={'on' if strict else 'off'}",
        "-chardev",
        f"socket,id=chrtpm,path={swtpm_sock}",
        "-tpmdev",
        "emulator,id=tpm0,chardev=chrtpm",
        "-device",
        "tpm-tis,tpmdev=tpm0",
        "-drive",
        f"file={image},format=raw,if=none,id=hd,snapshot={'on' if snapshot else 'off'}",
        "-device",
        "ide-hd,drive=hd",
        "-display",
        "none",
        "-vga",
        "none",
        "-nic",
        "none",
        "-qmp",
        f"unix:{qmp_sock},server,nowait",
        "-d",
        "guest_errors",
    ]
    if firmware is not None:
        args += ["-drive", f"if=pflash,format=raw,file={firmware}"]
    if log_file is not None:
        args += ["-D", str(log_file)]
    for trace in LAUNCH_TRACES:
        args += ["-trace", trace]
    return args


def start_swtpm(state_dir: Path, sock: str, log_f) -> subprocess.Popen:
    """Starts a TPM 2.0 emulator on a Unix socket and waits for the socket.

    QEMU's `emulator` backend drives swtpm over its control channel, so one
    socket serves both. Errors go to stderr regardless of `--log`, so an
    empty log means a clean run.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [
            "swtpm",
            "socket",
            "--tpm2",
            "--tpmstate",
            f"dir={state_dir}",
            "--ctrl",
            f"type=unixio,path={sock}",
        ],
        stdout=log_f,
        stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if Path(sock).exists():
            return process
        if process.poll() is not None:
            raise RuntimeError(
                f"swtpm exited with {process.returncode} before creating its socket"
            )
        time.sleep(0.05)
    process.kill()
    raise TimeoutError(f"swtpm never created its control socket at {sock}")


def _short_socket_path(prefix: str) -> str:
    # AF_UNIX paths are capped at about 108 bytes, so sockets cannot live
    # under a long per-boot log directory. Reserve a short unique name and
    # hand the daemon the bare path, which it creates itself.
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".sock")
    os.close(fd)
    os.unlink(path)
    return path


def _free_tcp_port() -> int:
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
    """Runs one boot of the image as a `with` block.

    `log_dir` receives the QEMU process's own output and log (`qemu.log`),
    the swtpm log and the raw serial capture (`serial.log`), written as they
    arrive so they are useful even if the boot times out.

    The serial console is read by a background thread for the life of the
    block, and `expect` waits on it from a cursor that advances with every
    match, so one prompt seen twice is two matches.

    `save_firmware_to` keeps the firmware copy after a clean exit, which is
    how the warmed image is made.
    """

    def __init__(
        self,
        log_dir: Path,
        firmware: Path,
        image: Path,
        cpu: str = DEFAULT_CPU,
        smp: int = DEFAULT_SMP,
        mem: str = DEFAULT_MEM,
        strict: bool = True,
        save_firmware_to: Path | None = None,
    ):
        self.log_dir = Path(log_dir)
        self.firmware = Path(firmware)
        self.image = Path(image)
        self.cpu = cpu
        self.smp = smp
        self.mem = mem
        self.strict = strict
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
        self._workdir = tempfile.mkdtemp(prefix="tbtest-")
        serial_log = open(self.log_dir / "serial.log", "wb")
        qemu_out = open(self.log_dir / "qemu-stderr.log", "wb")
        swtpm_log = open(self.log_dir / "swtpm.log", "wb")
        self._files = [serial_log, qemu_out, swtpm_log]
        self._serial_log = serial_log

        # The variable store lives in this image, so each boot gets a copy.
        firmware = Path(self._workdir) / "firmware.rom"
        shutil.copy(self.firmware, firmware)
        self._firmware_copy = firmware

        self._swtpm_sock = _short_socket_path("tbtest-swtpm-")
        self._swtpm = start_swtpm(
            Path(self._workdir) / "swtpm-state", self._swtpm_sock, swtpm_log
        )
        self._qmp_sock = _short_socket_path("tbtest-qmp-")
        serial_port = _free_tcp_port()
        args = qemu_args(
            firmware,
            self.image,
            self._swtpm_sock,
            self._qmp_sock,
            cpu=self.cpu,
            smp=self.smp,
            mem=self.mem,
            strict=self.strict,
            log_file=self.log_dir / "qemu.log",
        )
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

        Strict mode stops the VM through the panic path, which leaves the
        process running and the console silent, so the run state is what
        says a launch rule broke. Polled at most once a second.
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
