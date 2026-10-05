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
  TECH v0.7.1 extended-item API (only when the target carries the item engine, ext_items=True):
    give_ext_item <id $100-$13F>               # event cmd $66 lo hi   (XC0_Ev66 -> XGiveExt)
    take_ext_item <id $100-$13F>               # event cmd $67 lo hi   (XC0_Ev67 -> XTakeExt)
    has_ext_item <id $100-$13F> -> <BIT_NAME>  # event cmd $68 lo hi sw (XC0_Ev68 -> XHasExt: bit := owned)
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
            unknown = flags - {"Z_UPPER", "SHOW_TITLE", "SET_PARENT", "STARTUP_EVENT", "NO_FADE_IN"}
            if unknown:
                raise EventAsmError(f"unknown load_map flags {unknown}")
            w = m | (d << 12) | (0x400 if "Z_UPPER" in flags else 0) | (0x800 if "SHOW_TITLE" in flags else 0) \
                | (0x200 if "SET_PARENT" in flags else 0)
            f2 = (0x80 if "STARTUP_EVENT" in flags else 0) | (0x40 if "NO_FADE_IN" in flags else 0)
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
        elif op == "colosseum":
            self._emit(line, [0x9A])
        elif op in ("status_clear", "status_set"):
            c, m = (_num(t) for t in args.split())
            if not (0 <= c <= 0x0F and 0 <= m <= 0xFFFF):
                raise EventAsmError(f"{op}: character $00-$0F, 16-bit mask")
            self._emit(line, [0x88 if op == "status_clear" else 0x89, c, m & 0xFF, m >> 8])
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
