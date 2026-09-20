# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The AMD launch machine every boot of the image runs on, as QEMU options.
`docs/qemu.md` explains each one.
"""

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
    "x86_skinit",
    "x86_vm_cr_write",
    "x86_sipi_after_launch",
    "x86_init_held",
    "x86_init_redirected",
)

# What the probe at session start asks for. Upstream refuses the option.
PROBE_OPTIONS = ["-machine", "q35,amd-drtm=on"]


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
) -> list[str]:
    """The machine and the image, without the flash, the TPM or the console.

    `strict` makes the platform device stop the VM on a broken launch rule,
    so a wrong launch is a panic the harness sees rather than a line in
    the log.
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
    for trace in LAUNCH_TRACES:
        args += ["-trace", trace]
    return args
