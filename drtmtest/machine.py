# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The AMD launch machine every boot of the image runs on, as QEMU options.
`docs/qemu.md` explains each one.
"""

import os
import shlex
from collections.abc import Sequence
from pathlib import Path

from drtmtest import qemu_vm

# A model with the SKINIT feature. Under `amd-drtm=on` the machine turns
# the feature on for any model, but Genoa is what the image was built for.
DEFAULT_CPU = "EPYC-Genoa"
DEFAULT_SMP = 2
DEFAULT_MEM = "2G"

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

# What the probe at session start asks for. Upstream refuses the option.
PROBE_OPTIONS = ["-machine", "q35,amd-drtm=on"]

# The Secure Processor with its DRTM service behind the mailbox, which the
# shorthand does not add. GRUB, SKL and Xen find it through the SMN pair
# on the host bridge and take the PSP-assisted launch path.
PSP_DEVICE = "amd-psp,drtm-service=on"


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


def unsupported_binary() -> str | None:
    """Why the QEMU in use cannot boot this image, or `None` if it can."""
    return qemu_vm.unsupported_binary(PROBE_OPTIONS)


def options(
    image: Path,
    cpu: str = DEFAULT_CPU,
    smp: int = DEFAULT_SMP,
    mem: str = DEFAULT_MEM,
    strict: bool = True,
    snapshot: bool = True,
    psp: bool = False,
    extra: Sequence[str] | None = None,
) -> list[str]:
    """The machine and the image, without the flash, the TPM or the console.

    `strict` makes the platform device stop the VM on a broken launch rule,
    so a wrong launch is a panic the harness sees rather than a line in
    the log. `psp` adds the Secure Processor with its DRTM service.
    `extra` comes last, what `extra_args()` reads from `DRTM_QEMU_ARGS`
    when `None`: a caller on a boot's thread passes what it read up front.
    """
    args = [
        "-machine",
        "q35,smm=on,amd-drtm=on",
        "-cpu",
        cpu,
        "-smp",
        str(smp),
        "-m",
        mem,
        "-global",
        f"amd-drtm-platform.strict={'on' if strict else 'off'}",
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
    for trace in LAUNCH_TRACES:
        args += ["-trace", trace]
    return args + (list(extra) if extra is not None else extra_args())
