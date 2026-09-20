<!--
SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>

SPDX-License-Identifier: BSD-3-Clause
-->

# Building the `drtm` QEMU, its command line and its traces

How to build the `drtm` branch of QEMU, what the harness runs on it
for every boot, argument by argument, what the `amd-drtm=on` machine
option stands for, and how to read the launch traces it writes to
`qemu.log`. `uv run tb-boot -n` prints the exact command for a boot by
hand.

## Building the `drtm` branch

Upstream QEMU raises `#UD` on `SKINIT` and knows none of the DRTM
devices, so every boot needs a build of the `drtm` branch. QEMU's own
build wants a C toolchain, `ninja-build`, `pkg-config`, Python 3 with
`tomli`, `libglib2.0-dev` and `libpixman-1-dev`. Two more things decide
what a launch under it can do:

- `libgcrypt20-dev` or `nettle-dev` at build time. The PSP DRTM service
    verifies the SKL's RSA-PSS signature at `LAUNCH` through QEMU's crypto
    layer, which has no RSA without one of them. A build with neither
    skips the check and reports the signature as `unsupported` in the
    launch record. The configure summary's `libgcrypt` and `nettle` lines
    say which one a build has. Configure finds libgcrypt on its own,
    and nettle if libgcrypt is missing, unless a gnutls development
    package is installed: QEMU then takes gnutls for its crypto and
    looks for neither, and gnutls has no RSA path for the check. On
    such a host add `--enable-gcrypt`. The nettle path also needs
    `libgmp-dev`, which its RSA support is built on.
- `swtpm` and `swtpm-tools` at run time. The `emulator` backend is the
    only one carrying the locality 4 hash sequence, and the harness seeds
    each TPM state with `swtpm_setup`.

The configure line the suite is developed against, from an empty `build`
directory inside the tree:

```sh
../configure --target-list=x86_64-softmmu --enable-tpm --disable-docs
ninja qemu-system-x86_64
```

Name the target: a bare `ninja` builds every test binary as well and takes
many times longer. Check the summary for `TPM support: YES`, and run
configure again after installing a library, since the build does not
notice a new one on its own.

## The command

A TPM emulator first, then QEMU pointed at its socket. This is the full
form, every device the launch needs spelled out:

```sh
swtpm socket --tpm2 --tpmstate dir=tpmstate \
    --ctrl type=unixio,path=swtpm.sock &

qemu-system-x86_64 \
    -machine q35,smm=on \
    -accel tcg \
    -cpu EPYC-Genoa,skinit=on \
    -smp 2 \
    -m 2G \
    -global q35-pcihost.mch-multifunction=on \
    -global q35-pcihost.cf8-extended-config=on \
    -device amd-drtm-platform,strict=on \
    -action panic=pause \
    -device amd-nb,bus=pcie.0,addr=18.0 \
    -device AMDVI-PCI,id=amd-drtm-iommu,bus=pcie.0,addr=0.2 \
    -device amd-iommu,pci-id=amd-drtm-iommu,firmware-enabled=on,dma-remap=on \
    -chardev socket,id=chrtpm,path=swtpm.sock \
    -tpmdev emulator,id=tpm0,chardev=chrtpm \
    -device tpm-tis,tpmdev=tpm0 \
    -drive file=image.wic,format=raw,if=none,id=hd,snapshot=on \
    -device ide-hd,drive=hd \
    -display none -vga none -nic none \
    -qmp unix:qmp.sock,server,nowait \
    -d guest_errors \
    -drive if=pflash,format=raw,file=firmware.rom \
    -D qemu.log \
    -trace 'amd_drtm_*' -trace 'amd_nb_*' \
    -trace x86_skinit -trace x86_vm_cr_write \
    -trace x86_sipi_after_launch \
    -trace x86_init_held -trace x86_init_redirected \
    -serial mon:stdio
```

`qemu-system-x86_64` is the `drtm` branch build from above.

### The `amd-drtm=on` shorthand

