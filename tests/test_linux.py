# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The Linux launch, which panics on the releases under UEFI and boots
through SeaBIOS, and the normal Linux boot: the kernel booted directly is
the one that found no disk when the launch machine's IOMMU passed DMA
through, so it stays under test."""

from conftest import Boot, broken
from test_xen import assert_launched, assert_not_launched

# What the kernel prints on a launch it recognises, as seen on hardware:
# the early setup in the decompressor's slaunch code, then the module.
LINUX_SETUP_DONE = "slaunch: AMD SKINIT setup complete"
LINUX_MODULE_UP = "slmodule: SKINIT Secure Launch module setup"


@broken("linux_launch")
def test_launch_is_recorded_by_the_platform(linux_launch: Boot):
    assert_launched(linux_launch)


@broken("linux_launch")
def test_launch_is_seen_by_linux(linux_launch: Boot):
    assert LINUX_SETUP_DONE in linux_launch.dmesg, linux_launch.dmesg
    assert LINUX_MODULE_UP in linux_launch.dmesg, linux_launch.dmesg
    assert "No such file" not in linux_launch.securityfs, linux_launch.securityfs


def test_legacy_launch_is_recorded_by_the_platform(linux_legacy_launch: Boot):
    assert_launched(linux_legacy_launch)


def test_legacy_launch_is_seen_by_linux(linux_legacy_launch: Boot):
    boot = linux_legacy_launch
    assert LINUX_SETUP_DONE in boot.dmesg, boot.dmesg
    assert LINUX_MODULE_UP in boot.dmesg, boot.dmesg
    assert "No such file" not in boot.securityfs, boot.securityfs


def test_normal_boot_launches_nothing(linux: Boot):
    assert_not_launched(linux)
    assert "slaunch" not in linux.dmesg.lower(), linux.dmesg
