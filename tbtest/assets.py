# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The firmware and the image, pinned by URL and SHA-256 and kept under
`dl-cache/` beside this package, the image unpacked once.
"""

import gzip
import hashlib
import os
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "dl-cache"


@dataclass(frozen=True)
class Asset:
    """One download, stored under its SHA-256 as QEMU's asset cache does."""

    url: str
    sha256: str

    @property
    def path(self) -> Path:
        return CACHE_DIR / self.sha256

    def fetch(self) -> Path:
        """The cached file, downloaded and checked first if missing."""
        CACHE_DIR.mkdir(exist_ok=True)
        if self.path.exists():
            return self.path
        tmp = self.path.with_suffix(".tmp")
        urllib.request.urlretrieve(self.url, tmp)
        digest = hashlib.sha256()
        with open(tmp, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                digest.update(chunk)
        if digest.hexdigest() != self.sha256:
            tmp.unlink()
            raise RuntimeError(
                f"{self.url} hashed to {digest.hexdigest()}, not {self.sha256}"
            )
        tmp.rename(self.path)
        return self.path


# Dasharo's coreboot+UEFI build for QEMU Q35, the firmware Dasharo's own
# TrenchBoot tests run on. Pinned so runs are reproducible, bump on purpose.
FIRMWARE = Asset(
    url=(
        "https://github.com/Dasharo/coreboot/releases/download/"
        "qemu_q35_v0.2.1/qemu_q35_all_menus.rom"
    ),
    sha256="c6be232bc9884888b4b9dbe0fa85aa2a48042bdda456e3608c3f1d93e519d95d",
)

# The meta-trenchboot releases: GRUB with the TrenchBoot loader, SKL, Xen
# with slaunch and a Linux with slaunch, six GRUB entries between them.
# `DRTM_TB_RELEASE` picks one by tag, the default being the newest release
# that is not a release candidate.
_IMAGE_URL = (
    "https://github.com/zarhus/meta-trenchboot/releases/download/"
    "{tag}/tb-full-image-genericx86-64.rootfs.wic.gz"
)
RELEASES: dict[str, Asset] = {
    "v0.5.2": Asset(
        url=_IMAGE_URL.format(tag="v0.5.2"),
        sha256="702276d64f8aa9633a6aef1c88767716311d733a1dcbede2ed9e4d7a1cb380ca",
    ),
    "v0.5.3-rc1": Asset(
        url=_IMAGE_URL.format(tag="v0.5.3-rc1"),
        sha256="3ae50150714d1591aefb961ce88515ca9b3a07bea2e0f3c9fcb7fa37e129ff0e",
    ),
}
DEFAULT_RELEASE = "v0.5.2"


def release() -> str:
    """The tag of the image under test."""
    return os.environ.get("DRTM_TB_RELEASE", DEFAULT_RELEASE)


def image() -> Asset:
    tag = release()
    if tag not in RELEASES:
        known = ", ".join(RELEASES)
        raise RuntimeError(f"DRTM_TB_RELEASE={tag} is not pinned here, known: {known}")
    return RELEASES[tag]


def unpacked_image() -> Path:
    """The image as a raw disk, unpacked beside its download on first use.

    1.2 GB, so it lives in the cache rather than in a scratch directory
    per boot, and every boot opens it with `snapshot=on`.
    """
    asset = image()
    path = CACHE_DIR / f"{asset.sha256}.wic"
    if path.exists():
        return path
    tmp = path.with_suffix(".tmp")
    with gzip.open(asset.fetch(), "rb") as src, open(tmp, "wb") as dst:
        shutil.copyfileobj(src, dst, 1 << 20)
    tmp.rename(path)
    return path


def warmed_firmware_path() -> Path:
    """Where the once-booted copy of the firmware belongs.

    The firmware populates its variable store on an image that has never
    booted, which costs a few seconds. Keeping one booted copy per release
    pays that once. Producing it is `tests/conftest.py`'s job.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    return CACHE_DIR / f"{FIRMWARE.sha256}.warm"
