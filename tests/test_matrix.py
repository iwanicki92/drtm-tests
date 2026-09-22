# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The matrix's configurations, which one an environment is, and what
the workflow and a cell of it get."""

import json

import pytest

from drtmtest import matrix, trenchboot


def test_the_workflow_gets_every_release_under_every_configuration(capsys):
    assert matrix.main([]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == {
        "release": list(trenchboot.RELEASES),
        "configuration": list(matrix.CONFIGURATIONS),
    }


def test_a_selection_of_releases_is_kept_in_the_order_given():
    assert matrix.releases("v0.5.2, amd-drtm-test-image") == [
        "v0.5.2",
        "amd-drtm-test-image",
    ]
    with pytest.raises(SystemExit, match="v0.5.9"):
        matrix.releases("v0.5.9")


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ({}, "classic"),
        ({"DRTM_PSP": "on"}, "psp"),
        ({"DRTM_PCR_BANKS": "sha256"}, "sha256"),
        ({"DRTM_PSP": "on", "DRTM_PCR_BANKS": "sha256"}, "psp-sha256"),
        ({"DRTM_PCR_BANKS": "sha1,sha256,sha384"}, "sha384"),
        ({"DRTM_PSP": "classic"}, "psp"),
        ({"DRTM_PCR_BANKS": "sha384"}, None),
    ],
)
def test_the_environment_names_its_configuration(monkeypatch, env, expected):
    monkeypatch.delenv("DRTM_PSP", raising=False)
    monkeypatch.delenv("DRTM_PCR_BANKS", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    assert matrix.current() == expected


def test_a_cell_replaces_the_configuration_variables_and_the_local_image(monkeypatch):
    monkeypatch.setenv("DRTM_PSP", "on")
    monkeypatch.setenv("DRTM_PCR_BANKS", "sha256")
    monkeypatch.setenv("DRTM_TB_IMAGE", "/tmp/local.wic")
    monkeypatch.setenv("DRTM_QEMU_BINARY", "/opt/qemu")
    env = matrix.environment("v0.5.2", "classic")
    assert env["DRTM_TB_RELEASE"] == "v0.5.2"
    assert env["DRTM_QEMU_BINARY"] == "/opt/qemu"
    assert "DRTM_PSP" not in env
    assert "DRTM_PCR_BANKS" not in env
    assert "DRTM_TB_IMAGE" not in env
    assert (
        matrix.environment("v0.5.2", "sha384")["DRTM_PCR_BANKS"] == "sha1,sha256,sha384"
    )
    # The service under an upstream release is the classic session: its SKL
    # never talks to the service, so the launches are expected to fail.
    assert matrix.environment("v0.5.2", "psp")["DRTM_PSP"] == "classic"
    assert matrix.environment("amd-drtm-test-image", "psp-sha256")["DRTM_PSP"] == "on"
    with pytest.raises(SystemExit, match="not pinned"):
        matrix.environment("v9", "classic")
    with pytest.raises(SystemExit, match="not in drtmtest.matrix"):
        matrix.environment("v0.5.2", "psp-sha1")
