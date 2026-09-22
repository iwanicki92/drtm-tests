# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The results of a matrix run as one Markdown page and one badge per
release: `python -m drtmtest.report <dir>` reads every `results.json`
under `<dir>`, one per cell of the matrix, and writes `README.md` and
`badges/<release>.json` into `--out`. The page has one section per
configuration with a table of the GRUB entries against the releases,
and the full per-test table folded under it.
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from drtmtest import matrix, trenchboot

PASS = "✅"
FAIL = "❌"
NONE = "-"

# Outcomes by what the boot did, whatever the suite expected of it.
_DID_FAIL = {"failed", "xfailed"}
_DID_PASS = {"passed", "xpassed"}


@dataclass
class Cell:
    """The tests of one entry, or one test id, under one configuration
    and release."""

    tests: list[dict] = field(default_factory=list)

    @property
    def mark(self) -> str:
        outcomes = {test["outcome"] for test in self.tests}
        if outcomes & _DID_FAIL:
            return FAIL
        if outcomes & _DID_PASS:
            return PASS
        return NONE


def load(results_dir: Path) -> list[dict]:
    """Every `results.json` under the directory, in path order."""
    results = [
        json.loads(path.read_text())
        for path in sorted(results_dir.rglob("results.json"))
    ]
    if not results:
        raise SystemExit(f"no results.json under {results_dir}")
    return results


def _ordered(found: list[str], known: list[str]) -> list[str]:
    """`found` in the order of `known`, what `known` lacks after it."""
    return [name for name in known if name in found] + [
        name for name in found if name not in known
    ]


def _release(result: dict) -> str:
    return result["details"].get("release") or result["details"].get("image", "?")


def _configuration(result: dict) -> str:
    return result["details"].get("configuration") or "custom"


def _configuration_title(name: str, results: list[dict]) -> str:
    if name in matrix.CONFIGURATIONS:
        return matrix.CONFIGURATIONS[name].title
    details = results[0]["details"]
    return (
        f"psp={details.get('psp') or 'off'}, banks={','.join(details.get('banks', []))}"
    )


def _code(text: str) -> str:
    return f"`{text}`"


def _table(header: list[str], rows: list[list[str]]) -> list[str]:
    widths = [
        max(len(cell) for cell in column) for column in zip(header, *rows, strict=True)
    ]
    line = lambda cells: (
        "| "
        + " | ".join(
            cell.ljust(width) for cell, width in zip(cells, widths, strict=True)
        )
        + " |"
    )
    rule = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
    return [line(header), rule, *(line(row) for row in rows)]


def _section(name: str, cells: dict[str, dict], releases: list[str]) -> list[str]:
    """One configuration: the compact table, its notes and the full
    table. `cells` maps a release to its `results.json`."""
    results = [cells[release] for release in releases if release in cells]
    lines = [f"## {_configuration_title(name, results)}", ""]
    entries: dict[str, dict[str, Cell]] = defaultdict(lambda: defaultdict(Cell))
    tests: dict[str, dict[str, Cell]] = defaultdict(lambda: defaultdict(Cell))
    entry_order: list[str] = []
    for result in results:
        for entry in result["details"].get("entries", {}):
            if entry not in entry_order:
                entry_order.append(entry)
    for release in releases:
        if release not in cells:
            continue
        for test in cells[release]["tests"]:
            tests[test["id"]][release].tests.append(test)
            for entry in test["entries"]:
                entries[entry][release].tests.append(test)
    rows = [
        [_code(entry), *(entries[entry][release].mark for release in releases)]
        for entry in _ordered(list(entries), entry_order)
    ]
    lines += _table(["Entry", *releases], rows) + [""]
    lines += _notes(entries, cells, releases)
    lines += ["<details>", "<summary>Every test</summary>", ""]
    rows = [
        [_code(test), *(_outcome(tests[test][release]) for release in releases)]
        for test in tests
    ]
    lines += _table(["Test", *releases], rows) + ["", "</details>", ""]
    return lines


def _outcome(cell: Cell) -> str:
    outcomes = {test["outcome"] for test in cell.tests}
    return ", ".join(sorted(outcomes)) if outcomes else NONE


def _notes(
    entries: dict[str, dict[str, Cell]], cells: dict[str, dict], releases: list[str]
) -> list[str]:
    """What the suite expected of the marks: which failures were expected
    and why, which were not, and which cells have no results at all."""
    notes: list[str] = []
    for release in releases:
        if release not in cells:
            notes.append(f"- No results for {_code(release)}.")
            continue
        summary = _summary(cells[release]["tests"])
        notes.append(f"- {_code(release)}: {summary}.")
        for entry, by_release in entries.items():
            seen: set[str] = set()
            for test in by_release[release].tests:
                if test["outcome"] == "xfailed" and test["reason"] not in seen:
                    seen.add(test["reason"])
                    notes.append(f"    - {_code(entry)} expected: {test['reason']}")
            failed = [t for t in by_release[release].tests if t["outcome"] == "failed"]
            if failed:
                notes.append(f"    - {_code(entry)}: {len(failed)} failed unexpectedly")
            for test in by_release[release].tests:
                if test["outcome"] == "xpassed":
                    notes.append(
                        f"    - {_code(entry)} passed against the expectation: "
                        f"{test['reason']}"
                    )
    return notes + [""]


