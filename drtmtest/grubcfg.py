# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""GRUB's configuration as the image carries it, read off the FAT boot
partition with mtools, no mount and no copy, and a menu entry's commands
with a kernel parameter added, for a boot typed at GRUB's shell.
"""

import re
import struct
import subprocess
from pathlib import Path

# Where the image's GRUB reads its menu from. The legacy copy under
# `/grub/` is the same file.
CONFIG = "/EFI/BOOT/grub.cfg"

# The MBR partition type of an EFI system partition, the wic's boot one.
_ESP = 0xEF

_MENUENTRY_RE = re.compile(r"""^menuentry\s+(['"])(.*?)\1\s*\{$""")


def boot_partition_offset(image: Path) -> int:
    """Where the boot partition starts, in bytes, from the master boot
    record's table. The wic is MBR partitioned."""
    with open(image, "rb") as f:
        mbr = f.read(512)
    if len(mbr) < 512 or mbr[510:512] != b"\x55\xaa":
        raise ValueError(f"{image} has no master boot record")
    for i in range(4):
        entry = mbr[446 + 16 * i : 462 + 16 * i]
        if entry[4] == _ESP:
            return struct.unpack_from("<I", entry, 8)[0] * 512
    raise LookupError(f"{image} has no EFI system partition in its MBR")


def read(image: Path, path: str = CONFIG) -> str:
    """One file off the boot partition, through `mtype`."""
    offset = boot_partition_offset(image)
    result = subprocess.run(
        ["mtype", "-i", f"{image}@@{offset}", f"::{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"mtype could not read {path} off {image}: {result.stderr}")
    return result.stdout


def entries(config: str) -> dict[str, list[str]]:
    """Each menu entry's commands by title, comments and blank lines
    dropped. Functions and settings outside the entries are GRUB's once
    the menu is up, so an entry's commands run at the shell as they are."""
    found: dict[str, list[str]] = {}
    title = None
    for line in config.splitlines():
        line = line.strip()
        if title is None:
            match = _MENUENTRY_RE.match(line)
            if match:
                title = match.group(2)
                found[title] = []
        elif line == "}":
            title = None
        elif line and not line.startswith("#"):
            found[title].append(line)
    return found


def with_parameter(commands: list[str], parameter: str) -> list[str]:
    """The commands with `parameter` at the end of the kernel's line."""
    out = []
    found = False
    for command in commands:
        if command.split(maxsplit=1)[0] == "linux":
            command = f"{command} {parameter}"
            found = True
        out.append(command)
    if not found:
        raise LookupError(f"no linux command among {commands}")
    return out


def commands(image: Path, title: str, parameter: str) -> list[str]:
    """The commands of the image's entry `title` with `parameter` added
    to its kernel command line."""
    found = entries(read(image))
    if title not in found:
        raise LookupError(f"no GRUB entry {title!r} in the image, it has {list(found)}")
    return with_parameter(found[title], parameter)
