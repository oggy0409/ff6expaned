#!/usr/bin/env python3
"""Framework negative tests: every guard must FAIL CLOSED.
usage: selftest.py <clean_rev1.sfc>"""
import sys, os, json, copy, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from ff6x.romimage import load_clean_rom, RomImage, BuildError
from ff6x.allocations import Allocations, AllocationError
from ff6x import hirom
base = json.load(open(os.path.join(HERE, "data/baseline.json")))
clean = load_clean_rom(sys.argv[1], base)
ok = 0
def expect_fail(name, fn, exc=(BuildError, AllocationError, ValueError)):
    global ok
    try: fn()
    except exc as e: print(f"PASS {name}: rejected -> {str(e).splitlines()[0][:90]}"); ok += 1; return
    raise SystemExit(f"FAIL {name}: guard did not trigger")
# 1 hash guard
bad = bytearray(clean); bad[0x1234] ^= 1
p = tempfile.mktemp(); open(p, "wb").write(bad)
expect_fail("hash-mismatch", lambda: load_clean_rom(p, base))
hp = tempfile.mktemp(); open(hp, "wb").write(b"\0" * 512 + clean)
expect_fail("copier-header", lambda: load_clean_rom(hp, base))
# 2 overlapping allocations
raw = json.load(open(os.path.join(HERE, "data/allocations.json")))
r2 = copy.deepcopy(raw); r2["regions"].append({"name": "X", "snes_start": "F01800", "snes_end": "F018FF", "status": "active", "targets": ["evtest"], "purpose": "t"})
ap = tempfile.mktemp(); json.dump(r2, open(ap, "w"))
expect_fail("overlapping-allocation", lambda: Allocations(ap))
alloc = Allocations(os.path.join(HERE, "data/allocations.json"))
# 3 original-byte assert
def t3():
    r = RomImage(clean, alloc, "evtest"); r.expand()
    r.patch(0xC07FBF, bytes.fromhex("00 00 00 00"), b"\xEA" * 4, "T", "c", "r")
expect_fail("expected-byte-assert", t3)
# 4 write collision between two patches
def t4():
    r = RomImage(clean, alloc, "evtest"); r.expand()
    r.patch(0xC07FBF, bytes.fromhex("A9 CD 85 CB"), b"\xEA" * 4, "A", "c", "r")
    r.patch(0xC07FC1, bytes.fromhex("85 CB"), b"\xEA" * 2, "B", "c", "r")
expect_fail("write-collision", t4)
# 5 placement collision
def t5():
    r = RomImage(clean, alloc, "evtest"); r.expand()
    r.place("ENGINE_CODE", b"\x01" * 16, "a", "A", "r", "c", at=0xF01000)
    r.place("ENGINE_CODE", b"\x02" * 16, "b", "B", "r", "c", at=0xF01008)
expect_fail("placement-collision", t5)
# 6 write into reserved / blocked region
def t6():
    r = RomImage(clean, alloc, "evtest"); r.expand()
    r.place("ITEM_EXPANSION", b"\x01", "x", "X", "r", "c")
expect_fail("blocked-region", t6)
# 7 write outside a vanilla claim
def t7():
    r = RomImage(clean, alloc, "evtest"); r.expand()
    r.patch(0xCCE5F3, b"\xFF", b"\x00", "X", "c", "r", claim="EVTEST_NPC_TRAMPOLINE")
expect_fail("outside-vanilla-claim", t7)
# 8 non-canonical HiROM address
expect_fail("hirom-mirror", lambda: hirom.snes_to_pc(0x408000))
# 9 production targets must not contain EXPTEST or EVTEST content
import build
for t in ("production", "celes-tech"):
    _, out, _, _ = build.build_target(clean, alloc, t)
    assert bytes([0x84, 0x97, 0x8F, 0x93, 0x84, 0x92, 0x93]) not in out[0x300000:], t
    assert out[0x015F2B:0x015F2F] == bytes.fromhex("BF A0 CE D8"), t
    assert b"TECH v0.2" not in out and bytes.fromhex("33 24 22 27 7F 4F 54 65 56") not in out[0x330000:0x350000], t