def _summary(tests: list[dict]) -> str:
    counts: dict[str, int] = defaultdict(int)
    for test in tests:
        counts[test["outcome"]] += 1
    return ", ".join(f"{count} {outcome}" for outcome, count in sorted(counts.items()))


def _version(line: str | None, prefix: str) -> str:
    """The version out of a `--version` line, `11.1.1 (...)` out of QEMU's
    and `0.7.3` out of swtpm's."""
    if not line:
        return "?"
    return line.removeprefix(prefix).split(",")[0].strip()


def _header(results: list[dict], run: str | None, run_url: str | None) -> list[str]:
    commits = sorted({r["details"].get("commit") or "?" for r in results})
    finished = max(r["finished"] for r in results)
    bundles = sorted({r["details"].get("qemu_bundle") or "" for r in results} - {""})
    qemus = sorted(
        {_version(r["details"].get("qemu"), "QEMU emulator version ") for r in results}
    )
    swtpms = sorted(
        {_version(r["details"].get("swtpm"), "TPM emulator version ") for r in results}
    )
    parts = [f"Commit {', '.join(_code(c[:12]) for c in commits)}"]
    if run and run_url:
        parts.append(f"run [{run}]({run_url})")
    elif run:
        parts.append(f"run {run}")
    parts.append(f"finished {finished[:19].replace('T', ' ')}")
    qemu = ", ".join(qemus)
    if bundles:
        qemu = f"bundle {', '.join(_code(b) for b in bundles)} ({qemu})"
    return [
        "# Boot matrix results",
        "",
        f"{', '.join(parts)}.",
        f"QEMU {qemu}, swtpm {', '.join(swtpms)}.",
        "",
        "Rows are the GRUB entries the suite boots, named as their fixtures",
        f"in `tests/conftest.py`, columns the releases. {PASS} every test of the",
        f"entry passed, {FAIL} one failed, {NONE} nothing ran. A mark says what the",
        "boot did, and the notes under the table what the suite expected of it.",
        "",
    ]


def render(
    results: list[dict], run: str | None = None, run_url: str | None = None
) -> tuple[str, dict[str, dict]]:
    """The page and the badges, the latter by release in the shields
    endpoint schema."""
    by_configuration: dict[str, dict[str, dict]] = defaultdict(dict)
    for result in results:
        by_configuration[_configuration(result)][_release(result)] = result
    configurations = _ordered(list(by_configuration), list(matrix.CONFIGURATIONS))
    releases = _ordered(
        sorted({_release(r) for r in results}), list(trenchboot.RELEASES)
    )
    lines = _header(results, run, run_url)
    for name in configurations:
        lines += _section(name, by_configuration[name], releases)
    badges = {
        release: _badge(release, by_configuration, configurations)
        for release in releases
    }
    return "\n".join(lines).rstrip("\n") + "\n", badges


def _badge(release: str, by_configuration: dict, configurations: list[str]) -> dict:
    """Green with the passes counted when every configuration's tests
    were what the suite expected, red otherwise."""
    passed = failed = 0
    missing = [name for name in configurations if release not in by_configuration[name]]
    for name in configurations:
        for test in by_configuration[name].get(release, {"tests": []})["tests"]:
            if test["ok"]:
                passed += 1
            else:
                failed += 1
    if failed:
        message, color = f"{failed} failed", "red"
    elif missing:
        message, color = f"{len(missing)} missing", "red"
    else:
        message, color = f"{passed} passed", "brightgreen"
    return {"schemaVersion": 1, "label": release, "message": message, "color": color}


def write(out_dir: Path, page: str, badges: dict[str, dict]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "README.md").write_text(page)
    (out_dir / "badges").mkdir(exist_ok=True)
    for release, badge in badges.items():
        (out_dir / "badges" / f"{release}.json").write_text(
            json.dumps(badge, indent=2) + "\n"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m drtmtest.report", description=__doc__
    )
    parser.add_argument("results", type=Path, help="a directory of results.json files")
    parser.add_argument("--out", type=Path, default=Path("report"))
    parser.add_argument("--run", help="the run's number, for the header")
    parser.add_argument("--run-url", help="where the run's logs are")
    args = parser.parse_args(argv)
    page, badges = render(load(args.results), args.run, args.run_url)
    write(args.out, page, badges)
    print(args.out / "README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
