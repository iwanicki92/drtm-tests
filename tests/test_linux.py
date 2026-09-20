# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The Linux launch, which panics on this release. The Xen EFI entries
provide the control boot, so the normal Linux entry is not booted."""

from conftest import Boot, broken
from test_xen import assert_launched


@broken("linux_launch")
def test_launch_is_recorded_by_the_platform(linux_launch: Boot):
    assert_launched(linux_launch)


@broken("linux_launch")
def test_launch_is_seen_by_linux(linux_launch: Boot):
    assert "slaunch" in linux_launch.dmesg.lower(), linux_launch.dmesg
    assert "No such file" not in linux_launch.securityfs, linux_launch.securityfs
