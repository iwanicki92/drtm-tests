<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# Testing

## Running

```sh
export DRTM_QEMU_BINARY=/path/to/qemu-system-x86_64   # the drtm branch
uv run pytest                 # every entry
uv run pytest -k xen_efi      # one entry's tests, and only its boot
uv run pytest --collect-only  # what would run, booting nothing
```

The session refuses a QEMU that rejects `-machine q35,amd-drtm=on`
before booting anything. `DRTM_QEMU_ACCEL=kvm` switches to KVM, which
boots the normal entries faster and cannot run the launches.

Only the boots the collected tests need are started, and they start at
collection, so a run of one test boots once and a full run has every boot
in flight before the first assertion.

## The entries

The image's GRUB menu lists six entries and the suite adds a seventh,
`linux_alt_launch`. Each has a fixture of the same name in
`tests/conftest.py`, and a test takes the fixture of the boot it asserts
on. Only entries a test names are booted, so a full run boots six of
them, all but `xen_mb2`, which only serves the menu check. The Linux
control catches a QEMU configuration whose IOMMU passes DMA through
instead of translating it, `dma-remap=on` missing for instance: a Linux
booted directly then cannot find its disk, while Xen's dom0 boots
either way.

`linux_alt_launch` is the legacy Linux launch with `drtmtest=alt` added
to the kernel command line. It boots under SeaBIOS because the legacy
Linux launch is the one that works on every release, the EFI one
panicking on the upstream releases. It is not in any menu: the harness
reads `grub.cfg` off the image's boot partition with `mtype`, takes the
entry's commands, appends the parameter to the `linux` line, and types
them at GRUB's shell, entered from the menu with `c`, then `boot`. The
functions the config defines are GRUB's by then, so the commands run as
the entry would. The commands typed are kept as `grub-commands.txt` in
the boot's log directory. The two launches share the SKL and the kernel,
so PCR 17 has to come out the same and PCR 18 has to differ, with the
log's command line event the one that moved. The fork's image lists this
launch as an entry of its own as well, which the menu check allows and
nothing boots.

The MB2 entries are legacy boots and run under QEMU's SeaBIOS, the way a
BIOS board would run them. Under Dasharo's UEFI the MB2 launch runs SKL
and then stops. The EFI entries and the Linux ones run under Dasharo.

| Fixture               | GRUB entry                       | Firmware | Upstream releases        |
|-----------------------|----------------------------------|----------|--------------------------|
| `xen_efi_launch`      | Boot Xen with TrenchBoot (EFI)   | Dasharo  | launches                 |
| `xen_efi`             | Boot Xen normally (EFI)          | Dasharo  | boots, control           |
| `xen_mb2_launch`      | Boot Xen with TrenchBoot (MB2)   | SeaBIOS  | launches                 |
| `linux_launch`        | Boot Linux with TrenchBoot       | Dasharo  | kernel panic             |
| `linux_legacy_launch` | Boot Linux with TrenchBoot       | SeaBIOS  | launches                 |
| `linux`               | Boot Linux normally              | Dasharo  | boots, control           |
| `xen_mb2`             | Boot Xen normally (MB2)          | SeaBIOS  | not booted               |
| `linux_alt_launch`    | Boot Linux with TrenchBoot, alt  | SeaBIOS  | launches                 |

The fork's release launches or boots every entry.

Entries are selected by title from the menu GRUB draws, not by a fixed
index, so a new entry in the image moves nothing here. The highlight is
moved one key at a time, each waited for in GRUB's redraw and pressed
again if it drew nothing, since a starved guest can read the key's
escape sequence as three plain keys.

### Expected failures

The tests of an entry the session is known not to boot are strict
expected failures: they must fail, and a pass is reported as a failure
so the change is noticed and the expectation removed.
`Entry.broken_reason` in `tests/conftest.py` decides, from the release,
the image and `DRTM_PSP`. An image whose wic carries the EFI boot alone,
with a stub in its master boot record, has its SeaBIOS entries expected
broken.

### Under the PSP

