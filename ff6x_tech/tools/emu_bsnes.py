#!/usr/bin/env python3
"""TECH v0.9.3: a second, cycle-accurate emulator for the visual checks - bsnes (libretro core) driven through a minimal
ctypes libretro frontend, with the same API as tools/emu_harness.H (step / press / r8 / r16 / w8 / shot / evpc and
h.em.get_screen / get_state / set_state, h.gd.update_ram / memory.extract / assign / blocks), so the existing
helpers (emu_item_tech.T, emu_enablers_v092, ...) run unchanged on it. Extra: vram() / cgram() / oam() raw dumps.

Why: the v0.9.3 visual checks render on two independent emulators (snes9x via stable-retro, and bsnes with the accurate
PPU) and inspect frames, VRAM, CGRAM and OAM; the v0.9.2 evidence used snes9x only, and a test path that differed from
the user's (ROOT_CAUSE_VISUAL_v0.9.3.md).

The core: bsnes (https://github.com/bsnes-emu/bsnes, GPLv3) built as target=libretro with one extra translation unit
(tools/bsnes_ff6x/ff6x_dump.cpp, copied to bsnes/target-libretro/ff6x_dump.cpp) that exports retro_ff6x_wram /
retro_ff6x_dump. Build: tools/build_bsnes_core.sh. Location: env FF6X_BSNES_CORE (default
/tmp/claude-0/bsnes/bsnes/out/bsnes_libretro.so). PPU: env FF6X_BSNES_PPU = accurate (default) | fast.
"""
import ctypes as C, os, numpy as np
from PIL import Image

CORE = os.environ.get("FF6X_BSNES_CORE", "/tmp/claude-0/bsnes/bsnes/out/bsnes_libretro.so")
os.environ.setdefault("FF6X_BSNES_GAMMA", "1.0")      # raw 5-bit colours (bsnes default gamma 1.5 is a display filter)
BTN = ["B", "Y", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A", "X", "L", "R"]

ENV_GET_OVERSCAN, ENV_GET_CAN_DUPE, ENV_SET_PIXEL_FORMAT, ENV_GET_SYSTEM_DIR, ENV_GET_VARIABLE = 2, 3, 10, 9, 15
ENV_GET_VARIABLE_UPDATE, ENV_GET_SAVE_DIR = 17, 31


class retro_game_info(C.Structure):
    _fields_ = [("path", C.c_char_p), ("data", C.c_void_p), ("size", C.c_size_t), ("meta", C.c_char_p)]


class retro_variable(C.Structure):
    _fields_ = [("key", C.c_char_p), ("value", C.c_char_p)]


ENV_CB = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO_CB = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO_CB = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDIO_BATCH_CB = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_CB = C.CFUNCTYPE(None)
STATE_CB = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)

_LIB = None


