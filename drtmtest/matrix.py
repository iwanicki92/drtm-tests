# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The boot matrix CI runs: every pinned release under every machine
configuration, a configuration being the environment a session boots
with. `python -m drtmtest.matrix` prints the matrix as the workflow's
JSON, `python -m drtmtest.matrix run <release> <configuration>` runs one
cell of it, on the host as in CI.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field

from drtmtest import machine, qemu_vm, trenchboot


@dataclass(frozen=True)
class Configuration:
    """One machine configuration: whether the boots get the Secure
    Processor's DRTM service, the TPM's banks (`None` for the default
    two), and the title the results tables give it."""

    title: str
    psp: bool = False
    banks: str | None = None

    def env(self, release: str) -> dict[str, str]:
        """What the configuration sets for a release. The service goes
        with `DRTM_PSP=on` for an image whose SKL uses it and `classic`
        for the upstream releases, whose SKL never talks to it and whose
        launches are then expected to fail at the TPM."""
        env = {}
        if self.psp:
            upstream = trenchboot.RELEASES[release].upstream
            env["DRTM_PSP"] = "classic" if upstream else "on"
        if self.banks is not None:
            env["DRTM_PCR_BANKS"] = self.banks
        return env


CONFIGURATIONS: dict[str, Configuration] = {
    "classic": Configuration("Classic launch, TPM with SHA-1 and SHA-256"),
    "psp": Configuration("PSP DRTM service on", psp=True),
    "sha256": Configuration("TPM with SHA-256 alone", banks="sha256"),
    "psp-sha256": Configuration(
        "PSP DRTM service on, SHA-256 alone", psp=True, banks="sha256"
    ),
    "sha384": Configuration("TPM with SHA-384 on top", banks="sha1,sha256,sha384"),
}

# What a configuration sets, cleared before its own environment goes in.
_VARIABLES = ("DRTM_PSP", "DRTM_PCR_BANKS")


def current() -> str | None:
    """Which configuration this session's environment is, by what
    `DRTM_PSP` and `DRTM_PCR_BANKS` say, or `None` when it is none of
    them, a hand-made session."""
    psp = machine.psp_mode() is not None
    banks = qemu_vm.pcr_banks()
    for name, configuration in CONFIGURATIONS.items():
        wanted = configuration.banks or ",".join(qemu_vm.PCR_BANKS)
        if psp == configuration.psp and banks == tuple(wanted.split(",")):
            return name
    return None


def releases(selection: str = "") -> list[str]:
    """The releases to run, every pinned one unless `selection` names a
    comma-separated subset of them."""
    wanted = [tag.strip() for tag in selection.split(",") if tag.strip()]
    if not wanted:
        return list(trenchboot.RELEASES)
    unknown = [tag for tag in wanted if tag not in trenchboot.RELEASES]
    if unknown:
        raise SystemExit(f"not pinned in drtmtest.trenchboot: {', '.join(unknown)}")
    return wanted


def workflow_matrix(selection: str = "") -> dict[str, list[str]]:
    """The matrix as the workflow's `strategy.matrix` takes it."""
    return {
        "release": releases(selection),
        "configuration": list(CONFIGURATIONS),
    }


def environment(release: str, configuration: str) -> dict[str, str]:
    """The environment one cell of the matrix boots with, on top of the
    caller's, the configuration's variables replaced rather than merged."""
    if release not in trenchboot.RELEASES:
        raise SystemExit(f"{release} is not pinned in drtmtest.trenchboot")
    if configuration not in CONFIGURATIONS:
        raise SystemExit(f"{configuration} is not in drtmtest.matrix")
    env = {key: value for key, value in os.environ.items() if key not in _VARIABLES}
    env.pop("DRTM_TB_IMAGE", None)
    env["DRTM_TB_RELEASE"] = release
    env.update(CONFIGURATIONS[configuration].env(release))
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m drtmtest.matrix", description=__doc__
    )
    parser.add_argument(
        "--releases",
        default="",
        help="comma-separated release tags to run, every pinned one by default",
    )
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="run one cell of the matrix")
    run.add_argument("release")
    run.add_argument("configuration")
    run.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command != "run":
        print(json.dumps(workflow_matrix(args.releases)))
        return 0
    env = environment(args.release, args.configuration)
    os.environ.clear()
    os.environ.update(env)
    # Imported here, once the environment is what the session reads.
    import pytest

    return int(pytest.main(args.pytest_args))


if __name__ == "__main__":
    sys.exit(main())
