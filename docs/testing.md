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

`swtpm` and `swtpm_setup` (Debian: `swtpm-tools`) must be on `PATH`. The
session refuses a QEMU that rejects `-machine q35,amd-drtm=on` before
booting anything. `DRTM_QEMU_ACCEL=kvm` switches to KVM, which boots the
normal entries faster and cannot run the launches.

Only the boots the collected tests need are started, and they start at
collection, so a run of one test boots once and a full run has every boot
in flight before the first assertion.

## The entries

The image's GRUB menu lists six entries, and a fork build a seventh.
Each has a fixture of the same name in `tests/conftest.py`, and a test
takes the fixture of the boot it asserts on. Only entries a test names
are booted, so a run boots five on a release and six on a fork build:
the launches, the Xen EFI control and the Linux control. The Linux one is
kept because a kernel booted directly is what an IOMMU that passes DMA
through breaks, while Xen's dom0 never notices. The normal MB2 entry only
serves the menu check.

The seventh, `Boot Linux with TrenchBoot (alt)`, is the Linux launch
with `drtmtest=alt` on the kernel command line, which the fork's images
carry and the releases do not. Its tests skip on an image without it.
The two launches share the SKL and the kernel, so PCR 17 has to come out
the same and PCR 18 has to differ, with the log's command line event the
one that moved.

The MB2 entries are legacy boots and run under QEMU's SeaBIOS, the way a
BIOS board would run them. Under Dasharo's UEFI the MB2 launch runs SKL
and then stops. The EFI entries and the Linux ones run under Dasharo.

| Fixture               | GRUB entry                       | Firmware | On v0.5.2 here           |
|-----------------------|----------------------------------|----------|--------------------------|
| `xen_efi_launch`      | Boot Xen with TrenchBoot (EFI)   | Dasharo  | launches                 |
| `xen_efi`             | Boot Xen normally (EFI)          | Dasharo  | boots, control           |
| `xen_mb2_launch`      | Boot Xen with TrenchBoot (MB2)   | SeaBIOS  | launches                 |
| `linux_launch`        | Boot Linux with TrenchBoot       | Dasharo  | kernel panic             |
| `linux_legacy_launch` | Boot Linux with TrenchBoot       | SeaBIOS  | launches                 |
| `linux`               | Boot Linux normally              | Dasharo  | boots, control           |
| `xen_mb2`             | Boot Xen normally (MB2)          | SeaBIOS  | not booted               |
| `linux_alt_launch`    | Boot Linux with TrenchBoot (alt) | SeaBIOS  | not in the menu, skipped |

Entries are selected by title from the menu GRUB draws, not by a fixed
index, so a new entry in the image moves nothing here. The tests of an
entry the session is known not to boot are strict expected failures: they
must fail, and a pass is reported as a failure so the change is noticed
and the expectation removed. `Entry.broken_reason` in `tests/conftest.py`
decides, from the release, the image and `DRTM_PSP`.

### Under the PSP

`DRTM_PSP=on` boots everything with the Secure Processor's DRTM service,
for an image built with the `AMDSL` SKL. `DRTM_PSP=classic` is the same
service under a release or the classic SKL, which never talk to it and
extend into locked localities. The README says what the service does.
What each session expects:

| Fixture               | `DRTM_PSP=on`, `AMDSL` image      | `DRTM_PSP=classic`, classic image |
|-----------------------|-----------------------------------|-----------------------------------|
| `xen_efi_launch`      | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `xen_efi`             | boots, control                    | boots, control                    |
| `xen_mb2_launch`      | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `linux_launch`        | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `linux_legacy_launch` | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `linux_alt_launch`    | PSP-assisted launch, TMR released | boots, PCRs not extended          |
| `linux`               | boots, control                    | boots, control                    |

The event log replay is a strict expected failure under `DRTM_PSP=on`:
the service extends PCR 17 and 18 too, at its `LAUNCH` and at the SKL's
request, and logs those in a log of its own that `GET_TCG_LOGS` hands out
and nothing in the image fetches. The SKL's log alone cannot reach the
PCRs there: the `AMDSL` SKL's log opens with `SKINIT` and goes straight
to the OS's events, the DLME measurement having gone to the service. The
day an image merges the two, the run says so.

The first `AMDSL` build taught the harness two things. Its wic carried
the EFI boot alone, with a stub in the master boot record that boots
nothing, so the SeaBIOS entries could not start on it. The harness reads
the record and expects them broken on any such image. And its kernel
walked the PCI devices for the PSP in `setup_arch()`, before any is
enumerated, so it never learned of the service, never released the TMR
GRUB set up over all of memory, and stopped at the missing root with its
disk's DMA blocked. Both are fixed in the build that followed: the kernel
finds the PSP through configuration space and releases the TMR from its
IOMMU setup, and the launch tests assert on the release.

The `AMDSL` SKL needs the service. Without it the SKL still sends its
`LAUNCH` and extend to a mailbox that is not there, both fail, it never
releases SL_DEV, and the launch tests fail on that. The plain matrix is
for a classic image, the one `env.sh` selects.

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
- PCRs 17 to 22 from `tpm2_pcrread`, in one read.
- Xen's `slaunch` and `drtm` lines from `xl dmesg`, the same from `dmesg`,
    and the listing of `/sys/kernel/security/slaunch`.
- What the OS says of its IOMMU: Xen's `virt_caps` line from `xl info`,
    or the kernel's `/sys/class/iommu` and `/sys/kernel/iommu_groups`
    listings. A Linux boot also keeps `/proc/cmdline`.
- On a launch, the DRTM event log the SKL wrote, as hex over the
    console: Linux exposes it at `/sys/kernel/security/slaunch/eventlog`,
    and under Xen dom0 reads the range Xen's "reserving event log" line
    names out of `/dev/mem`. With it, the length field of the SLB header
    of the image's `/boot/skl.bin` and the SHA-256 of that many bytes of
    it, what `SKINIT` measures.
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
so agrees with the TPM under Xen only.

The launch tests check that the log opens with `SKINIT`'s event on
PCR 17, whose digest is the SLB's, that the platform's record has the
same SLB length as the header, and that the replay of PCR 17 and 18
reaches what `tpm2_pcrread` returned. The parser has its own tests in
`tests/test_eventlog.py`, against the logs two v0.5.3-rc1 launches left
in `tests/fixtures/`.

## Logs

Each run gets `logs/NNNN-YYYY-MM-DD/`, with one `boot-<fixture>/`
directory per boot holding `serial.log`, `qemu.log` with the launch traces
and guest errors (`qemu.md` says how to read them), `qemu-stderr.log`,
`swtpm.log` and `qemu-args.txt`, and `results.txt` naming the image and
summarising every test's outcome and duration. The first run on a machine
also has `boot-warm-firmware/`, the boot that produced the warmed firmware
image in `dl-cache/`.

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
