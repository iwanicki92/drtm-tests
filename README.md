<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# drtm-tests

[![amd-drtm-test-image][badge-fork]][results]
[![v0.5.2][badge-v0.5.2]][results]
[![v0.5.3-rc1][badge-v0.5.3-rc1]][results]

Boots the [meta-trenchboot](https://github.com/zarhus/meta-trenchboot)
image under a QEMU that runs AMD's `SKINIT`, one boot per GRUB entry, and
checks what each launch leaves behind: the emulator's launch record, the
TPM's PCRs, the event log that has to replay to them, and what Xen or
Linux say about it.

Upstream QEMU raises `#UD` on `SKINIT`. The [`drtm` branch][qemu-fork] of
our QEMU fork adds the launch machine, `-machine q35,amd-drtm=on`, and
this suite needs that build. Point `DRTM_QEMU_BINARY` at it.

## Requirements

- The `drtm` branch of QEMU, built for `x86_64-softmmu` with
    `--enable-tpm`. `task ci:qemu` fetches the release CI boots with and
    prints its binary. It was built on Ubuntu 24.04 and links that
    release's glibc, glib and pixman, so on another host you will likely
    have to [build the `drtm` branch](docs/qemu.md#building-the-drtm-branch)
    yourself.
- `swtpm` and `swtpm-tools` on `PATH`.
- `mtools` on `PATH`, to read `grub.cfg` off the image without mounting
    it.
- `uv`, which installs the Python side on the first run.

## Running

```sh
export DRTM_QEMU_BINARY=/path/to/qemu-system-x86_64
uv run pytest
```

To boot the image by hand, with the serial console on stdio:

```sh
uv run tb-boot
uv run tb-boot query    # the launch record of the running instance
```

The first run downloads the Dasharo firmware and the image release into
`dl-cache/` and unpacks the image there, about 1.5 GB in all. Each run
writes its logs to a numbered directory under `logs/`.

| Variable           | Default               | Meaning                                                                                                            |
|--------------------|-----------------------|--------------------------------------------------------------------------------------------------------------------|
| `DRTM_QEMU_BINARY` | none, required        | The `drtm` branch's `qemu-system-x86_64`.                                                                          |
| `DRTM_TB_RELEASE`  | `amd-drtm-test-image` | Image release to boot, a tag pinned in `drtmtest/trenchboot.py`.                                                   |
| `DRTM_TB_IMAGE`    | unset                 | A local `.wic` to boot instead, read in place. No entry is expected broken on it. Excludes `DRTM_TB_RELEASE`.      |
| `DRTM_PSP`         | `off`                 | Adds the PSP DRTM service, see below.                                                                              |
| `DRTM_PCR_BANKS`   | `sha1,sha256`         | PCR banks active in every boot's TPM.                                                                              |
| `DRTM_QEMU_ARGS`   | unset                 | Words appended to every QEMU command line, so what they repeat wins. `tb-boot` takes the same after `--`.          |
| `DRTM_QEMU_ACCEL`  | `tcg`                 | `kvm` boots the normal entries faster and cannot run the launches.                                                 |

The default image is the `amd-drtm-test-image` release of [our
meta-trenchboot fork][tb-fork], a build of its `amd-drtm` branch with
both SKL builds and the fixes the upstream releases lack.

## The PSP path

AMD's Secure Processor can take part in the launch through its DRTM
service. Only an image with the `AMDSL` SKL (the SKL build with PSP
support) uses it, and a launch with the classic SKL fails under it.

`tb-boot --psp` starts the image with the service.

For the tests, `DRTM_PSP` adds the service to every boot and says which
SKL is in the image, so the tests know what to expect:

| Value           | Image                                         | Launch entries' tests       |
|-----------------|-----------------------------------------------|-----------------------------|
| `off` (default) | any                                           | pass, plain `SKINIT` launch |
| `on`            | `AMDSL` SKL: the fork's release or `amd-drtm` | pass, PSP-assisted launch   |
| `classic`       | classic SKL: upstream releases                | expected to fail            |

`classic` checks that the classic SKL does fail under the service. A
test that passes when it should fail fails the session, so a wrong
value for the image shows. The control entries, `xen_efi` and `linux`,
pass under every value. [Under the PSP](docs/testing.md#under-the-psp)
has the details.

## CI

Every push and pull request is linted. Pull requests to `main` and
pushes to `main` boot every pinned release under every configuration
of the matrix, and a push to `main` also publishes the tables to the
[`results` branch][results] the badges read. [The matrix in
CI](docs/testing.md#the-matrix-in-ci) says how to run one cell on a
host.

## Documentation

- [Design](docs/design.md): why the suite is shaped as it is.
- [Testing](docs/testing.md): what a boot looks like and what the tests
    assert.
- [QEMU](docs/qemu.md): how to build the `drtm` branch, what every QEMU
    argument is for and how to read the launch traces.

## License

BSD-3-Clause, see [LICENSE](LICENSE). `drtmtest/qmp_client.py` is adapted
from third-party Apache-2.0 code and stays under that license, see
[NOTICE](NOTICE).

[qemu-fork]: https://github.com/iwanicki92/qemu/tree/drtm
[tb-fork]: https://github.com/iwanicki92/meta-trenchboot/tree/amd-drtm
[results]: https://github.com/iwanicki92/drtm-tests/blob/results/README.md
[badge-fork]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iwanicki92/drtm-tests/results/badges/amd-drtm-test-image.json
[badge-v0.5.2]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iwanicki92/drtm-tests/results/badges/v0.5.2.json
[badge-v0.5.3-rc1]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iwanicki92/drtm-tests/results/badges/v0.5.3-rc1.json