print("PASS no-EXPTEST/EVTEST-in-production (production, celes-tech)"); ok += 1
# 10 map walkability validator rejects a leak and a border floor
import shutil
from ff6x.mapsrc import MapPackage, MapError
src = os.path.join(HERE, "maps", "celes_annex_tech")
tmp = tempfile.mkdtemp(); shutil.copytree(src, tmp + "/m")
rows = open(tmp + "/m/layout_bg1.txt").read().split("\n")
idx = [i for i, r in enumerate(rows) if r and not r.startswith("#")][5]       # y=5 row
rows[idx] = "f" + rows[idx][1:]                                                  # floor at x=0 (border)
open(tmp + "/m/layout_bg1.txt", "w").write("\n".join(rows))
expect_fail("map-border-floor", lambda: MapPackage(tmp + "/m").validate(clean), (MapError,))
shutil.copytree(src, tmp + "/n")
rows = open(tmp + "/n/layout_bg1.txt").read().split("\n")
idx = [i for i, r in enumerate(rows) if r and not r.startswith("#")][3]
rows[idx] = rows[idx][:9] + "." + rows[idx][10:]                                 # punch a hole in a wall row y=3 (void is impassable but makes no leak) ...
j = json.load(open(tmp + "/n/map.json")); j["legend"]["."]["tile"] = "01"      # ... and make void tile PASSABLE ($01)
json.dump(j, open(tmp + "/n/map.json", "w"))
open(tmp + "/n/layout_bg1.txt", "w").write("\n".join(rows))
expect_fail("map-passable-void-leak", lambda: MapPackage(tmp + "/n").validate(clean), (MapError,))
# 11 event bit that vanilla uses is refused
r3 = copy.deepcopy(raw); r3["event_bits"]["allocated"].append({"bit": "001", "name": "BAD", "kind": "event", "default": 0, "status": "x", "targets": ["celes-tech"]})
ap3 = tempfile.mktemp(); json.dump(r3, open(ap3, "w"))
audit = json.load(open(os.path.join(HERE, "audits/eventbit_audit.json")))
expect_fail("vanilla-used-event-bit", lambda: Allocations(ap3).event_bits("celes-tech", audit))
# 12 packed-table capacity overflow refused
from ff6x.tables import PackedTable
def t12():
    t = PackedTable(clean, "EVENT_TRIGGERS", 0xC40000, 0xC41A0F, 5, 417)
    for k in range(4): t.add(0x0C7, bytes(5), "x")
    t.serialize()
expect_fail("table-slack-overflow", t12)
# 13 dialogue line overflow refused
from patches import dialogue_hook
def t13():
    r = RomImage(clean, alloc, "celes-tech"); r.expand()
    dialogue_hook.build_dialogue_table(r, [("x", "This line is far too long for the window width")])
expect_fail("dialogue-width-overflow", t13)
# 14 TECH_TEST $0FF never reachable from production targets
assert "TECH_TEST" not in alloc.event_bits("celes-tech", audit) and "TECH_TEST" not in alloc.event_bits("production", audit)
print("PASS TECH_TEST $0FF not allocated to production/celes-tech"); ok += 1
# 15 QA harness isolation (TECH v0.3.1): QA_HARNESS never writable for production/celes-tech
for t in ("production", "celes-tech"):
    def t15(t=t):
        r = RomImage(clean, alloc, t); r.expand()
        r.place("QA_HARNESS", b"\x01", "x", "X", "r", "c")
    expect_fail(f"qa-region-not-active-for-{t}", t15)
# 16 no Q-patches / QA bytes in production builds; QA build contains them
for t in ("production", "celes-tech"):
    rom_, out, _, _ = build.build_target(clean, alloc, t)
    assert not any(r["patch_id"].startswith("Q") for r in rom_.records), t
    assert out[0x3F0000:0x400000] == b"\xFF" * 0x10000, t           # FF bank untouched
    assert b"\x33\x24\x22\x27\x7F\x4F\x54\x65\x57\x7F\x30\x20" not in out, t   # "TECH v0.3 QA"
rom_, out, _, _ = build.build_target(clean, alloc, "celes-qa-v0.3.1")
qids = sorted({r["patch_id"] for r in rom_.records if r["patch_id"].startswith("Q")})
assert qids == ["Q100_QA_DLG", "Q101_QA_DLG_COUNT", "Q200_QA_EVENT", "Q303_QA_BATTLE_GROUP",
                "Q305_REPACK_EVENT_TRIGGERS_QA", "Q305_REPACK_SHORT_ENTRANCES_QA"], qids
print("PASS QA patches only in celes-qa-v0.3.1; production/celes-tech have no Q-patch and pristine FF bank"); ok += 1
# 17 project scripts may not write a vanilla read-only bit
from ff6x.eventasm import EventProgram, EventAsmError
def t17():
    EventProgram(0xFF0000, {}, {}, readonly_bits=alloc.vanilla_ref_bits("celes-qa-v0.3.1")).parse("set_switch VANILLA_TILE_EVENT_LATCH")
expect_fail("write-vanilla-readonly-bit", t17, (EventAsmError,))
# 18 override of bytes not owned by the named patch is refused
def t18():
    r = RomImage(clean, alloc, "celes-tech"); r.expand()
    r.place("ENGINE_CODE", b"\x01\x02", "a", "A", "r", "c", at=0xF01000)
    r.override(0xF01000, b"\x01\x02", b"\x03\x04", "Q", "B", "c", "r")
expect_fail("override-wrong-owner", t18)
# ---------------- TECH v0.4 map foundation guards ----------------
from ff6x.maptables import RelocTable
from patches import map_foundation as MF
# 19 a vanilla patch flagged as operand retarget outside the audited consumer list is refused
def t19():
    r = RomImage(clean, alloc, "production"); r.expand()
    r.patch(0xC0BCB1, clean[0xBCB1:0xBCB4], b"\x00\x00\xF6", "X", "c", "r", retarget=True)   # not an audited instruction
expect_fail("retarget-undeclared-consumer", t19)
# 20 retarget not allowed for a v0.3 target (manifest scope)
def t20():
    r = RomImage(clean, alloc, "celes-tech-v0.3.0"); r.expand()
    r.patch(0xC0BCAF, bytes.fromhex("02 00 C4"), bytes.fromhex("02 00 F6"), "X", "c", "r", retarget=True)
