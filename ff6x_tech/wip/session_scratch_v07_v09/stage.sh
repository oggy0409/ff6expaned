#!/bin/bash
set -e
S=/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad
R=/home/user/ff6expaned; T=$R/ff6x_tech; E=$T/out/emulator_v09
rm -rf $E; mkdir -p $E
cp -a $S/v9/c1 $E/consumables; cp -a $S/v9/c2 $E/consumable_battle; cp -a $S/v9/c3 $E/rare_items; cp -a $S/v9/c4 $E/stress
cp $S/v9/c1.log $E/consumables.log; cp $S/v9/c2.log $E/consumable_battle.log; cp $S/v9/c3.log $E/rare_items.log; cp $S/v9/c4.log $E/stress.log
cp $S/v9/selftest.log $S/v9/b_leak_audit.log $E/
for d in item_tech item_qa item_battle eq8 eq8b eq8s v061_regr v061_cmds celes celes_boot colosseum; do cp -a $S/emu09r/$d $E/$d; done
for f in item_tech item_qa item_battle eq8 eq8b eq8s v061_save v061_load v061_cmds celes celes_boot colosseum colosseum_wrongref; do cp $S/emu09r/$f.log $E/$f.log; done
rm -f $E/*.state $E/*/*.state
# package staging
P=$S/pkg; rm -rf $P; mkdir -p $P/out
cd $R; git ls-files ff6x_tech | grep -v '^ff6x_tech/out/' | while read f; do mkdir -p "$P/$(dirname "$f")"; cp -a "$f" "$P/$f"; done
cd $T/out
cp FF6X_Rev1_TECH_v0.9_* BUILD_SUMMARY.json build_log_v09_all_targets.txt HASHES_v0.9.txt DELTA_v0.8_to_v0.9.csv *_V09_*SHEET.png $P/out/
cp -a emulator_v09 $P/out/
cd $P; rm -f $R/FF6X_TECH_v0.9_CONSUMABLE_RARE_ITEM_EXPANSION_QA.zip
find . -type f | LC_ALL=C sort | TZ=UTC zip -q -X -9 -@ $R/FF6X_TECH_v0.9_CONSUMABLE_RARE_ITEM_EXPANSION_QA.zip
ls -la $R/FF6X_TECH_v0.9_CONSUMABLE_RARE_ITEM_EXPANSION_QA.zip
