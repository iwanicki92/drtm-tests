# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The Linux launch, which panics on the releases under UEFI and boots
through SeaBIOS, and the normal Linux boot: the kernel booted directly is
the one that found no disk when the launch machine's IOMMU passed DMA
through, so it stays under test."""

from conftest import Boot, expects_boot, expects_skls_banks
from test_xen import (
    assert_iommu_up,
    assert_launched,
    assert_log_declares_the_tpms_banks,
    assert_log_replays,
    assert_not_launched,
)

# What the kernel prints on a launch it recognises, as seen on hardware:
# the early setup in the decompressor's slaunch code, then the module.
LINUX_SETUP_DONE = "slaunch: AMD SKINIT setup complete"
LINUX_MODULE_UP = "slmodule: SKINIT Secure Launch module setup"


def assert_seen_by_linux(boot: Boot) -> None:
    """The kernel's own view of the launch: the early setup done, the
    module up and its securityfs entry there."""
    assert LINUX_SETUP_DONE in boot.dmesg, boot.dmesg
    assert LINUX_MODULE_UP in boot.dmesg, boot.dmesg
    assert "No such file" not in boot.securityfs, boot.securityfs


@expects_boot("linux_launch")
def test_launch_is_recorded_by_the_platform(linux_launch: Boot):
    assert_launched(linux_launch)


@expects_boot("linux_launch")
def test_launch_is_seen_by_linux(linux_launch: Boot):
    assert_seen_by_linux(linux_launch)


@expects_boot("linux_launch")
def test_launch_brings_the_iommu_up(linux_launch: Boot):
    assert_iommu_up(linux_launch)


@expects_boot("linux_launch")
def test_launch_log_replays_to_the_pcrs(linux_launch: Boot):
    assert_log_replays(linux_launch)


@expects_boot("linux_launch")
@expects_skls_banks()
def test_launch_log_declares_the_tpms_banks(linux_launch: Boot):
    assert_log_declares_the_tpms_banks(linux_launch)


@expects_boot("linux_legacy_launch")
def test_legacy_launch_is_recorded_by_the_platform(linux_legacy_launch: Boot):
    assert_launched(linux_legacy_launch)


@expects_boot("linux_legacy_launch")
def test_legacy_launch_is_seen_by_linux(linux_legacy_launch: Boot):
    assert_seen_by_linux(linux_legacy_launch)


@expects_boot("linux_legacy_launch")
def test_legacy_launch_brings_the_iommu_up(linux_legacy_launch: Boot):
    assert_iommu_up(linux_legacy_launch)


@expects_boot("linux_legacy_launch")
def test_legacy_launch_log_replays_to_the_pcrs(linux_legacy_launch: Boot):
    assert_log_replays(linux_legacy_launch)


@expects_boot("linux_legacy_launch")
@expects_skls_banks()
def test_legacy_launch_log_declares_the_tpms_banks(linux_legacy_launch: Boot):
    assert_log_declares_the_tpms_banks(linux_legacy_launch)


@expects_boot("linux_alt_launch")
def test_alt_launch_is_recorded_by_the_platform(linux_alt_launch: Boot):
    assert_launched(linux_alt_launch)


@expects_boot("linux_alt_launch")
def test_alt_launch_is_seen_by_linux(linux_alt_launch: Boot):
    assert_seen_by_linux(linux_alt_launch)
    assert "drtmtest=alt" in linux_alt_launch.cmdline, linux_alt_launch.cmdline


@expects_boot("linux_alt_launch")
def test_alt_launch_log_replays_to_the_pcrs(linux_alt_launch: Boot):
    assert_log_replays(linux_alt_launch)


@expects_boot("linux_alt_launch")
@expects_skls_banks()
def test_alt_launch_log_declares_the_tpms_banks(linux_alt_launch: Boot):
    assert_log_declares_the_tpms_banks(linux_alt_launch)


@expects_boot("linux_alt_launch")
@expects_boot("linux_legacy_launch")
def test_the_command_line_is_measured_into_pcr_18_alone(
    linux_legacy_launch: Boot, linux_alt_launch: Boot
):
    """The two launches share the SKL and the kernel and differ in the
    command line, so PCR 17 and 18 have to tell only that apart, and the
    log's command line event is where."""
    plain, alt = linux_legacy_launch, linux_alt_launch
    assert "drtmtest=alt" not in plain.cmdline, plain.cmdline
    assert plain.pcrs[17] == alt.pcrs[17], (plain.pcrs, alt.pcrs)
    assert plain.pcrs[18] != alt.pcrs[18], (plain.pcrs, alt.pcrs)
    plain_events = {e.data: e for e in plain.events if e.pcr == 18}
    alt_events = {e.data: e for e in alt.events if e.pcr == 18}
    assert set(plain_events) == set(alt_events), (plain_events, alt_events)
    differing = [
        data for data in plain_events if plain_events[data] != alt_events[data]
    ]
    assert differing == [b"Measured Kernel command line"], differing


def test_normal_boot_launches_nothing(linux: Boot):
    assert_not_launched(linux)
    assert "slaunch" not in linux.dmesg.lower(), linux.dmesg