expect_fail("retarget-wrong-target", t20)
# 21 static equivalence: relocated tables in the v0.4 production ROM decode to the vanilla records
rom_p, outp, _, _ = build.build_target(clean, alloc, "production-v0.4.0")
van = MF.vanilla_tables(clean)
for name, region, pid, rel in MF.PACKED:
    reg = alloc.region(region, "production-v0.4.0")
    t = RelocTable.parse(outp, name, 0xC00000 + reg["pc_start"], 513, van[name].size, rel,
                         0xC00000 + reg["pc_end"], 512)
    assert t.records == van[name].records, name
mp = MF.RELOC["tables"]["MAP_PROPS"]
a = alloc.region("MAPX_MAP_PROPS", "production-v0.4.0")["pc_start"]
assert outp[a:a + 415 * 33] == clean[0x2D8F00:0x2D8F00 + 415 * 33] and outp[a + 415 * 33:a + 512 * 33] == bytes(97 * 33)
a = alloc.region("MAPX_SUBTILEMAP_PTRS", "production-v0.4.0")["pc_start"]
assert outp[a:a + 3 * 0x15F] == clean[0x19CD90:0x19CD90 + 3 * 0x15F]
print("PASS relocated tables == vanilla records for all maps (5 packed tables, 415 prop rows, 351 layout ptrs)"); ok += 1
# 22 every audited consumer now points into its relocated table; no other vanilla code byte changed
changed = [i for i in range(0x300000) if outp[i] != clean[i]]
allowed = set()
for name, t in MF.RELOC["tables"].items():
    for c in t["consumers"]:
        a0 = int(c["snes"], 16) - 0xC00000
        allowed |= {a0 + 1, a0 + 2, a0 + 3}
allowed |= set(range(0x007FBF, 0x007FC3)) | set(range(0x0052E6, 0x0052EB)) | set(range(0xFFDC, 0xFFE0))
extra = [hex(i) for i in changed if i not in allowed]
assert not extra, extra[:10]
print(f"PASS v0.4 production vanilla-space diff limited to {len(changed)} declared bytes (90 operands + hook + router site + checksum)"); ok += 1
# 23 QA parts (Q4xx, QA_HARNESS) only in map-tech
for t in ("production-v0.4.0", "celes-tech-v0.4.0"):
    r_, o_, _, _ = build.build_target(clean, alloc, t)
    assert not any(x["patch_id"].startswith("Q") for x in r_.records), t
    assert o_[0x3F0000:0x400000] == b"\xFF" * 0x10000, t
r_, o_, _, _ = build.build_target(clean, alloc, "map-tech-v0.4.0")
q = sorted({x["patch_id"] for x in r_.records if x["patch_id"].startswith("Q")})
assert q == ["Q400_QA_EVENT", "Q401_QA_DLG", "Q403_QA_BATTLE_GROUP"], q
print("PASS QA harness patches only in map-tech; production/celes-tech FF bank pristine"); ok += 1
# 24 celes-tech v0.4 uses no CA-CD bridge bytes and no vanilla table repack
r_, o_, _, _ = build.build_target(clean, alloc, "celes-tech-v0.4.0")
assert o_[0x0CE5EE:0x0CE600] == clean[0x0CE5EE:0x0CE600] and o_[0x19D1AD:0x19D1B0] == clean[0x19D1AD:0x19D1B0]
assert o_[0x040000:0x046AC0] == clean[0x040000:0x046AC0] and o_[0x2DA8A7:0x2DA8C8] == clean[0x2DA8A7:0x2DA8C8]
print("PASS celes-tech v0.4: no CA-CD bridges, no vanilla table/props/layout-slot writes"); ok += 1
# 25 compose-map leak is refused (BG1 fill reachable)
from ff6x.mapsrc4 import MapPackageV4
tmp2 = tempfile.mkdtemp(); shutil.copytree(os.path.join(HERE, "maps", "map_tech_b"), tmp2 + "/b")
j = json.load(open(tmp2 + "/b/map.json")); j["bg1"]["compose"]["overrides"] = [[13, 20, "E0"], [13, 21, "E0"]]
j["bg1"]["compose"]["blits"][0]["src"] = [22, 3, 12, 12]
json.dump(j, open(tmp2 + "/b/map.json", "w"))
e = json.load(open(tmp2 + "/b/exits.json")); e["short_entrances"] = []; json.dump(e, open(tmp2 + "/b/exits.json", "w"))
expect_fail("compose-map-leak", lambda: MapPackageV4(tmp2 + "/b").validate(clean), (MapError,))
# ---------------- TECH v0.5 monster expansion guards ----------------
from patches import monster_v05 as MV
from ff6x.monsters import MonsterSource, FormationSource, MonsterError, compile_ai, encode_name
# 26 static equivalence: every vanilla monster / formation record in the relocated tables is byte-identical
rom5, out5, _, _ = build.build_target(clean, alloc, "production-v0.5.0")
def table_at(out, name):
    reg = alloc.region(MV.TABLE_REGION[name], "production-v0.5.0")
    return out[reg["pc_start"]:reg["pc_end"] + 1]
