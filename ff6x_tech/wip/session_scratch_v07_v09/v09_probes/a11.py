# quick: J1 only
import sys, os
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_qa import boot_new_game, inv16, write_sram, continue_slot1
from emu_equip_stress_v08 import save_menu
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
clean="/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"
hv=T(clean); boot_new_game(hv)
hv.run_event(sum(([0x80, v] for v in range(0x27, 0x2F)), []) + [0x80, 0xE9, 0x80, 0xE9])
vinv=inv16(hv); print('vinv', vinv, hv.rbytes(0x1E1D,6).hex())
vblk, vsram = save_menu(hv); hv.close()
hq=T(S+'/o09/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'); write_sram(hq,vblk,vsram); continue_slot1(hq)
print('qinv', inv16(hq), hq.rbytes(0x1E1D,6).hex(), [hex(i) for s,i,n in hq.inv() if i>=0x100])
