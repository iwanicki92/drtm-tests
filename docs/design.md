<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# Design

## Why a repository of its own

Three things test the AMD dynamic launch under QEMU, and each has a home:

- The QEMU tree's functional test boots one GRUB entry and proves the
    emulator does what its branch claims. It lives with the code it tests
    and stays in the shape upstream expects.
- The `drtm` repository boots its own UEFI binary, a precondition checker,
    in a few seconds per configuration. Its harness is tuned for that
    binary and its scope is that binary.
- This repository boots the whole image, every entry, and will grow axes
    the other two should not: image and loader versions, a second
    firmware, hardware logs.

The harness here started as a copy of the `drtm` one and diverged where a
disk image differs from a scratch ESP. If the copies drift apart in ways
that matter, the shared part becomes a package both take.

## What a boot is

One QEMU process on `-machine q35,smm=on,amd-drtm=on` with an `EPYC-Genoa`
CPU, Dasharo's coreboot+UEFI build as flash or QEMU's SeaBIOS for the
legacy entries, the image behind an IDE controller with `snapshot=on`, and
an `swtpm` behind `tpm-tis`. Strict mode is on, so a launch rule the
emulator would otherwise only log stops the VM as a panic, and the panic
action is set to pause so the stopped VM stays for the harness to see,
which reports it within a second instead of at the timeout.

The serial console is the only way in. A reader thread drains it into
`serial.log` for the life of the boot, and the driver waits for prompts
from a cursor that advances with every match, so a prompt seen twice is
two matches and a command's output is what came between its echo and the
next prompt.

Every GRUB entry is booted once per session, as many at a time as the CPUs
and free memory allow, and the tests assert on what the boot gathered
before the VM went away: the `query-amd-drtm` record, four PCRs, and the
`slaunch` lines from Xen's log, `dmesg` and securityfs.

## What is asserted

A launch leaves the platform's record saying so, with the SLB hashed and
SL_DEV released by the loader, and the DRTM PCRs reset by the locality 4
start: 17 and 18 then extended, 19 left at zero since nothing on the AMD
path extends it. A normal boot leaves no record and those PCRs at all
ones, which is how a TPM 2.0 reports them until a launch resets them.

Entries known not to boot on the pinned release are expected failures with
the reason in the test, strictly, so the day one boots the run says so.

## Where the time goes

Under TCG a boot to the login prompt is dominated by Xen and dom0, with
the firmware and GRUB's loading of Xen, the kernel and the initrd before
it. The harness takes what it can: the firmware image is warmed once per
release so no boot populates the variable store, the boot manager's prompt
is answered rather than waited out, no VGA or NIC, and the loader's "press
any key" pause is answered when it appears. KVM cannot help, since it does
not run `SKINIT`.
