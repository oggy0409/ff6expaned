"""Deterministic two-pass 65816 assembler for builder-owned hook/routine sources (TECH v0.7.1+).

Syntax (a reviewable subset of ca65):
    .section NAME $C3F091      start a section at a fixed 24-bit SNES origin (all labels are global)
    .a8 .a16 .i8 .i16          declare M/X width (decides immediate operand size; never inferred)
    NAME = expr                constant
    label:                     label (address = current section pc)
    .byte e, e, "TEXT"         .word e, ...   .faraddr e, ...  (3 bytes)   .res n, fill
    mnemonic operand           all 256 opcodes (ff6x/op65816.py)
Operands:  #e (#<e #>e #^e)  e  e,x  e,y  (e)  (e),y  (e,x)  [e]  [e],y  e,s  (e,s),y  a:e  f:e  z:e
Sizing:    f: = long, a: = absolute, z: = direct page. Without a prefix a pure number <= $FF is direct page,
           <= $FFFF absolute, else long; any expression containing a symbol is ABSOLUTE (bank-relative,
           the symbol's low 16 bits) unless f: is given. JSR/JMP take absolute, JSL/JML long.
           Branches are relative (BRL/PER 16-bit). Absolute operands referring to a symbol must lie in the
           same bank as the instruction (checked) unless written with an explicit a: prefix.
Local labels: @name is scoped to the preceding global label (ca65 cheap locals).
Expressions: + - * & | << >> ( ) unary < > ^ - ; $hex %bin decimal 'c' ; label, label+n.
"""
import re
from .op65816 import OPCODES, BY_NAME

BRANCH8 = {"BPL", "BMI", "BVC", "BVS", "BCC", "BCS", "BNE", "BEQ", "BRA"}


class AsmError(Exception):
    pass


class _Expr:
    TOK = re.compile(r"\s*(\$[0-9A-Fa-f]+|%[01]+|\d+|'.'|[A-Za-z_@.][\w.@]*|<<|>>|[-+*&|^()<>~])")

    def __init__(self, text, syms, pc):
        self.toks = []
        pos = 0
        text = text.strip()
        while pos < len(text):
            m = self.TOK.match(text, pos)
            if not m:
                raise AsmError(f"bad expression '{text}'")
            self.toks.append(m.group(1))
            pos = m.end()
        self.i, self.syms, self.pc, self.used_sym = 0, syms, pc, False

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self):
        t = self.peek(); self.i += 1; return t

    def parse(self):
        v = self.p_or()
        if self.peek() is not None:
            raise AsmError(f"trailing tokens in expression: {self.toks[self.i:]}")
        return v

    def p_or(self):
        v = self.p_and()
        while self.peek() == "|":
            self.take(); v |= self.p_and()
        return v

    def p_and(self):
        v = self.p_shift()
        while self.peek() == "&":
            self.take(); v &= self.p_shift()
        return v

    def p_shift(self):
        v = self.p_add()
        while self.peek() in ("<<", ">>"):
            op = self.take(); r = self.p_add()
            v = v << r if op == "<<" else v >> r
        return v

    def p_add(self):
        v = self.p_mul()
        while self.peek() in ("+", "-"):
            op = self.take(); r = self.p_mul()
            v = v + r if op == "+" else v - r
        return v

    def p_mul(self):
        v = self.p_un()
        while self.peek() == "*":
            self.take(); v *= self.p_un()
        return v

    def p_un(self):
        t = self.peek()
        if t == "<":
            self.take(); return self.p_un() & 0xFF
        if t == ">":
            self.take(); return (self.p_un() >> 8) & 0xFF
        if t == "^":
            self.take(); return (self.p_un() >> 16) & 0xFF
        if t == "-":
            self.take(); return -self.p_un()
        if t == "~":
            self.take(); return ~self.p_un()
        return self.p_atom()

    def p_atom(self):
        t = self.take()
        if t is None:
            raise AsmError("unexpected end of expression")
        if t == "(":
            v = self.p_or()
            if self.take() != ")":
                raise AsmError("missing )")
            return v
        if t.startswith("$"):
            return int(t[1:], 16)
        if t.startswith("%"):
            return int(t[1:], 2)
        if t[0].isdigit():
            return int(t)
        if t.startswith("'"):
            return ord(t[1])
        if t == "*":
            return self.pc
        self.used_sym = True
        if t not in self.syms:
            raise _Undef(t)
        return self.syms[t]


