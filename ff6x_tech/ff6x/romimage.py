"""Guarded ROM image: every write is asserted, attributed and collision-checked."""
import hashlib, json, zlib
from .hirom import snes_to_pc, pc_to_snes, fmt_snes, ROM_SIZE_EXPANDED, ROM_SIZE_VANILLA


class BuildError(Exception):
    pass


def sha1(b): return hashlib.sha1(b).hexdigest()
def crc32(b): return f"{zlib.crc32(b) & 0xFFFFFFFF:08X}"
def md5(b): return hashlib.md5(b).hexdigest()


def load_clean_rom(path, baseline):
    """Read the master ROM read-only and fail closed on any identity mismatch."""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) == ROM_SIZE_VANILLA + 0x200:
        raise BuildError("Input has a 512-byte copier header. Use the clean UNHEADERED Rev 1 ROM.")
    errs = []
    if len(data) != baseline["size"]:
        errs.append(f"size {len(data):#x} != {baseline['size']:#x}")
    if sha1(data) != baseline["sha1"]:
        errs.append(f"SHA-1 {sha1(data)} != {baseline['sha1']}")
    if crc32(data) != baseline["crc32"]:
        errs.append(f"CRC32 {crc32(data)} != {baseline['crc32']}")
    if errs:
        raise BuildError("BASELINE HASH MISMATCH - ABORT (not clean FFIII USA Rev 1):\n  " + "\n  ".join(errs))
    h = baseline["header"]
    if data[0xFFD5] != int(h["map_mode"], 16) or data[0xFFD7] != int(h["rom_size"], 16) \
            or data[0xFFDB] != int(h["revision"], 16):
        raise BuildError("Header map-mode / size / revision mismatch")
    return bytes(data)


