# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The launch machine every boot of the image runs on, as QEMU options: AMD's
with `SKINIT` or Intel's with TXT, as `DRTM_VENDOR` picks. `docs/qemu.md`
explains each option.
"""

import os
import shlex
from collections.abc import Sequence
from pathlib import Path

from drtmtest import qemu_vm

VENDORS = ("amd", "intel")

# A model with the SKINIT feature. Under `amd-drtm=on` the machine turns
# the feature on for any model, but Genoa is what the image was built for.
DEFAULT_CPU = "EPYC-Genoa"
DEFAULT_SMP = 2
DEFAULT_MEM = "2G"

# A model with SMX, and MONITOR, which every TXT CPU has and Linux's AP
# wake after the launch executes.
INTEL_CPU = "Skylake-Client,+smx,+monitor"

# RAM above 4 GiB too: with none there GRUB asks for a high PMR at 0 with
# a nonzero size, which SENTER refuses. q35 keeps 2 GiB low and maps the
# rest above 4 GiB from 2.75 GiB up.
INTEL_MEM = "3G"

# VT-d, which TXT locks the DPR through and the OS turns the PMRs off
# with. Xen's dom0 loses interrupts under remapping without EIM.
INTEL_IOMMU = "intel-iommu,intremap=on,eim=on"

# What the launch devices log when asked to, into qemu.log.
LAUNCH_TRACES = (
    "amd_drtm_*",
    "amd_nb_*",
    "amd_psp_*",
    "x86_skinit",
    "x86_vm_cr_write",
    "x86_sipi_after_launch",
    "x86_init_held",
    "x86_init_redirected",
)

INTEL_TRACES = ("txt_*", "getsec_*")

# What the probe at session start asks for. Upstream refuses the options.
PROBE_OPTIONS = {
    "amd": ["-machine", "q35,amd-drtm=on"],
    "intel": ["-machine", "q35,txt-firmware=off"],
}

# The Secure Processor with its DRTM service behind the mailbox, which the
# shorthand does not add. GRUB, SKL and Xen find it through the SMN pair
# on the host bridge and take the PSP-assisted launch path.
PSP_DEVICE = "amd-psp,drtm-service=on"


def vendor() -> str:
    """What `DRTM_VENDOR` asks for: `amd`, the default, launches through
    `SKINIT`, `intel` through TXT's `GETSEC[SENTER]`."""
    value = os.environ.get("DRTM_VENDOR", "").strip().lower() or "amd"
    if value not in VENDORS:
        raise RuntimeError(f"DRTM_VENDOR={value!r} is not amd or intel")
    return value


def memory(vendor: str) -> str:
    """The guest memory a vendor's machine gets by default."""
    return INTEL_MEM if vendor == "intel" else DEFAULT_MEM


def psp_mode() -> str | None:
    """What `DRTM_PSP` asks for: `None` for no Secure Processor, `on` for
    the service under an image whose SKL uses it, `classic` for the
    service under an image with the classic SKL, whose launches are then
    expected to fail at the TPM behind the service's locality locks."""
    value = os.environ.get("DRTM_PSP", "").strip().lower()
    if value in ("", "off"):
        return None
    if value in ("on", "classic"):
        return value
    raise RuntimeError(f"DRTM_PSP={value!r} is not off, on or classic")


def extra_args() -> list[str]:
    """What `DRTM_QEMU_ARGS` adds to every boot, split like a shell would.
    QEMU takes the last of a repeated argument, so `-m 6G` here overrides
    the memory, and a `-machine` merges into the machine options."""
    return shlex.split(os.environ.get("DRTM_QEMU_ARGS", ""))


def unsupported_binary(vendor: str = "amd") -> str | None:
    """Why the QEMU in use cannot boot this image on a vendor's machine,
    or `None` if it can."""
    return qemu_vm.unsupported_binary(PROBE_OPTIONS[vendor])


def options(
    image: Path,
    cpu: str | None = None,
    smp: int = DEFAULT_SMP,
    mem: str | None = None,
    strict: bool = True,
    snapshot: bool = True,
    psp: bool = False,
    extra: Sequence[str] | None = None,
    vendor: str = "amd",
) -> list[str]:
    """The machine and the image, without the flash, the TPM or the console.

    `vendor` picks AMD's machine or Intel's, and with it the default `cpu`
    and `mem`. On AMD `strict` makes the platform device stop the VM on a
    broken launch rule, so a wrong launch is a panic the harness sees
    rather than a line in the log, and `psp` adds the Secure Processor
    with its DRTM service. `extra` comes last, what `extra_args()` reads
    from `DRTM_QEMU_ARGS` when `None`: a caller on a boot's thread passes
    what it read up front.
    """
    if vendor == "intel":
        if psp:
            raise ValueError("the PSP is AMD's, the Intel machine has none")
        args = [
            "-machine",
            "q35,smm=on,txt=on,txt-firmware=on",
            "-device",
            INTEL_IOMMU,
            "-cpu",
            cpu or INTEL_CPU,
        ]
        traces = INTEL_TRACES
    else:
        args = [
            "-machine",
            "q35,smm=on,amd-drtm=on",
            "-cpu",
            cpu or DEFAULT_CPU,
            "-global",
            f"amd-drtm-platform.strict={'on' if strict else 'off'}",
        ]
        traces = LAUNCH_TRACES
    args += [
        "-smp",
        str(smp),
        "-m",
        mem or memory(vendor),
        "-drive",
        f"file={image},format=raw,if=none,id=hd,snapshot={'on' if snapshot else 'off'}",
        "-device",
        "ide-hd,drive=hd",
        "-vga",
        "none",
        "-nic",
        "none",
        "-d",
        "guest_errors",
    ]
    if psp:
        args += ["-device", PSP_DEVICE]
    for trace in traces:
        args += ["-trace", trace]
    return args + (list(extra) if extra is not None else extra_args())
