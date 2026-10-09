#!/bin/bash
# TECH v0.9 full emulator regression (the exact suite set behind REGRESSION_REPORT_v0.9.md).
#
# usage: tools/run_regression_v09.sh <clean Rev 1 .sfc> <built out dir> <evidence dir> <v0.7.1 ITEM_BANK_QA .sfc> [steps...]
#   <built out dir>  = output of `python3 build.py <clean> --target all --out <dir>` (needs the v0.9, v0.8, v0.7.x, v0.6.0 ROMs)
#   <v0.7.1 QA .sfc> = FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc (+ its .manifest.json next to it), only for the Colosseum
#                      root-cause reference (in FF6X_TECH_v0.7.1_SIGNATURE_EQUIPMENT_BANK_QA.zip, out/)
#   steps (default: all) = cons cbat rare stress tech qa battle v061 celes colo eq8 eq8b eq8s selftest
# Needs: python3, stable-retro, numpy, Pillow. Each step writes <evidence>/<step>.log and a screenshot/report folder.
set -u
C="$1"; F="$2"; E="$3"; V071="$4"; shift 4
STEPS="${*:-cons cbat rare stress tech qa battle v061 celes colo eq8 eq8b eq8s selftest}"
QA=$F/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc; QM=$F/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.manifest.json
PR=$F/FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc; CT=$F/FF6X_Rev1_TECH_v0.9_CELES_TECH.sfc
# the v0.9 QA hub moved the older menus: these variables tell the older suites where they are now
export FF6X_QA_V08_ROOT='{"0": [2, 1], "1": [2, 2, 0]}'
mkdir -p "$E"; cd "$(dirname "$0")/.."
for step in $STEPS; do
case "$step" in
 cons)   timeout 4000 python3 tools/emu_cons_v09.py "$QA" "$QM" "$C" "$E/consumables" > "$E/consumables.log" 2>&1 ;;
 cbat)   timeout 4000 python3 tools/emu_cons_battle_v09.py "$QA" "$QM" "$E/consumable_battle" > "$E/consumable_battle.log" 2>&1 ;;
 rare)   timeout 4000 python3 tools/emu_rare_v09.py "$QA" "$QM" "$PR" "$C" "$E/rare_items" > "$E/rare_items.log" 2>&1 ;;
 stress) timeout 6000 python3 tools/emu_stress_v09.py "$F" "$C" "$E/stress" > "$E/stress.log" 2>&1 ;;
 tech)   timeout 3000 python3 tools/emu_item_tech.py "$QA" "$E/item_tech" "$C" > "$E/item_tech.log" 2>&1 ;;
 qa)     timeout 5000 python3 tools/emu_item_qa.py "$QA" "$PR" "$C" "$E/item_qa" > "$E/item_qa.log" 2>&1 ;;
 battle) FF6X_QA_ITEM_ROOT=2,2,0,0 timeout 4000 python3 tools/emu_item_battle.py "$QA" "$QM" "$E/item_battle" "$C" > "$E/item_battle.log" 2>&1 ;;
 v061)   export FF6X_QA_PREFIX=2,2,0,1 FF6X_QA_SAVE_PICKS=2,2,1
         timeout 3000 python3 tools/emu_enemy_tech.py save "$QA" "$E/v061_regr" > "$E/v061_save.log" 2>&1
         timeout 3000 python3 tools/emu_enemy_tech.py load "$QA" "$E/v061_regr" > "$E/v061_load.log" 2>&1
         timeout 3000 python3 tools/emu_enemy_tech.py cmds "$QA" "$E/v061_cmds" > "$E/v061_cmds.log" 2>&1 ;;
 celes)  timeout 900 python3 tools/emu_boot.py "$CT" "$E/celes_boot" "$E/celes_ctl.state" > "$E/celes_boot.log" 2>&1
         timeout 3000 python3 tools/emu_celes_suite.py "$CT" "$E/celes_ctl.state" "$E/celes" > "$E/celes.log" 2>&1 ;;
 colo)   FF6X_COLO_EXTRA="v060prod=$F/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc,v072prod=$F/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc,v08prod=$F/FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc,v09prod=$PR" \
         timeout 6000 python3 tools/emu_colosseum.py "$QA" "$QM" "$C" "$E/colosseum" "$V071" "${V071%.sfc}.manifest.json" > "$E/colosseum.log" 2>&1 ;;
 eq8)    timeout 6000 python3 tools/emu_equip_v08.py "$QA" "$QM" "$C" "$E/eq8" > "$E/eq8.log" 2>&1 ;;
 eq8b)   timeout 6000 python3 tools/emu_equip_battle_v08.py "$QA" "$QM" "$E/eq8b" > "$E/eq8b.log" 2>&1 ;;
 eq8s)   timeout 7000 python3 tools/emu_equip_stress_v08.py "$QA" "$QM" "$PR" "$C" "$E/eq8s" > "$E/eq8s.log" 2>&1 ;;
 selftest) timeout 3000 python3 tools/selftest.py "$C" > "$E/selftest.log" 2>&1 ;;
 *) echo "unknown step $step"; continue ;;
esac
echo "done $step"
done
# summary: last line of every log (expected values: REGRESSION_REPORT_v0.9.md)
for f in "$E"/*.log; do echo "$(basename "$f"): $(tail -1 "$f")"; done
