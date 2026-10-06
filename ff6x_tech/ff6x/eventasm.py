"""Event-script assembler for project .evt source files.

Every opcode encoding below was cross-checked against the Rev 1-verified
disassembly macros (ca65 oracle, tools/oracle_check.py). Only the commands
the project needs are supported; anything else is a build error.

Source syntax (one command per line, '#' comments):
    @Label
    dlg <dialogue-label | $hex> [bottom] [textonly]
    if_switch <BIT_NAME>=<0|1> -> <Label>
    set_switch <BIT_NAME> / clr_switch <BIT_NAME>
    call <Label | $CAxxxx-style absolute SNES>
    choice <Label>, <Label>[, ...]
    battle <group dec/$hex> [bg $hex]
    give_item <item $hex>
    give_esper <esper $36-$50>                 # event cmd $86 (EventCmd_86 C0:ADB8-area, sets $1A69 bit)
    hide_obj <obj $hex> / show_obj <obj $hex>
    load_map <map $hex> <x> <y> <UP|RIGHT|DOWN|LEFT> [Z_UPPER] [SHOW_TITLE] [STARTUP_EVENT] [NO_FADE_IN]
    party_step <UP|RIGHT|DOWN|LEFT> <1-8>      # obj_script SLOT_1 { move dir,n ; end }
    fade_in / fade_out / wait_fade / wait_15f / return
    take_item <item $hex>                      # event cmd $81 (EventCmd_81)
    shop <shop $hex>                           # event cmd $9B (EventCmd_9b, C0:B06D)
    colosseum                                  # event cmd $9A (EventCmd_9a, C0:B0B2)
    status_clear <char $hex> <mask $hex16>     # event cmd $88 (EventCmd_88: $1614,y &= mask)
    status_set <char $hex> <mask $hex16>       # event cmd $89 (EventCmd_89: $1614,y |= mask)
  TECH v0.7.3 (vanilla party commands, same encoding as the vanilla recruit scripts, e.g. Locke joins at CC:A621):
    char_prop <char $00-$0F> <actor props $00-$3F>  # event cmd $40 (EventCmd_40: stats/equipment/level/actor)
    obj_gfx <obj $00-$0F> <gfx $hex>           # event cmd $37 (EventCmd_37: object + character graphics $1601)
    char_name <char $00-$0F> <name $hex>       # event cmd $7F (EventCmd_7f: character name)
    create_obj <obj $00-$0F> / delete_obj <obj $00-$0F>   # event cmd $3D / $3E
    char_party <char $00-$0F> <party 0-7>      # event cmd $3F (EventCmd_3f: 0 = remove from party)
  TECH v0.8 (vanilla commands):
    give_gp <amount 1-65535> / take_gp <amount 1-65535>   # event cmd $84 / $85 ($85 sets vanilla switch $1BE if short)
    loop <count 1-254> / end_loop              # event cmd $B0 count / $B1
  TECH v0.7.1 extended-item API (only when the target carries the item engine, ext_items=True):
    give_ext_item <id $100-$13F>               # event cmd $66 lo hi   (XC0_Ev66 -> XGiveExt)
    take_ext_item <id $100-$13F>               # event cmd $67 lo hi   (XC0_Ev67 -> XTakeExt)
    has_ext_item <id $100-$13F> -> <BIT_NAME>  # event cmd $68 lo hi sw (XC0_Ev68 -> XHasExt: bit := owned)
  TECH v0.9 rare-item API (only with the v0.9 item engine, ext_items="v09"):
    give_rare <rare id 0-51>                   # event cmd $69 id      (XC0_Ev69 -> XRareGive)
    take_rare <rare id 0-51>                   # event cmd $6D id      (XC0_Ev6D -> XRareTake)
    has_rare <rare id 0-51> -> <BIT_NAME>      # event cmd $6E id sw   (XC0_Ev6E -> XRareHas: bit := owned)
  TECH v0.9.2 (vanilla commands, encodings from the Rev 1 interpreter field/event.asm):
    load_map ... [SET_PARENT] [AIRSHIP]         # $6A: word bit 9 = set parent; flags byte bit 0 = world vehicle airship
    world_end                                  # $FF: end of the world/vehicle script that follows a world-map load_map
    party_case                                 # $DE: event bits $1A0+char := character is in the active party
    load_pal <cgram row 0-15> <palette 0-255>  # $60: MapSpritePal[palette] -> palette row (8-15 = sprite slots 0-7)
    set_tiles <BG1|BG2> <x> <y> <w> <h> <tile hex> ... # $73: change w*h map tiles (immediate update)
"""
from .hirom import event_offset

