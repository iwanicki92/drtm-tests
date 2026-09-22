# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The console driver's parsing, against text as GRUB draws it."""

from conftest import ENTRIES, Boot

from drtmtest.console import menu_titles

MENU = (
    "\x1b[05;03H*Boot Linux normally                    \x1b[0m"
    "\x1b[06;03H Boot Linux with TrenchBoot             "
    "\x1b[07;03H Boot Xen normally (MB2)                "
    "\x1b[5;3H*Boot Linux normally                     \x1b[m"
)


def test_titles_come_out_in_menu_order_once_each():
    assert menu_titles(MENU) == [
        "Boot Linux normally",
        "Boot Linux with TrenchBoot",
        "Boot Xen normally (MB2)",
    ]


# The fork's image lists the alt Linux launch as an entry of its own. The
# suite types that launch at GRUB's shell instead, on every image.
FORK_ENTRIES = {"Boot Linux with TrenchBoot (alt)"}


def test_the_image_lists_every_entry_this_suite_knows(xen_efi: Boot):
    """Every entry the suite relies on is in the menu, and nothing the
    suite does not know is."""
    titles = set(xen_efi.titles)
    known = {entry.title for entry in ENTRIES.values()}
    assert known <= titles, known - titles
    assert titles <= known | FORK_ENTRIES, titles - known
