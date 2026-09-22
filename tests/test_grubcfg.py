# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Reading GRUB's menu off an image and turning an entry into commands
for the shell, against an excerpt shaped like the images' `grub.cfg`."""

import struct
from pathlib import Path

import pytest

from drtmtest.grubcfg import (
    boot_partition_offset,
    entries,
    with_parameter,
)

CONFIG = """\
serial --unit=0 --speed=115200
default=boot
timeout=5

insmod slaunch

# slaunch sets slaunch_psp on AMD when a PSP with the DRTM service is there.
function load_skl {
  if [ "$slaunch_psp" = "1" ]; then
    slaunch_module /skl-amdsl.bin
  else
    slaunch_module /skl.bin
  fi
}

menuentry 'Boot Linux normally'{
  echo 'Loading Linux ...'
  linux /bzImage rootwait root=LABEL=root console=ttyS0,115200
}

menuentry 'Boot Linux with TrenchBoot'{
  echo 'Enabling slaunch ...'
  slaunch

  # The SKL, then the kernel.
  load_skl
  linux /bzImage rootwait root=LABEL=root console=ttyS0,115200
}

menuentry "Boot Xen with TrenchBoot (MB2)" {
  slaunch
  slaunch_module /skl.bin
  multiboot2 /xen placeholder console=com1
  module2 /bzImage rootwait root=LABEL=root
}
"""


def test_entries_keep_their_commands_in_order_without_the_noise():
    found = entries(CONFIG)
    assert list(found) == [
        "Boot Linux normally",
        "Boot Linux with TrenchBoot",
        "Boot Xen with TrenchBoot (MB2)",
    ]
    assert found["Boot Linux with TrenchBoot"] == [
        "echo 'Enabling slaunch ...'",
        "slaunch",
        "load_skl",
        "linux /bzImage rootwait root=LABEL=root console=ttyS0,115200",
    ]
    assert found["Boot Xen with TrenchBoot (MB2)"][2].startswith("multiboot2 ")


def test_the_parameter_lands_on_the_kernel_line_alone():
    commands = entries(CONFIG)["Boot Linux with TrenchBoot"]
    assert with_parameter(commands, "drtmtest=alt") == [
        *commands[:3],
        "linux /bzImage rootwait root=LABEL=root console=ttyS0,115200 drtmtest=alt",
    ]


def test_an_entry_without_a_kernel_line_is_refused():
    commands = entries(CONFIG)["Boot Xen with TrenchBoot (MB2)"]
    with pytest.raises(LookupError):
        with_parameter(commands, "drtmtest=alt")


def _mbr(partitions: list[tuple[int, int]]) -> bytes:
    """A master boot record with (type, first LBA) partitions."""
    table = b""
    for type_, lba in partitions:
        table += bytes([0x80, 0, 0, 0, type_, 0, 0, 0]) + struct.pack("<II", lba, 1)
    return bytes(446) + table.ljust(64, b"\0") + b"\x55\xaa"


def test_the_boot_partition_is_the_efi_system_partition(tmp_path: Path):
    image = tmp_path / "disk.wic"
    image.write_bytes(_mbr([(0x83, 100), (0xEF, 2048), (0x83, 264192)]))
    assert boot_partition_offset(image) == 2048 * 512


def test_a_disk_without_one_is_refused(tmp_path: Path):
    image = tmp_path / "disk.wic"
    image.write_bytes(_mbr([(0x83, 2048)]))
    with pytest.raises(LookupError):
        boot_partition_offset(image)
    image.write_bytes(bytes(512))
    with pytest.raises(ValueError):
        boot_partition_offset(image)