class _Undef(Exception):
    pass


def _split_args(s):
    out, depth, cur, q = [], 0, "", False
    for ch in s:
        if ch == '"':
            q = not q
        if not q and ch in "([":
            depth += 1
        if not q and ch in ")]":
            depth -= 1
        if ch == "," and depth == 0 and not q:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


class Program:
    """Assemble one or more sections. `externs` = name -> 24-bit address (vanilla symbols, other modules)."""

    def __init__(self, source, externs=None, name="asm"):
        self.name = name
        self.src = source
        self.externs = dict(externs or {})
        self.sections = {}          # name -> {"org", "code": bytearray, "listing": []}
        self.symbols = {}

    # ------------------------------------------------------------------ parsing helpers
    def _lines(self):
        for n, raw in enumerate(self.src.split("\n"), 1):
            line = raw
            # strip comments (not inside strings)
            q = False
            for i, ch in enumerate(line):
                if ch == '"':
                    q = not q
                if ch == ";" and not q:
                    line = line[:i]; break
            yield n, raw, line.rstrip()

    def _eval(self, text, pc, final):
        syms = dict(self.externs); syms.update(self.symbols)
        e = _Expr(text, syms, pc)
        try:
            return e.parse(), e.used_sym
        except _Undef as u:
            if final:
                raise AsmError(f"{self.name}: undefined symbol '{u.args[0]}'")
            return 0, True

    def _operand(self, mn, op, m8, x8, pc, final):
        """-> (mode, value, size, used_sym, explicit_abs)"""
        op = op.strip()
        if op == "":
            return ("imp", None, 0, False, False)
        if op.upper() == "A":
            return ("acc", None, 0, False, False)
        if mn in ("MVN", "MVP"):
            a, b = _split_args(op)
            va, _ = self._eval(a.lstrip("#"), pc, final); vb, _ = self._eval(b.lstrip("#"), pc, final)
            return ("blk", (va & 0xFF, vb & 0xFF), 2, False, False)
        if op.startswith("#"):
            body = op[1:]
            v, us = self._eval(body, pc, final)
            mode = "imm8" if (mn, "imm8") in BY_NAME else ("immm" if (mn, "immm") in BY_NAME else "immx")
            if mode == "imm8":
                return (mode, v, 1, us, False)
            flag = m8 if mode == "immm" else x8
            if flag is None:
                raise AsmError(f"{mn} immediate after PLP/RTI: declare .a8/.a16/.i8/.i16 first")
            w = 1 if flag else 2
            return (mode, v, w, us, False)
        if mn in BRANCH8:
            v, us = self._eval(op, pc, final)
            return ("rel8", v, 1, us, False)
        if mn in ("BRL", "PER"):
            v, us = self._eval(op, pc, final)
            return ("rel16", v, 2, us, False)
        m = re.fullmatch(r"\((.*),\s*[sS]\)\s*,\s*[yY]", op)
        if m:
            v, us = self._eval(m.group(1), pc, final); return ("sriy", v, 1, us, False)
        m = re.fullmatch(r"(.*),\s*[sS]", op)
        if m:
            v, us = self._eval(m.group(1), pc, final); return ("sr", v, 1, us, False)
        m = re.fullmatch(r"\[(.*)\]\s*,\s*[yY]", op)
        if m:
            v, us = self._eval(m.group(1), pc, final); return ("dpily", v, 1, us, False)
        m = re.fullmatch(r"\[(.*)\]", op)
        if m:
            inner = m.group(1).strip()
            if mn == "JML" or inner.startswith("a:"):
                v, us = self._eval(inner[2:] if inner.startswith("a:") else inner, pc, final)
                return ("absil", v, 2, us, True)
            v, us = self._eval(inner, pc, final); return ("dpil", v, 1, us, False)
        m = re.fullmatch(r"\((.*),\s*[xX]\)", op)
        if m:
            inner = m.group(1).strip()
            if mn in ("JMP", "JSR"):
                v, us = self._eval(inner.replace("a:", ""), pc, final); return ("absix", v, 2, us, True)
            v, us = self._eval(inner, pc, final); return ("dpix", v, 1, us, False)
        m = re.fullmatch(r"\((.*)\)\s*,\s*[yY]", op)
        if m:
            v, us = self._eval(m.group(1), pc, final); return ("dpiy", v, 1, us, False)
        m = re.fullmatch(r"\(([^()]*)\)", op)
        if m:
            inner = m.group(1).strip()
            if mn == "JMP":
                v, us = self._eval(inner.replace("a:", ""), pc, final); return ("absi", v, 2, us, True)
            v, us = self._eval(inner, pc, final); return ("dpi", v, 1, us, False)
        idx = None
        mm = re.fullmatch(r"(.*),\s*([xXyY])", op)
        if mm:
            op, idx = mm.group(1).strip(), mm.group(2).lower()
        force = None
        if op[:2] in ("f:", "a:", "z:"):
            force, op = op[0], op[2:]
        v, us = self._eval(op, pc, final)
        if mn in ("JSL", "JML"):
            size = "l"
        elif mn in ("JSR", "JMP"):
            size = "a"
        elif force:
            size = {"f": "l", "a": "a", "z": "d"}[force]
        elif us:
            size = "a"
        else:
            size = "d" if 0 <= v <= 0xFF else ("a" if v <= 0xFFFF else "l")
        mode = {("d", None): "dp", ("d", "x"): "dpx", ("d", "y"): "dpy", ("a", None): "abs", ("a", "x"): "absx",
                ("a", "y"): "absy", ("l", None): "absl", ("l", "x"): "abslx"}.get((size, idx))
        if mode is None or (mn, mode) not in BY_NAME:
            # fall back dp -> abs (e.g. LDX dp,Y exists but STZ dp,Y does not)
            if size == "d" and (mn, {"dpx": "absx", "dpy": "absy", "dp": "abs"}[mode or "dp"]) in BY_NAME:
                mode = {"dpx": "absx", "dpy": "absy", "dp": "abs"}[mode]
            else:
                raise AsmError(f"{self.name}: no addressing mode {mode} for {mn} {op}")
        n = {"dp": 1, "dpx": 1, "dpy": 1, "abs": 2, "absx": 2, "absy": 2, "absl": 3, "abslx": 3}[mode]
        return (mode, v, n, us, force == "a")

    # ------------------------------------------------------------------ assembly
    def _pass(self, final):
        sec = None
        pc = None
        m8 = x8 = True
        glob = ""
        secname = None
        for n, raw, line in self._lines():
            if secname is not None:
                self._cursor[secname] = pc          # keep the per-section cursor current on every path
            s = line.strip()
            if not s:
                continue
            lm0 = re.match(r"^([A-Za-z_][\w.]*):", s)
            if lm0:
                glob = lm0.group(1)
            s = re.sub(r"(?<![\w.])@(\w+)", lambda m: f"{glob}@{m.group(1)}", s)
            try:
                lm = re.match(r"^([A-Za-z_][\w@.]*):\s*(.*)$", s)
                if lm:
                    lab = lm.group(1)
                    if pc is None:
                        raise AsmError("label outside section")
                    if not final:
                        if lab in self.symbols and self._pass_no == 1:
                            raise AsmError(f"duplicate label {lab}")
                        self.symbols[lab] = pc
                    elif self.symbols[lab] != pc:
                        raise AsmError(f"label {lab} moved between passes")
                    if final:
                        sec["listing"].append((pc, b"", lab + ":"))
                    s = lm.group(2).strip()
                    if not s:
                        continue
                cm = re.match(r"^([A-Za-z_][\w.]*)\s*=\s*(.+)$", s)
                if cm:
                    v, _ = self._eval(cm.group(2), pc or 0, final)
                    self.symbols[cm.group(1)] = v
                    continue
                parts = s.split(None, 1)
                kw = parts[0]
                arg = parts[1] if len(parts) > 1 else ""
                kwl = kw.lower()
                if kwl == ".section":
                    nm, org = arg.split()
                    org = int(org.lstrip("$"), 16)
                    sec = self.sections.setdefault(nm, {"org": org, "code": bytearray(), "listing": []})
                    secname = nm
                    if sec["org"] != org:
                        raise AsmError(f"section {nm} re-opened at a different origin")
                    pc = sec["org"] + len(sec["code"]) if final else self._cursor.get(nm, org)
                    m8 = x8 = True
                    continue
                if kwl in (".a8", ".a16", ".i8", ".i16"):
                    if kwl == ".a8": m8 = True
                    if kwl == ".a16": m8 = False
                    if kwl == ".i8": x8 = True
                    if kwl == ".i16": x8 = False
                    continue
                if kwl in (".byte", ".word", ".faraddr", ".res"):
                    data = bytearray()
                    if kwl == ".res":
                        a = _split_args(arg)
                        cnt, _ = self._eval(a[0], pc, True)
                        fill = self._eval(a[1], pc, True)[0] if len(a) > 1 else 0
                        data = bytearray([fill & 0xFF] * cnt)
                    else:
                        for a in _split_args(arg):
                            if a.startswith('"'):
                                data += a.strip('"').encode("ascii"); continue
                            v, _ = self._eval(a, pc, final)
                            w = {".byte": 1, ".word": 2, ".faraddr": 3}[kwl]
                            if final and not (-(1 << (8 * w - 1)) <= v < (1 << (8 * w))):
                                raise AsmError(f"value {v:#x} does not fit {kwl}")
                            data += (v & ((1 << (8 * w)) - 1)).to_bytes(w, "little")
                    self._emit(sec, pc, bytes(data), s, final)
                    pc += len(data)
                    continue
                mn = kw.upper()
                if not any(k[0] == mn for k in BY_NAME):
                    raise AsmError(f"unknown mnemonic/directive '{kw}'")
                mode, v, size, us, explicit_abs = self._operand(mn, arg, m8, x8, pc, final)
                op = BY_NAME[(mn, mode)]
                b = bytearray([op])
                if mode in ("rel8", "rel16"):
                    rel = v - (pc + 1 + size)
                    if final:
                        lim = 0x80 if size == 1 else 0x8000
                        if not -lim <= rel < lim:
                            raise AsmError(f"branch out of range ({rel}) to {arg}")
                    b += (rel & ((1 << (8 * size)) - 1)).to_bytes(size, "little")
                elif mode == "blk":
                    b += bytes([v[1], v[0]])         # MVN src,dst -> opcode dst src
                elif size:
                    if mode in ("abs", "absx", "absy", "absi", "absix", "absil") and us and not explicit_abs and final:
                        if mn in ("JSR", "JMP") and mode in ("abs",) and (v >> 16) != (pc >> 16) and v > 0xFFFF:
                            raise AsmError(f"{mn} to {arg} ({v:06X}) crosses bank from {pc:06X}")
                        if mn not in ("JSR", "JMP", "PEA") and v > 0xFFFF and (v >> 16) != (pc >> 16):
                            raise AsmError(f"absolute operand {arg} ({v:06X}) is in another bank than {pc:06X}; use f: or a:")
                    if final and mode not in ("immm", "immx", "imm8") and v > 0xFFFFFF:
                        raise AsmError("operand too large")
                    if final and mode in ("immm", "immx", "imm8") and not (-(1 << (8 * size - 1)) <= v < (1 << (8 * size))):
                        raise AsmError(f"immediate {v:#x} does not fit {size} byte(s): {s}")
                    b += (v & ((1 << (8 * size)) - 1)).to_bytes(size, "little")
                if mn in ("PLP", "RTI"):
                    m8 = x8 = None          # width unknown until declared
                if mn == "REP" and v is not None:
                    if v & 0x20: m8 = False
                    if v & 0x10: x8 = False
                if mn == "SEP" and v is not None:
                    if v & 0x20: m8 = True
                    if v & 0x10: x8 = True
                self._emit(sec, pc, bytes(b), s, final)
                pc += len(b)
            except AsmError as e:
                raise AsmError(f"{self.name} line {n}: {e}  [{raw.strip()}]")
        if secname is not None:
            self._cursor[secname] = pc

    def _emit(self, sec, pc, data, text, final):
        if final:
            if sec["org"] + len(sec["code"]) != pc:
                raise AsmError("pc mismatch")
            sec["code"] += data
            sec["listing"].append((pc, data, text))
        if (pc & 0xFFFF) + len(data) > 0x10000:
            raise AsmError(f"section crosses a bank boundary at {pc:06X}")

    def assemble(self):
        self._cursor = {}
        self._pass_no = 1
        self._pass(False)
        self._cursor = {}
        self._pass_no = 2
        self._pass(False)                     # second sizing pass with all labels known
        for s in self.sections.values():
            s["code"] = bytearray(); s["listing"] = []
        self._cursor = {}
        self._pass(True)
        return {k: (v["org"], bytes(v["code"])) for k, v in self.sections.items()}

    def listing(self, section):
        out = []
        for a, b, t in self.sections[section]["listing"]:
            out.append(f"{a >> 16:02X}:{a & 0xFFFF:04X}  {b.hex(' ').upper()[:23]:<23} {t}")
        return "\n".join(out)
