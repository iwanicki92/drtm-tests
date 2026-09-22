<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

A pytest suite that boots the meta-trenchboot image under our QEMU build,
the one that runs `SKINIT`, one boot per GRUB entry, and a `tb-boot`
command that does the same boot by hand. See `docs/design.md` for why and
`docs/testing.md` for how. `README.md` covers running it.

The `drtmtest` package is also the harness the `drtm` repository's
`qemu-tests` take, as a path dependency on this checkout. A change to
`qemu_vm.py`, `session.py`, `assets.py` or `dasharo.py` is a change to
that suite too, so run it as well. `machine.py`, `console.py`,
`trenchboot.py` and `boot.py` are this suite's own.

## Comments and docs

Two or three lines, maximum. State what is true now, not how it was found
out or what was tried. Anything longer belongs in `docs/`, which is edited
in place rather than grown.

Committed files cite upstream sources only: QEMU, TrenchBoot, Dasharo and
meta-trenchboot paths and release tags. Never a private notes repository.

## Commands

- `uv run pytest` runs the suite, `uv run tb-boot` boots by hand. Both need
    `DRTM_QEMU_BINARY` pointing at the drtm branch's `qemu-system-x86_64`
    and `swtpm` on `PATH`, the suite `mtype` too.
- `pre-commit run --all-files` lints everything (`pre-commit install`
    once).
- `task test`, `task boot` and `task lint` wrap the above.
