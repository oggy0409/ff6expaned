#!/bin/bash
# TECH v0.9.2 full emulator regression (the exact suite set behind REGRESSION_REPORT_v0.9.2.md).
#
# usage: tools/run_regression_v092.sh <clean Rev 1 .sfc> <built out dir> <evidence dir> <v0.7.1 ITEM_BANK_QA .sfc> [steps...]
#   <built out dir> = output of `python3 build.py <clean> --target all --out <dir>`
#   <v0.7.1 QA .sfc> = FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc (+ manifest), only for the Colosseum root-cause reference
#   steps (default: all):
#     new in v0.9.1 / v0.9.2:  c91 cb91 en92 compat selftest
#     v0.9 suites on the NEW v0.9.2 QA ROM (the accepted v0.9 QA tree is unchanged under QaAccess6):
#                             rare tech qa battle v061 celes colo eq8 eq8b eq8s
#     v0.9 suites on the FROZEN v0.9 ROMs (byte-identical to the accepted build; toolchain check): eq8b9 cons09 cbat09 stress09
set -u
C="$1"; F="$2"; E="$3"; V071="$4"; shift 4
STEPS="${*:-c91 cb91 en92 compat rare tech qa battle v061 celes colo eq8 eq8b eq8s eq8b9 cons09 cbat09 stress09 selftest}"
QA=$F/FF6X_Rev1_TECH_v0.9.2_ITEM_ALIGNMENT_CELES_ENABLERS_QA.sfc; QM=${QA%.sfc}.manifest.json
PR=$F/FF6X_Rev1_TECH_v0.9.1_PRODUCTION.sfc; CT=$F/FF6X_Rev1_TECH_v0.9.1_CELES_TECH.sfc
QA9=$F/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc; QM9=${QA9%.sfc}.manifest.json; PR9=$F/FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc
export FF6X_QA_V08_ROOT='{"0": [2, 1], "1": [2, 2, 0]}'
mkdir -p "$E"; cd "$(dirname "$0")/.."
for step in $STEPS; do
case "$step" in
 c91)    timeout 4000 python3 tools/emu_cons_v091.py "$QA" "$QM" "$PR9" "$C" "$E/consumables_v091" > "$E/consumables_v091.log" 2>&1 ;;
 cb91)   timeout 4000 python3 tools/emu_cons_battle_v091.py "$QA" "$QM" "$E/consumable_battle_v091" > "$E/consumable_battle_v091.log" 2>&1 ;;
 en92)   timeout 4000 python3 tools/emu_enablers_v092.py "$QA" "$QM" "$E/enablers_v092" > "$E/enablers_v092.log" 2>&1 ;;
 compat) timeout 4000 python3 tools/emu_savecompat_v092.py "$QA9" "$QM9" "$PR" "$QA" "$E/save_compat_v092" > "$E/save_compat_v092.log" 2>&1 ;;
 rare)   FF6X_RARE_SRC=items/production_v091/rare_items.json timeout 4000 python3 tools/emu_rare_v09.py "$QA" "$QM" "$PR" "$C" "$E/rare_items" > "$E/rare_items.log" 2>&1 ;;
 tech)   timeout 3000 python3 tools/emu_item_tech.py "$QA" "$E/item_tech" "$C" > "$E/item_tech.log" 2>&1 ;;
 qa)     timeout 5000 python3 tools/emu_item_qa.py "$QA" "$PR" "$C" "$E/item_qa" > "$E/item_qa.log" 2>&1 ;;
 battle) FF6X_QA_ITEM_ROOT=2,2,0,0 timeout 4000 python3 tools/emu_item_battle.py "$QA" "$QM" "$E/item_battle" "$C" > "$E/item_battle.log" 2>&1 ;;
 v061)   # the v0.6.1 suite enters through the QA tile: v0.9.2 root -> Older QA (v0.9 tree) = one more level than v0.9
         export FF6X_QA_PREFIX=2,2,2,0,1 FF6X_QA_SAVE_PICKS=2,2,2,1
         timeout 3000 python3 tools/emu_enemy_tech.py save "$QA" "$E/v061_regr" > "$E/v061_save.log" 2>&1
         timeout 3000 python3 tools/emu_enemy_tech.py load "$QA" "$E/v061_regr" > "$E/v061_load.log" 2>&1
         timeout 3000 python3 tools/emu_enemy_tech.py cmds "$QA" "$E/v061_cmds" > "$E/v061_cmds.log" 2>&1 ;;
 celes)  timeout 900 python3 tools/emu_boot.py "$CT" "$E/celes_boot" "$E/celes_ctl.state" > "$E/celes_boot.log" 2>&1
         timeout 3000 python3 tools/emu_celes_suite.py "$CT" "$E/celes_ctl.state" "$E/celes" > "$E/celes.log" 2>&1 ;;
 colo)   FF6X_COLO_EXTRA="v060prod=$F/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc,v072prod=$F/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc,v08prod=$F/FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc,v09prod=$PR9,v091prod=$PR" \
         timeout 6000 python3 tools/emu_colosseum.py "$QA" "$QM" "$C" "$E/colosseum" "$V071" "${V071%.sfc}.manifest.json" > "$E/colosseum.log" 2>&1 ;;
 eq8)    FF6X_EQUIP_SRC=items/production_v091/equipment.json timeout 6000 python3 tools/emu_equip_v08.py "$QA" "$QM" "$C" "$E/eq8" > "$E/eq8.log" 2>&1 ;;
 eq8b)   timeout 6000 python3 tools/emu_equip_battle_v08.py "$QA" "$QM" "$E/eq8b" > "$E/eq8b.log" 2>&1 ;;
 eq8s)   timeout 7000 python3 tools/emu_equip_stress_v08.py "$QA" "$QM" "$PR" "$C" "$E/eq8s" > "$E/eq8s.log" 2>&1 ;;
 eq8b9)  timeout 6000 python3 tools/emu_equip_battle_v08.py "$QA9" "$QM9" "$E/eq8b_v09_frozen" > "$E/eq8b_v09_frozen.log" 2>&1 ;;
 cons09) timeout 4000 python3 tools/emu_cons_v09.py "$QA9" "$QM9" "$C" "$E/consumables_v09_frozen" > "$E/consumables_v09_frozen.log" 2>&1 ;;
 cbat09) timeout 4000 python3 tools/emu_cons_battle_v09.py "$QA9" "$QM9" "$E/consumable_battle_v09_frozen" > "$E/consumable_battle_v09_frozen.log" 2>&1 ;;
 stress09) timeout 6000 python3 tools/emu_stress_v09.py "$F" "$C" "$E/stress_v09_frozen" > "$E/stress_v09_frozen.log" 2>&1 ;;
 selftest) timeout 3000 python3 tools/selftest.py "$C" > "$E/selftest.log" 2>&1 ;;
 *) echo "unknown step $step"; continue ;;
esac
echo "done $step"
done
for f in "$E"/*.log; do echo "$(basename "$f"): $(tail -1 "$f")"; done
