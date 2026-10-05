"""Minimal, explicit 65816 assembler for small hook routines.

Only the opcodes the project actually uses are supported; each emits fixed
bytes. Immediate width is explicit in the method name (no implicit M/X
tracking) so the byte stream is fully reviewable.
"""

class Asm:
    def __init__(self, origin_snes):
        self.org = origin_snes
        self.code = bytearray()
        self.labels = {}
        self.fixups = []    # (pos, label, kind)
        self.listing = []

    @property
    def pc(self):
        return self.org + len(self.code)

    def _emit(self, text, *b):
        self.listing.append((self.pc, bytes(b), text))
        self.code += bytes(b)

    def label(self, name):
        if name in self.labels:
            raise ValueError(f"duplicate label {name}")
        self.labels[name] = self.pc
        self.listing.append((self.pc, b"", name + ":"))

    # --- processor status
    def rep(self, v): self._emit(f"REP #${v:02X}", 0xC2, v)
    def sep(self, v): self._emit(f"SEP #${v:02X}", 0xE2, v)
    def tdc(self): self._emit("TDC", 0x7B)
    # --- loads / stores
    def lda_dp(self, d): self._emit(f"LDA ${d:02X}", 0xA5, d)
    def sta_dp(self, d): self._emit(f"STA ${d:02X}", 0x85, d)
    def lda_abs(self, a): self._emit(f"LDA ${a:04X}", 0xAD, a & 0xFF, a >> 8)
    def adc_imm8(self, v): self._emit(f"ADC #${v:02X}", 0x69, v)
    def lda_imm8(self, v): self._emit(f"LDA #${v:02X}", 0xA9, v)
    def lda_imm16(self, v): self._emit(f"LDA #${v:04X}", 0xA9, v & 0xFF, v >> 8)
    def lda_long_x(self, a): self._emit(f"LDA ${a:06X},X", 0xBF, a & 0xFF, (a >> 8) & 0xFF, a >> 16)
    def cmp_imm16(self, v): self._emit(f"CMP #${v:04X}", 0xC9, v & 0xFF, v >> 8)
    def and_imm16(self, v): self._emit(f"AND #${v:04X}", 0x29, v & 0xFF, v >> 8)
    def asl_a(self): self._emit("ASL A", 0x0A)
    def and_imm8(self, v): self._emit(f"AND #${v:02X}", 0x29, v)
    def cmp_imm8(self, v): self._emit(f"CMP #${v:02X}", 0xC9, v)
    def sbc_imm8(self, v): self._emit(f"SBC #${v:02X}", 0xE9, v)
    def ldx_abs(self, a): self._emit(f"LDX ${a:04X}", 0xAE, a & 0xFF, a >> 8)
    def cpx_imm16(self, v): self._emit(f"CPX #${v:04X}", 0xE0, v & 0xFF, v >> 8)
    def lda_abs_x(self, a): self._emit(f"LDA ${a:04X},X", 0xBD, a & 0xFF, a >> 8)
    def adc_imm16(self, v): self._emit(f"ADC #${v:04X}", 0x69, v & 0xFF, v >> 8)
    def lda_abs_y(self, a): self._emit(f"LDA ${a:04X},Y", 0xB9, a & 0xFF, a >> 8)
    def sta_abs_y(self, a): self._emit(f"STA ${a:04X},Y", 0x99, a & 0xFF, a >> 8)
    def adc_sr(self, o): self._emit(f"ADC ${o:02X},S", 0x63, o)
    def pha(self): self._emit("PHA", 0x48)
    def pla(self): self._emit("PLA", 0x68)
    def phx(self): self._emit("PHX", 0xDA)
    def plx(self): self._emit("PLX", 0xFA)
    def clc(self): self._emit("CLC", 0x18)
    def sec(self): self._emit("SEC", 0x38)
    def rtl(self): self._emit("RTL", 0x6B)
    def tax(self): self._emit("TAX", 0xAA)
    # --- flow
    def jml(self, a): self._emit(f"JML ${a:06X}", 0x5C, a & 0xFF, (a >> 8) & 0xFF, a >> 16)
    def _branch(self, op, mn, label):
        self.fixups.append((len(self.code) + 1, label, "rel8"))
        self._emit(f"{mn} {label}", op, 0)
    def bcs(self, label): self._branch(0xB0, "BCS", label)
    def bcc(self, label): self._branch(0x90, "BCC", label)
    def bne(self, label): self._branch(0xD0, "BNE", label)
    def bmi(self, label): self._branch(0x30, "BMI", label)

    def assemble(self):
        for pos, label, kind in self.fixups:
            tgt = self.labels[label]
            rel = tgt - (self.org + pos + 1)
            if not -128 <= rel <= 127:
                raise ValueError(f"branch to {label} out of range")
            self.code[pos] = rel & 0xFF
        # refresh listing bytes after fixups
        out, off = [], 0
        for addr, b, text in self.listing:
            n = len(b)
            out.append((addr, bytes(self.code[off:off + n]), text)); off += n
        self.listing = out
        return bytes(self.code)

    def listing_text(self):
        return "\n".join(f"{a >> 16:02X}:{a & 0xFFFF:04X}  {b.hex(' ').upper():<14} {t}" for a, b, t in self.listing)
