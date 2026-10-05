"""FFVI field LZSS (C2:FF6D `Decompress`) - independent implementation.

Stream: u16 total_length (including these 2 bytes), then groups of
1 flag byte (LSB first; 1 = literal, 0 = back-reference) + 8 items.
Back-reference: 2 bytes, offset = b0 | (b1 & 0x07) << 8 into a 2 KiB ring
buffer (initial write position 0x7DE, zero-filled), length = (b1 >> 3) + 3
(matches reset.asm Decompress: `ora #>wDecompBuf` / `lsr3; adc #3`).
The encoder emits literals only: always valid, deterministic, trivially
reviewable (size = n + ceil(n/8) + 2).
"""

def decompress(src: bytes) -> bytes:
    total = src[0] | src[1] << 8
    ring = bytearray(0x800)
    rp = 0x7DE
    out = bytearray()
    i = 2
    while i < total:
        flags = src[i]; i += 1
        for bit in range(8):
            if i >= total:
                break
            if flags >> bit & 1:
                b = src[i]; i += 1
                out.append(b); ring[rp] = b; rp = (rp + 1) & 0x7FF
            else:
                b0, b1 = src[i], src[i + 1]; i += 2
                off = b0 | (b1 & 0x07) << 8
                for k in range((b1 >> 3) + 3):
                    b = ring[(off + k) & 0x7FF]
                    out.append(b); ring[rp] = b; rp = (rp + 1) & 0x7FF
    return bytes(out)


def compress_literal(data: bytes) -> bytes:
    body = bytearray()
    for g in range(0, len(data), 8):
        chunk = data[g:g + 8]
        body.append((1 << len(chunk)) - 1)
        body += chunk
    total = len(body) + 2
    if total > 0xFFFF:
        raise ValueError("LZSS stream too large")
    return bytes([total & 0xFF, total >> 8]) + bytes(body)
