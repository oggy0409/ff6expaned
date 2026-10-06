#!/bin/bash
S=/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad
F=$S/o09; E=$S/emu09r; C="/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"
QA=$F/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc; QM=$F/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.manifest.json
PR=$F/FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc; CT=$F/FF6X_Rev1_TECH_v0.9_CELES_TECH.sfc
export FF6X_QA_V08_ROOT='{"0": [2, 1], "1": [2, 2, 0]}'
mkdir -p $E; cd /home/user/ff6expaned/ff6x_tech
for step in "$@"; do
case "$step" in
 tech) timeout 3000 python3 tools/emu_item_tech.py $QA $E/item_tech "$C" > $E/item_tech.log 2>&1 ;;
 qa) timeout 5000 python3 tools/emu_item_qa.py $QA $PR "$C" $E/item_qa > $E/item_qa.log 2>&1 ;;
 battle) FF6X_QA_ITEM_ROOT=2,2,0,0 timeout 4000 python3 tools/emu_item_battle.py $QA $QM $E/item_battle "$C" > $E/item_battle.log 2>&1 ;;
 v061) export FF6X_QA_PREFIX=2,2,0,1 FF6X_QA_SAVE_PICKS=2,2,1
   timeout 3000 python3 tools/emu_enemy_tech.py save $QA $E/v061_regr > $E/v061_save.log 2>&1
   timeout 3000 python3 tools/emu_enemy_tech.py load $QA $E/v061_regr > $E/v061_load.log 2>&1
   timeout 3000 python3 tools/emu_enemy_tech.py cmds $QA $E/v061_cmds > $E/v061_cmds.log 2>&1 ;;
 celes) timeout 900 python3 tools/emu_boot.py $CT $E/celes_boot $E/celes_ctl.state > $E/celes_boot.log 2>&1
   timeout 3000 python3 tools/emu_celes_suite.py $CT $E/celes_ctl.state $E/celes > $E/celes.log 2>&1 ;;
 colo) FF6X_COLO_EXTRA="v08prod=$F/FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc,v09prod=$PR" \
   timeout 5000 python3 tools/emu_colosseum.py $QA $QM "$C" $E/colosseum $F/FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.sfc $F/FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.manifest.json > $E/colosseum.log 2>&1 ;;
 eq8) timeout 6000 python3 tools/emu_equip_v08.py $QA $QM "$C" $E/eq8 > $E/eq8.log 2>&1 ;;
 eq8b) timeout 6000 python3 tools/emu_equip_battle_v08.py $QA $QM $E/eq8b > $E/eq8b.log 2>&1 ;;
 eq8s) timeout 7000 python3 tools/emu_equip_stress_v08.py $QA $QM $PR "$C" $E/eq8s > $E/eq8s.log 2>&1 ;;
 selftest) timeout 3000 python3 tools/selftest.py "$C" > $E/selftest.log 2>&1 ;;
esac
echo done "$step" >> $E/done.txt
done