What the harness actually passes is shorter. `-machine q35,smm=on,amd-drtm=on`
stands for the seven launch lines in the command above:

```sh
    -cpu EPYC-Genoa,skinit=on
    -global q35-pcihost.mch-multifunction=on
    -global q35-pcihost.cf8-extended-config=on
    -device amd-drtm-platform
    -device amd-nb,bus=pcie.0,addr=18.0
    -device AMDVI-PCI,id=amd-drtm-iommu,bus=pcie.0,addr=0.2
    -device amd-iommu,pci-id=amd-drtm-iommu,firmware-enabled=on,dma-remap=on
```

It adds `skinit=on` to whatever `-cpu` names, so the CPU model stays a
free choice. Since the platform device is then created by the machine
rather than by a `-device` line, its `strict` property is set through
`-global amd-drtm-platform.strict=on` instead. Each device also works on
its own: `-device amd-drtm-platform` alone records launches and hashes
the SLB but has no IOMMU to enforce SL_DEV with, and `amd-nb` alone gives
SKL a MEMPROT_CR to write. The shorthand does not add the Secure
Processor, `-device amd-psp`, which publishes the ASPT and, with
`drtm-device=on`, the ACPI DRTM device: neither is needed for a launch
through `SKINIT` and no boot here uses them.

## The arguments