for name in MV.CONTENT_KEY:
    t = MV.RELOC["tables"][name]; rs, n = t["record_size"], t["vanilla_count"]
    tb = table_at(out5, name)
    assert tb[:rs * n] == MV.vanilla_blob(clean, name)[:rs * n], name
    assert tb[rs * n:rs * MV.IDS] == MV.DEFAULT[name] * (MV.IDS - n), name + " new ids not null in production"
van_g = MV.vanilla_blob(clean, "MONSTER_GFX_PROP")
assert table_at(out5, "MONSTER_GFX_PROP")[:len(van_g)] == van_g
van_ai = MV.vanilla_blob(clean, "AI_SCRIPT"); van_aip = MV.vanilla_blob(clean, "AI_SCRIPT_PTRS")
assert table_at(out5, "AI_SCRIPT")[:len(van_ai)] == van_ai and table_at(out5, "AI_SCRIPT_PTRS")[:768] == van_aip
assert table_at(out5, "FORMATION_PROP")[:4 * 576] == MV.vanilla_blob(clean, "FORMATION_PROP")[:4 * 576]
assert table_at(out5, "FORMATION_MONSTERS")[:15 * 576] == MV.vanilla_blob(clean, "FORMATION_MONSTERS")[:15 * 576]
assert table_at(out5, "FORMATION_MONSTERS")[15 * 576:15 * 1024] == bytes(15 * 448)
print("PASS v0.5 relocated monster/formation tables: 384 monsters, 416 gfx slots, 384 AI scripts, 576 formations "
      "byte-identical; production new IDs/formations null"); ok += 1
# 27 v0.5 production vanilla-space diff = v0.4 declared bytes + 71 monster operands + 3 hook sites + checksum
changed5 = [i for i in range(0x300000) if out5[i] != clean[i]]
allowed5 = set(allowed)
for name, t in MV.RELOC["tables"].items():
    for c in t["consumers"]:
        a0 = int(c["snes"], 16) - 0xC00000
        allowed5 |= {a0 + 1, a0 + 2, a0 + 3}
for site, exp in (MV.HOOK1, MV.HOOK2, MV.COLO_SITE):
    allowed5 |= set(range(site - 0xC00000, site - 0xC00000 + len(exp)))
extra5 = [hex(i) for i in changed5 if i not in allowed5]
assert not extra5, extra5[:10]
for snes, exp in MV.RAGE_GUARDS:
    assert out5[snes - 0xC00000:snes - 0xC00000 + len(exp)] == exp
print(f"PASS v0.5 production vanilla-space diff limited to {len(changed5)} declared bytes; Rage/Veldt guards untouched"); ok += 1
# 28 QA monster content (Q5xx, monsters $180/$181, formation $240) only in monster-tech
for t in ("production-v0.5.0", "celes-tech-v0.5.0"):
    r_, o_, _, _ = build.build_target(clean, alloc, t)
    assert not any(x["patch_id"].startswith("Q") for x in r_.records), t
    assert o_[0x3F0000:0x400000] == b"\xFF" * 0x10000, t
    assert o_[0x0F53F8:0x0F53FC] == clean[0x0F53F8:0x0F53FC], t
r_, o_, _, _ = build.build_target(clean, alloc, "monster-tech-v0.5.0")
q = sorted({x["patch_id"] for x in r_.records if x["patch_id"].startswith("Q")})
assert q == ["Q500_QA_EVENT", "Q501_QA_EVENT_BATTLE_GROUP", "Q502_QA_DLG", "Q503_QA_ANNEX_BATTLE_GROUP"], q
reg = alloc.region("MONX_PROP", "monster-tech-v0.5.0")
assert o_[reg["pc_start"] + 32 * 0x180:reg["pc_start"] + 32 * 0x182] != bytes(64)
print("PASS QA monsters/formation/event group only in monster-tech; production/celes-tech null + pristine FF bank"); ok += 1
# 29 monster / formation source guards fail closed
tmp5 = tempfile.mkdtemp(); shutil.copytree(os.path.join(HERE, "monsters", "tech_0180"), tmp5 + "/m")
def with_json(fn, key, val):
    j = json.load(open(tmp5 + "/m/" + fn)); old = copy.deepcopy(j); j[key] = val
    json.dump(j, open(tmp5 + "/m/" + fn, "w"))
    try: MonsterSource(tmp5 + "/m").compile(clean)
    finally: json.dump(old, open(tmp5 + "/m/" + fn, "w"))
expect_fail("monster-id-in-vanilla-range", lambda: with_json("monster.json", "id", "0x17F"), (MonsterError,))
expect_fail("monster-id-null-1FF", lambda: with_json("monster.json", "id", "0x1FF"), (MonsterError,))
expect_fail("monster-name-too-long", lambda: with_json("monster.json", "name", "TESTMOB AAAA"), (MonsterError,))
expect_fail("palette-outside-table", lambda: with_json("palette.json", "palette_index", "0x2FF"), (MonsterError,))
expect_fail("palette-bpp-mismatch", lambda: with_json("palette.json", "expect_bpp", "3bpp"), (MonsterError,))
expect_fail("ai-missing-counter-end", lambda: compile_ai("random BATTLE BATTLE $1B\nend"), (MonsterError,))
fj = json.load(open(os.path.join(HERE, "formations", "tech_0240.json")))
def bad_form(mod):
    j = copy.deepcopy(fj); mod(j); p = tempfile.mktemp(suffix=".json"); json.dump(j, open(p, "w"))
    return FormationSource(p).compile(clean, {0x180, 0x181})
