# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Rendering matrix results into the page and the badges, on results
shaped like the session writes them."""

import json
from pathlib import Path

import pytest

from drtmtest.report import FAIL, NONE, PASS, load, main, render

XEN = "tests/test_xen.py::test_efi_launch_is_recorded"
XEN_REPLAY = "tests/test_xen.py::test_efi_launch_log_replays"
LINUX = "tests/test_linux.py::test_launch_is_seen_by_linux"
PARSER = "tests/test_eventlog.py::test_the_header_declares_the_banks"


def _test(
    id: str,
    entries: list[str],
    outcome: str = "passed",
    reason: str | None = None,
) -> dict:
    return {
        "id": id,
        "file": id.split("::")[0],
        "entries": entries,
        "outcome": outcome,
        "ok": outcome in ("passed", "skipped", "xfailed"),
        "reason": reason,
        "duration": 1.0,
    }


def _result(release: str, configuration: str | None, tests: list[dict]) -> dict:
    return {
        "finished": "2026-09-22T19:40:10+02:00",
        "exit_status": 0 if all(t["ok"] for t in tests) else 1,
        "duration": 60.0,
        "details": {
            "release": release,
            "image": release,
            "configuration": configuration,
            "psp": "on" if configuration and "psp" in configuration else None,
            "banks": ["sha1", "sha256"],
            "qemu": "QEMU emulator version 11.1.1 (v11.1.1-43-gabcdef)",
            "qemu_bundle": "drtm-11.1.1-1",
            "swtpm": "TPM emulator version 0.7.3, Copyright (c) 2014-2021 IBM Corp.",
            "commit": "0123456789abcdef0123456789abcdef01234567",
            "entries": {
                "xen_efi_launch": {"title": "Boot Xen (EFI)", "firmware": "dasharo"},
                "linux_launch": {"title": "Boot Linux", "firmware": "dasharo"},
            },
        },
        "tests": tests,
    }


ALL_GOOD = [
    _test(XEN, ["xen_efi_launch"]),
    _test(XEN_REPLAY, ["xen_efi_launch"]),
    _test(LINUX, ["linux_launch"]),
    _test(PARSER, []),
]

# v0.5.2: the Linux launch expected broken, and one Xen test failing.
UPSTREAM = [
    _test(XEN, ["xen_efi_launch"]),
    _test(XEN_REPLAY, ["xen_efi_launch"], "failed"),
    _test(LINUX, ["linux_launch"], "xfailed", "panics in check_timer"),
    _test(PARSER, []),
]

# The rc: the Linux launch passed against its expectation, nothing on Xen.
RC = [
    _test(LINUX, ["linux_launch"], "xpassed", "panics in check_timer"),
    _test(PARSER, []),
]


def _row(page: str, section: str, label: str) -> list[str]:
    body = page.split(f"## {section}")[1].split("## ", 1)[0]
    for line in body.splitlines():
        if line.startswith(f"| `{label}`"):
            return [cell.strip() for cell in line.strip("|").split("|")][1:]
    raise LookupError(label)


@pytest.fixture
def results() -> list[dict]:
    return [
        _result("amd-drtm-test-image", "classic", ALL_GOOD),
        _result("v0.5.2", "classic", UPSTREAM),
        _result("v0.5.3-rc1", "classic", RC),
        _result("amd-drtm-test-image", "psp", ALL_GOOD),
    ]


def test_a_cell_says_what_the_boot_did(results: list[dict]):
    page, _ = render(results)
    title = "Classic launch, TPM with SHA-1 and SHA-256"
    assert _row(page, title, "xen_efi_launch") == [PASS, FAIL, NONE]
    assert _row(page, title, "linux_launch") == [PASS, FAIL, PASS]


def test_the_notes_say_what_was_expected(results: list[dict]):
    page, _ = render(results)
    assert "- `linux_launch` expected: panics in check_timer" in page
    assert "- `xen_efi_launch`: 1 failed unexpectedly" in page
    assert "- `linux_launch` passed against the expectation: panics" in page
    assert "- `v0.5.2`: 1 failed, 2 passed, 1 xfailed." in page


def test_a_release_without_results_is_a_missing_column(results: list[dict]):
    page, _ = render(results)
    psp = page.split("## PSP DRTM service on")[1]
    header = psp.strip().splitlines()[0]
    assert [c.strip() for c in header.strip("|").split("|")] == [
        "Entry",
        "amd-drtm-test-image",
        "v0.5.2",
        "v0.5.3-rc1",
    ]
    assert _row(page, "PSP DRTM service on", "xen_efi_launch") == [PASS, NONE, NONE]
    assert "- No results for `v0.5.2`." in psp
    assert "- No results for `v0.5.3-rc1`." in psp


def test_the_full_table_has_every_test_and_the_parser_ones_only_there(
    results: list[dict],
):
    page, _ = render(results)
    title = "Classic launch, TPM with SHA-1 and SHA-256"
    assert _row(page, title, XEN_REPLAY) == ["passed", "failed", NONE]
    assert _row(page, title, LINUX) == ["passed", "xfailed", "xpassed"]
    assert _row(page, title, PARSER) == ["passed", "passed", "passed"]
    with pytest.raises(LookupError):
        _row(page, title, "test_eventlog.py")


def test_the_sections_and_columns_follow_the_matrix_order(results: list[dict]):
    page, badges = render(list(reversed(results)))
    assert page.index("## Classic launch") < page.index("## PSP DRTM service on")
    assert list(badges) == ["amd-drtm-test-image", "v0.5.2", "v0.5.3-rc1"]


def test_the_header_names_the_commit_the_run_and_the_tools(results: list[dict]):
    page, _ = render(results, run="12", run_url="https://example.invalid/12")
    assert "Commit `0123456789ab`, run [12](https://example.invalid/12)," in page
    assert (
        "QEMU bundle `drtm-11.1.1-1` (11.1.1 (v11.1.1-43-gabcdef)), swtpm 0.7.3."
        in page
    )


def test_a_badge_is_green_only_when_every_configuration_passed(results: list[dict]):
    _, badges = render(results)
    assert badges["amd-drtm-test-image"] == {
        "schemaVersion": 1,
        "label": "amd-drtm-test-image",
        "message": "8 passed",
        "color": "brightgreen",
    }
    assert badges["v0.5.2"]["message"] == "1 failed"
    assert badges["v0.5.2"]["color"] == "red"
    # The rc's one strict expected failure passed, which pytest counts a
    # failure, and it has no PSP results at all.
    assert badges["v0.5.3-rc1"]["message"] == "1 failed"


def test_a_missing_configuration_alone_is_red_too():
    _, badges = render([_result("v0.5.2", "classic", ALL_GOOD)])
    assert badges["v0.5.2"] == {
        "schemaVersion": 1,
        "label": "v0.5.2",
        "message": "4 passed",
        "color": "brightgreen",
    }
    _, badges = render(
        [
            _result("v0.5.2", "classic", ALL_GOOD),
            _result("amd-drtm-test-image", "psp", ALL_GOOD),
        ]
    )
    assert badges["v0.5.2"] == {
        "schemaVersion": 1,
        "label": "v0.5.2",
        "message": "1 missing",
        "color": "red",
    }


def test_a_hand_made_session_gets_a_section_of_its_own():
    result = _result("v0.5.2", None, ALL_GOOD)
    result["details"]["banks"] = ["sha256", "sha384"]
    page, _ = render([result])
    assert "## psp=off, banks=sha256,sha384" in page


def test_main_reads_a_tree_of_results_and_writes_the_page_and_badges(
    tmp_path: Path, results: list[dict]
):
    for index, result in enumerate(results):
        path = tmp_path / "logs" / f"job-{index}" / "0001-2026-09-22" / "results.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(result))
    assert len(load(tmp_path / "logs")) == 4
    out = tmp_path / "report"
    assert main([str(tmp_path / "logs"), "--out", str(out)]) == 0
    assert (out / "README.md").read_text().startswith("# Boot matrix results\n")
    badge = json.loads((out / "badges" / "v0.5.2.json").read_text())
    assert badge["label"] == "v0.5.2"
    with pytest.raises(SystemExit):
        load(tmp_path / "empty")
