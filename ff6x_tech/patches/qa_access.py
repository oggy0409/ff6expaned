"""Q1xx-Q3xx - TECH v0.3.1 QA ACCESS harness (target `celes-qa` ONLY).

QA HARNESS ONLY - NOT A PRODUCTION BASELINE.

Purpose: let the user QA the v0.3 Celes Annex slice from a New Game, without a
World of Ruin / Falcon save. Everything the v0.3 slice writes is produced by the
same code path (patches/celes_tech.py, identical sources); this module only adds:

  Q100_QA_DLG                    QA prompt string in QA_HARNESS (FF) + pointer slot $100B (F3:002C)
  Q101_QA_DLG_COUNT              hook bound CMP #$000B -> #$000C at F0:1017 (override of P100)
  Q200_QA_EVENT                  QA access event at FF:0000
  Q303_QA_BATTLE_GROUP           v0.3 door battle group $28 -> $01 (override of T300 byte)
  Q305_REPACK_EVENT_TRIGGERS_QA  trigger table = v0.3 records + map $013 (34,43) -> FF:0000
  Q305_REPACK_SHORT_ENTRANCES_QA short entrances = v0.3 records with the Annex exit
                                 redirected to map $013 (35,43)
"""
import json, os
from ff6x.eventasm import EventProgram
from ff6x.hirom import event_offset, fmt_snes, snes_to_pc
from ff6x.tables import PackedTable, decode_npc
from ff6x.text import encode_dialogue, line_widths, FONT_WIDTH_SNES, LINE_LIMIT_PX

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DIR = os.path.join(HERE, "events", "celes_qa_access")

QA_MAP = 0x013                    # Narshe, opening streets (first controllable field map)
QA_TILE = (34, 43)                # plaza corner, lower z (prop $02), off the scripted path
QA_RETURN = (35, 43)              # one tile right of the QA tile, lower z, facing LEFT
QA_EVENT_ORG = 0xFF0000
QA_TEXT_ORG = 0xFF0800
VANILLA_SAVEPOINT = (0xCC9AEB, bytes.fromhex("C0 B5 81 B3 5E 00"))   # if_switch $1B5=1 -> EventReturn
V03_MSG_COUNT = 11                # $1000 diagnostic + $1001-$100A
HOOK_COUNT_OPERAND = 0xF01017     # operand of CMP #count in P100 DlgHook
BATTLE_OPCODE = 0x4D


def qa_messages():
    d = json.load(open(os.path.join(QA_DIR, "dialogue.json")))
    return [(m["label"], m["text"]) for m in d["messages"]]


def add_dialogue(rom, base_count):
    """Append QA messages after the v0.3 table without touching P101 bytes."""
    if base_count != V03_MSG_COUNT:
        raise SystemExit(f"Q100: v0.3 message count {base_count} != {V03_MSG_COUNT}")
    fw = rom.clean[snes_to_pc(FONT_WIDTH_SNES):snes_to_pc(FONT_WIDTH_SNES) + 256]
    ids, ptrs, at = {}, bytearray(), QA_TEXT_ORG
    for k, (label, text) in enumerate(qa_messages()):
        data = encode_dialogue(text)
        lw = line_widths(data, fw)
        if max(lw) > LINE_LIMIT_PX or len(lw) > 4:
            raise SystemExit(f"Q100: '{label}' would wrap: {lw}")
        n = base_count + k
        s = rom.place("QA_HARNESS", data, f"qa_dlg_{0x1000 + n:04X}_{label}", "Q100_QA_DLG", at=at,
                      reason=f"QA dialogue ${0x1000 + n:04X}: {text!r}",
                      consumer="field text renderer via $C9/$CB set by P100 hook")
        at = s + len(data)
        ptrs += bytes([s & 0xFF, (s >> 8) & 0xFF, s >> 16, 0])
        ids[label] = 0x1000 + n
    rom.place("DIALOGUE_PTRS", bytes(ptrs), "qa_dlg_ptr_slots", "Q100_QA_DLG", at=0xF30000 + 4 * base_count,
              reason=f"pointer slot(s) for QA IDs ${0x1000 + base_count:04X}+ appended after the v0.3 table",
              consumer="P100 hook (LDA.l F3:0000,X)")
    new_count = base_count + len(ids)
    rom.override(HOOK_COUNT_OPERAND, base_count.to_bytes(2, "little"), new_count.to_bytes(2, "little"),
                 "Q101_QA_DLG_COUNT", "P100_DLG_HOOK",
                 consumer="DlgHook F0:1016 CMP #count (expansion-ID range bound)",
                 reason=f"QA: accept IDs up to ${0x1000 + new_count - 1:04X}")
    return ids


