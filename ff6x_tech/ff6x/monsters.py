"""TECH v0.5 monster / formation source compiler (monsters/<name>/, formations/<name>.json).

Each monster package separates: identity (monster.json), stats (stats.json), AI (ai.txt),
graphics resource (graphics.json), palette resource (palette.json), loot (loot.json),
Control (control.json) and Sketch (sketch.json), so graphics/palettes can be replaced later
without changing the monster ID.
"""
import json, os
from .hirom import snes_to_pc

MONSTER_PROP = 0xCF0000
MONSTER_GFX_PROP = 0xD27000
MONSTER_ITEMS = 0xCF3000
MONSTER_OVERLAP = 0xCF3600
MONSTER_SPECIAL_ANIM = 0xCF37C0
NEW_ID_MIN, NEW_ID_MAX, NULL_ID = 0x180, 0x1FE, 0x1FF
PALETTE_UNITS_VANILLA = 0x300          # MonsterPal D2:7820, 0x3000 bytes / 16

STAT_FIELDS = {   # name: (offset, size)   (Rev 1 LoadMonsterProp C2:2C30 / LoadRageProp C2:2DC1)
    "speed": (0, 1), "attack": (1, 1), "hit": (2, 1), "evade": (3, 1), "mblock": (4, 1),
    "defense": (5, 1), "mdefense": (6, 1), "magic_power": (7, 1), "hp": (8, 2), "mp": (10, 2),
    "exp": (12, 2), "gold": (14, 2), "level": (16, 1),
}
ATTACK_NAMES = {"BATTLE": 0xEE, "SPECIAL": 0xEF, "NONE": 0xFF}


class MonsterError(ValueError):
    pass


def encode_name(text, size=10):
    out = bytearray()
    for ch in text:
        if "A" <= ch <= "Z": out.append(0x80 + ord(ch) - 65)
        elif "a" <= ch <= "z": out.append(0x9A + ord(ch) - 97)
        elif "0" <= ch <= "9": out.append(0xB4 + ord(ch) - 48)
        elif ch == " ": out.append(0xFE)
        else: raise MonsterError(f"unencodable character {ch!r} in name {text!r}")
    if len(out) > size:
        raise MonsterError(f"name {text!r} longer than {size}")
    return bytes(out) + b"\xFF" * (size - len(out))


def attack_id(tok):
    tok = tok.strip()
    if tok.upper() in ATTACK_NAMES:
        return ATTACK_NAMES[tok.upper()]
    if tok.startswith("$"):
        return int(tok[1:], 16)
    raise MonsterError(f"bad attack token {tok!r}")


def compile_ai(text):
    """ai.txt: one command per line ('#' comments).
         random A B C   -> F0 A B C      use A -> A (A < $F0)
         wait           -> FD           end   -> FF (end of main / end of counter section)
       Exactly two 'end' (main + counter), like every vanilla script."""
    out, ends = bytearray(), 0
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        op, *args = line.split()
        if op == "random":
            if len(args) != 3: raise MonsterError("random needs 3 attacks")
            out += bytes([0xF0] + [attack_id(a) for a in args])
        elif op == "use":
            a = attack_id(args[0])
            if a >= 0xF0: raise MonsterError("use: attack id must be < $F0")
            out.append(a)
        elif op == "wait":
            out.append(0xFD)
        elif op == "end":
            out.append(0xFF); ends += 1
        else:
            raise MonsterError(f"unsupported AI command {op!r}")
    if ends != 2 or out[-1] != 0xFF:
        raise MonsterError("AI script must contain exactly 2 'end' (main section + counter section)")
    return bytes(out)


