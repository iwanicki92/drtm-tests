# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Drives the image's boot over the serial console: the firmware prompt, the
GRUB menu, the OS banner, the login and commands at the shell.
"""

import re
from dataclasses import dataclass

from tbtest.qemu_vm import QemuVm

# Dasharo's boot manager prompt. ENTER boots the default entry at once
# instead of after its own timeout.
BOOT_PROMPT = "ENTER to boot directly"

# GRUB prints this under the finished menu and boots the first entry a few
# seconds later unless a key arrives.
MENU_READY = "The highlighted entry will be executed automatically"

# The TrenchBoot loader's pause before handing over. It times out on its
# own, so answering it is for robustness rather than time.
ANY_KEY = "Press any key to continue"

XEN_BANNER = "(XEN) Xen version"
LINUX_BANNER = "Linux version"
LOGIN_PROMPT = "tb login:"
SHELL_PROMPT = "root@tb:~#"

# What ends a boot early. Xen's panic, Linux's, and the strict-mode stop
# QEMU reports through the run state rather than the console.
FAILURES = ("Panic on CPU", "Kernel panic")

KEY_DOWN = b"\x1b[B"

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[()][A-Z0-9]|\x1b[=>]")
# A menu entry as GRUB draws it: an optional highlight marker, the title,
# then the padding to the box's edge.
_TITLE_RE = re.compile(r"\*?(Boot [A-Za-z0-9 ()]+?)\s{2,}")
_PCR_RE = re.compile(r"(\d+)\s*: 0x([0-9A-Fa-f]{64})")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def menu_titles(menu: str) -> list[str]:
    """The entry titles in the order GRUB lists them, from one menu render."""
    titles: list[str] = []
    for title in _TITLE_RE.findall(strip_ansi(menu)):
        if title not in titles:
            titles.append(title)
    return titles


@dataclass
class Console:
    """The boot sequence over a `QemuVm`'s serial console.

    Each step waits with its own timeout. `boot_timeout` covers the long
    ones, the GRUB menu and the login prompt, under a loaded machine.
    """

    vm: QemuVm
    boot_timeout: float
    command_timeout: float = 60.0

    def select_entry(self, title: str) -> list[str]:
        """Answers the firmware, then picks `title` in GRUB's menu.

        The index comes from the titles the menu shows, so the image decides
        where an entry sits. Returns the titles for the record.
        """
        self.vm.expect(BOOT_PROMPT, self.boot_timeout)
        self.vm.send(b"\r")
        menu = self.vm.expect(MENU_READY, self.boot_timeout)
        titles = menu_titles(menu)
        if title not in titles:
            raise LookupError(f"no GRUB entry {title!r}, the menu lists {titles}")
        self.vm.send(KEY_DOWN * titles.index(title) + b"\r")
        return titles

    def wait_for_login(self, banner: str) -> None:
        """Waits for the OS banner and then the login prompt, answering the
        loader's pause on the way and stopping on a panic."""
        self.vm.expect(
            banner, self.boot_timeout, failures=FAILURES, answers={ANY_KEY: b"\r"}
        )
        self.vm.expect(LOGIN_PROMPT, self.boot_timeout, failures=FAILURES)

    def login(self) -> None:
        self.vm.send(b"root\r")
        self.vm.expect(SHELL_PROMPT, self.command_timeout)

    def run(self, command: str) -> str:
        """Runs one command at the shell and returns what it printed."""
        self.vm.send(command.encode() + b"\r")
        out = self.vm.expect(SHELL_PROMPT, self.command_timeout)
        # Drop the echoed command line and the prompt that ends the output.
        lines = strip_ansi(out).replace("\r", "").split("\n")
        return "\n".join(lines[1:-1]).strip()

    def pcr(self, index: int) -> str:
        """One SHA-256 PCR as 64 hex digits, lower case."""
        out = self.run(f"tpm2_pcrread sha256:{index}")
        for found, value in _PCR_RE.findall(out):
            if int(found) == index:
                return value.lower()
        raise LookupError(f"no PCR {index} in {out!r}")
