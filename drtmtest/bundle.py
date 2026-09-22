# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The QEMU `drtm` branch as CI runs it: a tarball of one build, released
on the QEMU fork by hand and pinned here like the images are. Unpacked
it is `qemu/bin/qemu-system-x86_64` beside `qemu/share/qemu/`, so the
binary finds its firmware blobs through its own relative data directory.
`python -m drtmtest.bundle` fetches it and prints the binary's path,
`python -m drtmtest.bundle pack <build dir>` makes a new one.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from drtmtest.assets import Asset
from drtmtest.trenchboot import CACHE_DIR

# Built on Ubuntu 24.04, whose glibc, glib and pixman the `ubuntu-24.04`
# runner image has. Bump the tag and the hash together, on purpose.
TAG = "drtm-11.1.1-1"
_URL = "https://github.com/iwanicki92/qemu/releases/download/{tag}/{name}"
_NAME = "qemu-{tag}-ubuntu-24.04.tar.gz"
BUNDLE = Asset(
    url=_URL.format(tag=TAG, name=_NAME.format(tag=TAG)),
    sha256="7ec8f23af945176907c733b17b9af1da267c48256e51af3abd339f07a04e5181",
)

BINARY = Path("qemu/bin/qemu-system-x86_64")
DATA = Path("qemu/share/qemu")


def binary(cache_dir: Path = CACHE_DIR) -> Path:
    """The bundle's QEMU, fetched and unpacked beside the images on first
    use, under the tarball's hash like the unpacked images."""
    root = cache_dir / f"{BUNDLE.sha256}-qemu"
    path = root / BINARY
    if path.exists():
        return path
    archive = BUNDLE.fetch(cache_dir)
    tmp = root.with_suffix(".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    with tarfile.open(archive) as tar:
        tar.extractall(tmp, filter="data")
    if not (tmp / BINARY).exists() or not (tmp / DATA).is_dir():
        raise RuntimeError(f"{BUNDLE.url} does not carry {BINARY} and {DATA}")
    tmp.rename(root)
    return path


def is_bundled(qemu: Path, cache_dir: Path = CACHE_DIR) -> bool:
    """Whether `qemu` is the pinned bundle's binary."""
    return qemu.resolve() == (cache_dir / f"{BUNDLE.sha256}-qemu" / BINARY).resolve()


def _version(qemu: Path) -> str:
    """The version the binary reports, `11.1.1` for instance."""
    out = subprocess.run([qemu, "--version"], capture_output=True, text=True)
    words = out.stdout.split()
    if out.returncode != 0 or "version" not in words:
        raise RuntimeError(f"{qemu} --version said {out.stdout!r} {out.stderr!r}")
    return words[words.index("version") + 1]


def pack(build: Path, out_dir: Path, tag: str | None = None) -> tuple[Path, str]:
    """The tarball of the build at `build`: its `qemu-system-x86_64`,
    stripped, and the data directory of the install tree meson lays out
    in the build as `qemu-bundle/`, symlinks followed. No meson call, so
    a build of named targets alone packs. Returns the archive and its
    SHA-256."""
    build = build.resolve()
    qemu = build / "qemu-system-x86_64"
    if not qemu.exists():
        raise RuntimeError(f"{build} has no qemu-system-x86_64")
    data = list((build / "qemu-bundle").rglob("share/qemu"))
    if len(data) != 1:
        raise RuntimeError(f"{build}/qemu-bundle has {len(data)} share/qemu trees")
    if tag is None:
        tag = f"drtm-{_version(qemu)}-1"
    with tempfile.TemporaryDirectory(prefix="qemu-bundle-") as tmp:
        tree = Path(tmp) / "qemu"
        (tree / BINARY.relative_to("qemu")).parent.mkdir(parents=True)
        shutil.copy2(qemu, tree / BINARY.relative_to("qemu"))
        subprocess.run(["strip", tree / BINARY.relative_to("qemu")], check=True)
        # The tree links to blobs the build did not make, other targets'
        # firmware, and those links are left out.
        shutil.copytree(
            data[0],
            tree / DATA.relative_to("qemu"),
            symlinks=False,
            ignore_dangling_symlinks=True,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        archive = out_dir / _NAME.format(tag=tag)
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(tree, arcname="qemu")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive, digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m drtmtest.bundle", description=__doc__
    )
    subparsers = parser.add_subparsers(dest="command")
    packer = subparsers.add_parser("pack", help="make a bundle from a build")
    packer.add_argument("build", type=Path, help="the QEMU build directory")
    packer.add_argument(
        "--tag", help="the release tag, drtm-<version>-1 by default"
    )
    packer.add_argument(
        "--out", type=Path, default=Path("dist"), help="where the tarball goes"
    )
    args = parser.parse_args(argv)
    if args.command == "pack":
        archive, digest = pack(args.build, args.out, args.tag)
        print(f"{archive}\n{digest}")
        return 0
    print(binary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