class _Core:
    """one process-wide core instance (libretro cores are singletons)"""

    def __init__(self):
        self.lib = C.CDLL(CORE)
        self.mask = [0] * 12
        self.frame = np.zeros((224, 256, 3), np.uint8)
        self.ppu = os.environ.get("FF6X_BSNES_PPU", "accurate")
        import tempfile
        self._tmp = tempfile.mkdtemp(prefix="ff6x_bsnes_")
        self._sysdir = C.c_char_p(self._tmp.encode())       # system / save directory: fresh per load (see load())
        self._vars = {b"bsnes_ppu_fast": b"OFF" if self.ppu == "accurate" else b"ON",
                      b"bsnes_ppu_show_overscan": b"OFF", b"bsnes_blur_emulation": b"OFF",
                      b"bsnes_run_ahead_frames": b"OFF"}
        self._keep = []
        self.cb = [ENV_CB(self._env), VIDEO_CB(self._video), AUDIO_CB(lambda l, r: None),
                   AUDIO_BATCH_CB(lambda d, n: n), POLL_CB(lambda: None), STATE_CB(self._state)]
        L = self.lib
        L.retro_set_environment(self.cb[0])
        L.retro_set_video_refresh(self.cb[1])
        L.retro_set_audio_sample(self.cb[2])
        L.retro_set_audio_sample_batch(self.cb[3])
        L.retro_set_input_poll(self.cb[4])
        L.retro_set_input_state(self.cb[5])
        L.retro_init()
        L.retro_ff6x_wram.restype = C.c_void_p
        L.retro_serialize_size.restype = C.c_size_t
        L.retro_serialize.argtypes = [C.c_void_p, C.c_size_t]
        L.retro_unserialize.argtypes = [C.c_void_p, C.c_size_t]
        L.retro_ff6x_dump.argtypes = [C.c_uint, C.c_void_p]
        self.loaded = False

    def _env(self, cmd, data):
        cmd &= 0xFFFF
        if cmd == ENV_SET_PIXEL_FORMAT:
            self.fmt = C.cast(data, C.POINTER(C.c_int))[0]
            return True
        if cmd in (ENV_GET_SYSTEM_DIR, ENV_GET_SAVE_DIR):
            C.cast(data, C.POINTER(C.c_char_p))[0] = self._sysdir      # pointer stays valid (held by self)
            return True
        if cmd == ENV_GET_VARIABLE:
            v = C.cast(data, C.POINTER(retro_variable))[0]
            val = self._vars.get(v.key)
            if val is None:
                return False
            buf = C.create_string_buffer(val); self._keep.append(buf)    # stable C memory, held by self
            C.cast(data, C.POINTER(C.c_void_p))[1] = C.addressof(buf)    # retro_variable.value (2nd pointer)
            return True
        if cmd == ENV_GET_VARIABLE_UPDATE:
            C.cast(data, C.POINTER(C.c_bool))[0] = False
            return True
        if cmd == ENV_GET_CAN_DUPE:
            C.cast(data, C.POINTER(C.c_bool))[0] = True
            return True
        if cmd == ENV_GET_OVERSCAN:
            C.cast(data, C.POINTER(C.c_bool))[0] = False
            return True
        return False

    def _video(self, data, w, h, pitch):
        if not data:
            return
        if getattr(self, "fmt", 0) == 1:                       # XRGB8888
            a = np.ctypeslib.as_array(C.cast(data, C.POINTER(C.c_uint32)), shape=(h, pitch // 4))[:, :w]
            rgb = np.stack([(a >> 16) & 0xFF, (a >> 8) & 0xFF, a & 0xFF], axis=-1).astype(np.uint8)
        else:                                                   # RGB565
            a = np.ctypeslib.as_array(C.cast(data, C.POINTER(C.c_uint16)), shape=(h, pitch // 2))[:, :w]
            rgb = np.stack([((a >> 11) & 31) * 255 // 31, ((a >> 5) & 63) * 255 // 63, (a & 31) * 255 // 31],
                           axis=-1).astype(np.uint8)
        if w >= 512:                                            # hi-res output -> 256 wide
            rgb = rgb[:, ::2]
        if h >= 448:
            rgb = rgb[::2]
        self.frame = rgb.copy()

    def _state(self, port, device, index, id_):
        if port != 0 or device != 1:
            return 0
        if id_ == 256:
            return sum(1 << i for i, b in enumerate(self.mask) if b)
        return 1 if id_ < 12 and self.mask[id_] else 0

    def load(self, rom):
        """every load starts with blank battery RAM, like stable-retro: the core reads / writes <save dir>/<rom>.srm,
        so each load gets a new empty save directory (a .srm left by an earlier run would make the title screen
        default to Continue)"""
        import tempfile
        if self.loaded:
            # a reload must reset the whole core: with only unload + load, the SMP cothread could resume against
            # the previous CPU thread (segfault in SMP::readIO $F4 after a field-map session, seen in this cycle)
            self.lib.retro_unload_game()
            self.lib.retro_deinit()
            L = self.lib
            L.retro_set_environment(self.cb[0]); L.retro_set_video_refresh(self.cb[1])
            L.retro_set_audio_sample(self.cb[2]); L.retro_set_audio_sample_batch(self.cb[3])
            L.retro_set_input_poll(self.cb[4]); L.retro_set_input_state(self.cb[5])
            L.retro_init()
        self._keep.append(self._sysdir)                 # the core may still hold the previous directory pointer
        self._sysdir = C.c_char_p(tempfile.mkdtemp(prefix="ff6x_bsnes_").encode())
        self.romdata = open(rom, "rb").read()
        self._keep.append(getattr(self, "_rb", None))   # previous ROM buffer / info stay valid for the process lifetime
        self._keep.append(getattr(self, "_info", None))
        self._rb = C.create_string_buffer(self.romdata, len(self.romdata))
        self._path = C.c_char_p(rom.encode())             # kept alive: the core may keep the path / info pointers
        self._info = info = retro_game_info(self._path.value, C.cast(self._rb, C.c_void_p), len(self.romdata), None)
        if not self.lib.retro_load_game(C.byref(info)):
            raise RuntimeError("bsnes: retro_load_game failed")
        self.lib.retro_set_controller_port_device(0, 1)
        self.loaded = True
        self.wram = np.ctypeslib.as_array(C.cast(self.lib.retro_ff6x_wram(), C.POINTER(C.c_uint8)), shape=(0x20000,))
        self.lib.retro_ff6x_sram.restype = C.c_void_p
        n = self.lib.retro_ff6x_sram_size()
        self.sram = np.ctypeslib.as_array(C.cast(self.lib.retro_ff6x_sram(), C.POINTER(C.c_uint8)), shape=(n,)) if n else None


def core():
    global _LIB
    if _LIB is None:
        _LIB = _Core()
    return _LIB


SRAM_KEY = 0x306000                                     # cartridge battery RAM (HiROM $30:6000), as stable-retro's blocks


class _Mem:
    def __init__(self, c):
        self.c = c

    @property
    def blocks(self):
        b = {0x7E0000: self.c.wram.tobytes()}
        if self.c.sram is not None:
            b[SRAM_KEY] = self.c.sram.tobytes()
        return b

    def _ref(self, addr):
        if self.c.sram is not None and SRAM_KEY <= addr < SRAM_KEY + len(self.c.sram):
            return self.c.sram, addr - SRAM_KEY
        return self.c.wram, (addr - 0x7E0000) & 0x1FFFF

    def extract(self, addr, fmt="|u1"):
        a, i = self._ref(addr)
        return int(a[i])

    def assign(self, addr, fmt, v):
        a, i = self._ref(addr)
        a[i] = v & 0xFF


class _GD:
    def __init__(self, c):
        self.memory = _Mem(c)

    def update_ram(self):
        pass


class _EM:
    def __init__(self, c):
        self.c = c

    def get_screen(self):
        return self.c.frame.copy()

    def get_state(self):
        n = self.c.lib.retro_serialize_size()
        buf = C.create_string_buffer(n)
        if not self.c.lib.retro_serialize(buf, n):
            raise RuntimeError("bsnes: serialize failed")
        return buf.raw

    def set_state(self, st):
        buf = C.create_string_buffer(st, len(st))
        if not self.c.lib.retro_unserialize(buf, len(st)):
            raise RuntimeError("bsnes: unserialize failed")


class B:
    """drop-in replacement for emu_harness.H on bsnes"""

    def __init__(s, rom):
        s.c = core()
        s.c.load(rom)
        s.em, s.gd, s.f = _EM(s.c), _GD(s.c), 0

    def close(s):
        pass

    def step(s, n=1, btn=()):
        for i, b in enumerate(BTN):
            s.c.mask[i] = 1 if b in btn else 0
        for _ in range(n):
            s.c.lib.retro_run(); s.f += 1

    def press(s, b, hold=4, rel=8):
        s.step(hold, (b,)); s.step(rel)

    def r8(s, a):
        return int(s.c.wram[a & 0x1FFFF])

    def r16(s, a):
        return s.r8(a) | s.r8(a + 1) << 8

    def w8(s, a, v):
        s.c.wram[a & 0x1FFFF] = v & 0xFF

    def shot(s, p):
        Image.fromarray(s.em.get_screen()).resize((512, 448), Image.NEAREST).save(p)

    def evpc(s):
        return s.r8(0xE5) | s.r8(0xE6) << 8 | s.r8(0xE7) << 16

    def _dump(s, which, n):
        buf = (C.c_uint8 * n)()
        s.c.lib.retro_ff6x_dump(which, buf)
        return bytes(buf)

    def vram(s):
        return s._dump(0, 0x10000)

    def cgram(s):
        return s._dump(1, 512)

    def oam(s):
        return s._dump(2, 544)


def use_bsnes():
    """make emu_harness.H (and every class built on it, e.g. emu_item_tech.T) run on bsnes"""
    import emu_harness
    for name in ("__init__", "close", "step", "press", "r8", "r16", "w8", "shot", "evpc", "_dump", "vram", "cgram",
                 "oam"):
        setattr(emu_harness.H, name, getattr(B, name))
