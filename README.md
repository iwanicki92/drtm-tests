<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# drtm-tests

Boots the [meta-trenchboot](https://github.com/zarhus/meta-trenchboot)
image under a QEMU that runs AMD's `SKINIT`, one boot per GRUB entry, and
checks what each launch leaves behind: the emulator's launch record, the
TPM's PCRs and what Xen or Linux say about it.

Upstream QEMU raises `#UD` on `SKINIT`. The `drtm` branch of our QEMU
tree adds the launch machine, `-machine q35,amd-drtm=on`, and this suite
needs that build. Point `DRTM_QEMU_BINARY` at it.

## Requirements

- The `drtm` branch of QEMU, built for `x86_64-softmmu` with
    `--enable-tpm`. Its build wants a C toolchain, `ninja-build`,
    `pkg-config`, Python 3 with `tomli`, `libglib2.0-dev` and
    `libpixman-1-dev`, plus `libgcrypt20-dev` for the RSA behind the PSP
    path's signature check. Without it, or nettle in its place, the
    build still runs, and the check is skipped and reported as
    `unsupported`. [Building the `drtm`
    branch](docs/qemu.md#building-the-drtm-branch) has the configure
    line.
- `swtpm` and `swtpm-tools` on `PATH`. The `emulator` backend is the only
    one carrying the locality 4 hash sequence, and every boot seeds a
    fresh TPM state with `swtpm_setup`.
- `uv`, which installs the Python side on the first run.
- About 1.5 GB under `dl-cache/` for the firmware and the unpacked image,
    and under a megabyte of logs per run.

## Running

```sh
export DRTM_QEMU_BINARY=/path/to/qemu-system-x86_64
uv run pytest
```

The first run downloads the Dasharo firmware and the image release into
`dl-cache/` and unpacks the image there, about 1.5 GB in all. Each run
writes its logs to a numbered directory under `logs/`.

The image is the newest meta-trenchboot release by default. Set
`DRTM_TB_RELEASE` to another tag pinned in `drtmtest/trenchboot.py` to boot that
one instead, a release candidate for instance. Each release keeps its own
download and unpacked disk in `dl-cache/`.

`DRTM_TB_IMAGE` boots a build of your own instead: the raw `.wic` bitbake
deploys, read where it is. No entry is expected broken on it, since a local
build is usually there to test a fix, so a test the releases only xfail has
to pass. Set together with `DRTM_TB_RELEASE` it is refused.

To boot the image by hand, with the serial console on stdio:

```sh
uv run tb-boot
uv run tb-boot query    # the launch record of the running instance
```

`docs/design.md` says why the suite is shaped as it is,
`docs/testing.md` what a boot looks like and what the tests assert, and
`docs/qemu.md` how to build the `drtm` branch, what every QEMU argument
is for and how to read the launch traces.

## License

BSD-3-Clause, see [LICENSE](LICENSE). `drtmtest/qmp_client.py` is adapted
from third-party Apache-2.0 code and stays under that license, see
[NOTICE](NOTICE).