def make_qa(qa_ids, readonly_bits):
    """Returns the callback celes_tech.build() calls once the v0.3 events are placed."""
    def qa(rom, L):
        notes = {}
        pc = snes_to_pc(VANILLA_SAVEPOINT[0])
        if rom.clean[pc:pc + 6] != VANILLA_SAVEPOINT[1]:
            raise SystemExit("Q200: vanilla SavePoint CC:9AEB mismatch")
        # ---- QA event (FF) --------------------------------------------------------------
        prog = EventProgram(QA_EVENT_ORG, {}, qa_ids,
                            {"EvAnnexEnter_Yes": L["EvAnnexEnter_Yes"], "VanillaSavePoint": VANILLA_SAVEPOINT[0]},
                            readonly_bits=readonly_bits)
        prog.parse(open(os.path.join(QA_DIR, "qa_access.evt")).read(), "qa_access.evt")
        code = prog.assemble()
        if prog.bits_used != {"VANILLA_TILE_EVENT_LATCH"}:
            raise SystemExit(f"Q200: unexpected bit use {prog.bits_used}")
        rom.place("QA_HARNESS", code, "qa_access_event", "Q200_QA_EVENT", at=QA_EVENT_ORG,
                  reason="QA HARNESS ONLY: map $013 QA tile prompt -> v0.3 Annex entry / vanilla SavePoint",
                  consumer="event trigger map $013 (34,43) (24-bit pointer)")
        notes["event_listing"] = prog.listing_text()

        # ---- battle group override (exact consumer: battle cmd in EvBattleDoor_Fight) ----
        bat = L["EvBattleDoor_Fight"] + 3            # after 'dlg battle_start' (4B lo hi)
        cur = bytes(rom.buf[snes_to_pc(bat):snes_to_pc(bat) + 3])
        if cur != bytes([BATTLE_OPCODE, 0x28, 0x3F]):
            raise SystemExit(f"Q303: expected '4D 28 3F' at {fmt_snes(bat)}, found {cur.hex(' ')}")
        rom.override(bat, cur, bytes([BATTLE_OPCODE, 0x01, 0x3F]), "Q303_QA_BATTLE_GROUP", "T300_EVENTS",
                     consumer="event cmd $4D in EvBattleDoor_Fight (EventBattleGroup CF:5000 index)",
                     reason="QA: group $28 (Mega Armor+ProtoArmor) -> $01 (vanilla opening Guard battle, "
                            "formation $002) so a New Game party can finish the battle step")
        grp = rom.clean[0x0F5000 + 4:0x0F5000 + 8]
        if grp != bytes.fromhex("02 00 02 00"):
            raise SystemExit("Q303: vanilla event battle group 1 is not formation $002")

        # ---- vanilla map $013 must have nothing on the QA tiles --------------------------
        t = rom.alloc.table("EVENT_TRIGGERS", rom.target)
        tt = PackedTable(rom.clean, "EVENT_TRIGGERS", int(t["ptr_snes"], 16), int(t["data_end_snes"], 16), 5, 417)
        for r in tt.records[QA_MAP]:
            if (r[0], r[1]) in (QA_TILE, QA_RETURN):
                raise SystemExit(f"Q305: map $013 already has a trigger at {r[0]},{r[1]}")
        notes["map013_vanilla_triggers"] = [[r[0], r[1]] for r in tt.records[QA_MAP]]
        e = rom.alloc.table("SHORT_ENTRANCES", rom.target)
        et = PackedTable(rom.clean, "SHORT_ENTRANCES", int(e["ptr_snes"], 16), int(e["data_end_snes"], 16), 6, 513)
        for r in et.records[QA_MAP]:
            if (r[0], r[1]) in (QA_TILE, QA_RETURN):
                raise SystemExit(f"Q305: map $013 already has an entrance at {r[0]},{r[1]}")
        lt = PackedTable(rom.clean, "LONG_ENTRANCES", 0xEDF480, 0xEDFDFF, 7, 513)   # read-only check
        for r in lt.records[QA_MAP]:
            n = (r[2] & 0x7F) + 1
            cells = [(r[0], r[1] + k) if r[2] & 0x80 else (r[0] + k, r[1]) for k in range(n)]
            if set(cells) & {QA_TILE, QA_RETURN}:
                raise SystemExit("Q305: map $013 long entrance covers a QA tile")
        n = rom.alloc.table("NPC_PROPS", rom.target)
        nt = PackedTable(rom.clean, "NPC_PROPS", int(n["ptr_snes"], 16), int(n["data_end_snes"], 16), 9, 417)
        npcs13 = [decode_npc(r) for r in nt.records[QA_MAP]]
        for d in npcs13:
            if (d["x"], d["y"]) in (QA_TILE, QA_RETURN):
                raise SystemExit("Q305: a vanilla map $013 NPC starts on a QA tile")
        notes["map013_vanilla_npcs"] = [[d["x"], d["y"]] for d in npcs13]

        trig = [(QA_MAP, bytes(QA_TILE) + event_offset(QA_EVENT_ORG).to_bytes(3, "little"), "QaAccess")]

        def exit_override(ents):
            out = []
            hit = 0
            for m, rec, label in ents:
                if m == 0x0C7 and label == "exit->00C":
                    w = QA_MAP | (3 << 12)               # facing LEFT, lower z, no flags
                    rec = rec[:2] + bytes([w & 0xFF, w >> 8, QA_RETURN[0], QA_RETURN[1]])
                    label = "exit->013(QA)"
                    hit += 1
                out.append((m, rec, label))
            if hit != 1:
                raise SystemExit("Q305: v0.3 Annex exit record not found exactly once")
            return out

        notes.update({"status": "QA HARNESS ONLY - NOT A PRODUCTION BASELINE",
                      "qa_trigger": {"map": "013", "tile": list(QA_TILE), "event": fmt_snes(QA_EVENT_ORG)},
                      "qa_exit": {"from": "0C7 (16,29)", "to": "013 (35,43) LEFT lower-z"},
                      "battle_override": {"snes": fmt_snes(bat + 1), "from": "$28", "to": "$01"},
                      "dialogue_ids": {k: f"${v:04X}" for k, v in qa_ids.items()}})
        return {"triggers": trig, "exit_override": exit_override, "notes": notes}
    return qa
