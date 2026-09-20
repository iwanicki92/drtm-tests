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

To boot the image by hand, with the serial console on stdio:

```sh
uv run tb-boot
uv run tb-boot query    # the launch record of the running instance
```

`docs/design.md` says why the suite is shaped as it is,
`docs/testing.md` what a boot looks like and what the tests assert, and
`docs/qemu.md` what every QEMU argument is for and how to read the launch
traces.

## License

BSD-3-Clause, see [LICENSE](LICENSE). `drtmtest/qmp_client.py` is adapted
from third-party Apache-2.0 code and stays under that license, see
[NOTICE](NOTICE).
