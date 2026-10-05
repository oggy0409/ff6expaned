"""Vanilla FFVI (US) field-dialogue encoder - plain characters only (no DTE).

Codes (field dialogue): $00 end, $01 newline, $13 new page, $15 choice marker,
$20-$7F single characters (A=$20 ... z=$53, 0=$54, space=$7F).
DTE codes ($80-$FF) are deliberately never emitted, so the output does not
depend on the DTE table at C0:DFA0.
"""
_CH = {}
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    _CH[c] = 0x20 + i
for c, v in {"!": 0x5E, "?": 0x5F, "/": 0x60, ":": 0x61, '"': 0x62, "'": 0x63, "-": 0x64,
             ".": 0x65, ",": 0x66, "…": 0x67, ";": 0x68, "#": 0x69, "+": 0x6A, "(": 0x6B,
             ")": 0x6C, "%": 0x6D, "~": 0x6E, "*": 0x6F, "@": 0x70, "=": 0x72, " ": 0x7F}.items():
    _CH[c] = v
TOKENS = {"{n}": 0x01, "{page}": 0x13, "{choice}": 0x15}

def encode_dialogue(text: str) -> bytes:
    out = bytearray()
    i = 0
    while i < len(text):
        for tok, code in TOKENS.items():
            if text.startswith(tok, i):
                out.append(code); i += len(tok); break
        else:
            c = text[i]
            if c not in _CH:
                raise ValueError(f"unencodable character {c!r} in {text!r}")
            out.append(_CH[c]); i += 1
    out.append(0x00)
    return bytes(out)

def decode_plain(b: bytes) -> str:
    rev = {v: k for k, v in _CH.items()}
    s = ""
    for x in b:
        if x == 0: break
        s += {0x01: "{n}", 0x13: "{page}", 0x15: "{choice}"}.get(x) or rev.get(x, f"{{{x:02X}}}")
    return s


FONT_WIDTH_SNES = 0xC48FC0     # variable-width font character widths (256 bytes)
LINE_LIMIT_PX = 0xE0 - 5       # field text: wraps when x + word >= $E0 (UpdateDlgTextOneLine: ADC width / CMP $C8 / BCC); x starts at 4 -> max 219 px (TECH v0.6 fix: was off by one)


def line_widths(encoded: bytes, widths: bytes):
    out, cur = [], 0
    for b in encoded:
        if b == 0x00:
            break
        if b in (0x01, 0x13):
            out.append(cur); cur = 0
        elif b >= 0x20:
            cur += widths[b]
    out.append(cur)
    return out