expect_fail("formation-without-no-veldt", lambda: bad_form(lambda j: j.pop("no_veldt")), (MonsterError,))
expect_fail("formation-unassigned-monster", lambda: bad_form(lambda j: j["slots"][0].update(monster="0x182")), (MonsterError,))
# 30 retargeting a monster-table operand at an undeclared instruction is refused
def t30():
    r = RomImage(clean, alloc, "production-v0.5.0"); r.expand()
    r.patch(0xC22C31, clean[0x022C31:0x022C34], b"\x00\x00\xF8", "X", "c", "r", retarget=True)
expect_fail("retarget-undeclared-monster-consumer", t30)
# ---------------- TECH v0.6 enemy asset + magic point guards ----------------
from patches import enemy_v06 as EV
from ff6x.enemygfx import EnemyAsset, AssetError
from ff6x.png import write_indexed, read_indexed
# 31 static equivalence of the relocated palette / stencil / magic-point tables; production has no custom assets
rom6, out6, _, _ = build.build_target(clean, alloc, "production-v0.6.0")
R6 = lambda n: alloc.region(n, "production-v0.6.0")
pal = out6[R6("ENEMYX_PAL")["pc_start"]:R6("ENEMYX_PAL")["pc_end"] + 1]
assert pal[:0x3000] == clean[0x127820:0x12A820] and pal[0x3000:] == bytes(0x1000)
assert out6[R6("ENEMYX_PAL_EMPTY_SLOT")["pc_start"]:R6("ENEMYX_PAL_EMPTY_SLOT")["pc_start"] + 16] == clean[0x137810:0x137820]
st = out6[R6("ENEMYX_STENCIL")["pc_start"]:R6("ENEMYX_STENCIL")["pc_end"] + 1]
assert st[:4] == bytes.fromhex("04 40 04 48") and st[4:0x404] == clean[0x12A824:0x12AC24] and st[0x804:0x804 + 48 * 32] == clean[0x12AC24:0x12B224]
mp = out6[R6("FORMX_MAGIC_POINTS")["pc_start"]:R6("FORMX_MAGIC_POINTS")["pc_end"] + 1]
assert mp[:512] == clean[0x1FB400:0x1FB600] and mp[512:] == bytes(512)
assert out6[R6("ENEMYX_GFX")["pc_start"]:R6("ENEMYX_GFX")["pc_end"] + 1] == b"\xFF" * 0x20000
assert all(clean[0x127000 + 5 * i + 2] & 0x7C == 0 for i in range(416))       # vanilla never sets byte2 bits 2-6
print("PASS v0.6 relocated MonsterPal (768 units + empty-slot shadow), MonsterStencil (128 small + 48 large), MP (512 + zero $200-$3FF) identical; no custom assets in production"); ok += 1
# 32 v0.6 production vanilla-space diff = v0.5 declared set + 15 enemy operands + 2 hook sites + checksum
changed6 = [i for i in range(0x300000) if out6[i] != clean[i]]
allowed6 = set(allowed5)
for name, t in EV.RELOC["tables"].items():
    for c in t["consumers"]:
        a0 = int(c["snes"], 16) - 0xC00000
        allowed6 |= {a0 + 1, a0 + 2, a0 + 3}
allowed6 |= set(range(0x0120FF, 0x012104)) | {0x025D98, 0x025D99}
extra6 = [hex(i) for i in changed6 if i not in allowed6]
assert not extra6, extra6[:10]
print(f"PASS v0.6 production vanilla-space diff limited to {len(changed6)} declared bytes"); ok += 1
# 33 QA content (Q6xx, custom assets, QA formations/groups) only in monster-tech
for t in ("production-v0.6.0", "celes-tech-v0.6.0"):
    r_, o_, _, _ = build.build_target(clean, alloc, t)
    assert not any(x["patch_id"].startswith("Q") for x in r_.records), t
    assert o_[0x3F0000:0x400000] == b"\xFF" * 0x10000, t
    assert o_[0x0F53EC:0x0F53FC] == clean[0x0F53EC:0x0F53FC], t
r_, o_, _, n_ = build.build_target(clean, alloc, "monster-tech-v0.6.1")
q = sorted({x["patch_id"] for x in r_.records if x["patch_id"].startswith("Q")})
assert q == ["Q601_QA_EVENT_BATTLE_GROUP_FB", "Q601_QA_EVENT_BATTLE_GROUP_FC", "Q601_QA_EVENT_BATTLE_GROUP_FD",
             "Q601_QA_EVENT_BATTLE_GROUP_FE", "Q610_QA_EVENT", "Q612_QA_DLG", "Q613_QA_ANNEX_BATTLE_GROUP"], q
