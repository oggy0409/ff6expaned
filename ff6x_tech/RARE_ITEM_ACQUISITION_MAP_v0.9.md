# RARE / KEY ITEM ACQUISITION MAP — TECH v0.9

One binding per key item (future event symbol, prerequisite flags, one-time). The events themselves are story content (hard stop for v0.9); they will use the v0.9 event API (`RARE_ITEM_EVENT_API_v0.9.md`).

| rare id | name | planned source | event symbol | prerequisites | one-time | consumed |
|---|---|---|---|---|---|---|
| 20 | Darill's Token | Setzer arc: Darill's tomb / Falcon | `EV_RARE_DARILLS_TOKEN` | PREREQ_SETZER_ARC | yes | no |
| 21 | Concord Sigil | Sanctuary of Concord | `EV_RARE_CONCORD_SIGIL` | PREREQ_SANCTUARY_OF_CONCORD | yes | no |
| 22 | Cinder Sigil | arc design (source not recovered) | `EV_RARE_CINDER_SIGIL` | PREREQ_TBD_ARC_DESIGN | yes | no |
| 23 | Triune Sigil | joins the Concord and Cinder sigils | `EV_RARE_TRIUNE_SIGIL` | HAS_RARE KEY_CONCORD_SIGIL, HAS_RARE KEY_CINDER_SIGIL | yes | no (the two sigils are kept: consumption not locked) |
| 24 | Broken Seal | late story (World of Ruin) | `EV_RARE_BROKEN_SEAL` | PREREQ_TBD_ARC_DESIGN | yes | no |

Triune Sigil (23): its prerequisite is owning both Concord Sigil (21) and Cinder Sigil (22) — an event checks `HAS_RARE 21` and `HAS_RARE 22` before `GIVE_RARE 23`. The two sigils are kept (consumption is not locked).
