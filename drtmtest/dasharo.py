# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Dasharo's coreboot+UEFI build for QEMU Q35, the firmware both suites boot
under: Dasharo tests TrenchBoot on it, so a launch is a path it already
walks.
"""

import threading
from collections.abc import Callable
from pathlib import Path

from drtmtest.assets import Asset

FIRMWARE = Asset(
    url=(
        "https://github.com/Dasharo/coreboot/releases/download/"
        "qemu_q35_v0.2.1/qemu_q35_all_menus.rom"
    ),
    sha256="c6be232bc9884888b4b9dbe0fa85aa2a48042bdda456e3608c3f1d93e519d95d",
)

# The boot manager's prompt, the first thing on the serial console. ENTER
# boots the default entry at once instead of after its own timeout.
BOOT_PROMPT = "ENTER to boot directly"

_warm_lock = threading.Lock()


def warmed_firmware(cache_dir: Path, boot: Callable[[Path], None]) -> Path:
    """The firmware after one boot, made on first use and kept beside the
    download.

    Populating the variable store happens once, on an image that has never
    booted, and costs a few seconds, so every boot after this one starts
    from a store that is there. `boot(scratch)` runs that one boot with
    `save_firmware_to=scratch`, and what it boots is the suite's choice.
    """
    path = cache_dir / f"{FIRMWARE.sha256}.warm"
    with _warm_lock:
        if path.exists():
            return path
        scratch = path.with_suffix(".warming")
        boot(scratch)
        # Renamed only once it holds a complete boot, so an interrupted run
        # leaves no half-written image for the next one to trust.
        scratch.replace(path)
    return path