| Argument                                                                   | Why                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-machine q35,smm=on`                                                      | Q35 is the chipset the Dasharo build targets. `smm=on` gives the firmware the SMM it sets up on.                                                                                                                                                                                                                                                                                                                                                            |
| `-accel tcg`                                                               | The only accelerator that runs `SKINIT`, since it is emulated in TCG. `DRTM_QEMU_ACCEL=kvm` or `auto` picks KVM for booting the normal entries faster.                                                                                                                                                                                                                                                                                                      |
| `-cpu EPYC-Genoa,skinit=on`                                                | An AMD model with SVM, so `SKINIT` is decodable, and the `skinit` CPUID bit the loaders check for. TCG warns about features it cannot provide, AVX-512 among them, which is harmless.                                                                                                                                                                                                                                                                       |
| `-smp 2`                                                                   | One BSP and one AP, so the launch has an AP to park and restart, which is where INIT handling matters.                                                                                                                                                                                                                                                                                                                                                      |
| `-m 2G`                                                                    | Enough for Xen with a dom0 or Linux with the image's initramfs. `conftest.py` counts guests against free memory at this size.                                                                                                                                                                                                                                                                                                                               |
| `-global q35-pcihost.mch-multifunction=on`                                 | Marks the host bridge at 00:00.0 multifunction, without which nothing enumerates the IOMMU at function 2 of the same slot.                                                                                                                                                                                                                                                                                                                                  |
| `-global q35-pcihost.cf8-extended-config=on`                               | Decodes AMD's extended register bits in port `0xcf8`, which is how SKL reaches MEMPROT_CR at offset 0x384, beyond the 256 bytes conventional configuration space covers.                                                                                                                                                                                                                                                                                    |
| `-device amd-drtm-platform,strict=on`                                      | The device that keeps the state of a launch. When a CPU executes `SKINIT` it records the SLB, hashes it into PCR 17 through the TPM and blocks device DMA to it, and it is what `query-amd-drtm` reads. Without it `SKINIT` is an undefined opcode, as upstream. `strict=on` turns a broken launch rule into a VM stop in the `guest-panicked` state, so the harness sees a failed boot rather than a logged line. `--no-strict` in `tb-boot` turns it off. |
| `-action panic=pause`                                                      | What QEMU does after a strict stop. The default, `shutdown`, exits the process, which would turn a broken rule into "QEMU exited". Pausing keeps the stopped VM, so `query-status` names the stop and `query-amd-drtm` still answers.                                                                                                                                                                                                                       |
| `-device amd-nb,bus=pcie.0,addr=18.0`                                      | The northbridge PCI function at 00:18.0, where AMD firmware and SKL expect it. It carries the MEMPROT_CR register. After the launch, SKL clears the enable bit in that register to release SL_DEV, and the northbridge reports the write to the platform device, which then lifts the DMA block.                                                                                                                                                            |
| `-device AMDVI-PCI,id=amd-drtm-iommu,bus=pcie.0,addr=0.2`                  | The IOMMU's PCI function at 00:00.2, its usual place on AMD. Given an id so the IOMMU proper can be tied to it.                                                                                                                                                                                                                                                                                                                                             |
| `-device amd-iommu,pci-id=amd-drtm-iommu,firmware-enabled=on,dma-remap=on` | The IOMMU itself, bound to that function. `firmware-enabled` leaves it enabled as firmware would, which SKL relies on. `dma-remap` makes it translate rather than pass DMA through, which a Linux booted directly needs to find its disk. Its `ivrs` default publishes the IVRS table.                                                                                                                                                                      |
| `-chardev socket,id=chrtpm,path=...`                                       | The Unix socket swtpm serves its control channel on.                                                                                                                                                                                                                                                                                                                                                                                                        |
| `-tpmdev emulator,id=tpm0,chardev=chrtpm`                                  | QEMU's swtpm backend. This is the backend that carries the locality 4 hash sequence, so a launch can extend PCR 17.                                                                                                                                                                                                                                                                                                                                         |
| `-device tpm-tis,tpmdev=tpm0`                                              | The TIS frontend at its usual MMIO. The launch hashes the SLB through it, at locality 4.                                                                                                                                                                                                                                                                                                                                                                    |
| `-drive file=...,format=raw,if=none,id=hd,snapshot=on`                     | The unpacked image, opened as a raw disk. `snapshot=on` throws writes away so boots do not change the cached file. `tb-boot -w` makes it writable.                                                                                                                                                                                                                                                                                                          |
| `-device ide-hd,drive=hd`                                                  | The disk on Q35's AHCI controller, which both firmwares boot from and both kernels find.                                                                                                                                                                                                                                                                                                                                                                    |
| `-display none -vga none -nic none`                                        | No window, no VGA and no network card: everything goes over serial, and a NIC would add a DMA-capable device the tests do not use.                                                                                                                                                                                                                                                                                                                          |
| `-qmp unix:...,server,nowait`                                              | The monitor socket `query-amd-drtm` is asked on, plus `query-status` once a second to notice a strict-mode stop.                                                                                                                                                                                                                                                                                                                                            |
| `-d guest_errors`                                                          | Logs guest-side mistakes QEMU catches, the launch rules among them, into the log file.                                                                                                                                                                                                                                                                                                                                                                      |
| `-drive if=pflash,format=raw,file=...`                                     | The Dasharo ROM as flash. Left out for the MB2 entries, which then boot QEMU's SeaBIOS. The firmware writes its variable store into this file, so it is a copy.                                                                                                                                                                                                                                                                                             |
| `-D qemu.log`                                                              | Where `-d` and `-trace` output goes.                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `-trace ...`                                                               | The launch events, listed below. Pattern arguments need quoting in a shell.                                                                                                                                                                                                                                                                                                                                                                                 |
| `-serial mon:stdio`                                                        | `tb-boot`'s console on the terminal, with the monitor on the same stream. The tests use `-serial tcp:127.0.0.1:<port>,server` and read it over a socket.                                                                                                                                                                                                                                                                                                    |

The swtpm side:

- `socket` serves QEMU over a socket rather than a character device.
- `--tpm2` makes it a TPM 2.0, which has the DRTM PCRs 17 to 22 and the
    locality 4 start that resets them.
- `--tpmstate dir=...` holds the NVRAM. The tests make a fresh one per boot,
    `tb-boot` reseeds the one under `run/` on every start.
- `--ctrl type=unixio,path=...` is the control socket. QEMU's `emulator`
    backend drives both the control and the data channel through it.
- Every start begins with a state holding only the SHA-1 and SHA-256
    banks, written by `swtpm_setup --tpm2 --pcr-banks sha1,sha256
    --overwrite`. swtpm's default activates every bank libtpms has, and
    the Linux launch then dies in the kernel's late PCR extend: the SKL
    log carries one digest per bank a discrete TPM ships with, and the
    kernel hands the TPM exactly those, which it refuses with more banks
    active. Overwriting is what keeps a state from before this seeding, or
    one swtpm wrote on its own, from coming back.

## Reading the traces

A control boot writes nothing to `qemu.log`. A launch writes about twenty
lines, this being the Xen EFI launch:

```text
x86_skinit cpu 0 slb 0x7e270000 entry 0x46 length 0x3440
amd_drtm_launch SLB base 0x7e270000 length 0x3440
amd_drtm_unblock_dma sl_dev found 0
amd_drtm_block_dma sl_dev base 0x7e270000 len 0x10000 enforced 1
amd_drtm_hash SLB base 0x7e270000 length 0x3440: ok
x86_vm_cr_write cpu 0 0x7 -> 0x3
amd_drtm_dma_blocked sl_dev addr 0x7e27e480 size 8 write 0
amd_drtm_dma_blocked sl_dev addr 0x7e27e488 size 8 write 0
amd_drtm_dma_blocked sl_dev addr 0x7e27b000 size 8 write 1
amd_drtm_dma_blocked sl_dev addr 0x7e27b008 size 8 write 1
amd_drtm_dma_blocked sl_dev addr 0x7e27e490 size 8 write 0
amd_drtm_dma_blocked sl_dev addr 0x7e27e498 size 8 write 0
amd_drtm_dma_blocked sl_dev addr 0x7e27b010 size 8 write 1
amd_drtm_dma_blocked sl_dev addr 0x7e27b018 size 8 write 1
amd_nb_memprot_write MEMPROT_CR 0x0 platform 1
amd_drtm_sl_dev_release launched 1 sl_dev 1
amd_drtm_unblock_dma sl_dev found 1
x86_vm_cr_write cpu 0 0x3 -> 0x1
x86_sipi_after_launch cpu 1 starts with GIF clear and VM_CR DPD, R_INIT and DIS_A20M set
x86_vm_cr_write cpu 1 0x7 -> 0x5
```

In the order they appear:

- `x86_skinit`: CPU 0 executed `SKINIT` with the SLB at `slb`. `entry` and
    `length` are the two words at the start of the SLB, the offset SKL is
    entered at and how many bytes get measured.
- `amd_drtm_launch`: the platform recorded the launch. `query-amd-drtm`
    reports `launched` true from here on, with this base and length.
- `amd_drtm_unblock_dma ... found 0`: a block is placed by first removing
    any older one of the same name. `found 0` on a first launch is normal.
- `amd_drtm_block_dma sl_dev ... len 0x10000 enforced 1`: the 64 KB SL_DEV
    window over the SLB. `enforced 1` means the IOMMU answers every device
    access to it with an error, as hardware does. `enforced 0` would mean no
    IOMMU on the machine and a block that is a record only.
- `amd_drtm_hash ...: ok`: the first `length` bytes of the SLB went to the
    TPM at locality 4, which reset PCRs 17 to 22 and extended 17. `failed`
    means the SLB was not readable memory, `unsupported` a TPM with no
    locality 4 path or none at all. PCR 17 then stays at all ones.
- `x86_vm_cr_write cpu 0 0x7 -> 0x3`: a write to the VM_CR MSR by CPU 0,
    shown as the value before the write, then the value after it. The
    bits are DPD (bit 0), R_INIT (bit 1), DIS_A20M (bit 2), LOCK (bit 3)
    and SVMDIS (bit 4). `SKINIT` set the first three, hence 0x7, and this
    write clears bit 2: SKL turns DIS_A20M off first thing. LOCK and
    SVMDIS are never touched on this path.
- `amd_drtm_dma_blocked sl_dev ...`: SKL programmed the IOMMU with its
    command buffer and event log inside the SLB, and the IOMMU's own fetches
    hit the block. Reads (`write 0`) are command fetches, writes (`write 1`)
    event log entries. On hardware SL_DEV fails these the same way, and
    SKL's IOMMU setup expects it: the failed first attempt is what makes it
    release SL_DEV and try again. Expected, not an error.
- `amd_nb_memprot_write MEMPROT_CR 0x0 platform 1`: SKL wrote the
    northbridge's MEMPROT_CR with MEMPROT_EN clear. `platform 1` says the
    platform object was there to be told. This is the SL_DEV release.
- `amd_drtm_sl_dev_release launched 1 sl_dev 1`: the release during an
    active launch. `launched 0` here breaks a rule, see below.
- `amd_drtm_unblock_dma sl_dev found 1`: the block came off, and
    `query-amd-drtm` reports `sl-dev` false and `dma-blocks` empty.
- `x86_vm_cr_write cpu 0 0x3 -> 0x1`: the kernel cleared R_INIT, bit 1,
    before starting the APs, leaving only DPD. INIT is a normal INIT again
    from here.
- `x86_sipi_after_launch cpu 1`: the AP's first SIPI after the launch, and
    it starts as the APM says, with GIF clear and the three VM_CR bits
    set.
- `x86_vm_cr_write cpu 1 0x7 -> 0x5`: the AP clears its own R_INIT, from
    all three bits set to DPD and DIS_A20M.

The MB2 launch reads the same apart from the addresses. The Linux launch
stops after the unblock, since the kernel panics before it clears R_INIT
or starts the AP. Two events are absent from a healthy boot of this image:

- `x86_init_held`: an INIT arrived while GIF was clear and is held until
    `STGI`.
- `x86_init_redirected`: an INIT arrived with R_INIT set and was taken as
    `#SX`.

