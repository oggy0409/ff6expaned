"""TECH v0.4 relocatable per-map tables.

Vanilla layout (Rev 1): `ptr_count` 16-bit pointers followed by packed records.
Map m owns records [ptr[m], ptr[m+1]). Pointer values are relative to `rel_base`:
the pointer-table start for triggers/NPCs/entrances, the record-data start for
treasure (vanilla TreasurePropPtrs[0] == 0).

`RelocTable.parse()` reads the vanilla table from the CLEAN ROM; `serialize()`
emits a relocated copy with a new pointer count (513 = maps $000-$1FF + end
marker) using the same relative-pointer convention, so every vanilla consumer
keeps its exact logic and only the 24-bit operand changes.
"""
from .hirom import snes_to_pc


class RelocError(Exception):
    pass


class RelocTable:
    def __init__(self, name, record_size, maps, rel_to_data):
        self.name, self.size, self.rel_to_data = name, record_size, rel_to_data
        self.records = [[] for _ in range(maps)]
        self.inserted = []

    @classmethod
    def parse(cls, clean, name, ptr_snes, ptr_count, record_size, rel_to_data, end_snes, maps_out=512):
        base = snes_to_pc(ptr_snes)
        ptrs = [clean[base + 2 * i] | clean[base + 2 * i + 1] << 8 for i in range(ptr_count)]
        data_pc = base + 2 * ptr_count
        rel = data_pc if rel_to_data else base
        if rel_to_data and ptrs[0] != 0:
            raise RelocError(f"{name}: first pointer {ptrs[0]:#x} != 0 (data-relative table)")
        if not rel_to_data and ptrs[0] != 2 * ptr_count:
            raise RelocError(f"{name}: first pointer {ptrs[0]:#x} != {2 * ptr_count:#x}")
        if any(b < a for a, b in zip(ptrs, ptrs[1:])):
            raise RelocError(f"{name}: pointers not monotonic")
        t = cls(name, record_size, maps_out, rel_to_data)
        for m in range(ptr_count - 1):
            a, b = rel + ptrs[m], rel + ptrs[m + 1]
            if (b - a) % record_size:
                raise RelocError(f"{name}: map {m:03X} run not a multiple of {record_size}")
            if b - 1 > snes_to_pc(end_snes):
                raise RelocError(f"{name}: map {m:03X} run beyond table end")
            t.records[m] = [bytes(clean[k:k + record_size]) for k in range(a, b, record_size)]
        t.vanilla_maps = ptr_count - 1
        t.vanilla_count = sum(len(r) for r in t.records)
        return t

    def add(self, m, rec, label):
        if len(rec) != self.size:
            raise RelocError(f"{self.name}: record size {len(rec)} != {self.size}")
        if not 0 <= m < len(self.records):
            raise RelocError(f"{self.name}: map {m:03X} out of range")
        self.records[m].append(bytes(rec))
        self.inserted.append((m, label, bytes(rec)))

    def replace(self, m, index, rec, label):
        if len(rec) != self.size:
            raise RelocError(f"{self.name}: record size")
        self.records[m][index] = bytes(rec)
        self.inserted.append((m, label + " (replace)", bytes(rec)))

    def serialize(self, capacity):
        n = len(self.records) + 1                       # pointers incl. end marker
        hdr = 2 * n
        out = bytearray(hdr)
        data = bytearray()
        for m in range(n - 1):
            p = len(data) + (0 if self.rel_to_data else hdr)
            out[2 * m:2 * m + 2] = p.to_bytes(2, "little")
            for r in self.records[m]:
                data += r
        p = len(data) + (0 if self.rel_to_data else hdr)
        out[2 * (n - 1):2 * n] = p.to_bytes(2, "little")
        out += data
        if len(out) > capacity:
            raise RelocError(f"{self.name}: {len(out):#x} bytes exceed sub-region capacity {capacity:#x}")
        if hdr + len(data) > 0x10000 or p > 0xFFFF:
            raise RelocError(f"{self.name}: 16-bit relative pointer overflow")
        self.used = len(out)
        self.capacity = capacity
        self.count = sum(len(r) for r in self.records)
        return bytes(out)

    def capacity_records(self):
        n = len(self.records) + 1
        return (self.capacity - 2 * n) // self.size

    def runs_equal_vanilla(self, other_records):
        return all(self.records[m] == other_records[m] for m in range(len(other_records)))
