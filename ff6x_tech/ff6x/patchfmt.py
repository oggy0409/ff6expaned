"""IPS and BPS writers + reference appliers (used for self-verification)."""
import zlib


# ----------------------------------------------------------------- IPS
def make_ips(src: bytes, dst: bytes) -> bytes:
    """IPS with RLE records for runs >= 8 equal bytes. Bytes beyond the source
    length (the 1 MiB expansion) are always emitted so patchers grow the file."""
    if len(dst) < len(src):
        raise ValueError("IPS cannot express truncation")
    out = bytearray(b"PATCH")
    n = len(dst)
    def differs(i):
        return i >= len(src) or src[i] != dst[i]
    def rec(off, data, rle):
        if off == 0x454F46 or off > 0xFFFFFF:
            raise ValueError("IPS offset invalid / collides with EOF marker")
        if rle:
            return off.to_bytes(3, "big") + b"\x00\x00" + len(data).to_bytes(2, "big") + data[:1]
        return off.to_bytes(3, "big") + len(data).to_bytes(2, "big") + data
    pc = 0
    while pc < n:
        if not differs(pc):
            pc += 1
            continue
        s = pc
        while pc < n and differs(pc):
            pc += 1
        i = s                       # split [s, pc) into RLE runs and literals
        lit = s
        while i < pc:
            j = i
            while j < pc and dst[j] == dst[i] and j - i < 0xFFFF:
                j += 1
            if j - i >= 8:
                while lit < i:
                    k = min(i, lit + 0xFFFF); out += rec(lit, dst[lit:k], False); lit = k
                out += rec(i, dst[i:j], True)
                lit = j
            i = j
        while lit < pc:
            k = min(pc, lit + 0xFFFF); out += rec(lit, dst[lit:k], False); lit = k
    out += b"EOF"
    return bytes(out)


def apply_ips(src: bytes, patch: bytes) -> bytes:
    assert patch[:5] == b"PATCH"
    buf = bytearray(src)
    i = 5
    while patch[i:i + 3] != b"EOF":
        off = int.from_bytes(patch[i:i + 3], "big"); i += 3
        size = int.from_bytes(patch[i:i + 2], "big"); i += 2
        if size == 0:
            cnt = int.from_bytes(patch[i:i + 2], "big"); val = patch[i + 2]; i += 3
            data = bytes([val]) * cnt
        else:
            data = patch[i:i + size]; i += size
        if off + len(data) > len(buf):
            buf += b"\x00" * (off + len(data) - len(buf))
        buf[off:off + len(data)] = data
    return bytes(buf)


# ----------------------------------------------------------------- BPS
def _vint(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def make_bps(src: bytes, dst: bytes, metadata: bytes = b"") -> bytes:
    out = bytearray(b"BPS1")
    out += _vint(len(src)) + _vint(len(dst)) + _vint(len(metadata)) + metadata
    pc, n = 0, len(dst)
    tgt_rel = 0          # targetRelativeOffset state
    def same(i):
        return i < len(src) and src[i] == dst[i]
    while pc < n:
        if same(pc):
            s = pc
            while pc < n and same(pc):
                pc += 1
            out += _vint(((pc - s) - 1) << 2 | 0)          # SourceRead
            continue
        s = pc
        while pc < n and not same(pc):
            pc += 1
        seg = dst[s:pc]
        # run-length via TargetCopy for long single-value runs
        i = 0
        while i < len(seg):
            j = i
            while j < len(seg) and seg[j] == seg[i]:
                j += 1
            run = j - i
            if run >= 16:
                out += _vint((1 - 1) << 2 | 1) + seg[i:i + 1]   # TargetRead 1 byte
                here = s + i                                    # absolute pos of literal
                rel = here - tgt_rel
                out += _vint(((run - 1) - 1) << 2 | 3)           # TargetCopy run-1
                out += _vint((abs(rel) << 1) | (1 if rel < 0 else 0))
                tgt_rel = here + (run - 1)
                i = j
            else:
                k = i
                while k < len(seg):
                    m = k
                    while m < len(seg) and seg[m] == seg[k]:
                        m += 1
                    if m - k >= 16:
                        break
                    k = m
                out += _vint(((k - i) - 1) << 2 | 1) + seg[i:k]  # TargetRead
                i = k
    out += zlib.crc32(src).to_bytes(4, "little") + zlib.crc32(dst).to_bytes(4, "little")
    out += zlib.crc32(bytes(out)).to_bytes(4, "little")
    return bytes(out)


def apply_bps(src: bytes, patch: bytes) -> bytes:
    assert patch[:4] == b"BPS1"
    i = 4
    def rd():
        nonlocal i
        data, shift = 0, 1
        while True:
            x = patch[i]; i += 1
            data += (x & 0x7F) * shift
            if x & 0x80:
                return data
            shift <<= 7
            data += shift
    ssz, tsz, msz = rd(), rd(), rd()
    i += msz
    if zlib.crc32(src) != int.from_bytes(patch[-12:-8], "little"):
        raise ValueError("BPS: source CRC mismatch (wrong input ROM)")
    if zlib.crc32(patch[:-4]) != int.from_bytes(patch[-4:], "little"):
        raise ValueError("BPS: patch CRC mismatch")
    out = bytearray()
    srel = trel = 0
    end = len(patch) - 12
    while i < end:
        d = rd(); cmd = d & 3; ln = (d >> 2) + 1
        if cmd == 0:
            out += src[len(out):len(out) + ln]
        elif cmd == 1:
            out += patch[i:i + ln]; i += ln
        elif cmd == 2:
            o = rd(); srel += (-1 if o & 1 else 1) * (o >> 1)
            out += src[srel:srel + ln]; srel += ln
        else:
            o = rd(); trel += (-1 if o & 1 else 1) * (o >> 1)
            for _ in range(ln):
                out.append(out[trel]); trel += 1
    if len(out) != tsz or zlib.crc32(out) != int.from_bytes(patch[-8:-4], "little"):
        raise ValueError("BPS: target mismatch")
    return bytes(out)
