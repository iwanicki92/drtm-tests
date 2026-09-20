# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The meta-trenchboot image under test: the pinned releases, which one
`DRTM_TB_RELEASE` picks, the raw disk unpacked once into `dl-cache/`, and
the local build `DRTM_TB_IMAGE` boots in place of a release.
"""

import gzip
import os
import shutil
from datetime import datetime
from pathlib import Path

from drtmtest.assets import Asset

CACHE_DIR = Path(__file__).resolve().parent.parent / "dl-cache"

# GRUB with the TrenchBoot loader, SKL, Xen with slaunch and a Linux with
# slaunch, six GRUB entries between them. The default is the newest release
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


def local_image() -> Path | None:
    """The raw disk `DRTM_TB_IMAGE` names, a build of one's own to boot in
    place of a release, or `None` when unset or empty."""
    value = os.environ.get("DRTM_TB_IMAGE")
    if not value:
        return None
    if os.environ.get("DRTM_TB_RELEASE"):
        raise RuntimeError("DRTM_TB_IMAGE and DRTM_TB_RELEASE are both set, unset one")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"DRTM_TB_IMAGE={value} is not a file")
    return path


def release() -> str | None:
    """The tag of the release under test, `None` for a local image."""
    if local_image() is not None:
        return None
    return os.environ.get("DRTM_TB_RELEASE", DEFAULT_RELEASE)


def description() -> str:
    """What a run booted, for its `results.txt`: the release tag, or the
    local image's path and modification time."""
    local = local_image()
    if local is None:
        return str(release())
    modified = datetime.fromtimestamp(local.stat().st_mtime).astimezone()
    return f"{local} (modified {modified.isoformat(timespec='seconds')})"


def image() -> Asset:
    tag = release()
    if tag is None:
        raise RuntimeError("DRTM_TB_IMAGE is set, there is no release to fetch")
    if tag not in RELEASES:
        known = ", ".join(RELEASES)
        raise RuntimeError(f"DRTM_TB_RELEASE={tag} is not pinned here, known: {known}")
    return RELEASES[tag]


def legacy_bootable() -> bool:
    """Whether the image boots under a BIOS: its master boot record carries
    GRUB's boot code, which names itself in its error strings. A wic built
    with the EFI plugin alone has a stub there that boots nothing."""
    with open(unpacked_image(), "rb") as f:
        return b"GRUB" in f.read(446)


def unpacked_image() -> Path:
    """The image as a raw disk, unpacked beside its download on first use.

    1.2 GB, so it lives in the cache rather than in a scratch directory
    per boot, and every boot opens it with `snapshot=on`. A local image is
    already raw and is used where it is.
    """
    local = local_image()
    if local is not None:
        return local
    asset = image()
    path = CACHE_DIR / f"{asset.sha256}.wic"
    if path.exists():
        return path
    tmp = path.with_suffix(".tmp")
    with gzip.open(asset.fetch(CACHE_DIR), "rb") as src, open(tmp, "wb") as dst:
        shutil.copyfileobj(src, dst, 1 << 20)
    tmp.rename(path)
    return path
