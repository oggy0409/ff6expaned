"""Menu navigation helpers for the TECH v0.7.1 emulator checks (menu state = DP $26, see menu_const.inc)."""
ST = {"MAIN": 0x05, "CHAR": 0x06, "ITEM": 0x08, "ITEM_OPT": 0x17, "ITEM_MOVE": 0x19, "EQUIP_OPT": 0x36,
      "EQUIP_SLOT": 0x55, "EQUIP_REMOVE": 0x56, "EQUIP_LIST": 0x57, "RELIC_OPT": 0x59, "RELIC_SLOT": 0x5A,
      "RELIC_LIST": 0x5B, "RELIC_REMOVE": 0x5C, "SAVE_SELECT": 0x14, "SAVE_CONFIRM": 0x16, "SHOP_OPT": 0x25,
      "SHOP_SELL": 0x29, "COLO_ITEM": 0x72, "ITEM_DETAILS": 0x64}
MAIN = {"Item": 0, "Skills": 1, "Equip": 2, "Relic": 3, "Status": 4, "Config": 5, "Save": 6}


class Nav:
    def __init__(self, h, log=None):
        self.h, self.log = h, log if log is not None else []

    def state(self):
        return self.h.r8(0x26)

    def wait(self, st, frames=240):
        for _ in range(frames):
            if self.state() == st:
                self.h.step(8)
                if self.state() == st:
                    return True
            self.h.step(1)
        return False

    def press(self, b, st=None, settle=12):
        self.h.press(b, 4, settle)
        ok = True if st is None else self.wait(ST.get(st, st))
        self.log.append((b, st, f"{self.state():02X}", ok))
        if not ok:
            raise RuntimeError(f"menu: after {b} expected state {st}, got {self.state():02X}")
        return ok

    def open_main(self):
        self.h.press("X", 4, 10)
        self.wait(ST["MAIN"], 400)

    def main_to(self, name):
        tgt = MAIN[name]
        for _ in range(10):
            cur = self.h.r8(0x4B)
            if cur == tgt:
                break
            self.h.press("DOWN" if cur < tgt else "UP", 4, 10)
        self.press("A")

    def cursor_to(self, tgt, addr=0x4B):
        for _ in range(40):
            cur = self.h.r8(addr)
            if cur == tgt:
                return
            self.h.press("DOWN" if cur < tgt else "UP", 4, 10)
        raise RuntimeError(f"cursor stuck at {self.h.r8(addr)} (want {tgt})")

    def cursor_lr(self, tgt, addr=0x4B):
        for _ in range(10):
            cur = self.h.r8(addr)
            if cur == tgt:
                return
            self.h.press("RIGHT" if cur < tgt else "LEFT", 4, 10)
        raise RuntimeError(f"cursor stuck at {self.h.r8(addr)} (want {tgt})")

    def back_to_main(self):
        for _ in range(8):
            if self.state() == ST["MAIN"]:
                return
            self.h.press("B", 4, 20)
            self.h.step(20)

    def close(self):
        self.back_to_main()
        self.h.press("B", 4, 10)
        for _ in range(600):
            self.h.step(1)
            if self.h.evpc() == 0xCA0000 and self.h.r8(0x26) != ST["MAIN"]:
                pass
        self.h.step(30)
