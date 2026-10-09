# RARE / KEY ITEM MASTER TABLE — TECH v0.9

Registry: `items/production_v09/rare_items.json` (source-controlled; validated by the builder). Logical rare ids 0–19 are the vanilla rare items (unchanged, event bits $1D0–$1E3); **20–51 are FF6X rare items (32 = capacity)**: 20–24 the 5 locked key items, 25–51 reserved (the QA build fills them with placeholders to prove the capacity). Locked: the 5 names. Story arc, source, prerequisites, consumption and ending dependency are DERIVED from the names / the locked concept list and need creative confirmation.

| rare id | code | name (13-char display) | arc | acquisition (symbol) | prerequisite | one-time | consumed | ending | storage |
|---|---|---|---|---|---|---|---|---|---|
| 20 | KI-01 | Darill's Token (Darill'sToken) | Setzer arc (Darill) | Setzer arc: Darill's tomb / Falcon (`EV_RARE_DARILLS_TOKEN`) | PREREQ_SETZER_ARC | yes | no | none | XRARE $1E1D bit 0 |
| 21 | KI-02 | Concord Sigil (Concord Sigil) | Sanctuary of Concord arc | Sanctuary of Concord (`EV_RARE_CONCORD_SIGIL`) | PREREQ_SANCTUARY_OF_CONCORD | yes | no | Triune Sigil prerequisite | XRARE $1E1D bit 1 |
| 22 | KI-03 | Cinder Sigil (Cinder Sigil) | arc TBD (Cinder) | arc design (source not recovered) (`EV_RARE_CINDER_SIGIL`) | PREREQ_TBD_ARC_DESIGN | yes | no | Triune Sigil prerequisite | XRARE $1E1D bit 2 |
| 23 | KI-04 | Triune Sigil (Triune Sigil) | reconstruction / finale | joins the Concord and Cinder sigils (`EV_RARE_TRIUNE_SIGIL`) | HAS_RARE KEY_CONCORD_SIGIL, HAS_RARE KEY_CINDER_SIGIL | yes | no (the two sigils are kept: consumption not locked) | ending / reconstruction dependency | XRARE $1E1D bit 3 |
| 24 | KI-05 | Broken Seal (Broken Seal) | finale / reconstruction | late story (World of Ruin) (`EV_RARE_BROKEN_SEAL`) | PREREQ_TBD_ARC_DESIGN | yes | no | ending / reconstruction dependency | XRARE $1E1D bit 4 |

Descriptions:

* 20 Darill's Token: *A token of Darill, kept / aboard the Falcon.*
* 21 Concord Sigil: *Sigil of the Sanctuary / of Concord.*
* 22 Cinder Sigil: *A sigil warm as / smoldering cinders.*
* 23 Triune Sigil: *Three sigils made one.*
* 24 Broken Seal: *A broken seal. Its power / is spent.*

Key items have no combat stats. Vanilla rare items (0–19): 0 Cider, 1 Old Clock-Key, 2 Fish, 3 Fish, 4 Fish, 5 Fish, 6 Lump of Metal, 7 Lola's Letter, 8 Coral, 9 Books, 10 Royal Letter, 11 Rust-Rid, 12 Autograph, 13 Manicure, 14 Opera Record, 15 Magn.Glass, 16 Eerie Stone, 17 Odd Picture, 18 Dull Picture, 19 Pendant
