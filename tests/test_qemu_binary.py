# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Exercises the check that a suite runs against our QEMU build.

Stand-in binaries play upstream's two ways of turning our options down, so
none of these boot anything.
"""

from pathlib import Path

import pytest

from drtmtest import machine
from drtmtest.qemu_vm import unsupported_binary


def _fake_qemu(tmp_path: Path, stderr: str, status: int) -> str:
    (tmp_path / "stderr").write_text(stderr + "\n")
    script = tmp_path / "qemu-system-x86_64"
    script.write_text(
        f"#!/bin/sh\ncat >/dev/null\ncat '{tmp_path}/stderr' >&2\nexit {status}\n"
    )
    script.chmod(0o755)
    return str(script)


def test_the_configured_binary_is_ours():
    assert machine.unsupported_binary() is None


def test_a_refused_option_is_reported(tmp_path, monkeypatch: pytest.MonkeyPatch):
    error = "qemu-system-x86_64: Property 'pc-q35-10.2-machine.amd-drtm' not found"
    monkeypatch.setenv("DRTM_QEMU_BINARY", _fake_qemu(tmp_path, error, 1))
    assert unsupported_binary(machine.PROBE_OPTIONS) == error


def test_a_warning_named_in_rejects_is_reported(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    warning = "warning: TCG doesn't support requested feature: ECX.skinit [bit 12]"
    monkeypatch.setenv("DRTM_QEMU_BINARY", _fake_qemu(tmp_path, warning, 0))
    rejects = {"skinit": "it does not report the skinit CPUID bit"}
    assert unsupported_binary(["-cpu", "EPYC,+skinit"], rejects) == rejects["skinit"]
    assert unsupported_binary(["-cpu", "EPYC,+skinit"]) is None


def test_a_missing_binary_is_reported(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DRTM_QEMU_BINARY", str(tmp_path / "absent"))
    reason = unsupported_binary(machine.PROBE_OPTIONS)
    assert reason is not None and "not found" in reason