DIRS = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
SIMPLE = {"return": 0xFE, "fade_in": 0x96, "fade_out": 0x97, "wait_fade": 0x5C, "wait_15f": 0x91}


class EventAsmError(Exception):
    pass


def _num(tok):
    tok = tok.strip()
    return int(tok[1:], 16) if tok.startswith("$") else int(tok, 0)


class EventProgram:
    def __init__(self, org_snes, bits, dialogue, externals=None, readonly_bits=None, ext_items=False):
        self.org, self.bits, self.dlg = org_snes, dict(bits), dialogue
        self.ext_items = ext_items
        self.readonly = dict(readonly_bits or {})
        for k, v in self.readonly.items():
            if k in self.bits:
                raise EventAsmError(f"bit name {k} is both allocated and read-only")
            self.bits[k] = v
        self.ext = externals or {}
        self.code = bytearray()
        self.labels = {}
        self.fix = []          # (pos, label)
        self.listing = []
        self.bits_used = set()

    def pc(self):
        return self.org + len(self.code)

    def _emit(self, text, data):
        self.listing.append((self.pc(), bytes(data), text))
        self.code += bytes(data)

    def _addr(self, label):
        # operand position: caller emits opcode bytes first in the same list,
        # so callers use _addr_at with the exact offset.
        raise NotImplementedError

    def _addr_at(self, pos, label):
        self.fix.append((pos, label))
        return [0, 0, 0]

    def _bit(self, name):
        if name not in self.bits:
            raise EventAsmError(f"unknown event bit {name}")
        self.bits_used.add(name)
        return self.bits[name]

    def parse(self, text, srcname="<evt>"):
        for ln, raw in enumerate(text.splitlines(), 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            try:
                self._line(line)
            except (EventAsmError, ValueError, KeyError) as e:
                raise EventAsmError(f"{srcname}:{ln}: {e} :: {raw.strip()}")

    def _line(self, line):
        if line.startswith("@"):
            name = line[1:]
            if name in self.labels:
                raise EventAsmError(f"duplicate label {name}")
            self.labels[name] = self.pc()
            self.listing.append((self.pc(), b"", "@" + name))
            return
        op, _, rest = line.partition(" ")
        args = rest.strip()
        if op in SIMPLE:
            self._emit(op, [SIMPLE[op]])
        elif op == "dlg":
            parts = args.split()
            i = _num(parts[0]) if parts[0].startswith("$") else self.dlg[parts[0]]
            hi = (i >> 8) & 0x1F
            if "bottom" in parts[1:]: hi |= 0x80
            if "textonly" in parts[1:]: hi |= 0x40
            self._emit(line, [0x4B, i & 0xFF, hi])
        elif op == "if_switch":
            cond, _, lab = args.partition("->")
            name, _, val = cond.strip().partition("=")
            b = self._bit(name.strip())
            w = b | (0x8000 if val.strip() == "1" else 0)
            if val.strip() not in ("0", "1"):
                raise EventAsmError("if_switch needs =0 or =1")
            self._emit(line, [0xC0, w & 0xFF, w >> 8] + self._addr_at(len(self.code) + 3, lab.strip()))
        elif op in ("set_switch", "clr_switch"):
            if args in self.readonly:
                raise EventAsmError(f"{args} is a vanilla read-only bit; project scripts may not write it")
            b = self._bit(args)
            if b > 0x6FF:
                raise EventAsmError("switch out of range")
            base = 0xD0 if op == "set_switch" else 0xD1
            self._emit(line, [base + (b >> 8) * 2, b & 0xFF])
        elif op == "call":
            self._emit(line, [0xB2] + self._addr_at(len(self.code) + 1, args))
        elif op == "choice":
            labs = [l.strip() for l in args.split(",")]
            data = [0xB6]
            for lab in labs:
                data += self._addr_at(len(self.code) + len(data), lab)
            self._emit(line, data)
        elif op == "battle":
            parts = args.split()
            g = _num(parts[0])
            bg = _num(parts[2]) if len(parts) >= 3 and parts[1] == "bg" else 0x3F
            self._emit(line, [0x4D, g, bg])
        elif op == "give_item":
            self._emit(line, [0x80, _num(args)])
        elif op == "give_esper":
            e = _num(args)
            if not 0x36 <= e <= 0x50:
                raise EventAsmError("give_esper operand must be $36-$50")
            self._emit(line, [0x86, e])
        elif op in ("hide_obj", "show_obj"):
            self._emit(line, [0x42 if op == "hide_obj" else 0x41, _num(args)])
        elif op == "load_map":
            p = args.split()
            m, x, y, d = _num(p[0]), int(p[1]), int(p[2]), DIRS[p[3]]
            flags = set(p[4:])
            unknown = flags - {"Z_UPPER", "SHOW_TITLE", "SET_PARENT", "STARTUP_EVENT", "NO_FADE_IN", "AIRSHIP"}
            if unknown:
                raise EventAsmError(f"unknown load_map flags {unknown}")
            w = m | (d << 12) | (0x400 if "Z_UPPER" in flags else 0) | (0x800 if "SHOW_TITLE" in flags else 0) \
                | (0x200 if "SET_PARENT" in flags else 0)
            f2 = (0x80 if "STARTUP_EVENT" in flags else 0) | (0x40 if "NO_FADE_IN" in flags else 0) \
                | (0x01 if "AIRSHIP" in flags else 0)
            if "AIRSHIP" in flags and m > 2:
                raise EventAsmError("AIRSHIP only when loading a world map ($000-$002)")
            self._emit(line, [0x6A, w & 0xFF, w >> 8, x, y, f2])
        elif op == "party_step":
            d, n = args.split()
            n = int(n)
            if not 1 <= n <= 8:
                raise EventAsmError("party_step 1..8")
            self._emit(line, [0x31, 0x82, 0x80 | ((n - 1) << 2) | DIRS[d], 0xFF])
        elif op == "take_item":
            self._emit(line, [0x81, _num(args)])
        elif op == "shop":
            self._emit(line, [0x9B, _num(args)])
        elif op == "world_end":
            self._emit(line, [0xFF])
        elif op == "party_case":
            self._emit(line, [0xDE])
        elif op == "load_pal":
            sl, pl = (_num(t) for t in args.split())
            if not (0 <= sl <= 15 and 0 <= pl <= 0xFF):
                raise EventAsmError("load_pal: CGRAM palette row 0-15 (8-15 = sprite slots 0-7), palette 0-255")
            self._emit(line, [0x60, sl, pl])
        elif op == "set_tiles":
            p = args.split()
            layer = {"BG1": 0, "BG2": 0x40}[p[0]]
            x, y, w, hh = (int(t) for t in p[1:5])
            tiles = [int(t, 16) for t in p[5:]]
            if not (0 <= x <= 255 and 0 <= y <= 63 and w >= 1 and hh >= 1 and len(tiles) == w * hh):
                raise EventAsmError("set_tiles: BG x y(0-63) w h + w*h tile bytes")
            self._emit(line, [0x73, x, layer | y, w, hh] + tiles)
        elif op == "colosseum":
            self._emit(line, [0x9A])
        elif op in ("status_clear", "status_set"):
            c, m = (_num(t) for t in args.split())
            if not (0 <= c <= 0x0F and 0 <= m <= 0xFFFF):
                raise EventAsmError(f"{op}: character $00-$0F, 16-bit mask")
            self._emit(line, [0x88 if op == "status_clear" else 0x89, c, m & 0xFF, m >> 8])
        elif op in ("char_prop", "obj_gfx", "char_name", "char_party"):
            c, v = (_num(t) for t in args.split())
            lim = {"char_prop": 0x3F, "obj_gfx": 0xFF, "char_name": 0x3F, "char_party": 7}[op]
            if not (0 <= c <= 0x0F and 0 <= v <= lim):
                raise EventAsmError(f"{op}: character/object $00-$0F, operand <= ${lim:02X}")
            self._emit(line, [{"char_prop": 0x40, "obj_gfx": 0x37, "char_name": 0x7F, "char_party": 0x3F}[op], c, v])
        elif op in ("give_gp", "take_gp"):
            v = _num(args)
            if not 1 <= v <= 0xFFFF:
                raise EventAsmError(f"{op}: amount 1-65535")
            self._emit(line, [0x84 if op == "give_gp" else 0x85, v & 0xFF, v >> 8])
        elif op == "loop":
            v = _num(args)
            if not 1 <= v <= 0xFE:
                raise EventAsmError("loop count 1-254 ($FF = loop-until-bit is not supported)")
            self._emit(line, [0xB0, v])
        elif op == "end_loop":
            self._emit(line, [0xB1])
        elif op in ("create_obj", "delete_obj"):
            c = _num(args)
            if not 0 <= c <= 0x0F:
                raise EventAsmError(f"{op}: character object $00-$0F only")
            self._emit(line, [0x3D if op == "create_obj" else 0x3E, c])
        elif op in ("give_ext_item", "take_ext_item", "has_ext_item"):
            if not self.ext_items:
                raise EventAsmError(f"{op} needs the TECH v0.7.1 item engine (event opcodes $66-$68)")
            ids, _, lab = args.partition("->")
            i = _num(ids)
            if not 0x100 <= i <= 0x13F:
                raise EventAsmError(f"{op}: extended item id must be $100-$13F")
            if op == "has_ext_item":
                name = lab.strip()
                if name in self.readonly:
                    raise EventAsmError(f"{name} is a vanilla read-only bit; project scripts may not write it")
                b = self._bit(name)
                if b > 0x6FF:
                    raise EventAsmError("switch out of range")
                self._emit(line, [0x68, i & 0xFF, i >> 8, b & 0xFF, b >> 8])
            else:
                if lab:
                    raise EventAsmError(f"{op} takes no switch")
                self._emit(line, [0x66 if op == "give_ext_item" else 0x67, i & 0xFF, i >> 8])
        elif op in ("give_rare", "take_rare", "has_rare"):
            if self.ext_items != "v09":
                raise EventAsmError(f"{op} needs the TECH v0.9 item engine (event opcodes $69 / $6D / $6E)")
            ids, _, lab = args.partition("->")
            i = _num(ids)
            if not 0 <= i <= 51:
                raise EventAsmError(f"{op}: rare id must be 0-51")
            if op == "has_rare":
                name = lab.strip()
                if name in self.readonly:
                    raise EventAsmError(f"{name} is a vanilla read-only bit; project scripts may not write it")
                b = self._bit(name)
                if b > 0x6FF:
                    raise EventAsmError("switch out of range")
                self._emit(line, [0x6E, i, b & 0xFF, b >> 8])
            else:
                if lab:
                    raise EventAsmError(f"{op} takes no switch")
                self._emit(line, [0x69 if op == "give_rare" else 0x6D, i])
        else:
            raise EventAsmError(f"unsupported command '{op}'")

    def assemble(self):
        for pos, lab in self.fix:
            if lab in self.labels:
                tgt = self.labels[lab]
            elif lab in self.ext:
                tgt = self.ext[lab]
            elif lab.startswith("$"):
                tgt = _num(lab)
            else:
                raise EventAsmError(f"undefined label {lab}")
            self.code[pos:pos + 3] = event_offset(tgt).to_bytes(3, "little")
        res = []
        for k, (a, d, t) in enumerate(self.listing):
            n = len(d)
            res.append((a, bytes(self.code[a - self.org:a - self.org + n]), t))
        self.listing = res
        return bytes(self.code)

    def listing_text(self):
        return "\n".join(f"{a >> 16:02X}:{a & 0xFFFF:04X}  {d.hex(' ').upper():<22} {t}" for a, d, t in self.listing)
