# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The TCG2 event log parser and its replay, against logs two v0.5.3-rc1
launches left: the SKL's events under Xen, and under Linux the same plus
the kernel's own, bracketed by its EV_NO_ACTION tags. The PCR values are
what `tpm2_pcrread` returned in those boots."""

from pathlib import Path

import pytest

from drtmtest.eventlog import EV_NO_ACTION, EV_SLAUNCH, parse, replay

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> bytes:
    text = (FIXTURES / f"eventlog-{name}-v0.5.3-rc1.hex").read_text()
    return bytes.fromhex("".join(text.split()))


XEN_PCRS = {
    "sha256": {
        17: "e17d42476df9d13cd73119cbd30d14795bdf8304c6a1f85e7c1eca554e07c055",
        18: "3e282d7905a8caff55b6537b255e16dc3b3cede1048481ea67d267bea7b3608e",
    },
    "sha1": {
        17: "0318a2c7cc558c5d9dd6f4d5acf751c2a2dcec01",
        18: "1d770ad1285cb8f85dcb4dd03e4cdfb4c301a30e",
    },
}
LINUX_PCRS = {
    "sha256": {
        17: "67be67686d82da37b760991194fff2cca163a4bad507b37927ae1742545aafe1",
        18: "8790e9bccaebfe038e13173cfb2d3b8f41434643669055978ec2e210da724a38",
    },
    "sha1": {
        17: "a8c09473c7a5f90a84098e779f276333cdbf661a",
        18: "153de987125e37f9cd9e7a61791222f65ee7036b",
    },
}


def test_the_xen_log_is_the_skls_events_then_xens():
    events = parse(fixture("xen"))
    assert [(e.pcr, e.data) for e in events] == [
        (17, b"SKINIT"),
        (17, b"DLME entry offset"),
        (17, b"DLME"),
        (18, b""),
        (18, b"Xen's command line"),
        (18, b"MB module string"),
        (17, b"MB module"),
    ]
    assert all(e.type == EV_SLAUNCH for e in events)
    assert set(events[0].digests) == {"sha1", "sha256"}


@pytest.mark.parametrize("alg", ["sha256", "sha1"])
@pytest.mark.parametrize("pcr", [17, 18])
def test_the_xen_log_replays_to_the_pcrs(alg: str, pcr: int):
    assert replay(parse(fixture("xen")), pcr, alg) == XEN_PCRS[alg][pcr]


def test_the_linux_log_has_the_kernels_tags():
    events = parse(fixture("linux"))
    tags = [e for e in events if e.type == EV_NO_ACTION]
    assert len(events) == 8
    assert [(e.pcr, e.data) for e in tags] == [(17, b""), (17, b"")]
    assert events[0].data == b"SKINIT"


@pytest.mark.parametrize("alg", ["sha256", "sha1"])
@pytest.mark.parametrize("pcr", [17, 18])
def test_the_linux_log_replays_to_the_pcrs_with_the_tags_skipped(
    alg: str, pcr: int
):
    assert replay(parse(fixture("linux")), pcr, alg) == LINUX_PCRS[alg][pcr]


def test_the_zero_tail_of_the_log_region_is_not_an_event():
    raw = fixture("linux")
    assert parse(raw + bytes(4096)) == parse(raw)


def test_an_empty_or_foreign_buffer_is_refused():
    with pytest.raises(ValueError):
        parse(b"")
    with pytest.raises(ValueError):
        parse(bytes(64))
