"""Minimal indexed-colour PNG reader/writer (no third-party dependency).

Supports what the project's asset sources use: colour type 3 (palette), bit depth 1/2/4/8,
no interlace. Writer emits 8-bit indexed PNGs (deterministic: fixed zlib level, no metadata).
"""
import struct, zlib


class PngError(ValueError):
    pass


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def read_indexed(path):
    """-> (width, height, rows[list[list[int]]], palette[list[(r,g,b)]])"""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PngError(f"{path}: not a PNG")
    pos, idat, plte, hdr = 8, b"", None, None
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if zlib.crc32(typ + body) & 0xFFFFFFFF != struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0]:
            raise PngError(f"{path}: CRC error in {typ}")
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE":
            plte = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + n
    w, h, depth, ctype, comp, filt, interlace = hdr
    if ctype != 3 or interlace != 0 or depth not in (1, 2, 4, 8):
        raise PngError(f"{path}: must be an indexed (palette) PNG, non-interlaced")
    raw = zlib.decompress(idat)
    stride = (w * depth + 7) // 8
    rows, prev, p = [], bytearray(stride), 0
    for y in range(h):
        ft = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        for i in range(stride):
            a = line[i - 1] if i else 0
            b = prev[i]; c = prev[i - 1] if i else 0
            if ft == 1: line[i] = (line[i] + a) & 0xFF
            elif ft == 2: line[i] = (line[i] + b) & 0xFF
            elif ft == 3: line[i] = (line[i] + ((a + b) >> 1)) & 0xFF
            elif ft == 4: line[i] = (line[i] + _paeth(a, b, c)) & 0xFF
            elif ft != 0: raise PngError("bad filter")
        prev = line
        px, per = [], 8 // depth
        for x in range(w):
            byte = line[x * depth // 8]
            shift = 8 - depth - (x % per) * depth if depth < 8 else 0
            px.append((byte >> shift) & ((1 << depth) - 1))
        rows.append(px)
    return w, h, rows, plte or []


def write_indexed(path, rows, palette):
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)
    pl = b"".join(bytes(c) for c in palette)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 3, 0, 0, 0)) + \
        chunk(b"PLTE", pl) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)


def write_rgb(path, rows):
    """rows: list of bytes/bytearray, 3 bytes per pixel (8-bit RGB, colour type 2). Deterministic."""
    h, w = len(rows), len(rows[0]) // 3
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + \
        chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)
