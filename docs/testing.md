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

`swtpm` must be on `PATH`. The session refuses a QEMU that rejects
`-machine q35,amd-drtm=on` before booting anything. `DRTM_QEMU_ACCEL=kvm`
switches to KVM, which boots the normal entries faster and cannot run the
launches.

Only the boots the collected tests need are started, and they start at
collection, so a run of one test boots once and a full run has every boot
in flight before the first assertion.

## The entries

The image's GRUB menu lists six entries. Each has a fixture of the same
name in `tests/conftest.py`, and a test takes the fixture of the boot it
asserts on. Only entries a test names are booted, so a run boots five:
the three launches, the Xen EFI control and the Linux control. The Linux
one is kept because a kernel booted directly is what an IOMMU that passes
DMA through breaks, while Xen's dom0 never notices. The normal MB2 entry
only serves the menu check.

The MB2 entries are legacy boots and run under QEMU's SeaBIOS, the way a
BIOS board would run them. Under Dasharo's UEFI the MB2 launch runs SKL
and then stops. The EFI entries and the Linux ones run under Dasharo.

| Fixture          | GRUB entry                       | Firmware | On v0.5.2 here |
|------------------|----------------------------------|----------|----------------|
| `xen_efi_launch` | Boot Xen with TrenchBoot (EFI)   | Dasharo  | launches       |
| `xen_efi`        | Boot Xen normally (EFI)          | Dasharo  | boots, control |
| `xen_mb2_launch` | Boot Xen with TrenchBoot (MB2)   | SeaBIOS  | launches       |
| `linux_launch`   | Boot Linux with TrenchBoot       | Dasharo  | kernel panic   |
| `linux`          | Boot Linux normally              | Dasharo  | boots, control |
| `xen_mb2`        | Boot Xen normally (MB2)          | SeaBIOS  | not booted     |

Entries are selected by title from the menu GRUB draws, not by a fixed
index, so a new entry in the image moves nothing here. The tests of an
entry marked broken are strict expected failures: they must fail, and a
pass is reported as a failure so the change is noticed and the mark
removed.

## What a boot gathers

Once the shell answers, before the VM is torn down:

- `query-amd-drtm` over QMP: `launched`, the hash verdict, the SLB length,
    whether SL_DEV is still held and which DMA blocks remain.
- PCRs 17 to 22 from `tpm2_pcrread`, in one read.
- Xen's `slaunch` and `drtm` lines from `xl dmesg`, the same from `dmesg`,
    and the listing of `/sys/kernel/security/slaunch`.
- The whole console capture. The Xen tests read the hypervisor's lines
    off it, the ones tagged `(XEN)`, rather than off `xl dmesg`: the
    console ring is small and a verbose boot pushes the early lines out
    of it, while the serial output keeps them.

## Logs

Each run gets `logs/NNNN-YYYY-MM-DD/`, with one `boot-<fixture>/`
directory per boot holding `serial.log`, `qemu.log` with the launch traces
and guest errors (`qemu.md` says how to read them), `qemu-stderr.log`,
`swtpm.log` and `qemu-args.txt`, and `results.txt` naming the release and
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
