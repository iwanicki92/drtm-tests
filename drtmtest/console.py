# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Drives the image's boot over the serial console: the firmware prompt, the
GRUB menu, the OS banner, the login and commands at the shell.
"""

import re
from dataclasses import dataclass

from drtmtest.dasharo import BOOT_PROMPT
from drtmtest.qemu_vm import QemuVm

# GRUB prints this under the finished menu and boots the first entry a few
# seconds later unless a key arrives.
MENU_READY = "The highlighted entry will be executed automatically"

# The TrenchBoot loader's pause before handing over. It times out on its
# own, so answering it is for robustness rather than time.
ANY_KEY = "Press any key to continue"

# The hypervisor's first line, with or without the timestamp that
# `console_timestamps=` puts after the "(XEN) " prefix. dom0's own
# "Xen version:" line comes later and has a colon.
XEN_BANNER = "Xen version "
LINUX_BANNER = "Linux version"
LOGIN_PROMPT = "tb login:"
SHELL_PROMPT = "root@tb:~#"

# GRUB's own shell, entered from the menu with `c`.
GRUB_PROMPT = "grub> "

# What ends a boot early. Xen's panic, Linux's, and the strict-mode stop
# QEMU reports through the run state rather than the console.
FAILURES = ("Panic on CPU", "Kernel panic")

KEY_DOWN = b"\x1b[B"

# How long GRUB may take to draw the highlight after a key. A starved
# guest can read the key's escape sequence as three plain keys and move
# nothing, so a move that draws nothing is pressed once more.
KEY_TIMEOUT = 10.0

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[()][A-Z0-9]|\x1b[=>]")
# A hypervisor line, wherever it lands. Xen ends it with a newline, so
# the output around it closes up once it is gone.
_XEN_LINE_RE = re.compile(r"\(XEN\)[^\n]*")
# A menu entry as GRUB draws it: an optional highlight marker, the title,
# then the padding to the box's edge.
_TITLE_RE = re.compile(r"\*?(Boot [A-Za-z0-9 ()]+?)\s{2,}")
_PCR_RE = re.compile(r"(\d+)\s*: 0x([0-9A-Fa-f]+)")
# One bank in `tpm2_getcap pcrs`, with the PCRs it has, if any.
_BANK_RE = re.compile(r"^\s*-\s*(\w+)\s*:\s*\[([^\]]*)\]", re.MULTILINE)


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def hex_dump(out: str) -> bytes:
    """The bytes a hex dump printed at the shell spells. Xen writes to
    the serial port dom0 reads commands on, and a long dump is traffic
    enough for its uart watchdog to report itself into the middle of one,
    so a hypervisor line goes before the hex is decoded. Anything else
    that is not hex raises `ValueError`."""
    return bytes.fromhex(_XEN_LINE_RE.sub("", out))


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

    def _menu(self, boot_prompt: bool) -> list[str]:
        """Answers the firmware and waits for GRUB's menu, whose titles it
        returns. `boot_prompt` is Dasharo's, which SeaBIOS never shows."""
        if boot_prompt:
            self.vm.expect(BOOT_PROMPT, self.boot_timeout)
            self.vm.send(b"\r")
        menu = self.vm.expect(MENU_READY, self.boot_timeout)
        return menu_titles(menu)

    def select_entry(self, title: str, boot_prompt: bool = True) -> list[str]:
        """Answers the firmware, then picks `title` in GRUB's menu.

        The index comes from the titles the menu shows, so the image
        decides where an entry sits. Returns the titles for the record.
        """
        titles = self._menu(boot_prompt)
        if title not in titles:
            raise LookupError(f"no GRUB entry {title!r}, the menu lists {titles}")
        for step in range(titles.index(title)):
            self._move_down(titles[step + 1])
        self.vm.send(b"\r")
        return titles

    def _move_down(self, expected: str) -> None:
        """One Down, until GRUB draws the highlight on `expected`."""
        for _ in range(2):
            self.vm.send(KEY_DOWN)
            try:
                self.vm.expect("*" + expected, KEY_TIMEOUT)
                return
            except TimeoutError:
                continue
        raise RuntimeError(f"GRUB did not move the highlight to {expected!r}")

    def type_entry(self, commands: list[str], boot_prompt: bool = True) -> list[str]:
        """Answers the firmware, then runs `commands` at GRUB's shell in
        place of a menu entry and boots what they loaded. Returns the
        menu's titles, as `select_entry` does."""
        titles = self._menu(boot_prompt)
        self.vm.send(b"c")
        self.vm.expect(GRUB_PROMPT, self.command_timeout)
        # GRUB echoes every character between cursor moves, so the echo
        # is not matched, only the prompt that follows the command's run.
        for command in commands:
            self.vm.send(command.encode() + b"\r")
            self.vm.expect(GRUB_PROMPT, self.command_timeout)
        self.vm.send(b"boot\r")
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
        return self.pcrs([index])[index]

    def pcr_banks(self) -> list[str]:
        """The banks the TPM has PCRs in, in its order, as `tpm2_getcap
        pcrs` lists them. A bank the TPM knows but has no PCRs in is
        listed empty and left out."""
        out = self.run("tpm2_getcap pcrs")
        banks = [bank for bank, pcrs in _BANK_RE.findall(out) if pcrs.strip()]
        if not banks:
            raise LookupError(f"no PCR banks in {out!r}")
        return banks

    def pcrs(self, indices: list[int], bank: str = "sha256") -> dict[int, str]:
        """PCRs of `bank` by index, each as hex digits, lower case, from
        one read."""
        selection = ",".join(str(i) for i in indices)
        out = self.run(f"tpm2_pcrread {bank}:{selection}")
        found = {int(i): value.lower() for i, value in _PCR_RE.findall(out)}
        missing = [i for i in indices if i not in found]
        if missing:
            raise LookupError(f"no PCR {missing} in {out!r}")
        return {i: found[i] for i in indices}
