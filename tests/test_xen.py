# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The Xen entries: a launch through SKINIT on the EFI path under Dasharo,
its control boot without one, and the MB2 launch under SeaBIOS."""

from conftest import PCR_ONES, PCR_ZERO, Boot


def assert_launched(boot: Boot) -> None:
    """What every launch leaves: the platform's record of it, PCRs 17 and
    18 reset and extended, and PCR 19 reset by the same locality 4 start
    but extended by nothing on this path."""
    assert boot.record["launched"] is True
    assert boot.record["hash"] == "ok"
    assert boot.record["slb-length"] > 0
    assert boot.record["sl-dev"] is False, "SKL should have released SL_DEV"
    assert boot.record["dma-blocks"] == []
    assert boot.pcrs[17] not in (PCR_ZERO, PCR_ONES), boot.pcrs
    assert boot.pcrs[18] not in (PCR_ZERO, PCR_ONES), boot.pcrs
    assert boot.pcrs[19] == PCR_ZERO, boot.pcrs


def assert_not_launched(boot: Boot) -> None:
    """Without a launch the DRTM PCRs stay as the TPM started them."""
    assert boot.record["launched"] is False
    assert boot.pcrs[17] == PCR_ONES, boot.pcrs
    assert boot.pcrs[19] == PCR_ONES, boot.pcrs


def test_efi_launch_is_recorded_by_the_platform(xen_efi_launch: Boot):
    assert_launched(xen_efi_launch)


def test_efi_launch_is_seen_by_xen(xen_efi_launch: Boot):
    assert "SLAUNCH" in xen_efi_launch.xen_log, xen_efi_launch.xen_log


def test_efi_normal_boot_launches_nothing(xen_efi: Boot):
    assert_not_launched(xen_efi)
    assert "SLAUNCH" not in xen_efi.xen_log, xen_efi.xen_log


def test_mb2_launch_is_recorded_by_the_platform(xen_mb2_launch: Boot):
    assert_launched(xen_mb2_launch)


def test_mb2_launch_is_seen_by_xen(xen_mb2_launch: Boot):
    assert "SLAUNCH" in xen_mb2_launch.xen_log, xen_mb2_launch.xen_log
