# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The Xen entries: a launch through SKINIT on the EFI path under Dasharo,
its control boot without one, and the MB2 launch under SeaBIOS."""

import re

from conftest import (
    PCR_CAPPED,
    PCR_ONES,
    PCR_ZERO,
    PSP,
    Boot,
    expects_boot,
)

from drtmtest.eventlog import EV_SLAUNCH, replay

# What Xen prints while taking over from the loader, on hardware and here.
XEN_RESERVES_EVENT_LOG = "SLAUNCH: reserving event log"
XEN_RESERVES_SLB = "SLAUNCH: reserving SLB"

# What Xen's PSP driver prints: the launch it found the service made, and
# the TMR it releases once its IOMMU is programmed.
XEN_PSP_LAUNCH = "SLAUNCH: PSP-assisted launch"
XEN_RELEASES_TMR = "SLAUNCH: released TMR 0"

# The service's DRTM_CMD_TMR_RELEASE, the last command a boot through the
# service issues before the shell.
PSP_CMD_TMR_RELEASE = 3


def assert_launched(boot: Boot) -> None:
    """What every launch leaves: the platform's record of it, PCRs 17 and
    18 reset and extended, PCR 18 not the cap a failed PSP launch leaves,
    and PCR 19 to 22 reset by the same locality 4 start but extended by
    nothing on this path. Under the service, its own record too: kicked,
    the launch passed with the SKL's signature checked, and the TMR
    released as the last command."""
    assert boot.record["launched"] is True
    assert boot.record["hash"] == "ok"
    assert boot.record["slb-length"] > 0
    assert boot.record["sl-dev"] is False, "SKL should have released SL_DEV"
    assert boot.record["dma-blocks"] == []
    assert boot.pcrs[17] not in (PCR_ZERO, PCR_ONES), boot.pcrs
    assert boot.pcrs[18] not in (PCR_ZERO, PCR_ONES, PCR_CAPPED), boot.pcrs
    for index in range(19, 23):
        assert boot.pcrs[index] == PCR_ZERO, boot.pcrs
    if PSP is None:
        assert "psp" not in boot.record, boot.record
        return
    psp = boot.record["psp"]
    assert psp["kicked"] is True, psp
    assert psp["launch"] == "ok", psp
    # A QEMU built without gcrypt cannot check the signature and says so.
    assert psp["signature"] in ("verified", "unsupported"), psp
    assert psp["command"] == PSP_CMD_TMR_RELEASE, psp
    assert psp["status"] == 0, psp


def assert_seen_by_xen(boot: Boot) -> None:
    """Xen's own view of the launch, and of the service when it is there:
    the PSP driver reports the launch and releases the TMR."""
    assert XEN_RESERVES_EVENT_LOG in boot.xen_lines, boot.xen_lines
    assert XEN_RESERVES_SLB in boot.xen_lines, boot.xen_lines
    if PSP is None:
        assert XEN_PSP_LAUNCH not in boot.xen_lines, boot.xen_lines
        return
    assert XEN_PSP_LAUNCH in boot.xen_lines, boot.xen_lines
    assert XEN_RELEASES_TMR in boot.xen_lines, boot.xen_lines


def assert_log_replays(boot: Boot) -> None:
    """The event log the SKL left accounts for the DRTM PCRs: it opens
    with SKINIT's measurement of the SLB, which is the digest of the SKL
    the image ships over the length its header gives, and replaying its
    extends reaches what the TPM reads for PCR 17 and 18."""
    events = boot.events
    assert events, "no event log was dumped"
    first = events[0]
    assert (first.pcr, first.type, first.data) == (17, EV_SLAUNCH, b"SKINIT"), first
    assert first.digests["sha256"] == boot.slb_sha256, (first, boot.slb_sha256)
    assert boot.record["slb-length"] == boot.slb_length, boot.record
    for pcr in (17, 18):
        assert replay(events, pcr) == boot.pcrs[pcr], (pcr, events)


def assert_iommu_up(boot: Boot) -> None:
    """The launched OS brought the IOMMU up: Xen reports direct I/O among
    its capabilities, Linux has the AMD IOMMU registered and devices in
    its groups."""
    if boot.entry.os == "xen":
        assert "hvm_directio" in boot.iommu, boot.iommu
    else:
        assert "ivhd0" in boot.iommu, boot.iommu
        assert re.search(r"iommu_groups:\n\s*\d", boot.iommu), boot.iommu


def assert_not_launched(boot: Boot) -> None:
    """Without a launch the DRTM PCRs stay as the TPM started them."""
    assert boot.record["launched"] is False
    for index in range(17, 23):
        assert boot.pcrs[index] == PCR_ONES, boot.pcrs


@expects_boot("xen_efi_launch")
def test_efi_launch_is_recorded_by_the_platform(xen_efi_launch: Boot):
    assert_launched(xen_efi_launch)


@expects_boot("xen_efi_launch")
def test_efi_launch_is_seen_by_xen(xen_efi_launch: Boot):
    assert_seen_by_xen(xen_efi_launch)


@expects_boot("xen_efi_launch")
def test_efi_launch_brings_the_iommu_up(xen_efi_launch: Boot):
    assert_iommu_up(xen_efi_launch)


@expects_boot("xen_efi_launch")
def test_efi_launch_log_replays_to_the_pcrs(xen_efi_launch: Boot):
    assert_log_replays(xen_efi_launch)


def test_efi_normal_boot_launches_nothing(xen_efi: Boot):
    assert_not_launched(xen_efi)
    assert "SLAUNCH" not in xen_efi.xen_lines, xen_efi.xen_lines


@expects_boot("xen_mb2_launch")
def test_mb2_launch_is_recorded_by_the_platform(xen_mb2_launch: Boot):
    assert_launched(xen_mb2_launch)


@expects_boot("xen_mb2_launch")
def test_mb2_launch_is_seen_by_xen(xen_mb2_launch: Boot):
    assert_seen_by_xen(xen_mb2_launch)


@expects_boot("xen_mb2_launch")
def test_mb2_launch_brings_the_iommu_up(xen_mb2_launch: Boot):
    assert_iommu_up(xen_mb2_launch)


@expects_boot("xen_mb2_launch")
def test_mb2_launch_log_replays_to_the_pcrs(xen_mb2_launch: Boot):
    assert_log_replays(xen_mb2_launch)
