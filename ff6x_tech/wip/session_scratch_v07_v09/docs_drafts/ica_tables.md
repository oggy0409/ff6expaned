### A. Inventory / equipment RAM accesses (every Rev 1 instruction)

| SNES | Insn | Kind | Routine | Status | Hook / reviewed reason |
|---|---|---|---|---|---|
| C0:4A6C | `LDA 1623` | equipment | DoPoisonDmg | REVIEWED | RANGE: Tintinabar relic test (relic ids $B0-$E6); extended low bytes are $00-$3F |
| C0:4A73 | `LDA 1624` | equipment | DoPoisonDmg | REVIEWED | RANGE: as C0:4A6C (relic 2) |
| C0:9FE7 | `LDA 161F` | equipment | Loop | HOOKED | I213_EVCMD8D_SLOT |
| C0:9FF2 | `STA 161F` | equipment | Loop | REVIEWED | EventCmd_8d writes $FF after I213 (XC0_8dLoad) already returned an extended item to the inventory and cleared its bit |
| C0:9FF7 | `LDA 1869` | inventory id | Loop | HOOKED | I214_EVCMD8D_FIND |
| C0:A006 | `LDA 1869` | inventory id | Loop | REVIEWED | EMPTY-TEST: empty-slot scan (CMP #$FF) on the raw low byte; an extended slot is never $FF, so it is correctly treated as occupied |
| C0:A017 | `STA 1869` | inventory id | Loop | HOOKED | I215_EVCMD8D_PUT |
| C0:A01C | `STA 1969` | inventory qty | Loop | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:A021 | `LDA 1969` | inventory qty | FoundItem | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:A029 | `STA 1969` | inventory qty | FoundItem | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:A0D0 | `STA 161F` | equipment | EventCmd_40 | HOOKED | I216_CHARINIT_EQUIP |
| C0:A0D7 | `STA 1620` | equipment | EventCmd_40 | REVIEWED | COVERED: CharProp init stores vanilla ids; I216 (C0:A0D0) clears the record's 6 equipment bits first |
| C0:A0DE | `STA 1621` | equipment | EventCmd_40 | REVIEWED | COVERED: as C0:A0D7 |
| C0:A0E5 | `STA 1622` | equipment | EventCmd_40 | REVIEWED | COVERED: as C0:A0D7 |
| C0:A0EC | `STA 1623` | equipment | EventCmd_40 | REVIEWED | COVERED: as C0:A0D7 |
| C0:A0F3 | `STA 1624` | equipment | EventCmd_40 | REVIEWED | COVERED: as C0:A0D7 |
| C0:ACFE | `LDA 1869` | inventory id | GiveItem | HOOKED | I210_GIVEITEM_FIND |
| C0:AD0D | `LDA 1869` | inventory id | GiveItem | REVIEWED | EMPTY-TEST: empty-slot scan (CMP #$FF) on the raw low byte; an extended slot is never $FF, so it is correctly treated as occupied |
| C0:AD19 | `STA 1869` | inventory id | GiveItem | HOOKED | I211_GIVEITEM_PUT |
| C0:AD1E | `STA 1969` | inventory qty | GiveItem | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:AD22 | `LDA 1969` | inventory qty | GiveItem | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:AD29 | `INC 1969` | inventory qty | GiveItem | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:AD2F | `LDA 1869` | inventory id | EventCmd_81 | HOOKED | I212_TAKEITEM_FIND |
| C0:AD3E | `DEC 1969` | inventory qty | EventCmd_81 | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:AD41 | `LDA 1969` | inventory qty | EventCmd_81 | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C0:AD48 | `STA 1869` | inventory id | EventCmd_81 | REVIEWED | SELECTED: TakeItem empties a vanilla slot found by the masked search I212 (its bit is already 0) |
| C0:BDC0 | `STZ 1969` | inventory qty | InitNewGame | REVIEWED | New Game inventory init ($FF / 0); I220 then zeroes every extension bit |
| C0:BDC3 | `STA 1869` | inventory id | InitNewGame | REVIEWED | New Game inventory init ($FF / 0); I220 then zeroes every extension bit |
| C1:4BD4 | `LDA 2B86` | battle hand id/list | DrawEquipListText | REVIEWED | COVERED: R-hand header id; the name is chosen through the XBTLNAME queue (I540/I541) |
| C1:4BDA | `LDA 2B9A` | battle hand id/list | DrawEquipListText | HOOKED | I540_HANDNAMES |
| C1:7126 | `LDA 2B9D` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:712D | `DEC 2B9D` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7133 | `STA 2B9A` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7138 | `STA 2B9B` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:713B | `STZ 2B9C` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:713E | `STZ 2B9D` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7141 | `STZ 2B9E` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7145 | `LDA 2B89` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:714C | `DEC 2B89` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7152 | `STA 2B86` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7157 | `STA 2B87` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:715A | `STZ 2B88` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:715D | `STZ 2B89` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:7160 | `STZ 2B8A` | battle hand id/list | set_target_data | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:8A58 | `LDA 2B86` | battle hand id/list | set_item_one | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8A5E | `LDA 2B87` | battle hand id/list | set_item_one | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8A69 | `LDA 2B9A` | battle hand id/list | set_item_one | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8A6F | `LDA 2B9B` | battle hand id/list | set_item_one | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8B50 | `LDA 2B86` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B63 | `LDA 2B86` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B6D | `STA 2B86` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B72 | `STA 2B87` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B76 | `STA 2B88` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B79 | `STA 2B89` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B7C | `STA 2B8A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B85 | `STA 2B86` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B8B | `STA 2B87` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B91 | `STA 2B88` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B97 | `STA 2B8A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8B9C | `STA 2B89` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C05 | `LDA 2B9A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C18 | `LDA 2B9A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C22 | `STA 2B9A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C27 | `STA 2B9B` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C2B | `STA 2B9C` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C2E | `STA 2B9D` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C31 | `STA 2B9E` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C3A | `STA 2B9A` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C40 | `STA 2B9B` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C46 | `STA 2B9C` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C4C | `STA 2B9E` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8C51 | `STA 2B9D` | battle hand id/list | set_item_one | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8E72 | `LDA 2B86` | battle hand id/list | SelectEquipItem | REVIEWED | COVERED: R-hand <-> L-hand exchange; I545 (C1:8E8F, XC1_HandSwapBits) swaps the two equipment bits with the entries |
| C1:8E84 | `LDA 2B9A` | battle hand id/list | SelectEquipItem | REVIEWED | COVERED: R-hand <-> L-hand exchange; I545 (C1:8E8F, XC1_HandSwapBits) swaps the two equipment bits with the entries |
| C1:8E87 | `STA 2B86` | battle hand id/list | SelectEquipItem | REVIEWED | COVERED: R-hand <-> L-hand exchange; I545 (C1:8E8F, XC1_HandSwapBits) swaps the two equipment bits with the entries |
| C1:8E97 | `STA 2B9A` | battle hand id/list | SelectEquipItem | REVIEWED | COVERED: R-hand <-> L-hand exchange; I545 (C1:8E8F, XC1_HandSwapBits) swaps the two equipment bits with the entries |
| C1:8ED7 | `LDA 2B9A` | battle hand id/list | SelectEquipItem | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:8EDE | `LDA 2B9B` | battle hand id/list | SelectEquipItem | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:8EE5 | `LDA 2B86` | battle hand id/list | SelectEquipItem | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:8EEC | `LDA 2B87` | battle hand id/list | SelectEquipItem | REVIEWED | use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX) |
| C1:8F2F | `LDA 2B9A` | battle hand id/list | SelectEquipItem | REVIEWED | read-only copy of the selected hand for the cursor display (w7e890d/e) |
| C1:8F35 | `LDA 2B9B` | battle hand id/list | SelectEquipItem | REVIEWED | read-only copy of the selected hand for the cursor display (w7e890d/e) |
| C1:8F3D | `LDA 2B86` | battle hand id/list | SelectEquipItem | REVIEWED | read-only copy of the selected hand for the cursor display (w7e890d/e) |
| C1:8F43 | `LDA 2B87` | battle hand id/list | SelectEquipItem | REVIEWED | read-only copy of the selected hand for the cursor display (w7e890d/e) |
| C1:8F79 | `LDA 2B86` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8F9A | `LDA 2B9A` | battle hand id/list | hand_r2item | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8FA0 | `LDA 2B9B` | battle hand id/list | hand_r2item | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:8FC2 | `LDA 2B86` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8FD8 | `STA 2B86` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8FDE | `STA 2B87` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8FE4 | `STA 2B88` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8FEA | `STA 2B8A` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:8FEF | `STA 2B89` | battle hand id/list | hand_r2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:9040 | `LDA 2B9A` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:9061 | `LDA 2B86` | battle hand id/list | hand_l2item | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:9067 | `LDA 2B87` | battle hand id/list | hand_l2item | REVIEWED | check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended |
| C1:9089 | `LDA 2B9A` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:909F | `STA 2B9A` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:90A5 | `STA 2B9B` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:90AB | `STA 2B9C` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:90B1 | `STA 2B9E` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:90B6 | `STA 2B9D` | battle hand id/list | hand_l2item | REVIEWED | hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand) |
| C1:BA2F | `LDA 2B87` | battle hand id/list | CheckNullTarget | REVIEWED | Jump: usage flag $10 of the hand (an extended weapon carries the weapon flag like a vanilla weapon); index hooked I543/I544 |
| C1:BA36 | `LDA 2B9B` | battle hand id/list | CheckNullTarget | REVIEWED | as C1:BA2F (left hand) |
| C1:BA41 | `LDA 2B9A` | battle hand id/list | CheckNullTarget | HOOKED | I543_JUMPANIM_L |
| C1:BA47 | `LDA 2B86` | battle hand id/list | CheckNullTarget | HOOKED | I544_JUMPANIM_R |
| C2:0629 | `STA 3CA8` | battle hand id/list | SetRage | REVIEWED | SetRage (Gau): hands := monster attack type; extended weapons/shields can never be equippable by Gau/Umaro (builder refuses) |
| C2:062C | `STA 3CA9` | battle hand id/list | SetRage | REVIEWED | as C2:0629 |
| C2:0EE6 | `LDA 15FB` | equipment (UpdateEquip) | UpdateEquip | HOOKED | I500_UPDEQ_LOAD |
| C2:1814 | `LDA 3CA8` | battle hand id/list | InitUmaroAttack | HOOKED | I531_SPEAR_R |
| C2:181A | `LDA 3CA9` | battle hand id/list | InitUmaroAttack | HOOKED | I532_SPEAR_L |
| C2:20AB | `LDA 2B86` | battle hand id/list | _equipchange | REVIEWED | battle write-back source (see C2:20B9) |
| C2:20AF | `LDA 2B9A` | battle hand id/list | _equipchange | REVIEWED | battle write-back source (see C2:20B9) |
| C2:20B9 | `STA 1620` | equipment | _equipchange | REVIEWED | battle hand write-back of the low byte; the high bit is untouched and an extended hand cannot change in battle (I542 swap guard) |
| C2:20BD | `STA 161F` | equipment | _equipchange | REVIEWED | as C2:20B9 (R-hand) |
| C2:2930 | `STA 3CA8` | battle hand id/list | UpdateEquipBattle | REVIEWED | RHandItem := equipment low byte (CalcEquipEffect $11C6); extended-ness is taken from the slot bit by I530-I533 |
| C2:29FE | `LDA 3CA8` | battle hand id/list | _magicpunch | HOOKED | I530_ANIM_ID |
| C2:2D00 | `STA 3CA8` | battle hand id/list | LoadMonsterProp | REVIEWED | monster entries only (MonsterProp attack type) |
| C2:3F0B | `LDA 2B86` | battle hand id/list | AttackerEffectNone | HOOKED | I533_OGRE_NIX |
| C2:3F14 | `STA 2B86` | battle hand id/list | AttackerEffectNone | REVIEWED | Ogre Nix break write: reached only when I533 matched, never for an extended weapon |
| C2:3F17 | `STA 2B87` | battle hand id/list | AttackerEffectNone | REVIEWED | as C2:3F14 |
| C2:3F1A | `STZ 2B89` | battle hand id/list | AttackerEffectNone | REVIEWED | as C2:3F14 |
| C2:498A | `STA 1869` | inventory id | UpdateSRAM | REVIEWED | DEAD: inside C2:4981-C2:499D, bypassed by I520 (XBattleEndInv) |
| C2:4993 | `STA 1969` | inventory qty | UpdateSRAM | REVIEWED | DEAD: inside C2:4981-C2:499D, bypassed by I520 (XBattleEndInv) |
| C2:49AD | `CMP 1869` | inventory id | UpdateSRAM | HOOKED | I521_BTLEND_WAGER |
| C2:49B2 | `DEC 1969` | inventory qty | UpdateSRAM | REVIEWED | SELECTED: colosseum wager slot found by the masked compare I521 |
| C2:49BB | `STA 1869` | inventory id | UpdateSRAM | REVIEWED | SELECTED: as C2:49B2 |
| C2:49BE | `STZ 1969` | inventory qty | UpdateSRAM | REVIEWED | SELECTED: as C2:49B2 |
| C2:5481 | `LDA 1620` | equipment | InitInventory | HOOKED | I510_BINV_HAND_L |
| C2:5493 | `LDA 161F` | equipment | InitInventory | HOOKED | I512_BINV_HAND_R |
| C2:54A1 | `LDA 1969` | inventory qty | InitInventory | REVIEWED | COVERED: vanilla battle-inventory copy loop kept; I516 (C2:54B0, XC2_ExtSlotsEmpty) re-copies every extended slot exactly as an empty slot |
| C2:54A7 | `LDA 1869` | inventory id | InitInventory | REVIEWED | COVERED: as C2:54A1 |
| C2:54B4 | `LDA 1869` | inventory id | InitInventory | REVIEWED | RANGE: battle tool-list builder (ids $A3-$AA); extended low bytes are $00-$3F |
| C2:5FF3 | `LDA 161F` | equipment | LearnItemMagic | REVIEWED | RANGE: Cursed Shld ($66) -> Paladin Shld; extended low bytes are $00-$3F |
| C2:6009 | `STA 161F` | equipment | LearnItemMagic | REVIEWED | RANGE: as C2:5FF3 (writes $67 only into a slot that held vanilla $66) |
| C3:26BA | `LDA 1869` | inventory id | _c326b8 | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:26C3 | `STA 1869` | inventory id | _c326b8 | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:26CE | `LDA 1969` | inventory qty | _c326b8 | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:26D6 | `STA 1969` | inventory qty | _c326b8 | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:272C | `STA 1869` | inventory id | FindItemsWithIcon | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:2733 | `STA 1969` | inventory qty | FindItemsWithIcon | REVIEWED | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| C3:27BA | `LDA 1869` | inventory id | FindItemsWithIcon | REVIEWED | COVERED: item move swaps raw bytes; I309 (C3:27DE, XC3_SwapBits) swaps the two high bits |
| C3:27BF | `LDA 1969` | inventory qty | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27C8 | `LDA 1869` | inventory id | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27CB | `STA 1869` | inventory id | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27D0 | `STA 1869` | inventory id | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27D3 | `LDA 1969` | inventory qty | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27D6 | `STA 1969` | inventory qty | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:27DB | `STA 1969` | inventory qty | FindItemsWithIcon | REVIEWED | COVERED: as C3:27BA |
| C3:7FA8 | `LDA 1969` | inventory qty | DrawItemList | HOOKED | I300_ITEMLIST_QTY |
| C3:8056 | `LDA 1869` | inventory id | GetItemNameColor | REVIEWED | ALIAS-SAFE: item-list text colour (usable test via vanilla props of the low byte); aliases $00-$3F are weapons -> grey, identical to an extended (never usable) item |
| C3:80C7 | `LDA 1869` | inventory id | LoadListItemName | HOOKED | I301_ITEMLIST_NAME |
| C3:82F8 | `LDA 1869` | inventory id | InitItemDesc | HOOKED | I302_ITEMDESC_ID |
| C3:8359 | `LDA 1869` | inventory id | CountInventoryItems | REVIEWED | count of non-empty slots (CMP #$FF): an extended slot correctly counts as an item |
| C3:849D | `LDA 1869` | inventory id | UseItem | HOOKED | I304_USEITEM_ID |
| C3:84C4 | `LDA 1869` | inventory id | UseItem | REVIEWED | USABLE-ONLY: field item-use path, reached only for type-6 menu-usable items (UseItem prop pointer is hooked, I305); extended items are equipment |
| C3:8696 | `LDA 1869` | inventory id | DrawItemDetails | HOOKED | I306_DETAILS_ID |
| C3:87A0 | `LDA 1869` | inventory id | DrawWeaponPower | HOOKED | I308_DETAILS_POWER |
| C3:8A75 | `LDA 1969` | inventory qty | ItemTargetDrawQty | REVIEWED | USABLE-ONLY: field item-use path, reached only for type-6 menu-usable items (UseItem prop pointer is hooked, I305); extended items are equipment |
| C3:8B02 | `LDA 1969` | inventory qty | ItemTargetDrawQty | REVIEWED | USABLE-ONLY: field item-use path, reached only for type-6 menu-usable items (UseItem prop pointer is hooked, I305); extended items are equipment |
| C3:8C2F | `LDA 1869` | inventory id | GetInventoryItemID | REVIEWED | USABLE-ONLY: field item-use path, reached only for type-6 menu-usable items (UseItem prop pointer is hooked, I305); extended items are equipment |
| C3:8FC2 | `LDA 001F` | equipment (char ptr) | DrawPartyEquipItems | HOOKED | I320_PARTYEQ_NAME_ID |
| C3:9070 | `LDA 0023` | equipment (char ptr) | DrawRelicMenu | REVIEWED | RANGE: DrawRelicMenu saves the relic low bytes for CheckReequipRelics, which tests vanilla relic ids only; an extended relic's low byte is $00-$3F and differs from every relic id |
| C3:9075 | `LDA 0024` | equipment (char ptr) | DrawRelicMenu | REVIEWED | RANGE: as C3:9070 |
| C3:925F | `LDA 001F` | equipment (char ptr) | _c39233 | HOOKED | I330_PREVIEW_SAVE |
| C3:9264 | `LDA 1869` | inventory id | _c39233 | HOOKED | I331_PREVIEW_CAND |
| C3:9267 | `STA 001F` | equipment (char ptr) | _c39233 | HOOKED | I332_PREVIEW_PUT |
| C3:931C | `STA 001F` | equipment (char ptr) | _c39233 | HOOKED | I333_PREVIEW_RESTORE |
| C3:9405 | `LDA 001F` | equipment (char ptr) | _c393fc | HOOKED | I322_EQNAME_RH |
| C3:9417 | `LDA 0020` | equipment (char ptr) | _c393fc | HOOKED | I323_EQNAME_LH |
| C3:9420 | `LDA 001F` | equipment (char ptr) | _c3941d | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:9427 | `LDA 0020` | equipment (char ptr) | _c3941d | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:943D | `LDA 0021` | equipment (char ptr) | _c39435 | HOOKED | I324_EQNAME_HEAD |
| C3:944B | `LDA 0022` | equipment (char ptr) | _c39443 | HOOKED | I325_EQNAME_BODY |
| C3:9459 | `LDA 0023` | equipment (char ptr) | _c39451 | HOOKED | I326_EQNAME_RELIC1 |
| C3:9467 | `LDA 0024` | equipment (char ptr) | _c3945f | HOOKED | I327_EQNAME_RELIC2 |
| C3:96AB | `LDA 001F` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96B1 | `LDA 0020` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96B7 | `LDA 0021` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96BD | `LDA 0022` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96C5 | `STA 001F` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96C8 | `STA 0020` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96CB | `STA 0021` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:96CE | `STA 0022` | equipment (char ptr) | EquipRemoveAll | REVIEWED | DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll) |
| C3:9712 | `STA 001F` | equipment (char ptr) | EquipOptimum | HOOKED | I341_OPT_2H_STORE |
| C3:972A | `STA 001F` | equipment (char ptr) | EquipOptimum | HOOKED | I343_OPT_W_STORE |
| C3:9749 | `STA 0020` | equipment (char ptr) | EquipOptimum | HOOKED | I345_OPT_S_STORE |
| C3:9763 | `STA 0020` | equipment (char ptr) | EquipOptimum | HOOKED | I347_OPT_G_STORE |
| C3:977A | `STA 0021` | equipment (char ptr) | EquipOptimum | HOOKED | I349_OPT_H_STORE |
| C3:978F | `STA 0022` | equipment (char ptr) | EquipOptimum | HOOKED | I351_OPT_A_STORE |
| C3:979F | `LDA 1869` | inventory id | GetValidWeapons | HOOKED | I353_VALIDW_ID |
| C3:97E1 | `LDA 1869` | inventory id | GetValidShields | HOOKED | I355_VALIDS_ID |
| C3:9829 | `LDA 1869` | inventory id | GetBestEquip | REVIEWED | DEAD: GetBestEquip body, replaced by I357 (JMP XC3_GetBestEquip) |
| C3:9855 | `LDA 1869` | inventory id | GetBest2Hand | REVIEWED | DEAD: GetBest2Hand body, replaced by I358 (JMP XC3_GetBest2Hand) |
| C3:98E6 | `LDA 001F` | equipment (char ptr) | GetBest2Hand | HOOKED | I359_REMOVE_ID |
| C3:98EE | `STA 001F` | equipment (char ptr) | GetBest2Hand | HOOKED | I361_REMOVE_CLR |
| C3:9923 | `LDA 001F` | equipment (char ptr) | GetBest2Hand | HOOKED | I362_EQUIP_OLD |
| C3:9936 | `LDA 1869` | inventory id | GetBest2Hand | HOOKED | I364_EQUIP_NEW |
| C3:9939 | `STA 001F` | equipment (char ptr) | GetBest2Hand | HOOKED | I365_EQUIP_STORE |
| C3:997F | `LDA 001F` | equipment (char ptr) | _c39975 | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:9986 | `LDA 0020` | equipment (char ptr) | _c39975 | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:99A6 | `LDA 0020` | equipment (char ptr) | _c39975 | HOOKED | I367_HANDTXT_LH |
| C3:99CA | `LDA 001F` | equipment (char ptr) | _c39975 | HOOKED | I369_HANDTXT_RH |
| C3:99FC | `LDA 001F` | equipment (char ptr) | CheckHandEffects | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:9A03 | `LDA 0020` | equipment (char ptr) | CheckHandEffects | REVIEWED | EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct) |
| C3:9A0E | `LDA 0020` | equipment (char ptr) | CheckHandEffects | HOOKED | I371_HANDFX_LH |
| C3:9A2B | `LDA 001F` | equipment (char ptr) | CheckHandEffects | HOOKED | I373_HANDFX_RH |
| C3:9A5D | `LDA 1869` | inventory id | CheckCanEquipItem | HOOKED | I375_CANEQ_ID |
| C3:9A79 | `LDA 0020` | equipment (char ptr) | CheckCanEquipItem | HOOKED | I377_CANEQ_LH |
| C3:9B76 | `LDA 1869` | inventory id | GetValidEquip | HOOKED | I381_VALIDE_ID |
| C3:9BB6 | `LDA 1869` | inventory id | GetValidEquip | HOOKED | I383_VALIDH_ID |
| C3:9BF2 | `LDA 1869` | inventory id | GetValidEquip | HOOKED | I385_VALIDA_ID |
| C3:9D25 | `LDA 1869` | inventory id | LoadEquipListItemName | HOOKED | I387_EQLIST_NAME_ID |
| C3:9D63 | `CMP 1869` | inventory id | IncItemQty | HOOKED | I389_INCQTY_FIND |
| C3:9D74 | `LDA 1869` | inventory id | IncItemQty | REVIEWED | EMPTY-TEST: empty-slot scan (CMP #$FF) on the raw low byte; an extended slot is never $FF, so it is correctly treated as occupied |
| C3:9D80 | `STA 1969` | inventory qty | IncItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9D85 | `STA 1869` | inventory id | IncItemQty | HOOKED | I390_INCQTY_PUT |
| C3:9D8A | `LDA 1969` | inventory qty | IncItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9D92 | `STA 1969` | inventory qty | IncItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9D9C | `CMP 1869` | inventory id | DecItemQty | HOOKED | I391_DECQTY_FIND |
| C3:9DA9 | `LDA 1969` | inventory qty | DecItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9DB0 | `LDA 1969` | inventory qty | DecItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9DB4 | `STA 1969` | inventory qty | DecItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9DBA | `STA 1969` | inventory qty | DecItemQty | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:9DBF | `STA 1869` | inventory id | DecItemQty | REVIEWED | SELECTED: DecItemQty empties a vanilla slot found by I391 (bit already 0); extended decrements use XC3_DecQtyB |
| C3:9F5F | `LDA 0023` | equipment (char ptr) | CheckReequipRelics | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F |
| C3:9F66 | `LDA 0024` | equipment (char ptr) | CheckReequipRelics | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F |
| C3:9F8B | `LDA 0023` | equipment (char ptr) | CheckReequipRelics | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F |
| C3:9F9A | `LDA 0024` | equipment (char ptr) | CheckReequipRelics | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F |
| C3:A05F | `LDA 1869` | inventory id | _c3a051 | HOOKED | I392_VALIDR_ID |
| C3:A0BB | `LDA 0023` | equipment (char ptr) | _c3a051 | HOOKED | I394_RELIC_OLD |
| C3:A0CE | `LDA 1869` | inventory id | _c3a051 | HOOKED | I396_RELIC_NEW |
| C3:A0D1 | `STA 0023` | equipment (char ptr) | _c3a051 | HOOKED | I397_RELIC_STORE |
| C3:A124 | `LDA 0023` | equipment (char ptr) | _c3a051 | HOOKED | I399_RELICRM_ID |
| C3:A12C | `STA 0023` | equipment (char ptr) | _c3a051 | HOOKED | I401_RELICRM_CLR |
| C3:A16D | `LDA 1869` | inventory id | SortValidEquip | HOOKED | I402_SORT_ID |
| C3:A1CD | `LDA 0023` | equipment (char ptr) | _c3a187 | HOOKED | I404_RELICDESC_1 |
| C3:A1D2 | `LDA 0024` | equipment (char ptr) | _c3a187 | HOOKED | I405_RELICDESC_2 |
| C3:A1E4 | `LDA 1869` | inventory id | _c3a1d8 | HOOKED | I407_RELICLDESC_ID |
| C3:ACFA | `LDA 1869` | inventory id | ? | HOOKED | I311_COLOSSEUM_PICK |
| C3:B4FF | `LDA 1869` | inventory id | _c3b4f8 | HOOKED | I420_SELLDESC |
| C3:B5BC | `CMP 1869` | inventory id | _c3b5b7 | HOOKED | I422_BUY_FIND |
| C3:B5C9 | `LDA 1869` | inventory id | _c3b5b7 | REVIEWED | EMPTY-TEST: empty-slot scan (CMP #$FF) on the raw low byte; an extended slot is never $FF, so it is correctly treated as occupied |
| C3:B5D5 | `STA 1969` | inventory qty | _c3b5b7 | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:B5DC | `STA 1869` | inventory id | _c3b5b7 | HOOKED | I423_BUY_PUT |
| C3:B5E4 | `ADC 1969` | inventory qty | _c3b5b7 | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:B5E7 | `STA 1969` | inventory qty | _c3b5b7 | REVIEWED | SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan |
| C3:B729 | `LDA 1969` | inventory qty | _c3b708 | REVIEWED | SELECTED: sell acts on the selected sell-list slot; extended slots cannot be selected (I421, emulator M2) |
| C3:B72F | `STA 1969` | inventory qty | _c3b708 | REVIEWED | SELECTED: as C3:B729 |
| C3:B739 | `STA 1869` | inventory id | _c3b708 | REVIEWED | SELECTED: as C3:B729 |
| C3:B73D | `STA 1969` | inventory qty | _c3b708 | REVIEWED | SELECTED: as C3:B729 |
| C3:BC66 | `CMP 1869` | inventory id | _c3bc57 | HOOKED | I424_OWNED_FIND |
| C3:BC76 | `LDA 1969` | inventory qty | _c3bc57 | REVIEWED | SELECTED: shop owned count after the masked search I424 |
| C3:BCA1 | `LDA 1969` | inventory qty | _c3bc9d | REVIEWED | SELECTED: quantity of the selected sell slot (never extended) |
| C3:BD5B | `LDA 0022` | equipment (char ptr) | _c3bcfd | HOOKED | I430_CMP_ARMOR_ID |
| C3:BDBA | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I432_CMP_W_EQ1 |
| C3:BDC1 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I433_CMP_W_EQ2 |
| C3:BDC9 | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I434_CMP_W_R |
| C3:BDE1 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I436_CMP_W_L |
| C3:BDF9 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I438_CMP_W_L2 |
| C3:BDFF | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I439_CMP_W_R2 |
| C3:BE4A | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I441_CMP_S_EQ1 |
| C3:BE51 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I442_CMP_S_EQ2 |
| C3:BE59 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I443_CMP_S_L |
| C3:BE6D | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I445_CMP_S_R |
| C3:BE81 | `LDA 001F` | equipment (char ptr) | _c3bcfd | HOOKED | I447_CMP_S_R2 |
| C3:BE87 | `LDA 0020` | equipment (char ptr) | _c3bcfd | HOOKED | I448_CMP_S_L2 |
| C3:BED3 | `LDA 0021` | equipment (char ptr) | _c3bcfd | HOOKED | I450_CMP_H_ID |
| C3:BF2E | `LDA 0023` | equipment (char ptr) | _c3bcfd | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F (shop relic branch @bf18, shop item is a relic) |
| C3:BF35 | `LDA 0024` | equipment (char ptr) | _c3bcfd | REVIEWED | RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F (as C3:BF2E) |
| C3:BFCF | `LDA 1869` | inventory id | _c3bfcb | HOOKED | I421_SELLITEM |
| E5:F7B7 | `STZ 19FF` | inventory qty | TheEnd_ext | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FAEB | `LDA 187C` | inventory id | DrawTheEndStars_01 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB0A | `STA 187C` | inventory id | DrawTheEndStars_01 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB0D | `LDA 187D` | inventory id | DrawTheEndStars_01 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB30 | `STA 187D` | inventory id | DrawTheEndStars_01 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB61 | `STA 187E` | inventory id | DrawTheEndStars_01 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB6B | `LDA 18FC` | inventory id | DrawTheEndStars_02 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB8A | `STA 18FC` | inventory id | DrawTheEndStars_02 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FB8D | `LDA 18FD` | inventory id | DrawTheEndStars_02 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FBB0 | `STA 18FD` | inventory id | DrawTheEndStars_02 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FBE1 | `STA 18FE` | inventory id | DrawTheEndStars_02 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FBEB | `LDA 197C` | inventory qty | DrawTheEndStars_03 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FC0A | `STA 197C` | inventory qty | DrawTheEndStars_03 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FC0D | `LDA 197D` | inventory qty | DrawTheEndStars_03 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FC30 | `STA 197D` | inventory qty | DrawTheEndStars_03 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |
| E5:FC61 | `STA 197E` | inventory qty | DrawTheEndStars_03 | REVIEWED | ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour) |

### B. Relocated-table consumers (118 long operands), by routine

| Routine | Sites | Class | How an id reaches it |
|---|---|---|---|
| CalcEquipEffect | ITEM_PROP@C2:0FA3, ITEM_PROP@C2:0FAC, ITEM_PROP@C2:0FB3, ITEM_PROP@C2:0FBA, ITEM_PROP@C2:0FC1, ITEM_PROP@C2:0FC8, ITEM_PROP@C2:0FEC, ITEM_PROP@C2:1018, ITEM_PROP@C2:101D, ITEM_PROP@C2:1033, ITEM_PROP@C2:103C, ITEM_PROP@C2:1043, ITEM_PROP@C2:1048, ITEM_PROP@C2:1051, ITEM_PROP@C2:1068, ITEM_PROP@C2:1087, ITEM_PROP@C2:10D3, ITEM_PROP@C2:10DA, ITEM_PROP@C2:10ED, ITEM_PROP@C2:10F4, ITEM_PROP@C2:10FB | EXT-AWARE | 9-bit id from I500 (XC2_EqLoad), offset from I501 (XC2_PropOfs) |
| InitItemTarget | ITEM_PROP@C2:2723, ITEM_PROP@C2:2729, ITEM_PROP@C2:2735 | VANILLA-ONLY | battle Item/Throw command ids: the battle item list never holds an extended id (extended slots are presented empty, extended hands are not usable/throwable) |
| _magicitem | ITEM_PROP@C2:2A66, ITEM_PROP@C2:2A6D, ITEM_PROP@C2:2A7B, ITEM_PROP@C2:2A89, ITEM_PROP@C2:2A90, ITEM_PROP@C2:2A99, ITEM_PROP@C2:2AF2, ITEM_PROP@C2:2B02 | VANILLA-ONLY | item/thrown item used in battle: same reason as InitItemTarget |
| LoadItemProp | ITEM_PROP@C2:54FC, ITEM_PROP@C2:5503, ITEM_PROP@C2:552C | VANILLA-ONLY | battle inventory: extended slots are re-copied as empty slots (I516); extended hands go through XC2_LoadItemPropX (I511/I513) |
| LearnItemMagic | ITEM_PROP@C2:6016, ITEM_PROP@C2:601B | EXT-AWARE | offset from I502 (XC2_LearnOfs, 9-bit id of the equipment slot) |
| GetItemNameColor | ITEM_PROP@C3:8073, ITEM_PROP@C3:807D | ALIAS-SAFE | see C3:8056 |
| UseItem | ITEM_PROP@C3:84AE, ITEM_PROP@C3:84B8, ITEM_PROP@C3:8523 | EXT-AWARE | prop pointer I305 (XC3_PropPtrB); extended items are not type 6, so the use path stops |
| DrawItemDetails | ITEM_PROP@C3:86B4, ITEM_PROP@C3:86E3, ITEM_PROP@C3:8706, ITEM_PROP@C3:8710, ITEM_PROP@C3:8720, ITEM_PROP@C3:8760, ITEM_PROP@C3:8771, ITEM_PROP@C3:8784 | EXT-AWARE | I306/I307 |
| DrawWeaponPower | ITEM_PROP@C3:87B3 | EXT-AWARE | X from I307; id test I308 |
| DrawWeaponLearnedMagic | ITEM_PROP@C3:87CE, ITEM_PROP@C3:87D6 | EXT-AWARE | X from I307 |
| DrawItemEvadeModifier | ITEM_PROP@C3:87FA | EXT-AWARE | X from I307 |
| _c388a0 | ITEM_PROP@C3:88A4 | EXT-AWARE | X from I307 |
| _c38959 | ITEM_PROP@C3:895D, ITEM_PROP@C3:896B, ITEM_PROP@C3:8979 | EXT-AWARE | X from I307 |
| _c38c33 | ITEM_PROP@C3:8C43, ITEM_PROP@C3:8C5E, ITEM_PROP@C3:8C76, ITEM_PROP@C3:8CA2 | VANILLA-ONLY | field item-use effects: usable items only |
| lpget | ITEM_PROP@C3:8CCD | VANILLA-ONLY | field item-use effects: usable items only |
| GetValidWeapons | ITEM_PROP@C3:97AC, ITEM_PROP@C3:97B8 | EXT-AWARE | I353/I354 |
| GetValidShields | ITEM_PROP@C3:97EE, ITEM_PROP@C3:97FA | EXT-AWARE | I355/I356 |
| GetBest2Hand | ITEM_PROP@C3:986D | EXT-AWARE | routine replaced by I358 (XC3_GetBest2Hand reads XItemProp with 9-bit ids) |
| _c39975 | ITEM_PROP@C3:99B5, ITEM_PROP@C3:99D3 | EXT-AWARE | I367-I370 |
| CheckHandEffects | ITEM_PROP@C3:9A1D, ITEM_PROP@C3:9A34 | EXT-AWARE | I371-I374 |
| CheckCanEquipItem | ITEM_PROP@C3:9A66, ITEM_PROP@C3:9A86, ITEM_PROP@C3:9A99, ITEM_PROP@C3:9AB2, ITEM_PROP@C3:9AC5 | EXT-AWARE | I375-I380 |
| GetValidEquip | ITEM_PROP@C3:9B83, ITEM_PROP@C3:9B93, ITEM_PROP@C3:9BC3, ITEM_PROP@C3:9BCF, ITEM_PROP@C3:9BFF, ITEM_PROP@C3:9C0B | EXT-AWARE | I381-I386 |
| _c3a051 | ITEM_PROP@C3:A06C, ITEM_PROP@C3:A078 | EXT-AWARE | I392/I393 |
| SortValidEquip | ITEM_PROP@C3:A176 | EXT-AWARE | I402/I403 |
| _c3b7e6 | ITEM_PROP@C3:B7EF | VANILLA-ONLY | shop item ids (1-byte shop lists) |
| CalcShopPrice | ITEM_PROP@C3:BA16 | VANILLA-ONLY | shop item ids |
| DrawShopItemStat | ITEM_PROP@C3:BAFE, ITEM_PROP@C3:BB11, ITEM_PROP@C3:BB33 | VANILLA-ONLY | shop item ids |
| _c3bb65 | ITEM_PROP@C3:BB75 | VANILLA-ONLY | shop item ids |
| _c3bcc9 | ITEM_PROP@C3:BCED | VANILLA-ONLY | shop item ids |
| _c3bcfd | ITEM_PROP@C3:BD19, ITEM_PROP@C3:BD1F, ITEM_PROP@C3:BD6C, ITEM_PROP@C3:BDD6, ITEM_PROP@C3:BDEE, ITEM_PROP@C3:BE0C, ITEM_PROP@C3:BE62, ITEM_PROP@C3:BE76, ITEM_PROP@C3:BE94, ITEM_PROP@C3:BEE4 | EXT-AWARE | party comparison: equipment ids from I430-I451 |
| _c3c19c | ITEM_PROP@C3:C1BC | VANILLA-ONLY | shop item ids |
| Loop3 | ITEM_NAME@C0:812F | VANILLA-ONLY | CalcItemWidth (field/text.asm, label inside the proc): dialogue item name, event-supplied 1-byte id |
| _83ee | ITEM_NAME@C0:83EE | VANILLA-ONLY | UpdateDlgText (field/text.asm, label inside the proc): dialogue item name, event-supplied 1-byte id |
| _c16048 | ITEM_NAME@C1:6066 | VANILLA-ONLY | battle message item names (steal / win / thrown): battle ids only |
| ListTextCmd_12 | ITEM_NAME@C1:652D | VANILLA-ONLY | battle item list rows: extended slots presented empty |
| ListTextCmd_0e | ITEM_NAME@C1:6575 | EXT-AWARE | hand names: I540/I541 (XBTLNAME queue -> XItemName + $100*13) |
| MenuTextCmd_12 | ITEM_NAME@C1:6A55 | VANILLA-ONLY | battle message item names |
| MenuTextCmd_0e | ITEM_NAME@C1:6A9F | VANILLA-ONLY | battle message item names |
| FindItemsWithIcon | ITEM_NAME@C3:271F | DEAD | DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange |
| _c380ce | ITEM_NAME@C3:80E2 | EXT-AWARE | called by XC3_ListNameY (I301) for vanilla names; extended names read XItemName directly |
| _c38fe1 | ITEM_NAME@C3:9010 | EXT-AWARE | replaced by I321 (XC3_EqpName) |
| LoadEquipListItemName | ITEM_NAME@C3:9D40 | EXT-AWARE | I387/I388 |
| LoadItemName | ITEM_NAME@C3:C08B | VANILLA-ONLY | shop list names (shop ids) |
| InitWeaponAnim | WEAPON_ANIM@C1:9DB5 | EXT-AWARE | animation number from I530 (XC2_AnimId: extended weapon -> $C0+low byte) |
| Jump animation (anim_cmd.asm:521, battle command $16 handler) | JUMP_ANIM@C1:BA4C | EXT-AWARE | ItemJumpThrowAnim index from I543/I544 (extended weapon -> $80 + low byte, XJumpAnim FA:3700); the Throw consumer C1:B9CC keeps D1:0040 (thrown ids are vanilla only) |

### C. Hook sites (154)

| ID | SNES | Original Rev 1 | Replacement | Consumer | Reason |
|---|---|---|---|---|---|
| I201_EVCMD_66 | C0:9926 | `(data)` | `.word XC0_Ev66 & $FFFF` | EventCmdTbl entry $66 (vanilla EventCmd_66 = RTS lock-up; unused by Rev 1 scripts) | GIVE_EXT_ITEM id16 (3 bytes) |
| I202_EVCMD_67 | C0:9928 | `(data)` | `.word XC0_Ev67 & $FFFF` | EventCmdTbl entry $67 (vanilla unused) | TAKE_EXT_ITEM id16 (3 bytes) |
| I203_EVCMD_68 | C0:992A | `(data)` | `.word XC0_Ev68 & $FFFF` | EventCmdTbl entry $68 (vanilla unused) | HAS_EXT_ITEM id16, switch16 (5 bytes) |
| I210_GIVEITEM_FIND | C0:ACFE | `@acfe:  lda     $1869,x` | `jsr XC0_LdaInvXMask` | GiveItem C0:ACFC (event $80, treasure chests) find-same-item loop | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I211_GIVEITEM_PUT | C0:AD19 | `sta     $1869,x` | `jsr XC0_StaInvXClr` | GiveItem first-empty-slot store | vanilla id stored -> slot high bit cleared |
| I212_TAKEITEM_FIND | C0:AD2F | `@ad2f:  lda     $1869,x` | `jsr XC0_LdaInvXMask` | EventCmd_81 take-item search | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I213_EVCMD8D_SLOT | C0:9FE7 | `lda     $161f,x` | `jsr XC0_8dLoad` | EventCmd_8d (remove character equipment) slot read | extended equipment returns to the inventory with its 9-bit id; vanilla path sees $FF and skips it |
| I214_EVCMD8D_FIND | C0:9FF7 | `:       lda     $1869,x` | `jsr XC0_LdaInvXMask` | EventCmd_8d find-same-item loop | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I215_EVCMD8D_PUT | C0:A017 | `sta     $1869,x` | `jsr XC0_StaInvXClr` | EventCmd_8d empty-slot store | vanilla id stored -> slot high bit cleared |
| I216_CHARINIT_EQUIP | C0:A0D0 | `sta     $161f,y` | `jsr XC0_InitEqp` | character init from CharProp (6 equipment bytes := vanilla ids) | clear the record's 6 equipment high bits |
| I220_NEWGAME_EXT | C0:BDE2 | `ldx     $00 / :       lda     f:BushidoName,x` | `jsl XJ_NewGame / bra $C0BDF1` | InitNewGame Bushido-name copy to $1CF8-$1D27 (JP leftover, never read by the EN game) | extended metadata := 0 + signature; the copy loop is bypassed |
| I221_LOADGAME_SANITIZE | C3:150E | `jsr     PopTimers` | `jsr XC3_LoadOK` | LoadSavedGame (game-over restart) after the slot checksum passed | no/legacy signature -> clear extended metadata; valid -> drop stale/undefined bits; then PopTimers |
| I222_LOADMENU_SANITIZE | C3:29EB | `jsr     LoadSaveSlot` | `jsr XC3_LoadSlotSan` | load menu slot select (title Continue) | same sanitize right after LoadSaveSlot |
| I300_ITEMLIST_QTY | C3:7FA8 | `lda     $1969,y` | `jsr XC3_LdaQtyList` | DrawItemListRow quantity | shop / colosseum: extended slot drawn as empty (qty 0) |
| I301_ITEMLIST_NAME | C3:80C7 | `lda     $1869,y / cmp     #ITEM::EMPTY` | `jsr XC3_ListNameY / rts` | LoadListItemName (item menu, shop sell list, colosseum list) | name via XItemName with the 9-bit id; shop/colosseum: extended slot drawn as empty |
| I302_ITEMDESC_ID | C3:82F8 | `lda     $1869,y` | `jsr XC3_LdaInvY` | InitItemDesc item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I303_ITEMDESC_LOAD | C3:82FB | `jsr     LoadItemDesc` | `jsr XC3_ItemDescB` | InitItemDesc LoadItemDesc | extended description from XDescPtr/XDescText (hidden in shop/colosseum) |
| I304_USEITEM_ID | C3:849D | `lda     $1869,y` | `jsr XC3_LdaInvY` | UseItem item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I305_USEITEM_PROP | C3:84A8 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | UseItem GetItemPropPtr | type / equippable characters of the extended item (item details screen) |
| I306_DETAILS_ID | C3:8696 | `lda     $1869,y` | `jsr XC3_LdaInvY` | DrawItemDetails item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I307_DETAILS_PROP | C3:8699 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | DrawItemDetails GetItemPropPtr | stats / elements / power of the extended item |
| I308_DETAILS_POWER | C3:87A0 | `lda     $1869,y` | `jsr XC3_LdaInvYMask` | DrawWeaponPower Atma/Soul Sabre/Dice id test | an extended weapon is never one of the vanilla '???' weapons (low byte alias) |
| I309_ITEM_SWAP_BITS | C3:27DE | `jmp     DrawItemList` | `jmp XC3_SwapBits` | item move: swap two inventory slots | swap the two slots' high bits too |
| I310_ARRANGE | C3:267F | `jsr     _c326b8 / jsr     SortItemsByIcon` | `jsl XJ_Arrange / nop / nop` | Arrange (copy + SortItemsByIcon) | same algorithm/buffers, 9-bit ids carried, icon from XItemName |
| I311_COLOSSEUM_PICK | C3:ACFA | `lda     $1869,x` | `jsr XC3_LdaInvXMask` | colosseum item select (wager) | extended items cannot be wagered |
| I320_PARTYEQ_NAME_ID | C3:8FC2 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | DrawPartyEquipItems equipment id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I321_EQNAME | C3:8FE1 | `@8fe1:  pha / ldx     #$9e8b` | `jmp XC3_EqpName / nop` | _c38fe1 equipped item name | name via XItemName with the 9-bit id |
| I322_EQNAME_RH | C3:9405 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | equip menu R-hand name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I323_EQNAME_LH | C3:9417 | `lda     $0020,y` | `jsr XC3_LdaEq20` | equip menu L-hand name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I324_EQNAME_HEAD | C3:943D | `lda     $0021,y` | `jsr XC3_LdaEq21` | equip menu helmet name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I325_EQNAME_BODY | C3:944B | `lda     $0022,y` | `jsr XC3_LdaEq22` | equip menu armor name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I326_EQNAME_RELIC1 | C3:9459 | `lda     $0023,y` | `jsr XC3_LdaEq23` | relic menu relic 1 name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I327_EQNAME_RELIC2 | C3:9467 | `lda     $0024,y` | `jsr XC3_LdaEq24` | relic menu relic 2 name | 16-bit id (B = high bit) for the following extended-aware lookup |
| I330_PREVIEW_SAVE | C3:925F | `lda     $001f,y / sta     z64` | `jsr XC3_PrevSave / nop / nop` | _c39233 stat preview: save equipped item | save the slot's high bit too (XSCRATCH $1E3F, transient) |
| I331_PREVIEW_CAND | C3:9264 | `lda     $1869,x` | `jsr XC3_LdaInvX` | _c39233 candidate id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I332_PREVIEW_PUT | C3:9267 | `sta     $001f,y` | `jsr XC3_StaEq1F` | _c39233 temporary equip of the candidate | equipment high bit := candidate high bit for UpdateEquip |
| I333_PREVIEW_RESTORE | C3:931A | `lda     z64 / sta     $001f,y` | `jsr XC3_PrevRestore / nop / nop` | _c39233 restore equipped item | restore the slot's id and high bit |
| I340_REMOVEALL | C3:96A8 | `@96a8:  jsr     GetSelCharPropPtr` | `jmp XC3_RemoveAll` | EquipRemoveAll (Empty, Optimum) | weapon/shield/helmet/armor return to the inventory with their 9-bit ids; high bits cleared |
| I341_OPT_2H_STORE | C3:9712 | `sta     $001f,y` | `jsr XC3_StaEq1F` | EquipOptimum 2-handed weapon store | high bit := B |
| I342_OPT_2H_DEC | C3:9715 | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | EquipOptimum DecItemQty | 9-bit id removal |
| I343_OPT_W_STORE | C3:972A | `sta     $001f,y` | `jsr XC3_StaEq1F` | EquipOptimum weapon store | high bit := B |
| I344_OPT_W_DEC | C3:972D | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | EquipOptimum DecItemQty | 9-bit id removal |
| I345_OPT_S_STORE | C3:9749 | `sta     $0020,y` | `jsr XC3_StaEq20` | EquipOptimum shield store | high bit := B |
| I346_OPT_S_DEC | C3:974C | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | EquipOptimum DecItemQty | 9-bit id removal |
| I347_OPT_G_STORE | C3:9763 | `sta     $0020,y` | `jsr XC3_StaEq20` | EquipOptimum genji off-hand store | high bit := B |
| I348_OPT_G_DEC | C3:9766 | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | EquipOptimum DecItemQty | 9-bit id removal |
| I349_OPT_H_STORE | C3:977A | `sta     $0021,y` | `jsr XC3_StaEq21` | EquipOptimum helmet store | high bit := B |
| I350_OPT_H_DEC | C3:977D | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | EquipOptimum DecItemQty | 9-bit id removal |
| I351_OPT_A_STORE | C3:978F | `sta     $0022,y` | `jsr XC3_StaEq22` | EquipOptimum armor store | high bit := B |
| I352_OPT_A_DEC | C3:9792 | `jmp     DecItemQty` | `jmp XC3_DecQtyB` | EquipOptimum DecItemQty (tail) | 9-bit id removal |
| I353_VALIDW_ID | C3:979F | `lda     $1869,y` | `jsr XC3_LdaInvY` | GetValidWeapons item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I354_VALIDW_PROP | C3:97A6 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | GetValidWeapons type/equippable | extended properties |
| I355_VALIDS_ID | C3:97E1 | `lda     $1869,y` | `jsr XC3_LdaInvY` | GetValidShields item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I356_VALIDS_PROP | C3:97E8 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | GetValidShields type/equippable | extended properties |
| I357_BESTEQUIP | C3:9819 | `@9819:  phy / phb / lda     #$7e` | `jmp XC3_GetBestEquip` | GetBestEquip (Optimum) | returns the 9-bit id; extended items are never imp items (ImpItem low-byte aliases $12/$16/$1C/$24) |
| I358_BEST2HAND | C3:983F | `@983f:  lda     $7e9d89` | `jmp XC3_GetBest2Hand / nop` | GetBest2Hand (Optimum, gauntlet) | returns the 9-bit id; 2-hand flag from the extended properties |
| I359_REMOVE_ID | C3:98E6 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | equip Remove (one slot) id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I360_REMOVE_INC | C3:98E9 | `jsr     IncItemQty` | `jsr XC3_IncQtyB` | equip Remove IncItemQty | 9-bit id back to inventory |
| I361_REMOVE_CLR | C3:98EE | `sta     $001f,y` | `jsr XC3_StaEq1F` | equip Remove slot := $FF | high bit cleared |
| I362_EQUIP_OLD | C3:9923 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | equip (item select) currently equipped id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I363_EQUIP_INC | C3:992A | `jsr     IncItemQty` | `jsr XC3_IncQtyB` | equip IncItemQty (old item back) | 9-bit id |
| I364_EQUIP_NEW | C3:9936 | `lda     $1869,x` | `jsr XC3_LdaInvX` | equip new item id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I365_EQUIP_STORE | C3:9939 | `sta     $001f,y` | `jsr XC3_StaEq1F` | equip store | high bit := B |
| I366_EQUIP_DEC | C3:993C | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | equip DecItemQty (new item out) | 9-bit id |
| I367_HANDTXT_LH | C3:99A6 | `@99a6:  lda     $0020,y` | `jsr XC3_LdaEq20` | R-Hand/L-Hand text (gauntlet) L-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I368_HANDTXT_LH_P | C3:99AF | `@99af:  jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | R-Hand/L-Hand text 2-hand flag | extended properties |
| I369_HANDTXT_RH | C3:99CA | `@99ca:  lda     $001f,y` | `jsr XC3_LdaEq1F` | R-Hand/L-Hand text R-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I370_HANDTXT_RH_P | C3:99CD | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | R-Hand/L-Hand text 2-hand flag | extended properties |
| I371_HANDFX_LH | C3:9A0E | `@9a0e:  lda     $0020,y` | `jsr XC3_LdaEq20` | CheckHandEffects L-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I372_HANDFX_LH_P | C3:9A17 | `@9a17:  jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | CheckHandEffects 2-hand flag | extended properties |
| I373_HANDFX_RH | C3:9A2B | `@9a2b:  lda     $001f,y` | `jsr XC3_LdaEq1F` | CheckHandEffects R-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I374_HANDFX_RH_P | C3:9A2E | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | CheckHandEffects 2-hand flag | extended properties |
| I375_CANEQ_ID | C3:9A5D | `lda     $1869,x` | `jsr XC3_LdaInvX` | CheckCanEquipItem candidate id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I376_CANEQ_PROP | C3:9A60 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | CheckCanEquipItem candidate type | extended properties |
| I377_CANEQ_LH | C3:9A79 | `lda     $0020,y` | `jsr XC3_LdaEq20` | CheckCanEquipItem L-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I378_CANEQ_LH_P | C3:9A80 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | CheckCanEquipItem L-hand type | extended properties |
| I379_CANEQ_RH | C3:9AA5 | `@9aa5:  lda     $001e,y` | `jsr XC3_LdaEq1E` | CheckCanEquipItem R-hand id ($001E,Y) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I380_CANEQ_RH_P | C3:9AAC | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | CheckCanEquipItem R-hand type | extended properties |
| I381_VALIDE_ID | C3:9B76 | `lda     $1869,y` | `jsr XC3_LdaInvY` | GetValidEquip weapon/shield id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I382_VALIDE_PROP | C3:9B7D | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | GetValidEquip weapon/shield type | extended properties |
| I383_VALIDH_ID | C3:9BB6 | `lda     $1869,y` | `jsr XC3_LdaInvY` | GetValidEquip helmet id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I384_VALIDH_PROP | C3:9BBD | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | GetValidEquip helmet type | extended properties |
| I385_VALIDA_ID | C3:9BF2 | `lda     $1869,y` | `jsr XC3_LdaInvY` | GetValidEquip armor id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I386_VALIDA_PROP | C3:9BF9 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | GetValidEquip armor type | extended properties |
| I387_EQLIST_NAME_ID | C3:9D25 | `lda     $1869,y` | `jsr XC3_LdaInvY` | LoadEquipListItemName id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I388_EQLIST_NAME_HI | C3:9D2F | `stz     hM7A` | `jsr XC3_HiM7A` | LoadEquipListItemName M7A high byte | name index = 9-bit id * 13 (ItemName retargeted to XItemName) |
| I389_INCQTY_FIND | C3:9D63 | `@9d63:  cmp     $1869,y` | `jsr XC3_CmpInvYMask` | IncItemQty find-same-item | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I390_INCQTY_PUT | C3:9D85 | `sta     $1869,y` | `jsr XC3_StaInvYClr` | IncItemQty empty-slot store | vanilla id stored -> high bit cleared |
| I391_DECQTY_FIND | C3:9D9C | `@9d9c:  cmp     $1869,y` | `jsr XC3_CmpInvYMask` | DecItemQty find item | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I392_VALIDR_ID | C3:A05F | `lda     $1869,y` | `jsr XC3_LdaInvY` | relic list builder id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I393_VALIDR_PROP | C3:A066 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | relic list builder type/equippable | extended properties |
| I394_RELIC_OLD | C3:A0BB | `lda     $0023,y` | `jsr XC3_LdaEq23` | relic equip currently equipped id ($0023,Y) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I395_RELIC_INC | C3:A0C2 | `jsr     IncItemQty` | `jsr XC3_IncQtyB` | relic equip IncItemQty | 9-bit id |
| I396_RELIC_NEW | C3:A0CE | `lda     $1869,x` | `jsr XC3_LdaInvX` | relic equip new id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I397_RELIC_STORE | C3:A0D1 | `sta     $0023,y` | `jsr XC3_StaEq23` | relic equip store | high bit := B |
| I398_RELIC_DEC | C3:A0D4 | `jsr     DecItemQty` | `jsr XC3_DecQtyB` | relic equip DecItemQty | 9-bit id |
| I399_RELICRM_ID | C3:A124 | `lda     $0023,y` | `jsr XC3_LdaEq23` | relic remove id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I400_RELICRM_INC | C3:A127 | `jsr     IncItemQty` | `jsr XC3_IncQtyB` | relic remove IncItemQty | 9-bit id |
| I401_RELICRM_CLR | C3:A12C | `sta     $0023,y` | `jsr XC3_StaEq23` | relic remove slot := $FF | high bit cleared |
| I402_SORT_ID | C3:A16D | `lda     $1869,y` | `jsr XC3_LdaInvY` | SortValidEquip id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I403_SORT_PROP | C3:A170 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | SortValidEquip attack/defense power | extended properties |
| I404_RELICDESC_1 | C3:A1CD | `lda     $0023,y` | `jsr XC3_LdaEq23` | relic slot description (relic 1) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I405_RELICDESC_2 | C3:A1D2 | `@a1d2:  lda     $0024,y` | `jsr XC3_LdaEq24` | relic slot description (relic 2) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I406_RELICDESC_LD | C3:A1D5 | `@a1d5:  jmp     LoadItemDesc` | `jmp XC3_ItemDescB` | relic slot LoadItemDesc | extended description |
| I407_RELICLDESC_ID | C3:A1E4 | `lda     $1869,x` | `jsr XC3_LdaInvX` | relic list description id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I408_RELICLDESC_LD | C3:A1E7 | `jmp     LoadItemDesc` | `jmp XC3_ItemDescB` | relic list LoadItemDesc | extended description |
| I420_SELLDESC | C3:B4FF | `lda     $1869,x` | `jsr XC3_LdaInvXMask` | shop sell description id | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I421_SELLITEM | C3:BFCF | `lda     $1869,y` | `jsr XC3_LdaInvYMask` | _c3bfcb shop selected inventory item (sell select/qty/price) | extended items cannot be sold |
| I422_BUY_FIND | C3:B5BC | `@b5bc:  cmp     $1869,y` | `jsr XC3_CmpInvYMask` | shop buy: find same item | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I423_BUY_PUT | C3:B5DC | `sta     $1869,y` | `jsr XC3_StaInvYClr` | shop buy: new slot store | high bit cleared |
| I424_OWNED_FIND | C3:BC66 | `@bc66:  cmp     $1869,y` | `jsr XC3_CmpInvYMask` | shop owned-quantity search | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I425_EQUIPPED_CNT | C3:BF97 | `@bf97:  lda     [ze7],y / cmp     ze0` | `jsr XC3_ShopEqCmp / nop` | shop equipped-count compare | an extended equipment byte never equals a shop (vanilla) item |
| I430_CMP_ARMOR_ID | C3:BD5B | `lda     $0022,y` | `jsr XC3_LdaEq22` | shop party compare: armor id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I431_CMP_ARMOR_P | C3:BD66 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: armor defense | extended power |
| I432_CMP_W_EQ1 | C3:BDBA | `lda     $001f,y` | `jsr XC3_LdaEqM1F` | shop party compare: weapon == shop item (R) | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I433_CMP_W_EQ2 | C3:BDC1 | `lda     $0020,y` | `jsr XC3_LdaEqM20` | shop party compare: weapon == shop item (L) | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I434_CMP_W_R | C3:BDC9 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | shop party compare: R-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I435_CMP_W_R_P | C3:BDD0 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: R-hand type | extended properties |
| I436_CMP_W_L | C3:BDE1 | `lda     $0020,y` | `jsr XC3_LdaEq20` | shop party compare: L-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I437_CMP_W_L_P | C3:BDE8 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: L-hand type | extended properties |
| I438_CMP_W_L2 | C3:BDF9 | `lda     $0020,y` | `jsr XC3_LdaEq20` | shop party compare: L-hand id (power) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I439_CMP_W_R2 | C3:BDFF | `lda     $001f,y` | `jsr XC3_LdaEq1F` | shop party compare: R-hand id (power) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I440_CMP_W_POW | C3:BE06 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: weapon power | extended power |
| I441_CMP_S_EQ1 | C3:BE4A | `lda     $001f,y` | `jsr XC3_LdaEqM1F` | shop party compare: shield == shop item (R) | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I442_CMP_S_EQ2 | C3:BE51 | `lda     $0020,y` | `jsr XC3_LdaEqM20` | shop party compare: shield == shop item (L) | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I443_CMP_S_L | C3:BE59 | `lda     $0020,y` | `jsr XC3_LdaEq20` | shop party compare: L-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I444_CMP_S_L_P | C3:BE5C | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: L-hand type | extended properties |
| I445_CMP_S_R | C3:BE6D | `lda     $001f,y` | `jsr XC3_LdaEq1F` | shop party compare: R-hand id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I446_CMP_S_R_P | C3:BE70 | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: R-hand type | extended properties |
| I447_CMP_S_R2 | C3:BE81 | `lda     $001f,y` | `jsr XC3_LdaEq1F` | shop party compare: R-hand id (power) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I448_CMP_S_L2 | C3:BE87 | `lda     $0020,y` | `jsr XC3_LdaEq20` | shop party compare: L-hand id (power) | 16-bit id (B = high bit) for the following extended-aware lookup |
| I449_CMP_S_POW | C3:BE8E | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: shield power | extended power |
| I450_CMP_H_ID | C3:BED3 | `lda     $0021,y` | `jsr XC3_LdaEq21` | shop party compare: helmet id | 16-bit id (B = high bit) for the following extended-aware lookup |
| I451_CMP_H_P | C3:BEDE | `jsr     GetItemPropPtr` | `jsr XC3_PropPtrB` | shop party compare: helmet power | extended power |
| I500_UPDEQ_LOAD | C2:0EE6 | `@0ee6:  lda     $15fb,x` | `jsr XC2_EqLoad` | UpdateEquip 6-slot loop equipment read ($15FB,X) | low byte + equipment high bit (B) for CalcEquipEffect: all stats/elements/effects of extended equipment |
| I501_CALCEQ_OFS | C2:0F9C | `xba / lda     #$1e / jsr     MultAB / tax` | `jsr XC2_PropOfs` | CalcEquipEffect id*30 (XBA/LDA #$1E/JSR MultAB/TAX) | 16-bit ItemProp offset of the 9-bit id (ItemProp retargeted to XItemProp) |
| I502_LEARN_OFS | C2:600C | `@600c:  xba / lda     #$1e / jsr     MultAB` | `jsr XC2_LearnOfs` | LearnItemMagic id*30 (battle end, equipped items) | spell-learning bytes of extended equipment from XItemProp |
| I510_BINV_HAND_L | C2:5481 | `lda     $1620,y` | `jsr XC2_HandL` | InitInventory L-hand (shield slot) read | 9-bit id of the hand item (also clears the battle name queue) |
| I511_BINV_HAND_L_CP | C2:5485 | `jsr     CopyItemProp` | `jsr XC2_CopyItemPropB` | InitInventory L-hand CopyItemProp | extended hand item: properties from XItemProp, never usable/throwable |
| I512_BINV_HAND_R | C2:5493 | `lda     $161f,y` | `jsr XC2_HandR` | InitInventory R-hand (weapon slot) read | 9-bit id |
| I513_BINV_HAND_R_CP | C2:5497 | `jsr     CopyItemProp` | `jsr XC2_CopyItemPropB` | InitInventory R-hand CopyItemProp | extended hand item: properties from XItemProp, never usable/throwable |
| I516_BINV_EXT_EMPTY | C2:54B0 | `sep #PSW_A|PSW_I / tdc` | `jsr XC2_ExtSlotsEmpty` | InitInventory: end of the 256-slot copy loop (SEP #$30 / TDC) | every extended slot is re-copied as the vanilla loop copies an empty slot (qty 0, CopyItemProp($FF)): not in Item/Throw/Tools lists, cannot be used or truncated; zero bitmap bytes skipped (battle init timing unchanged) |
| I520_BTLEND_INV | C2:4981 | `ldx     #$00ff / ldy     #$04fb` | `jsl XJ_BattleEndInv / bra $C2499E` | battle end: battle inventory -> $1869/$1969 | vanilla slots copied as before; extended slots preserved; vanilla items placed at their positions re-homed |
| I521_BTLEND_WAGER | C2:49AD | `@49ad:  cmp     $1869,x` | `jsr XC2_CmpInvXMask` | battle end: colosseum wager removal search | extended slot reads as $FF: never selectable / never matched by a vanilla id |
| I530_ANIM_ID | C2:29FE | `lda     near wTargetProp2::RHandItem,x` | `jsr XC2_AnimId` | weapon animation number (RHandItem+1 -> $B7) | extended weapon -> animation number $C0+low byte (XWeaponAnimFull) |
| I531_SPEAR_R | C2:1814 | `lda     near wTargetProp2::RHandItem,x / jsr     SpearEffect` | `jsr XC2_SpearR` | Jump: SpearEffect(RHandItem) | extended spear (XExtFlags bit1) doubles Jump damage like vanilla $1D-$24 |
| I532_SPEAR_L | C2:181A | `lda     near wTargetProp2::LHandItem,x / jsr     SpearEffect` | `jsr XC2_SpearL` | Jump: SpearEffect(LHandItem) | as above, left hand |
| I533_OGRE_NIX | C2:3F0B | `lda     near wRHandItemList::ItemID,x` | `jsr XC2_OgreLoad` | MP-crit weapon break test (Ogre Nix id $17) | an extended weapon never matches (would be broken/lost) |
| I540_HANDNAMES | C1:4BDA | `lda     near wLHandItemList::ItemID,y / sta     near w7e5755+11` | `jsl XJ_HandNames` | battle Item menu hand header (L-hand id store) | name queue for extended hand items |
| I541_NAMEIDX | C1:656C | `ldx     $30 / lda     z55 + 1` | `jsl XJ_NameIdx` | ListTextCmd_0e name index (LDX $30 / LDA $56) | extended hand name from XItemName |
| I542_SWAPGUARD | C1:89D2 | `@89d5:  lda     near w7e7b39 / cmp     #$ff` | `jsl XJ_SwapGuard` | check_equip (battle hand <-> inventory exchange, 3 callers) | the replaced hand (identified by the caller) cannot hold an extended item: refused like a vanilla refusal |
| I545_HANDSWAP_BITS | C1:8E8F | `ldx     near w7e7b05 / tdc` | `jsl XJ_HandSwapBits` | SelectEquipItem R-hand <-> L-hand exchange (LDX w7e7b05 / TDC) | the two hand equipment bits are swapped with the hand entries (write-back C2:20AB stores low bytes) |
| I543_JUMPANIM_L | C1:BA41 | `@ba44:  lda     near wLHandItemList::ItemID,x / inc` | `jsl XJ_JumpAnimL` | Jump animation: L-hand item id + 1 (ItemJumpThrowAnim index) | extended weapon -> $80 + low byte (XJumpAnim FA:3700; the C1:BA4C operand is retargeted) |
| I544_JUMPANIM_R | C1:BA47 | `@ba4a:  lda     near wRHandItemList::ItemID,x / inc` | `jsl XJ_JumpAnimR` | Jump animation: R-hand item id + 1 (ItemJumpThrowAnim index) | as I543 (right hand) |
