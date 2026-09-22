# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""A boot's settings come from the environment once, where the caller reads
them, never on the boot's own thread: a session's boots overlap with unit
tests that patch the environment, and a boot that read it at that moment
took the test's values."""

from pathlib import Path

import pytest

from drtmtest import machine
from drtmtest.qemu_vm import QemuVm, Settings, allocate_pcr_banks


def test_settings_hold_what_the_environment_said_when_read(monkeypatch):
    monkeypatch.setenv("DRTM_QEMU_BINARY", "/opt/one/qemu")
    monkeypatch.setenv("DRTM_QEMU_ACCEL", "tcg")
    monkeypatch.setenv("DRTM_PCR_BANKS", "sha256")
    monkeypatch.setenv("DRTM_SWTPM_LOG_LEVEL", "20")
    settings = Settings.from_environment()
    monkeypatch.setenv("DRTM_QEMU_BINARY", "/opt/two/qemu")
    monkeypatch.setenv("DRTM_PCR_BANKS", "sha1,sha256,sha384")
    monkeypatch.delenv("DRTM_SWTPM_LOG_LEVEL")
    assert settings.binary == "/opt/one/qemu"
    assert settings.kvm is False
    assert settings.banks == ("sha256",)
    assert settings.swtpm_log_level == "20"


def test_settings_name_the_swtpm_programs_by_path(tmp_path: Path, monkeypatch):
    """The stand-in `swtpm_setup` a unit test puts on PATH must not be what
    a boot starting at that moment runs."""
    binaries = tmp_path / "bin"
    binaries.mkdir()
    for name in ("swtpm_setup", "swtpm"):
        (binaries / name).write_text("#!/bin/sh\n")
        (binaries / name).chmod(0o755)
    monkeypatch.setenv("PATH", str(binaries))
    settings = Settings.from_environment()
    monkeypatch.setenv("PATH", str(tmp_path / "elsewhere"))
    assert settings.swtpm_setup == str(binaries / "swtpm_setup")
    assert settings.swtpm == str(binaries / "swtpm")


def test_settings_keep_a_missing_program_by_name(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))
    settings = Settings.from_environment()
    assert settings.swtpm_setup == "swtpm_setup"
    assert settings.swtpm == "swtpm"


def test_a_vm_keeps_the_settings_it_was_made_with(tmp_path: Path, monkeypatch):
    given = Settings("/opt/qemu", False, ("sha1",), None, "swtpm_setup", "swtpm")
    assert QemuVm(tmp_path, [], settings=given).settings is given
    monkeypatch.setenv("DRTM_PCR_BANKS", "sha256")
    vm = QemuVm(tmp_path, [])
    monkeypatch.setenv("DRTM_PCR_BANKS", "sha384")
    assert vm.settings.banks == ("sha256",)


@pytest.mark.parametrize(
    ("extra", "expected"),
    [(["-m", "6G"], ["-m", "6G"]), ([], []), (None, ["-machine", "pit=off"])],
)
def test_options_end_with_the_extra_arguments_given(monkeypatch, extra, expected):
    monkeypatch.setenv("DRTM_QEMU_ARGS", "-machine pit=off")
    args = machine.options(Path("/tmp/disk.wic"), extra=extra)
    assert args[len(args) - len(expected) :] == expected
    assert "-d" in args


def test_the_state_is_written_by_the_program_given(tmp_path: Path, monkeypatch):
    """A stand-in `swtpm_setup` by path, so the test never touches PATH:
    the session's boots run on their own threads while this one does."""
    script = tmp_path / "swtpm_setup"
    script.write_text(
        "#!/bin/sh\n"
        'while [ "$1" != --tpmstate ]; do shift; done\n'
        'echo "$@" > "$2/tpm2-00.permall"\n'
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path / "elsewhere"))
    with open(tmp_path / "swtpm.log", "wb") as log:
        allocate_pcr_banks(tmp_path / "state", ["sha256"], log, program=str(script))
    assert "--pcr-banks sha256" in (tmp_path / "state" / "tpm2-00.permall").read_text()
