#!/usr/bin/env python3
"""TECH v0.9 (from the v0.8 audit, engine asm/item_v09 + the v0.9 hook table) - static audit: can the extended-id high bit that a hook leaves in the B accumulator reach vanilla code
that consumes B?

For every hook whose routine can return with B != 0 (9-bit id loads, Optimum best-item, battle equipment loads),
walk the code that follows the hook site in the PATCHED ROM: both branch paths, into JSR'd vanilla routines (depth
limited), tracking M/X. B is "live" until an instruction overwrites it (TDC, TSC, XBA-load, 16-bit LDA/PLA/TXA/TYA,
REP+16-bit load). Report every instruction that consumes B while it is live:
  TAX / TAY / TCD / TCS with 16-bit index (full C copied), XBA, any 16-bit accumulator op, PHA with 16-bit A,
  and RTS/RTL (B returned to an unknown caller), PLP / RTI / indirect jumps (flags unknown: stop, review).

Hook routines are modelled by name (symbols of the assembled engine): CLEARS reset B (v0.8 asm/item_v08), PRODUCER
routines set it, every other FF6X routine leaves it unchanged. An XBA immediately followed by "LDA #imm / LDA zZero"
and XBA (the vanilla "B := 0" idiom) is not a use.

usage: b_leak_audit_v09.py <patched.sfc> <manifest.json> <engine asm dir> [hook_ids...]
env:   FF6X_INSN_TSV (Rev 1 instruction index), FF6X_DISASM (disassembly root with src/)
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ff6x.op65816 import OPCODES, operand_size
from patches.item_v09 import hooks as _hooks
HOOKS = _hooks()

INSN_TSV = os.environ.get("FF6X_INSN_TSV", "insn.tsv")
DIS = os.environ.get("FF6X_DISASM", "ff6dis")
PRODUCER = ("XC3_GetIdB", "XC3_LdaInvY", "XC3_LdaInvX", "XC3_LdaEq1E", "XC3_LdaEq1F", "XC3_LdaEq20", "XC3_LdaEq21",
            "XC3_LdaEq22", "XC3_LdaEq23", "XC3_LdaEq24", "XC3_GetBestEquip", "XC3_GetBest2Hand", "XC2_EqLoad")


def pc_of(snes):
    return snes & 0x3FFFFF


CLEARS_V071 = ("XC3_ItemDescB", "XC3_LdaEqM1F", "XC3_LdaEqM20")
CLEARS_V08 = CLEARS_V071 + ("XC3_PropPtrB", "XC3_DecQtyB", "XC3_IncQtyB", "XC3_HiM7A", "XC3_EqpName", "XC3_ClrB",
                            "XC3_PropPtrCur", "XC3_ShopListPtr", "XC3_ShopPtrX", "XC3_LoadItemNameCur",
                            "XC3_ShopLdaX", "XC3_DecSel", "XC3_ShopListName")


def engine_symbols(asm_dir):
    from patches import item_v09 as IV
    from ff6x.asm816 import Program
    src = "\n".join(f"; ==== {f}\n" + open(os.path.join(asm_dir, f)).read() for f in IV.SOURCES_V09)
    prog = Program(src, IV.table_externs(), "item_v09")
    prog.assemble()
    return {v: k for k, v in prog.symbols.items() if isinstance(v, int)}


def main(rom_path, manifest, asm_dir, only=()):
    rom = open(rom_path, "rb").read()
    sym_at = engine_symbols(asm_dir)
    CLEARS = CLEARS_V08 if "XC3_ClrB" in sym_at.values() else CLEARS_V071
    m = json.load(open(manifest))
    new_code = []                                   # FF6X code ranges (hook routines)
    for r in m["patches"]:
        s, e = int(r["snes_start"].replace(":", ""), 16), int(r["snes_end"].replace(":", ""), 16)
        if "STUBS" in r["patch_id"] or "ENGINE_CODE" in r["patch_id"]:
            new_code.append((s, e))
    hooks = {int(h["snes"], 16): h for h in HOOKS}

    def in_new(a):
        return any(s <= a <= e for s, e in new_code) or a in sym_at

    report = []
    # ---- vanilla function entries and call sites (Rev 1 instruction index + disassembly labels)
    rows = [l.rstrip("\n").split("\t") for l in open(INSN_TSV)]
    byfile = {}
    for r in rows:
        f, ln = r[5].rsplit(":", 1)
        byfile.setdefault(f, []).append((int(ln), int(r[0].replace(":", ""), 16)))
    entry_of = {}
    for f, lst in byfile.items():
        lst.sort()
        src = open(os.path.join(DIS, f.lstrip("./"))).read().splitlines()
        labels = [i + 1 for i, l in enumerate(src) if re.match(r"^[A-Za-z_]\w*:", l) or re.match(r"^\.proc\s", l)]
        li = 0
        cur = None
        for ln, ad in lst:
            while li < len(labels) and labels[li] < ln:
                cur = None if li + 1 < len(labels) and labels[li + 1] < ln else "new"
                li += 1
                if cur == "new":
                    cur = ad
            if cur is None:
                cur = ad
            entry_of[ad] = cur
    callers = {}
    for r in rows:
        if r[2] in ("JSR", "JSL") and r[3] in ("abs", "absl"):
            ad = int(r[0].replace(":", ""), 16)
            t = int(r[4], 16)
            t = (ad & 0xFF0000) | t if r[2] == "JSR" else t
            callers.setdefault(t, []).append((ad, 3 if r[2] == "JSR" else 4))

    def walk(start, m8, x8, origin, depth=0, path=()):
        seen = set()
        stack = [(start, m8, x8, (), 0, path)]
        while stack:
            pc, m8, x8, calls, up, path = stack.pop()
            prev = None
            for _ in range(600):
                key = (pc, m8, x8, calls)
                if key in seen:
                    break
                seen.add(key)
                op = rom[pc_of(pc)]
                mn, md = OPCODES[op]
                n = 1 + operand_size(md, m8, x8)
                arg = int.from_bytes(rom[pc_of(pc) + 1:pc_of(pc) + n], "little")
                nxt = (pc & 0xFF0000) | ((pc + n) & 0xFFFF)
                where = f"{pc >> 16:02X}:{pc & 0xFFFF:04X} {mn} {md} ${arg:X}"

                def use(why):
                    report.append({"hook": origin, "at": where, "why": why, "path": list(path)})
                if mn in ("TAX", "TAY") and not x8 or mn in ("TCD", "TCS"):
                    use("16-bit transfer of C"); break
                if mn == "XBA":
                    o2 = rom[pc_of(pc) + 1]; o3 = rom[pc_of(pc) + 3] if o2 in (0xA5,) else rom[pc_of(pc) + 3]
                    if m8 and o2 in (0xA9, 0xA5) and rom[pc_of(pc) + 3] == 0xEB and (o2 == 0xA9 and rom[pc_of(pc) + 2] == 0
                                                                                   or o2 == 0xA5):
                        break                             # XBA / LDA #0 (or LDA zZero) / XBA: vanilla "B := 0"
                    use("XBA reads B"); break
                if mn == "PHA" and not m8:
                    use("PHA 16-bit"); break
                if mn in ("TDC", "TSC"):
                    break
                if mn in ("LDA", "PLA", "TXA", "TYA") and not m8:
                    break
                if not m8 and (mn in ("ADC", "SBC", "AND", "ORA", "EOR", "CMP", "STA", "BIT") or
                               mn in ("ASL", "LSR", "ROL", "ROR", "INC", "DEC") and md == "acc"):
                    use("16-bit accumulator op"); break
                if mn == "REP":
                    m8 = m8 and not (arg & 0x20); x8 = x8 and not (arg & 0x10)
                elif mn == "SEP":
                    m8 = m8 or bool(arg & 0x20); x8 = x8 or bool(arg & 0x10)
                if mn in ("RTS", "RTL"):
                    if calls:
                        pc = calls[-1]; calls = calls[:-1]; continue
                    if up >= 2:
                        use("returns with B live (2 caller levels checked)"); break
                    ent = entry_of.get(pc)
                    cs = callers.get(ent, [])
                    if not cs:
                        use(f"returns with B live; no static caller of {ent >> 16 if ent else 0:02X}:{(ent or 0) & 0xFFFF:04X}"); break
                    for c, ln in cs:
                        stack.append((((c & 0xFF0000) | ((c + ln) & 0xFFFF)), m8, x8, (), up + 1,
                                      path + (f"ret->{c >> 16:02X}:{c & 0xFFFF:04X}",)))
                    break
                if mn in ("PLP", "RTI", "JML", "BRK", "COP", "STP", "WAI") or md in ("absi", "absix", "absil"):
                    use(f"{mn}: flow/flags unknown - review"); break
                if mn == "JSR" and md == "abs" or mn == "JSL":
                    tgt = (pc & 0xFF0000) | arg if mn == "JSR" else arg
                    name = sym_at.get(tgt, "")
                    if name in CLEARS or name in PRODUCER:
                        break                             # B := 0 (v0.8) / B re-defined by a producer (own start)
                    if in_new(tgt) or len(calls) >= 4:
                        pc = nxt; continue
                    calls = calls + (nxt,); pc = tgt; continue
                if mn == "JMP" and md == "abs":
                    tgt = (pc & 0xFF0000) | arg
                    if sym_at.get(tgt, "") in CLEARS or sym_at.get(tgt, "") in PRODUCER:
                        break
                    if in_new(tgt) and pc_of(tgt) < len(rom) and rom[pc_of(tgt)] == 0x4C and \
                            sym_at.get((tgt & 0xFF0000) | int.from_bytes(rom[pc_of(tgt) + 1:pc_of(tgt) + 3], "little"), "") in PRODUCER:
                        break
                    if in_new(tgt):
                        use(f"JMP into hook routine {sym_at.get(tgt, '?')} (tail) - review"); break
                    if rom[pc_of(tgt)] == 0x4C:
                        t2 = (tgt & 0xFF0000) | int.from_bytes(rom[pc_of(tgt) + 1:pc_of(tgt) + 3], "little")
                        if sym_at.get(t2, "") in PRODUCER or sym_at.get(t2, "") in CLEARS:
                            break
                    pc = tgt; continue
                empty_cmp = prev == ("CMP", 0xFF)
                prev = (mn, arg if md == "immm" else None)
                if md in ("rel8", "rel16"):
                    off = arg - (0x100 if md == "rel8" and arg & 0x80 else 0) - (0x10000 if md == "rel16" and arg & 0x8000 else 0)
                    tgt = (pc & 0xFF0000) | ((nxt + off) & 0xFFFF)
                    if mn in ("BRA", "BRL"):
                        pc = tgt; continue
                    if empty_cmp and mn == "BEQ":         # empty slot ($FF): its high bit is 0 (engine invariant)
                        pc = nxt; continue
                    if empty_cmp and mn == "BNE":
                        pc = tgt; continue
                    stack.append((tgt, m8, x8, calls, up, path))
                pc = nxt

    for a, h in sorted(hooks.items()):
        if only and h["id"] not in only:
            continue
        called = set(re.findall(r"(?:jsr|jmp|jsl|jml)\s+(\w+)", h["asm"]))
        if not called & set(PRODUCER):
            continue
        mode = h.get("mode", ".a8\n.i16")
        m8 = ".a8" in mode
        x8 = ".i8" in mode
        start = a + len(bytes.fromhex(h["expect"]))
        if h["asm"].startswith("jmp "):              # routine replaced: B leaves through its RTS to the callers
            for c, ln in callers.get(a, []):
                walk((c & 0xFF0000) | ((c + ln) & 0xFFFF), m8, x8, h["id"], 0, (f"ret->{c >> 16:02X}:{c & 0xFFFF:04X}",))
            continue
        walk(start, m8, x8, h["id"])
    return report


if __name__ == "__main__":
    rep = main(sys.argv[1], sys.argv[2], sys.argv[3], tuple(sys.argv[4:]))
    seen = set()
    for r in rep:
        k = (r["hook"], r["at"], r["why"])
        if k in seen:
            continue
        seen.add(k)
        print(f'{r["hook"]:22s} {r["at"]:32s} {r["why"]}  via {"/".join(r["path"])}')
    print(len(seen), "findings")