## A broken rule

Every line below goes to the one log file `-D` names, or to stderr
without `-D`. A rule violation produces up to four of them there, from
two sources. The first two are the same text through two channels: the
plain line is the guest-error log, which `-d guest_errors` enables, and
the `amd_drtm_guest_error` line is the trace, which `-trace 'amd_drtm_*'`
enables, with the strict setting appended. Either option alone gives one
of the two. The last two come from QEMU's panic path and appear only with
strict mode on, and only through `-d guest_errors`:

```text
amd-drtm: SKINIT with no TPM to measure the SLB at 0x100000, PCR 17 stays unmeasured
amd_drtm_guest_error amd-drtm: SKINIT with no TPM to measure the SLB at 0x100000, PCR 17 stays unmeasured (strict 1)
Guest crashed
AMD dynamic launch rule broken: amd-drtm: SKINIT with no TPM to measure the SLB at 0x100000, PCR 17 stays unmeasured
```

With strict mode on the VM stops in the `guest-panicked` run state and a
`GUEST_PANICKED` QMP event carries the rule. What happens next is QEMU's
`-action panic=` setting. The default is `shutdown`, under which QEMU then
exits with status 0. The harness passes `pause`, so the stopped VM stays,
`query-status` answers `guest-panicked` and the boot fails with that
reason, and `query-amd-drtm` can still be asked what the launch looked
like.

The rules are:

- `SKINIT` with no TPM to measure the SLB.
- An SLB that is not readable memory.
- A TPM with no locality 4 path, that is a TIS frontend on a backend other
    than swtpm.
- An SLB whose entry offset lies outside its measured length.
- `SKINIT` while another CPU is not parked in wait-for-SIPI.
- `STGI` with R_INIT still set, after which an INIT would arrive as `#SX`.
- SL_DEV released with no launch active.

The rule texts cite the APM section they come from. Anything else under
`-d guest_errors`, such as a write to an unmapped address, is not a launch
rule and does not stop a strict VM.
