# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Downloads pinned by URL and SHA-256, kept under a cache directory the
suite names, stored under the hash as QEMU's asset cache does.
"""

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Asset:
    """One download, pinned so runs are reproducible. Bump on purpose."""

    url: str
    sha256: str

    def path(self, cache_dir: Path) -> Path:
        return cache_dir / self.sha256

    def fetch(self, cache_dir: Path) -> Path:
        """The cached file, downloaded and checked first if missing."""
        cache_dir.mkdir(exist_ok=True)
        path = self.path(cache_dir)
        if path.exists():
            return path
        tmp = path.with_suffix(".tmp")
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
        tmp.rename(path)
        return path
