# SPDX-FileCopyrightText: 2026 iwanicki92 <iwanicki92@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""The DRTM event log as the SKL writes it: a TCG2 log with the SHA-1 and
SHA-256 banks, one `TCG_PCR_EVENT2` per extend, and a replay of it.

Xen reserves the log where the SKL left it and dom0 reads it from
`/dev/mem`. Linux exposes it in securityfs. Either way the region is
larger than the events and zero after them.
"""

import hashlib
import struct
from dataclasses import dataclass

EV_NO_ACTION = 0x3
EV_SLAUNCH = 0x502

_SPEC_ID_SIGNATURE = b"Spec ID Event03\0"
_ALG_NAMES = {0x0004: "sha1", 0x000B: "sha256", 0x000C: "sha384", 0x000D: "sha512"}


@dataclass(frozen=True)
class Event:
    pcr: int
    type: int
    digests: dict[str, str]
    data: bytes


def _algorithms(raw: bytes) -> dict[int, int]:
    """The banks the header declares, algorithm id to digest size."""
    # The header event: PCR, type, a SHA-1 sized digest, the data size.
    if len(raw) < 32 or struct.unpack_from("<II", raw)[1] != EV_NO_ACTION:
        raise ValueError("no TCG2 header event at the start of the log")
    size = struct.unpack_from("<I", raw, 28)[0]
    spec = raw[32 : 32 + size]
    if not spec.startswith(_SPEC_ID_SIGNATURE):
        raise ValueError("the header event is not a Spec ID Event03")
    count = struct.unpack_from("<I", spec, 24)[0]
    algorithms = {}
    for i in range(count):
        alg, digest_size = struct.unpack_from("<HH", spec, 28 + 4 * i)
        algorithms[alg] = digest_size
    return algorithms


def parse(raw: bytes) -> list[Event]:
    """The events after the header, up to the zeros that end them. A dump
    that dropped trailing zero bytes reads as if they were there."""
    raw = raw + bytes(16)
    algorithms = _algorithms(raw)
    events: list[Event] = []
    offset = 32 + struct.unpack_from("<I", raw, 28)[0]
    while offset + 12 <= len(raw):
        pcr, type_, count = struct.unpack_from("<III", raw, offset)
        if count == 0:
            break
        offset += 12
        digests = {}
        for _ in range(count):
            alg = struct.unpack_from("<H", raw, offset)[0]
            size = algorithms[alg]
            digests[_ALG_NAMES.get(alg, hex(alg))] = raw[
                offset + 2 : offset + 2 + size
            ].hex()
            offset += 2 + size
        size = struct.unpack_from("<I", raw, offset)[0]
        data = raw[offset + 4 : offset + 4 + size]
        offset += 4 + size
        events.append(Event(pcr, type_, digests, data))
    return events


def replay(events: list[Event], pcr: int, alg: str = "sha256") -> str:
    """What `pcr` reads after the extends the log records, from the zero
    a locality 4 start leaves. EV_NO_ACTION events are logged, not
    extended."""
    value = bytes(hashlib.new(alg).digest_size)
    for event in events:
        if event.pcr == pcr and event.type != EV_NO_ACTION:
            value = hashlib.new(alg, value + bytes.fromhex(event.digests[alg])).digest()
    return value.hex()
