#!/usr/bin/env python3
"""Boot -> title -> New Game -> first control; screenshots of the first vanilla
dialogue boxes (global dialogue hook regression) and saves the control state."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
rom, out, state = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
h = H(rom); idle = 0; shots = 0; last = None
for t in range(60000):
    if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
    else: h.step(1)
    if t % 10 == 0:
        ba, d0 = h.r8(0xBA), h.r16(0xD0)
        if ba and shots < 4 and d0 != last and d0:
            for _ in range(240):
                h.step(1)
                if h.em.get_screen().mean() > 12: break
            h.step(60); h.shot(os.path.join(out, f"02_opening_dlg{d0:04X}.png")); shots += 1; last = d0
        idle = idle + 1 if h.evpc() == 0xCA0000 else 0
        if idle >= 30: break
open(state, 'wb').write(h.em.get_state())
print('control at frame', h.f, 'opening dialogue shots', shots)