assert n_["enemy_foundation"]["magic_points"] == {"240": 0, "241": 3, "242": 0, "243": 0}
# v0.6.1: isolation formations $242/$243 use VRAM map 8 (template $002), birds in slots 0/2/3, never VRAM map 1 slot 5
for f_, ids_ in ((0x242, (0x028, 0x182, 0x183)), (0x243, (0x028, 0x028, 0x028))):
    fr = o_[0x38A000 + 15 * f_:0x38A000 + 15 * f_ + 15]
    assert fr[0] >> 4 == 8, (hex(f_), fr.hex())
    present = [s for s in range(6) if fr[1] & (1 << s)]
    assert present == [0, 2, 3], (hex(f_), present)
    got = tuple(fr[2 + s] | (((fr[14] >> s) & 1) << 8) for s in present)
    assert got == ids_, (hex(f_), [hex(x) for x in got])
print("PASS QA assets/formations/groups only in monster-tech; production/celes-tech FF bank + groups $FB-$FE pristine; v0.6.1 isolation $242/$243 on VRAM map 8 slots 0/2/3"); ok += 1
# 34 enemy asset guards fail closed
tmp6 = tempfile.mkdtemp()
def asset_with(mod_png=None, mod_json=None, folder="tech6_0180"):
    d = tmp6 + "/" + folder + str(len(os.listdir(tmp6)))
    shutil.copytree(os.path.join(HERE, "monsters", folder), d)
    if mod_png:
        w, h, rows, plte = read_indexed(d + "/sprite.png"); rows, plte = mod_png(rows, plte); write_indexed(d + "/sprite.png", rows, plte)
    if mod_json:
        fn, f = mod_json; j = json.load(open(d + "/" + fn)); f(j); json.dump(j, open(d + "/" + fn, "w"))
    return EnemyAsset(d)
expect_fail("asset-size-not-multiple-of-8", lambda: asset_with(mod_png=lambda r, p: ([x + [0, 0, 0] for x in r], p)), (AssetError,))
expect_fail("asset-3bpp-index-over-7", lambda: asset_with(mod_png=lambda r, p: ([[9] + x[1:] for x in r], p + [(1, 2, 3)] * 8), folder="tech6_0181"), (AssetError,))
expect_fail("asset-palette-count", lambda: asset_with(mod_json=("palette.json", lambda j: j["colors"].pop())), (AssetError,))
expect_fail("asset-top-row-empty", lambda: asset_with(mod_png=lambda r, p: ([[0] * 32] * 8 + r[:32], p)), (AssetError,))
expect_fail("asset-png-palette-mismatch", lambda: asset_with(mod_json=("palette.json", lambda j: j["colors"].__setitem__(3, "#FF00FF"))), (AssetError,))
def too_big():
    d = tmp6 + "/big"; shutil.copytree(os.path.join(HERE, "monsters", "tech6_0180"), d)
    w, h, rows, plte = read_indexed(d + "/sprite.png")
    write_indexed(d + "/sprite.png", [r + [3] * 16 for r in rows], plte)           # 48 px = 6 tiles wide
    EV.check_vram_box(EnemyAsset(d), 8, 2, "formation $240 slot 2")                  # VRAM map 8 slot 2 box = 4x8
expect_fail("asset-exceeds-vram-box", too_big, (AssetError,))
# 35 retargeting an undeclared enemy-graphics operand is refused
def t35():
    r = RomImage(clean, alloc, "production-v0.6.0"); r.expand()
    r.patch(0xC12103, clean[0x012103:0x012104], b"\x00", "X", "c", "r", retarget=True)
expect_fail("retarget-undeclared-enemy-consumer", t35)
# ---- TECH v0.6.2 formation safety -------------------------------------------------------------------------------
import build as B
from ff6x import formation_safety as FS
from ff6x.formation_preview import render as FPR
from ff6x.monsters import FormationSource, MonsterError
# 36 accepted v0.6.1 QA formations: report mode finds exactly the known placement issue; enforce mode refuses it
r_, o_, _, _ = B.build_target(clean, alloc, "monster-tech-v0.6.1")
rep = r_.formation_safety
errs = sorted((f["formation"], i["code"]) for f in rep["formations"] for i in f["issues"] if i["level"] == "ERROR")
assert rep["mode"] == "report" and errs == [("242", "edge_left"), ("243", "edge_left")], errs
assert not any(i["code"] == "magitek_vram_conflict" for f in rep["formations"] for i in f["issues"])
print("PASS v0.6.1 QA formations: report mode = only the known $242/$243 slot-0 left-edge issue, no Magitek conflict"); ok += 1
qa_paths = [os.path.join(HERE, "formations", f + ".json") for f in B.TARGETS["monster-tech-v0.6.1"]["formations"]]
expect_fail("formation-edge-enforce-on-v061-242", lambda: FS.check_target(o_, qa_paths, "enforce"), (FS.FormationSafetyError,))
expect_fail("formation-safety-unknown-mode", lambda: FS.check_target(o_, qa_paths, "lenient"), (FS.FormationSafetyError,))
# 37 production targets enforce by default
for t, m in B.TARGETS.items():
    if m.get("kind") in ("v06", "v07") and not m.get("qa_harness"):
        assert m.get("formation_safety", "enforce") == "enforce", t
