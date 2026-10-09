#!/bin/bash
S=/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad
F=$S/final; E=$S/emu_final; C="/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"
QA=$F/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc; PR=$F/FF6X_Rev1_TECH_v0.7.1_PRODUCTION.sfc; CT=$F/FF6X_Rev1_TECH_v0.7.1_CELES_TECH.sfc
cd /home/user/ff6expaned/ff6x_tech
case "$1" in
 battle) timeout 4000 python3 tools/emu_item_battle.py $QA $F/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.manifest.json $E/item_battle "$C" > $E/item_battle.log 2>&1 ;;
 v061) export FF6X_QA_PREFIX=1
   timeout 3000 python3 tools/emu_enemy_tech.py save $QA $E/v061_regr > $E/v061_save.log 2>&1
   timeout 3000 python3 tools/emu_enemy_tech.py load $QA $E/v061_regr > $E/v061_load.log 2>&1
   timeout 3000 python3 tools/emu_enemy_tech.py cmds $QA $E/v061_cmds > $E/v061_cmds.log 2>&1 ;;
 celes) timeout 900 python3 tools/emu_boot.py $CT $E/celes_boot $E/celes_ctl.state > $E/celes_boot.log 2>&1
   timeout 3000 python3 tools/emu_celes_suite.py $CT $E/celes_ctl.state $E/celes > $E/celes.log 2>&1 ;;
 diff) export FF6X_XINIT=1; MAPS=$(python3 -c "print(' '.join(f'{m:03X}' for m in range(3,0x19F)))")
   timeout 7000 python3 tools/emu_map_diff.py dump $PR $S/reg/start.state $E/maps_v071.json $MAPS > $E/maps.log 2>&1
   timeout 7000 python3 tools/emu_monster_diff.py dump $PR $S/reg/start.state $E/mon_v071.json 0 23F > $E/mon.log 2>&1 ;;
esac
echo done "$1" >> $E/done.txt
