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
build is usually there to test a fix: an entry marked xfail on the releases
has to pass on it. Set together with `DRTM_TB_RELEASE` it is refused.

`DRTM_QEMU_ARGS` appends its words to every QEMU command line of the
session, split like a shell would. QEMU takes the last of a repeated
argument, so `-m 6G` raises the memory and `-machine pit=off` merges into
the machine options. `docs/testing.md` has the recipe this is for.
`tb-boot` takes the same after `--`.

To boot the image by hand, with the serial console on stdio:

```sh
uv run tb-boot
uv run tb-boot query    # the launch record of the running instance
```

## The PSP path

`DRTM_PSP=on` adds the Secure Processor with its DRTM service,
`-device amd-psp,drtm-service=on`, to every boot. GRUB, SKL and Xen find
it through the SMN pair on the host bridge and take the PSP-assisted
launch: GRUB sets a TMR up, the `AMDSL` SKL has the service check and
launch it, and Xen or Linux releases the TMR once its IOMMU is
programmed. The launch tests then assert on the service's record too,
and on Xen's PSP lines. No release carries the `AMDSL` SKL, so this goes with
`DRTM_TB_IMAGE` naming a build that does. `tb-boot --psp` boots one by
hand.

`DRTM_PSP=classic` is the same service under an image with the classic
SKL, the releases among them. Neither that GRUB nor that SKL talks to
the service, and the service keeps TPM localities 1 to 4 locked until a
`LAUNCH` nobody issues. The launch still boots: the SKL's extends at
locality 2 go into a locked locality unnoticed, and the OS's own extends
fail with all-ones answers, so the DRTM PCRs end up as `SKINIT` left
them and the launch tests fail on them. They are strict expected
failures in that session and the control entries have to boot.

The emulated service follows AMD's DRTM guide where the hardware logs
agreed with it and the hardware where they did not:

- The service answers nothing until the guest kicks it with a zero
    write to `C2PMSG_72`. A command before the kick leaves the ready bit
    clear for good, which is the timeout GRUB's source describes.
- One command at a time: a write while one is in flight is dropped.
- `TMR_SETUP` takes an index below `tmr-count`, a base aligned to
    `tmr-alignment` and a size in 64 KiB units. Each TMR is a DMA block
    named `tmr0` to `tmr7` in `dma-blocks`, and the IOMMU drops device
    DMA and interrupt messages into it, which is what breaks Xen's
    IO-APIC timer check when a TMR from address zero is still up.
    `TMR_RELEASE` drops them all and is accepted at any time. After a
    launch `TMR_SETUP` is refused.
- `LAUNCH` needs an `SKINIT` on record, the SLB inside one TMR, a
    measured length matching the `$AS1` signature header, the RSA-PSS
    signature verifying against the key token, and PCR 17 as `SKINIT`
    left it. Each failure is the one `DRTM_LAUNCH_ERROR` status plus a
    guest-error line naming the check, caps PCR 18 to 20 with an
    all-ones extend and unlocks locality 4. Success extends PCR 17 with
    the SPLT version and the TSME and anti-rollback states, PCR 18 with
    the key token and the SecPatchLevel, releases SL_DEV and unlocks
    localities 1 and 2, seizing the one the guest holds.
- `EXTEND_OSSL_DIGEST` hashes a range inside a TMR into PCR 17 and 18,
    then the `AMDSL` marker after it. `TPM_LOCALITY_ACCESS` locks
    locality 2 and unlocks 4. Both are refused before a successful
    launch. `GET_TCG_LOGS` hands out the event log of those extends.
- `GET_TMR_DESCRIPTORS`, `ALLOCATE_SHARED_MEMORY` and
    `GET_IVRS_TABLE_INFO` answer `DRTM_NOT_SUPPORTED`, since no boot
    here issues them.

Every guest-error line above stops a strict VM, like the platform's own
rules. `docs/qemu.md` lists the device's properties and its traces.

`docs/design.md` says why the suite is shaped as it is,
`docs/testing.md` what a boot looks like and what the tests assert, and
`docs/qemu.md` how to build the `drtm` branch, what every QEMU argument
is for and how to read the launch traces.

## License

BSD-3-Clause, see [LICENSE](LICENSE). `drtmtest/qmp_client.py` is adapted
from third-party Apache-2.0 code and stays under that license, see
[NOTICE](NOTICE).