class RomImage:
    def __init__(self, clean: bytes, allocations, target: str):
        self.clean = clean                     # immutable master copy (3 MiB)
        self.buf = bytearray(clean)
        self.target = target
        self.alloc = allocations
        self.owner = {}                        # pc -> patch_id
        self.records = []                      # semantic patch log
        self.expanded = False
        self.placements = []                   # (region, pc_start, pc_end, label, patch_id)
        self.cursor = {}                       # region -> next free pc

    # ------------------------------------------------------------------ base
    def baseline_byte(self, pc):
        """Byte value of the (expanded) baseline: clean ROM, or 0xFF fill."""
        if pc < len(self.clean):
            return self.clean[pc]
        return 0xFF

    def expand(self, patch_id="P000_EXPAND_4MIB"):
        if self.expanded or len(self.buf) != ROM_SIZE_VANILLA:
            raise BuildError("expand() called twice or on wrong-size image")
        self.buf += b"\xFF" * (ROM_SIZE_EXPANDED - ROM_SIZE_VANILLA)
        self.expanded = True
        self.records.append({
            "patch_id": patch_id, "kind": "expand",
            "pc_start": f"{ROM_SIZE_VANILLA:06X}", "pc_end": f"{ROM_SIZE_EXPANDED - 1:06X}",
            "snes_start": fmt_snes(pc_to_snes(ROM_SIZE_VANILLA)), "snes_end": "FF:FFFF",
            "length": ROM_SIZE_EXPANDED - ROM_SIZE_VANILLA, "new": "FF fill",
            "reason": "Expand 3 MiB -> 4 MiB HiROM. Header ROM-size byte C0:FFD7 is already 0x0C (4 MiB class) in Rev 1; unchanged.",
            "consumer": "All F0-FF expansion allocations."})

    # ------------------------------------------------------------- ownership
    def _claim(self, pc, n, patch_id):
        for a in range(pc, pc + n):
            prev = self.owner.get(a)
            if prev is not None and prev != patch_id:
                raise BuildError(f"WRITE COLLISION at PC {a:06X} / {fmt_snes(pc_to_snes(a))}: "
                                 f"{patch_id} vs {prev}")
            self.owner[a] = patch_id

    def _check_permitted(self, pc, n, patch_id, vanilla_ok):
        end = pc + n - 1
        if end >= len(self.buf):
            raise BuildError(f"{patch_id}: write past end of image")
        if pc >= ROM_SIZE_VANILLA:
            if not self.alloc.covers(self.target, pc, end):
                raise BuildError(f"{patch_id}: expansion write {pc:06X}-{end:06X} not inside an "
                                 f"allocation active for target '{self.target}'")
        elif not vanilla_ok:
            raise BuildError(f"{patch_id}: unexpected vanilla-space write at {pc:06X}")

    # ------------------------------------------------------------- vanilla
    def patch(self, snes, expect: bytes, new: bytes, patch_id, consumer, reason, claim=None, table=None, retarget=False):
        """Patch vanilla space. `expect` is asserted against the CLEAN ROM and the
        current buffer. If `claim` names a vanilla_space_claim, the range must lie in it."""
        pc = snes_to_pc(snes)
        if len(expect) != len(new):
            raise BuildError(f"{patch_id}: expect/new length differ")
        if pc + len(new) > ROM_SIZE_VANILLA:
            raise BuildError(f"{patch_id}: patch() is for vanilla space; use place() for F0-FF")
        if bytes(self.clean[pc:pc + len(expect)]) != expect:
            raise BuildError(f"{patch_id}: ORIGINAL BYTE ASSERT FAILED at {fmt_snes(snes)} "
                             f"(PC {pc:06X}): found {self.clean[pc:pc+len(expect)].hex(' ').upper()} "
                             f"expected {expect.hex(' ').upper()}")
        if bytes(self.buf[pc:pc + len(expect)]) != expect:
            raise BuildError(f"{patch_id}: buffer already modified at {fmt_snes(snes)}")
        if claim is not None and not self.alloc.claim_covers(self.target, claim, pc, pc + len(new) - 1):
            raise BuildError(f"{patch_id}: write not inside vanilla claim {claim}")
        if table is not None and not self.alloc.table_covers(self.target, table, pc, pc + len(new) - 1):
            raise BuildError(f"{patch_id}: table repack {table} not declared for target {self.target} / range mismatch")
        if retarget and not self.alloc.retarget_ok(self.target, snes, len(new)):
            raise BuildError(f"{patch_id}: {fmt_snes(snes)} is not a declared consumer operand for target {self.target}")
        self._check_permitted(pc, len(new), patch_id, vanilla_ok=True)
        self._claim(pc, len(new), patch_id)
        self.buf[pc:pc + len(new)] = new
        self.records.append({
            "patch_id": patch_id, "kind": "vanilla_patch",
            "pc_start": f"{pc:06X}", "pc_end": f"{pc + len(new) - 1:06X}",
            "snes_start": fmt_snes(snes), "snes_end": fmt_snes(snes + len(new) - 1),
            "length": len(new),
            "expected_original": expect.hex(" ").upper() if len(new) <= 512 else f"<{len(new)} bytes, sha1 {sha1(expect)}>",
            "new": new.hex(" ").upper() if len(new) <= 512 else f"<{len(new)} bytes, sha1 {sha1(new)}>",
            "bytes_changed": sum(1 for a, b in zip(expect, new) if a != b),
            "consumer": consumer, "reason": reason, "vanilla_claim": claim, "table_repack": table,
            "operand_retarget": bool(retarget)})

    # ----------------------------------------------------------- expansion
    def place(self, region, data: bytes, label, patch_id, reason, consumer, align=1, at=None):
        """Allocate `data` inside a named expansion region. Returns SNES address.
        `at` (SNES) forces a fixed address (must lie in the region and be free)."""
        if not self.expanded:
            raise BuildError("place() before expand()")
        reg = self.alloc.region(region, self.target)
        if at is None:
            pc = self.cursor.get(region, reg["pc_start"])
            if pc % align:
                pc += align - pc % align
        else:
            pc = snes_to_pc(at)
        end = pc + len(data) - 1
        if pc < reg["pc_start"] or end > reg["pc_end"]:
            raise BuildError(f"{patch_id}: '{label}' ({len(data)} bytes) does not fit region {region}")
        if reg.get("no_bank_cross") and (pc >> 16) != (end >> 16):
            raise BuildError(f"{patch_id}: '{label}' crosses a bank in no_bank_cross region {region}")
        for p in self.placements:
            if not (end < p[1] or pc > p[2]):
                raise BuildError(f"ALLOCATION COLLISION: '{label}' {pc:06X}-{end:06X} overlaps "
                                 f"'{p[3]}' {p[1]:06X}-{p[2]:06X}")
        if any(self.buf[a] != 0xFF for a in range(pc, end + 1)):
            raise BuildError(f"{patch_id}: expansion bytes at {pc:06X} are not pristine 0xFF")
        self._check_permitted(pc, len(data), patch_id, vanilla_ok=False)
        self._claim(pc, len(data), patch_id)
        self.buf[pc:end + 1] = data
        self.placements.append((region, pc, end, label, patch_id))
        if at is None:
            self.cursor[region] = end + 1
        snes = pc_to_snes(pc)
        self.records.append({
            "patch_id": patch_id, "kind": "expansion_data", "region": region, "label": label,
            "pc_start": f"{pc:06X}", "pc_end": f"{end:06X}",
            "snes_start": fmt_snes(snes), "snes_end": fmt_snes(pc_to_snes(end)),
            "length": len(data), "expected_original": "FF fill (expansion)",
            "new": data.hex(" ").upper() if len(data) <= 512 else f"<{len(data)} bytes, sha1 {sha1(data)}>",
            "consumer": consumer, "reason": reason})
        return snes

    def write_into_placement(self, snes, data, patch_id):
        """Back-patch bytes inside a placement already owned by `patch_id` (label fixups)."""
        pc = snes_to_pc(snes)
        for a in range(pc, pc + len(data)):
            if self.owner.get(a) != patch_id:
                raise BuildError(f"{patch_id}: back-patch outside own placement at {a:06X}")
        self.buf[pc:pc + len(data)] = data

    def override(self, snes, expect: bytes, new: bytes, patch_id, owner_patch, consumer, reason):
        """Explicit, recorded override of bytes previously written by `owner_patch`
        (used only by the QA harness). Asserts current bytes and ownership."""
        pc = snes_to_pc(snes)
        for a in range(pc, pc + len(new)):
            if self.owner.get(a) != owner_patch:
                raise BuildError(f"{patch_id}: override target {a:06X} not owned by {owner_patch}")
        if bytes(self.buf[pc:pc + len(expect)]) != expect or len(expect) != len(new):
            raise BuildError(f"{patch_id}: override assert failed at {fmt_snes(snes)}: found "
                             f"{self.buf[pc:pc+len(expect)].hex(' ').upper()} expected {expect.hex(' ').upper()}")
        for a in range(pc, pc + len(new)):
            self.owner[a] = patch_id
        self.buf[pc:pc + len(new)] = new
        self.records.append({
            "patch_id": patch_id, "kind": "override", "overrides": owner_patch,
            "pc_start": f"{pc:06X}", "pc_end": f"{pc + len(new) - 1:06X}",
            "snes_start": fmt_snes(snes), "snes_end": fmt_snes(snes + len(new) - 1), "length": len(new),
            "expected_original": expect.hex(" ").upper(), "new": new.hex(" ").upper(),
            "consumer": consumer, "reason": reason})

    # ------------------------------------------------------------- checksum
    def fix_checksum(self):
        """SNES internal checksum for a power-of-two 4 MiB image: plain 16-bit sum
        with checksum=0000 / complement=FFFF during summation."""
        if len(self.buf) != ROM_SIZE_EXPANDED:
            raise BuildError("checksum: image must be 4 MiB")
        work = bytearray(self.buf)
        work[0xFFDC:0xFFE0] = b"\xFF\xFF\x00\x00"
        chk = sum(work) & 0xFFFF
        comp = chk ^ 0xFFFF
        new = comp.to_bytes(2, "little") + chk.to_bytes(2, "little")
        old = bytes(self.clean[0xFFDC:0xFFE0])
        for a in range(0xFFDC, 0xFFE0):
            self.owner[a] = "P999_CHECKSUM"
        self.buf[0xFFDC:0xFFE0] = new
        self.records.append({
            "patch_id": "P999_CHECKSUM", "kind": "checksum", "pc_start": "00FFDC", "pc_end": "00FFDF",
            "snes_start": "C0:FFDC", "snes_end": "C0:FFDF", "length": 4,
            "expected_original": old.hex(" ").upper(), "new": new.hex(" ").upper(),
            "consumer": "SNES header (emulator/flash-cart validation)",
            "reason": f"Recalculated checksum {chk:04X} / complement {comp:04X}"})
        return chk

    # -------------------------------------------------------------- verify
    def changed_ranges(self):
        """All byte ranges differing from the expanded baseline, with owner set."""
        out, start, owners = [], None, set()
        n = len(self.buf)
        for pc in range(n):
            diff = self.buf[pc] != self.baseline_byte(pc)
            if diff:
                if start is None:
                    start, owners = pc, set()
                own = self.owner.get(pc)
                if own is None:
                    raise BuildError(f"UNATTRIBUTED CHANGE at PC {pc:06X}")
                owners.add(own)
            if (not diff or pc == n - 1) and start is not None:
                end = pc - 1 if not diff else pc
                out.append((start, end, sorted(owners)))
                start = None
        return out