class MonsterSource:
    def __init__(self, folder):
        j = lambda n: json.load(open(os.path.join(folder, n)))
        self.folder = folder
        self.monster, self.stats, self.gfx = j("monster.json"), j("stats.json"), j("graphics.json")
        self.palette, self.loot = j("palette.json"), j("loot.json")
        self.control, self.sketch = j("control.json"), j("sketch.json")
        self.ai_text = open(os.path.join(folder, "ai.txt")).read()
        self.id = int(self.monster["id"], 16)
        if not NEW_ID_MIN <= self.id <= NEW_ID_MAX:
            raise MonsterError(f"{folder}: monster id {self.id:03X} outside new range $180-$1FE")

    def compile(self, clean):
        out = {}
        base = int(self.stats["base_vanilla_monster"], 16)
        if not 0 <= base < 0x180: raise MonsterError("base monster must be vanilla")
        p = snes_to_pc(MONSTER_PROP) + 32 * base
        rec = bytearray(clean[p:p + 32])
        for k, v in self.stats["fields"].items():
            off, n = STAT_FIELDS[k]
            if not 0 <= v < (1 << (8 * n)): raise MonsterError(f"stat {k} out of range")
            rec[off:off + n] = v.to_bytes(n, "little")
        out["prop"] = bytes(rec)
        out["name"] = encode_name(self.monster["name"])
        out["special_name"] = encode_name(self.monster["special_name"])
        sa = int(self.monster["special_anim_from_vanilla_monster"], 16)
        out["special_anim"] = bytes([clean[snes_to_pc(MONSTER_SPECIAL_ANIM) + sa]])
        if self.gfx.get("custom"):
            # TECH v0.6 custom graphics resource: gfx_prop is assigned by patches/enemy_v06.py
            out["gfx_prop"] = None
            out["overlap"] = bytes([int(self.gfx.get("overlap", 0)) & 0xFF])
        else:
            g = int(self.gfx["graphics_from_vanilla_monster"], 16)
            gp = snes_to_pc(MONSTER_GFX_PROP) + 5 * g
            grec = bytearray(clean[gp:gp + 5])
            pal = int(self.palette["palette_index"], 16)
            bpp3 = bool(grec[1] & 0x80)
            units = 1 if bpp3 else 2
            if pal < 0 or pal + units > PALETTE_UNITS_VANILLA:
                raise MonsterError("palette index outside the vanilla palette table")
            if self.palette.get("expect_bpp") and self.palette["expect_bpp"] != ("3bpp" if bpp3 else "4bpp"):
                raise MonsterError("palette bpp does not match graphics bpp")
            grec[2] = (grec[2] & 0xFC) | (pal >> 8)
            grec[3] = pal & 0xFF
            out["gfx_prop"] = bytes(grec)
            ov = int(self.gfx["overlap_from_vanilla_monster"], 16)
            out["overlap"] = bytes([clean[snes_to_pc(MONSTER_OVERLAP) + ov]])
        L = self.loot
        out["items"] = bytes(int(L[k], 16) for k in ("steal_rare", "steal_common", "drop_rare", "drop_common"))
        c = [attack_id(a) for a in self.control["attacks"]]
        s = [attack_id(a) for a in self.sketch["attacks"]]
        if len(c) != 4 or len(s) != 2: raise MonsterError("control needs 4, sketch needs 2 attacks")
        out["control"], out["sketch"] = bytes(c), bytes(s)
        out["ai"] = compile_ai(self.ai_text)
        return out


class FormationSource:
    """formations/<name>.json: 15-byte formation + 4-byte aux, built from a vanilla template.
    Optional "magic_points" (TECH v0.6, default 0) is consumed by patches/enemy_v06.py."""
    def __init__(self, path):
        self.path = path
        self.f = json.load(open(path))
        self.id = int(self.f["id"], 16)
        self.magic_points = int(self.f.get("magic_points", 0))
        if not 0 <= self.magic_points <= 0xFF:
            raise MonsterError(f"{path}: magic_points must be 0-255")

    def compile(self, clean, assigned_ids):
        t = int(self.f["template_vanilla_formation"], 16)
        rec = bytearray(clean[snes_to_pc(0xCF6200) + 15 * t: snes_to_pc(0xCF6200) + 15 * t + 15])
        aux = bytearray(clean[snes_to_pc(0xCF5900) + 4 * t: snes_to_pc(0xCF5900) + 4 * t + 4])
        present, msb = 0, 0
        lows = [0xFF] * 6
        pos = list(rec[8:14])
        for s in self.f["slots"]:
            k = s["slot"]
            mid = int(s["monster"], 16)
            if mid == NULL_ID or not (mid < 0x180 or mid in assigned_ids):
                raise MonsterError(f"{self.path}: slot {k} references unassigned/null monster {mid:03X}")
            present |= 1 << k
            lows[k] = mid & 0xFF
            if mid & 0x100: msb |= 1 << k
            if "pos" in s: pos[k] = int(s["pos"], 16)
        for k in range(6):
            if not present & (1 << k):
                lows[k] = 0xFF; msb |= 1 << k          # empty slot = $1FF (engine null)
        if "vram_map" in self.f:                        # TECH v0.6.2: explicit VRAM map (formation byte 0 bits 4-7)
            vm = self.f["vram_map"]
            if not isinstance(vm, int) or not 0 <= vm <= 12:
                raise MonsterError(f"{self.path}: vram_map must be an integer 0-12 (MonsterVRAMMapPtrs C2:D01A has 13 maps)")
            rec[0] = (rec[0] & 0x0F) | (vm << 4)
        rec[1] = (rec[1] & 0xC0) | present
        rec[2:8] = bytes(lows)
        rec[8:14] = bytes(pos)
        rec[14] = (rec[14] & 0xC0) | msb
        if any(int(s["monster"], 16) >= 0x100 for s in self.f["slots"]):
            if not self.f.get("no_veldt"):
                raise MonsterError(f"{self.path}: formations with monster IDs >= $100 must set no_veldt")
        if self.f.get("no_veldt"):
            aux[3] |= 0x02                              # $2F4B bit1: formation can't appear on the Veldt
        return bytes(rec), bytes(aux)