`DRTM_PSP=on` boots everything with the Secure Processor's DRTM service,
for an image built with the `AMDSL` SKL (the SKL build with PSP
support). `DRTM_PSP=classic` is the same service under an upstream
release or any classic SKL, which never talks to it and extends into
locked localities. Xen still boots but its extends fail: the tests that
check the launch (the platform's record, Xen's report and the PCR
replay) are expected to fail, the IOMMU and bank tests pass. Linux
panics in `slaunch_pcr_extend` and none of its launch tests are expected
to pass. [The PSP device](qemu.md#the-psp-device) says what the service
does. What each session expects:

| Fixture               | `DRTM_PSP=on`, `AMDSL` image      | `DRTM_PSP=classic`, classic image |
|-----------------------|-----------------------------------|-----------------------------------|
| `xen_efi_launch`      | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `xen_efi`             | boots, control                    | boots, control                    |
| `xen_mb2_launch`      | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `linux_launch`        | PSP-assisted launch, TMR released | panics on its extend              |
| `linux_legacy_launch` | PSP-assisted launch, TMR released | panics on its extend              |
| `linux_alt_launch`    | PSP-assisted launch, TMR released | panics on its extend              |
| `linux`               | boots, control                    | boots, control                    |

Under `DRTM_PSP=on` the launch tests also assert that Xen or Linux
released the TMR. The `AMDSL` SKL needs the service: without it the
SKL's `LAUNCH` and extend go to a mailbox that is not there, SL_DEV is
never released and the launch tests fail.

### A launch that keeps the TMR

An image whose Xen or Linux has no PSP client never releases the TMR,
and what the session then shows depends on memory. GRUB sizes the TMR
to the top of RAM. With the default 2 GiB it ends at `0x7ff00000` and
the boot goes on until the disk is needed: every AHCI transfer lands in
the TMR, `qemu.log` fills with `amd_drtm_dma_blocked tmr0`, the disk
never attaches and the boot hangs at init. With RAM above 4 GiB the TMR
covers the interrupt message window at `0xFEE00000` as well, so every
IO-APIC and MSI interrupt is dropped, and Xen's timer check walks its
fallbacks. QEMU still delivers the last one, the 8259 wired straight to
the CPU, so Xen carries on into a dom0 without device interrupts and
hangs there. Hardware where that wire is dead panics in the check
instead, with "IO-APIC + timer doesn't work!". Taking the 8254 away
gets the same panic here, which the harness reports as a guest panic:

```sh
DRTM_PSP=on DRTM_TB_IMAGE=/path/to/build.wic \
    DRTM_QEMU_ARGS="-m 6G -machine pit=off" \
    uv run pytest tests/test_xen.py -k launch
```

Neither is a session default. The memory is what lets six boots share
a 16 GB host, and a machine without an 8254 would change every boot for
the sake of one failure.

## What a boot gathers

Once the shell answers, before the VM is torn down:

- `query-amd-drtm` over QMP: `launched`, the hash verdict, the SLB length,
    whether SL_DEV is still held and which DMA blocks remain, and with the
    service its `psp` record: whether it was kicked, what its `LAUNCH`
    decided, what it found of the SKL's signature, and the last command
    with its status.
- PCRs 17 to 22 from `tpm2_pcrread`, in SHA-256 and then in every bank
    the TPM has, as `tpm2_getcap pcrs` lists them.
- Xen's `slaunch` and `drtm` lines from `xl dmesg`, the same from `dmesg`,
    and the listing of `/sys/kernel/security/slaunch`.
- What the OS says of its IOMMU: Xen's `virt_caps` line from `xl info`,
    or the kernel's `/sys/class/iommu` and `/sys/kernel/iommu_groups`
    listings. A Linux boot also keeps `/proc/cmdline`.
- On a launch, the DRTM event log the SKL wrote, as hex over the
    console: Linux exposes it at `/sys/kernel/security/slaunch/eventlog`,
    and under Xen dom0 reads the range Xen's "reserving event log" line
    names out of `/dev/mem`.
- On a launch, the bytes `SKINIT` measured: the start of the SKL the
    boot ran (`/boot/skl.bin`, or `/boot/skl-amdsl.bin` under the
    service), up to the length its header gives, dumped as hex the same
    way. The harness hashes them itself to check the log's `SKINIT`
    record, and to replay PCR 17 in banks where the SKL could only log a
    placeholder.
- The whole console capture. The Xen tests read the hypervisor's lines
    off it, the ones tagged `(XEN)`, rather than off `xl dmesg`: the
    console ring is small and a verbose boot pushes the early lines out
    of it, while the serial output keeps them.

## The event log

`drtmtest/eventlog.py` parses the log as the SKL writes it, a TCG2 log
with the SHA-1 and SHA-256 banks and one `TCG_PCR_EVENT2` per extend,
and replays a PCR from the zero a locality 4 start leaves. `EV_NO_ACTION`
events are logged but not extended, which matters on Linux: the kernel
brackets its own measurements with two such tags on PCR 17, and a replay
that extends them lands off the TPM's value. The image's own
`anti-evil-maid-dump-evt-log`, in v0.5.3-rc1 onwards, replays them and
so agrees with the TPM under Xen only. An event carrying one bank's
digest counts for that bank alone.

Under `DRTM_PSP=on` the service extends PCR 17 and 18 too, at its
`LAUNCH` and at the SKL's request, and logs those in a log of its own
that `GET_TCG_LOGS` hands out. The `AMDSL` SKL fetches it after the OSSL
extend and appends its records to its own log, all but the `SKINIT` one
it logged already, so the log carries every extend and replays to the
PCRs like the classic SKL's. The service logs the SHA-256 bank alone and
the SKL's log has two, so each appended record gets the TCG placeholder
digest, a one then zeros, in its SHA-1 bank, and the SKL extends the
SHA-1 bank of that PCR with it, so it replays like any other digest.
Linux resets on a record that does not carry every bank the header
declares, and again on a header that does not declare every bank the TPM
has, which rules out one-bank records and a one-bank header. An image
whose SKL does not merge the two logs fails the five replay tests under
the service.

The launch tests check that the log opens with `SKINIT`'s event on
PCR 17, whose digest is the SLB's, that the platform's record has the
same SLB length as the header, and that the replay of PCR 17 and 18
reaches what `tpm2_pcrread` returned. The parser has its own tests in
`tests/test_eventlog.py`, against the logs two v0.5.3-rc1 launches left
in `tests/fixtures/`.

## PCR banks

The SKL asks the TPM which banks have PCRs and declares exactly those,
in the TPM's order. Its own measurements carry SHA-1 and SHA-256 where
the TPM has them and the placeholder elsewhere, extended into that bank
as well, so a TPM with SHA-256 alone or with SHA-384 on top boots Linux
and replays too. `DRTM_PCR_BANKS` sets the banks of the fresh TPM state
to try that. `SKINIT`'s record gets the placeholder in a bank the SKL
cannot hash for, though the launch measured the SLB into that bank, so
the log alone does not replay there. The image's Xen skips the digests
of banks the log does not declare when it copies the multiboot
information's, so its legacy launch replays with SHA-256 alone too.

Two tests per launch cover this. The log's header must declare the
banks the TPM has PCRs in, as `tpm2_getcap pcrs` lists them, no more
and no fewer. And the replay runs in every bank the TPM has, with
`SKINIT`'s record taken as the SLB's digest in that bank, computed by
the harness from the SLB bytes the boot dumps, since the log carries
the placeholder where the SKL cannot hash while the launch measured the
SLB there too. The log's own `SKINIT` digest is checked against the
SLB's in SHA-1 and SHA-256, the banks the SKL hashes for. On the
upstream releases under any banks but the default two, the Linux
launches are expected not to boot and the bank test is expected to
fail, and with a bank beyond those two the MB2 replay is expected to
miss in it, since their Xen copies the multiboot information's digests
for SHA-1 and SHA-256 alone. `tests/conftest.py` holds the three.

## Logs

Each run gets `logs/NNNN-YYYY-MM-DD/`, with one `boot-<fixture>/`
directory per boot holding `serial.log`, `qemu.log` with the launch traces
and guest errors (`qemu.md` says how to read them), `qemu-stderr.log`,
`swtpm.log` and `qemu-args.txt`, and `results.txt` naming the image and
summarising every test's outcome and duration. The first run on a machine
also has `boot-warm-firmware/`, the boot that produced the warmed firmware
image in `dl-cache/`.

`results.json` beside it is the same for machines: the release, the
matrix configuration the environment amounts to, the QEMU and swtpm in
use, the commit under test, the entries and one record per test with
the fixtures it took and its outcome, where an expected failure is
`xfailed` and an unexpected pass `xpassed` rather than the `skipped`
and `failed` of `results.txt`. The report below is rendered from these.

## The matrix in CI

`.github/workflows/ci.yml` lints every push and pull request, and on
pull requests to `main`, pushes to `main` and by hand boots every
pinned release under every configuration, one job each. A
configuration is the environment a session boots with, from
`drtmtest/matrix.py`:

| Name         | Environment                             | What it exercises                          |
|--------------|-----------------------------------------|--------------------------------------------|
| `classic`    | none                                    | Classic launch, TPM with SHA-1 and SHA-256 |
| `psp`        | `DRTM_PSP=on`                           | PSP DRTM service on                        |
| `sha256`     | `DRTM_PCR_BANKS=sha256`                 | TPM with SHA-256 alone                     |
| `psp-sha256` | `DRTM_PSP=on`, `DRTM_PCR_BANKS=sha256`  | PSP DRTM service on, SHA-256 alone         |
| `sha384`     | `DRTM_PCR_BANKS=sha1,sha256,sha384`     | TPM with SHA-384 on top                    |

On the upstream releases the PSP configurations set `DRTM_PSP=classic`
instead, since their SKL never talks to the service. [Under the
PSP](#under-the-psp) says what each entry then does. A run by hand
takes an optional comma-separated list of release tags to boot a
subset.

The workflow calls `task` targets and nothing else, so a cell runs on a
host the same way:

```sh
export DRTM_QEMU_BINARY=$(task ci:qemu)   # the pinned bundle, once
task ci:test RELEASE=v0.5.2 CONFIG=sha256
task ci:test RELEASE=amd-drtm-test-image CONFIG=psp -- -k xen_efi
```

`ci:test` clears `DRTM_PSP`, `DRTM_PCR_BANKS` and `DRTM_TB_IMAGE` and
sets the cell's own, so the shell's setting cannot leak into a cell.
Everything else, `DRTM_QEMU_BINARY` and `DRTM_QEMU_ARGS` among them,
passes through.

### The QEMU bundle

CI does not build QEMU. The `drtm` branch is released as a tarball on
[our QEMU fork](https://github.com/iwanicki92/qemu/releases), tag
`drtm-<QEMU version>-<n>`. It holds `qemu/bin/qemu-system-x86_64` and
`qemu/share/qemu/`, so the binary finds its firmware blobs, which the
SeaBIOS entries need, through its own relative data directory. It was
built on Ubuntu 24.04, whose glibc, glib and pixman it links, and the
jobs run on that runner image, with the same swtpm 0.7.3.

`drtmtest/bundle.py` pins the tag and the SHA-256 the way the images are
pinned. `task ci:qemu` fetches the bundle into `dl-cache/`, unpacks it
under the hash and prints the binary's path.

`task qemu-bundle QEMU_BUILD=/path/to/qemu/build` makes a bundle from a
build directory: it takes the stripped binary and the data directory of
the install tree meson lays out in the build, and prints the tarball and
its hash. The release is created by hand with the tarball attached.

### Results

Every boot job uploads its `logs/` as an artifact, pass or fail, with
`results.json` in it. The `report` job downloads them all and runs
`task report RESULTS=<dir>`, which renders a page and one badge per
release: a section per configuration with a table of the entries the
suite boots against the releases, a cell being ✅ when every test of
the entry passed and ❌ when one failed, whatever the suite expected,
with the expectations noted under the table and the full per-test table
folded below. The page goes to the job summary and, on a push to
`main`, to the `results` branch, one commit per run, which the badges
in the README read.

## Timeouts

A boot to the login prompt takes a minute or two under TCG, longer when
several overlap. `BOOT_TIMEOUT` in `tests/conftest.py` allows for a full
batch, and the pytest timeout in `pyproject.toml` sits above it as a
backstop, raising inside the test so `results.txt` is still written. A
panic on the console, or the VM stopping under strict mode, which the
pause panic action keeps alive to be seen, ends the wait at once with the
reason, and a console silent for `IDLE_TIMEOUT` in
`drtmtest/qemu_vm.py` ends it as a hang, since no phase of a boot pauses
that long.
