"""Packed per-map tables (event triggers, NPCs, short/long entrances) and the
NPC record codec.

Vanilla layout (Rev 1): a table of 16-bit pointers (relative to the pointer
table base) followed by packed records. Map m owns records
[ptr[m], ptr[m+1]). The last pointer is the end marker. Free space is the
run of $FF between the end marker and the next table ("slack").
Inserting records for map m = append to m's run, shift every later map's
records and add the inserted size to every later pointer. The repacked image
is written back over [ptr_base, data_end] with the whole original region
asserted first.
"""
from .hirom import snes_to_pc


class PackedTable:
    def __init__(self, clean: bytes, name, ptr_snes, data_end_snes, record_size, ptr_count):
        self.name, self.size, self.n = name, record_size, ptr_count
        self.base = snes_to_pc(ptr_snes)
        self.end = snes_to_pc(data_end_snes)            # inclusive
        self.orig = bytes(clean[self.base:self.end + 1])
        ptrs = [self.orig[2 * i] | self.orig[2 * i + 1] << 8 for i in range(ptr_count)]
        if ptrs[0] != 2 * ptr_count:
            raise ValueError(f"{name}: first pointer {ptrs[0]:#x} != table size {2*ptr_count:#x}")
        if any(b < a for a, b in zip(ptrs, ptrs[1:])):
            raise ValueError(f"{name}: pointers not monotonic")
        self.records = []
        for m in range(ptr_count - 1):
            run = self.orig[ptrs[m]:ptrs[m + 1]]
            if len(run) % record_size:
                raise ValueError(f"{name}: map {m:03X} run not a multiple of {record_size}")
            self.records.append([run[k:k + record_size] for k in range(0, len(run), record_size)])
        self.used_end = ptrs[-1]
        slack = self.orig[self.used_end:]
        if set(slack) - {0xFF}:
            raise ValueError(f"{name}: slack region is not pristine $FF")
        self.capacity = len(self.orig)
        self.slack = len(slack)
        self.inserted = []

    def count(self, m):
        return len(self.records[m])

    def add(self, m, rec: bytes, label):
        if len(rec) != self.size:
            raise ValueError(f"{self.name}: record size")
        self.records[m].append(bytes(rec))
        self.inserted.append((m, label, bytes(rec)))

    def serialize(self) -> bytes:
        out = bytearray(2 * self.n)
        data = bytearray()
        for m in range(self.n - 1):
            p = 2 * self.n + len(data)
            out[2 * m:2 * m + 2] = p.to_bytes(2, "little")
            for r in self.records[m]:
                data += r
        p = 2 * self.n + len(data)
        out[2 * (self.n - 1):2 * self.n] = p.to_bytes(2, "little")
        out += data
        if len(out) > self.capacity:
            raise ValueError(f"{self.name}: repacked size {len(out):#x} exceeds capacity {self.capacity:#x} "
                             f"(slack {self.slack} bytes)")
        out += b"\xFF" * (self.capacity - len(out))
        return bytes(out)

    def slack_after(self):
        return self.slack - self.size * len(self.inserted)


# ------------------------------------------------------------- NPC codec
def encode_npc(event_snes, switch, x, y, gfx, pal, direction=2, speed=2, movement=0,
               sprite_priority=0, layer_priority=0, react=0, scroll_bg2=False,
               anim=None, vehicle=0, show_rider=0):
    """Normal (non-special) NPC record, bit layout per npc_prop end_npc:
    b0-1 ptr lo16 | b2 ptr hi2, pal<<2, bg2 scroll $20, switch&3 <<6 | b3 switch>>2 |
    b4 x | show_rider | b5 y | speed<<6 | b6 gfx | b7 vehicle/anim speed, sprite prio, movement |
    b8 dir/anim type, react, layer, anim frame."""
    off = event_snes - 0xCA0000
    if not (0 <= off <= 0x3FFFF):
        raise ValueError("NPC event pointer must be in CA:0000-CD:FFFF (18-bit)")
    sw = switch - 0x300
    if not (0 <= sw <= 0x3FF):
        raise ValueError("NPC switch must be $300-$6FF")
    if not (0 <= x < 128 and 0 <= y < 64 and 0 <= pal < 8 and 0 <= speed < 4):
        raise ValueError("NPC field out of range")
    b = bytearray(9)
    b[0], b[1] = off & 0xFF, (off >> 8) & 0xFF
    b[2] = (off >> 16) | (pal << 2) | (0x20 if scroll_bg2 else 0) | ((sw & 3) << 6)
    b[3] = sw >> 2
    b[4] = x | (show_rider & 0x80)
    b[5] = y | (speed << 6)
    b[6] = gfx
    if anim:   # (anim_type, anim_frame_bits, anim_speed_bits)
        atype, aframe, aspeed = anim
        b[7] = aspeed | sprite_priority | movement
        b[8] = atype | react | layer_priority | aframe
    else:
        b[7] = ((vehicle << 1) & 0xC0) | sprite_priority | movement
        b[8] = direction | react | layer_priority
    return bytes(b)


def decode_npc(r: bytes):
    off = r[0] | r[1] << 8 | (r[2] & 3) << 16
    d = {"event": 0xCA0000 + off, "switch": 0x300 + ((r[2] >> 6) | (r[3] << 2)),
         "pal": (r[2] >> 2) & 7, "scroll_bg2": bool(r[2] & 0x20), "x": r[4] & 0x7F,
         "show_rider": r[4] & 0x80, "y": r[5] & 0x3F, "speed": r[5] >> 6, "gfx": r[6],
         "sprite_priority": r[7] & 0x30, "movement": r[7] & 0x0F,
         "react": r[8] & 0x04, "layer_priority": r[8] & 0x18}
    if r[8] & 0xE0:
        d["anim"] = (r[8] & 3, r[8] & 0xE0, r[7] & 0xC0)
    else:
        d["direction"] = r[8] & 3
        d["vehicle"] = (r[7] & 0xC0) >> 1
    return d