print("PASS v0.6/v0.7 production targets run formation safety in enforce mode"); ok += 1
# 38 VRAM safety table = recomputation from the measured mask
vt = json.load(open(os.path.join(HERE, "data", "vram_safety.json")))
mask = FS.magitek_cells(vt)
assert mask == {(r, c) for r in range(12) for c in range(12, 16)}
assert vt["vram_maps"] == FS.build_vram_safety_table(mask)
assert [k for k, v in vt["vram_maps"].items() if v["magitek_all_slots_safe"]] == ["2", "8", "9", "10", "11"]
assert vt["vram_maps"]["1"]["slots"][5]["magitek"] == "unsafe" and vt["vram_maps"]["7"]["slots"][1]["magitek"] == "unsafe"
print("PASS data/vram_safety.json matches the measured Magitek mask (48 cells; all-safe maps 2/8/9/10/11)"); ok += 1
# 39 example formations: every rule fails closed / passes as documented
sys.path.insert(0, os.path.join(HERE, "tools"))
import formation_safety_examples as FX
ex = FX.run(clean)
want = {"ex1_edge_reject": ("ERROR", ["edge_left"]), "ex2_edge_fixed": ("OK", []),
        "ex3_magitek_reject": ("ERROR", ["magitek_vram_conflict"]), "ex4_magitek_fixed": ("OK", []),
        "ex5_boss_exception": ("WARNING", ["edge_left", "edge_top"]),
        "ex6_exception_on_small": ("ERROR", ["edge_left", "layout_exception_not_large"]),
        "ex7_missing_magitek_flag": ("ERROR", ["magitek_possible_missing"])}
got = {k: (v["status"], [i["code"] for i in v["issues"]]) for k, v in ex.items()}
assert got == want, got
assert ex["ex3_magitek_reject"]["suggested_vram_maps"] == [7]
assert all(i["level"] == "WARNING" for i in ex["ex5_boss_exception"]["issues"])
print("PASS formation-safety examples: edge reject/fix, Magitek reject (suggests map 7)/fix, large-boss exception, exception refused on small sprite, missing flag"); ok += 1
# 40 explicit vram_map override compiles into byte 0 bits 4-7 only; invalid values refused
fs4 = FormationSource(os.path.join(HERE, "formations", "examples", "ex4_magitek_fixed.json"))
rec4, _ = fs4.compile(clean, set())
t8 = clean[0xF6200 + 15 * 8]
assert rec4[0] == (t8 & 0x0F) | 0x70, hex(rec4[0])
def bad_vm(v):
    j = dict(fs4.f, vram_map=v); pth = tempfile.mktemp(suffix=".json"); json.dump(j, open(pth, "w"))
    FormationSource(pth).compile(clean, set())
expect_fail("vram-map-13", lambda: bad_vm(13), (MonsterError,))
expect_fail("vram-map-string", lambda: bad_vm("auto"), (MonsterError,))
# 41 previews are deterministic
pa, pb = tempfile.mktemp(suffix=".png"), tempfile.mktemp(suffix=".png")
FPR(o_, rep["formations"][2], pa); FPR(o_, rep["formations"][2], pb)
assert open(pa, "rb").read() == open(pb, "rb").read()
print("PASS vram_map override (byte 0 high nibble only) + deterministic preview PNG"); ok += 1
# ---- TECH v0.7.1 signature equipment bank ---------------------------------------------------------------------
from patches import item_v071 as IV
from patches.item_v071_hooks import HOOKS as IHOOKS
from ff6x.eventasm import EventProgram, EventAsmError
rom7, out7, _, _ = B.build_target(clean, alloc, "production")
pc = lambda a: a - 0xC00000
# 42 relocated item tables: vanilla records byte-identical, production has no extended content
assert out7[pc(IV.T_PROP):pc(IV.T_PROP) + 256 * 30] == clean[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30]
assert out7[pc(IV.T_PROP) + 256 * 30:pc(IV.T_PROP) + 320 * 30] == bytes(64 * 30)
assert out7[pc(IV.T_NAME):pc(IV.T_NAME) + 256 * 13] == clean[pc(IV.VAN_NAME):pc(IV.VAN_NAME) + 256 * 13]
assert out7[pc(IV.T_NAME) + 256 * 13:pc(IV.T_NAME) + 320 * 13] == b"\xFF" * (64 * 13)
assert out7[pc(IV.T_FLAGS):pc(IV.T_FLAGS) + 64] == bytes(64)
assert out7[pc(IV.T_ANIM):pc(IV.T_ANIM) + 0xC0 * 8] == clean[pc(IV.VAN_ANIM):pc(IV.VAN_ANIM) + 0xC0 * 8]
assert out7[pc(IV.T_JUMP):pc(IV.T_JUMP) + 0x100] == clean[pc(IV.VAN_JUMP):pc(IV.VAN_JUMP) + 0x100]   # production: no ext weapons
assert clean[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30] == out7[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30]   # vanilla table itself untouched
print("PASS v0.7.1 XItemProp/XItemName/XWeaponAnimFull: vanilla $00-$FF byte-identical; production extended ids undefined (flags 0)"); ok += 1
# 43 v0.7.1 production vanilla-space diff = v0.6 declared set + item operand retargets + hook sites + stub claims + checksum
changed7 = [i for i in range(0x300000) if out7[i] != clean[i]]
allowed7 = set(allowed6)
rel = json.load(open(os.path.join(HERE, "data", "item_relocation_v071.json")))
for t in rel["tables"].values():
    for c in t["consumers"]:
        a0 = pc(int(c["snes"], 16))
        allowed7 |= {a0 + 1, a0 + 2, a0 + 3}
