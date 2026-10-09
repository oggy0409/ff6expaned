# TECH v0.8 — weapon graphics / animation map

No new custom weapon graphic is locked, so every weapon uses a deliberate vanilla template of the same family. The builder copies the template's WeaponAnimProp entry (EC:E400, index template+1) into XWeaponAnimFull[$C0 + low byte] and its ItemJumpThrowAnim byte (D1:0040) into XJumpAnim[$80 + low byte]; the ItemProp record is built from the item definition only. The low-byte vanilla alias (e.g. $100 -> Dirk, $13D -> Chocobo Brsh) is never consulted for graphics. Verified in the emulator (`tools/emu_equip_battle_v08.py` W1/J1): the animation number used by Fight, and every rendered frame of Fight (all 13) and Jump (both spears) equal to the same battle continued with the template weapon in hand (one in-battle state, only the hand item id differs).

| ID | Weapon | Family | Template (graphic + animation) | Icon | Jump | Runic | 2-hand (Gauntlet) | Bushido flag | Dual wield | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| $100 | Tempered Edge | sword | $15 Falchion | Falchion's | yes | yes | yes | yes | Genji Glove: yes |  |
| $101 | Imperial Saber | sword | $13 Enhancer | Enhancer's | yes | yes | yes | yes | Genji Glove: yes |  |
| $102 | Leo's Blade | sword | $18 Excalibur | Excalibur's | yes | yes | yes | yes | Genji Glove: yes |  |
| $103 | Raider Knife | knife | $04 ThiefKnife | ThiefKnife's | yes | yes | yes | no | Genji Glove: yes | steal on hit (ThiefKnife special) |
| $104 | Sandpiercer | spear | $20 Partisan | Partisan's | x2 (spear) | yes | yes | no | Genji Glove: yes |  |
| $105 | Duncan Claw | claw | $59 Tiger Fangs | Tiger Fangs's | yes | no | no | no | Genji Glove: yes |  |
| $106 | Moonless | ninja blade | $28 Hardened | Hardened's | yes | yes | yes | no | Genji Glove: yes |  |
| $107 | Doma Edge | katana | $32 Sky Render | Sky Render's | yes | yes | yes | yes | Genji Glove: yes |  |
| $108 | Darill's Dirk | knife | $08 Graedus | Graedus's | yes | yes | yes | no | Genji Glove: yes |  |
| $109 | Magister Rod | rod | $3C Magus Rod | Magus Rod's | yes | no | yes | no | Genji Glove: yes |  |
| $10A | Concord Brush | brush | $40 Rainbow Brsh | Rainbow Brsh's | yes | no | yes | no | Genji Glove: yes |  |
| $10B | Gale Lance | spear | $23 Aura Lance | Aura Lance's | x2 (spear) | yes | yes | no | Genji Glove: yes |  |
| $10C | Echo Dagger | knife | $06 Man Eater | Man Eater's | yes | yes | yes | no | Genji Glove: yes |  |

Not throwable (Throw excluded under Option C). Offering (4 strikes) and Genji Glove (dual wield) use the same per-hand animation numbers (emulator O1 / G1). No weapon casts a spell (proc).
