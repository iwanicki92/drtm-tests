# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""`tb-boot`: the same boot as the tests, by hand, with the console on stdio.

    tb-boot [-f dasharo|seabios] [-m MEM] [-s SMP] [-w] [-n] [--no-strict]
            [-- QEMU ARGS]
    tb-boot query          query-amd-drtm on the running instance

Ctrl-A x quits, Ctrl-A c switches to the monitor. The firmware copy, the
TPM state, the QMP socket and qemu.log live under run/ in this repository.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from drtmtest import machine, trenchboot
from drtmtest.dasharo import FIRMWARE
from drtmtest.qemu_vm import (
    binary,
    pflash_args,
    qmp_args,
    start_swtpm,
    tpm_args,
    use_kvm,
)
from drtmtest.qmp_client import QmpClient

RUN_DIR = Path(__file__).resolve().parent.parent / "run"


def _query(qmp_sock: Path) -> int:
    record = QmpClient(str(qmp_sock)).execute("query-amd-drtm")
    print(json.dumps(record, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "-f",
        "--firmware",
        choices=["dasharo", "seabios"],
        default="dasharo",
        help="Dasharo's UEFI build as flash, or QEMU's SeaBIOS for legacy boot",
    )
    parser.add_argument("-m", "--mem", default=machine.DEFAULT_MEM)
    parser.add_argument("-s", "--smp", type=int, default=machine.DEFAULT_SMP)
    parser.add_argument(
        "-w", "--writable", action="store_true", help="write to the image, no snapshot"
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="print the command"
    )
    parser.add_argument(
        "--no-strict", action="store_true", help="log broken rules only"
    )
    parser.add_argument("rest", nargs="*", help="'query', or QEMU arguments after --")
    opts = parser.parse_args()

    qmp_sock = RUN_DIR / "qmp.sock"
    if opts.rest[:1] == ["query"]:
        return _query(qmp_sock)

    RUN_DIR.mkdir(exist_ok=True)
    firmware: Path | None = None
    if opts.firmware == "dasharo":
        firmware = RUN_DIR / "firmware.rom"
        if not firmware.exists():
            # Kept between runs, so the variable store persists like on a board.
            shutil.copy(FIRMWARE.fetch(trenchboot.CACHE_DIR), firmware)
    image = trenchboot.unpacked_image()
    swtpm_sock = RUN_DIR / "swtpm.sock"
    qmp_sock.unlink(missing_ok=True)
    # The same line the tests run, `docs/qemu.md` explains it, with the
    # console on stdio instead of a socket.
    args = [
        binary(),
        "-accel",
        "kvm" if use_kvm() else "tcg",
        "-display",
        "none",
        "-action",
        "panic=pause",
        "-D",
        str(RUN_DIR / "qemu.log"),
        *machine.options(
            image,
            smp=opts.smp,
            mem=opts.mem,
            strict=not opts.no_strict,
            snapshot=not opts.writable,
        ),
        *tpm_args(str(swtpm_sock)),
        *qmp_args(str(qmp_sock)),
    ]
    if firmware is not None:
        args += pflash_args(firmware)
    args += ["-serial", "mon:stdio", *opts.rest]
    if opts.dry_run:
        print(shlex.join(args))
        return 0

    print(f"traces and guest errors go to {RUN_DIR / 'qemu.log'}", file=sys.stderr)
    print("query the launch record with: tb-boot query", file=sys.stderr)
    with open(RUN_DIR / "swtpm.log", "wb") as swtpm_log:
        swtpm = start_swtpm(RUN_DIR / "tpmstate", str(swtpm_sock), swtpm_log)
        try:
            return subprocess.call(args, env=os.environ)
        finally:
            swtpm.terminate()
            swtpm.wait()


if __name__ == "__main__":
    sys.exit(main())