for h in IHOOKS:
    a0 = pc(int(h["snes"], 16))
    allowed7 |= set(range(a0, a0 + len(bytes.fromhex(h["expect"]))))
for c in ("ITEMX_C0_STUBS", "ITEMX_C2_STUBS", "ITEMX_C3_STUBS"):
    cl = [x for x in alloc.claims if x["name"] == c][0]
    allowed7 |= set(range(pc(int(cl["snes_start"], 16)), pc(int(cl["snes_end"], 16)) + 1))
extra7 = [hex(i) for i in changed7 if i not in allowed7]
assert not extra7, extra7[:10]
nh = sum(len(bytes.fromhex(h["expect"])) for h in IHOOKS)
nr = sum(len(t["consumers"]) for t in rel["tables"].values())
print(f"PASS v0.7.1 production vanilla-space diff limited to {len(changed7)} declared bytes ({len(IHOOKS)} hook sites/{nh} B, {nr} retargets, 3 stub claims)"); ok += 1
# 44 QA items / QA harness only in item-tech; production + celes-tech carry no QA content and a pristine FF bank
for t in ("production", "celes-tech"):
    r_, o_, _, _ = B.build_target(clean, alloc, t)
    assert not any(x["patch_id"].startswith("Q") for x in r_.records), t
    assert o_[0x3F0000:0x400000] == b"\xFF" * 0x10000, t
    assert o_[pc(IV.T_FLAGS):pc(IV.T_FLAGS) + 64] == bytes(64), t
r_, o_, _, _ = B.build_target(clean, alloc, "item-tech")
fl = o_[pc(IV.T_FLAGS):pc(IV.T_FLAGS) + 64]
assert [k for k in range(64) if fl[k]] == [0x3D, 0x3E, 0x3F] and all(fl[k] == 1 for k in (0x3D, 0x3E, 0x3F))
assert o_[pc(IV.T_PROP):pc(IV.T_PROP) + 256 * 30] == clean[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30]
print("PASS QA items $13D-$13F + QA harness only in item-tech (no spear flag); production/celes-tech undefined"); ok += 1
# 45 item / event-API guards fail closed
qa_meta = {"ext_item_sources": ["items/qa_v071/qa_items.json"]}
expect_fail("qa-items-in-non-qa-target", lambda: IV.load_defs(dict(qa_meta)), (SystemExit,))
def bad_items(mod):
    j = json.load(open(os.path.join(HERE, "items/qa_v071/qa_items.json"))); mod(j)
    pth = tempfile.mktemp(suffix=".json", dir=os.path.join(HERE, "items")); json.dump(j, open(pth, "w"))
    try: IV.load_defs({"ext_item_sources": [os.path.relpath(pth, HERE)], "qa_harness": True})
    finally: os.remove(pth)
expect_fail("qa-item-outside-13D-13F", lambda: bad_items(lambda j: j["items"][0].update(id="126")), (SystemExit,))
expect_fail("ext-item-id-out-of-bank", lambda: bad_items(lambda j: (j.update(qa=False), j["items"][0].update(id="140"))), (SystemExit,))
def gau_weapon():
    j = json.load(open(os.path.join(HERE, "items/qa_v071/qa_items.json"))); j["items"][0]["fields"]["equip_chars"] = "3FFF"
    pth = tempfile.mktemp(suffix=".json", dir=os.path.join(HERE, "items")); json.dump(j, open(pth, "w"))
    try: IV.build_tables(clean, IV.load_defs({"ext_item_sources": [os.path.relpath(pth, HERE)], "qa_harness": True}))
    finally: os.remove(pth)
expect_fail("ext-weapon-equippable-by-gau-umaro", gau_weapon, (SystemExit,))
expect_fail("duplicate-ext-item-id", lambda: bad_items(lambda j: j["items"][1].update(id="13D")), (SystemExit,))
expect_fail("give-ext-item-without-engine", lambda: EventProgram(0xFF0000, {}, {}).parse("give_ext_item $13D"), (EventAsmError,))
expect_fail("give-ext-item-vanilla-id", lambda: EventProgram(0xFF0000, {}, {}, ext_items=True).parse("give_ext_item $3D"), (EventAsmError,))
expect_fail("has-ext-item-readonly-bit", lambda: EventProgram(0xFF0000, {}, {}, readonly_bits={"V": 0x1B5}, ext_items=True)
            .parse("has_ext_item $13D -> V"), (EventAsmError,))
def bad_hook():
    r = RomImage(clean, alloc, "production"); r.expand()
    h = IHOOKS[0]
    r.patch(int(h["snes"], 16), b"\x00" * len(bytes.fromhex(h["expect"])), bytes.fromhex(h["expect"]), "X", "c", "r")
expect_fail("item-hook-original-bytes", bad_hook)
print(f"ALL {ok} SELF-TESTS PASS")
