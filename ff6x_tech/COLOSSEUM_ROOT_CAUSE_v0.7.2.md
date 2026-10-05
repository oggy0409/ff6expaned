# TECH v0.7.2 — Colosseum black screen: root cause and fix

**Status:** STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.

## 1. Reported failure (TECH v0.7.1 user runtime QA)
Every Colosseum attempt from the v0.7.1 QA ROM went to a black screen after the wager/fighter step, for every wager
item and fighter ("universal").

## 2. Root cause (one sentence)
The v0.7.1 **QA harness** entry "Colosseum (wager list)" ran event command `$9A` (open the Colosseum menu) **alone**.
`$9A` is only the first half of the vanilla sequence: it ends by disabling the next map fade-in and forcing a map
reload. The vanilla receptionist script then either starts the battle (`$AF`) or fades back in. The harness did
neither, so the screen stayed black and no battle started. **No engine, item-bank, battle-init or Colosseum code is
involved**: the same harness bytes black-screen identically on the clean Rev 1 ROM.

## 3. Evidence

### 3.1 What `$9A` does (Rev 1, C0:B0B2 `EventCmd_9a`)
```
lda #MENU_TYPE::COLOSSEUM / sta $0200 / jsr OpenMenu      ; wager list + fighter select
lda $0205 / cmp #$ff -> $1EBD bit 6 (event switch $1EE) = "valid wager chosen"
lda #$c0 / sta $11fa        ; map startup flags: bit 7 skip startup event, bit 6 DISABLE MAP FADE-IN
lda #$01 / sta $84          ; reload the map
```
Field init (C0 `init.asm`, after the reload): `lda $11fa / and #$40 / bne skip / jsr FadeIn` → with `$C0` the map
comes back **without** a fade-in. The script that called `$9A` must restore the screen itself.

### 3.2 What the vanilla receptionist does (Rev 1, NPC event CB:78C3 → choice "(With pleasure.)" → CB:78D9)
| Address | Bytes | Command |
|---|---|---|
| CB:78D9 | `5A 08` | fade_out 8 |
| CB:78DB | `5C` | wait_fade |
| CB:78DC | `9A` | colosseum menu |
| CB:78DD | `C0 EE 01 72 79 01` | if switch $1EE = 0 (no valid wager) → CB:7972 |
| CB:78E3 | `C0 EF 01 6C 79 01` | if switch $1EF = 0 → CB:796C (normal battle; $1EF = 1 is the Shadow scene) |
| CB:796C | `AF` | **colosseum battle** (battle $23F, background $1C, `$11FA = $C0`) |
| CB:796D | `B2 72 79 01` | call CB:7972 |
| CB:7971 | `FE` | return |
| CB:7972 | `59 04` | **fade_in 4** |
| CB:7974 | `5C FE` | wait_fade, return |

### 3.3 What the v0.7.1 QA harness did (QA ROM only, FF:0080 `QaColo7`)
| Address | Bytes | Command |
|---|---|---|
| FF:0080 | `9A` | colosseum menu |
| FF:0081 | `31 82 81 FF` | party_step RIGHT 1 |
| FF:0085 | `FE` | return |

No `$AF` and no fade-in: after the wager and fighter are confirmed, the menu closes, the map reloads with fade-in
disabled, and the script returns, leaving the screen black. Leaving the wager list with B gives the same black
screen, because `$9A` writes `$11FA = $C0` in both cases.

### 3.4 Emulator proof (`tools/emu_colosseum.py`, report `out/emulator_v072/colosseum/COLOSSEUM_EMULATOR_REPORT.json`, **60/60 PASS**)
| Run | Result |
|---|---|
| v0.7.1 QA ROM, harness → wager ThiefKnife, fighter Wedge | battle **not** entered, screen brightness **0.0** (= user report) |
| v0.7.1 QA ROM, harness → wager list left with B | screen brightness **0.0** |
| **clean Rev 1**, the same harness bytes `9A 31 82 81 FF FE` injected as a WRAM event | battle **not** entered, brightness **0.0**, the same failure without any FF6X code |
| v0.7.1 QA ROM, **real receptionist** on the Colosseum map $19D (CB:78C3) | battle $23F entered, identical frames/result to Rev 1 (`v071qa` rows) |
| clean Rev 1 / accepted v0.6.0 production / v0.7.2 production / v0.7.2 QA, real receptionist | identical to Rev 1 |
| v0.7.2 QA ROM, QA menu `Fight` (calls CB:78D9): 4 combinations with POKE-won battles (C1–C4, incl. Terra wearing the 3 QA items) + 4 natural combinations with the `Get wager kit` items | battle $23F, correct opponent and fighter, rendered, win → prize / loss → wager lost, return with fade-in and control; identical to Rev 1 for every combination that Rev 1 can run |
| v0.7.2 QA ROM, QA menu `Fight`, wager list left with B | screen fades back in, field control |

So the item engine was never the cause. The user's v0.7.1 test could only reach the Colosseum through the harness
(New Game; the real Colosseum is in the World of Ruin), and that path was broken by the harness script alone.

### 3.5 Checked and excluded (the ten areas named in the hotfix request)
| # | Area | Finding |
|---|---|---|
| 1 | transition after wager/fighter confirmation | cause found: harness lacked `$AF` / fade-in (§3.3) |
| 2 | opponent/formation lookup | ColosseumProp DF:B600 unchanged; opponent = ColosseumProp monster in all 39 Colosseum battles of the test; battle id $23F |
| 3 | battle-type / mode flags | `$AF` writes $11E0/$11E2/$11E4/$1ED7: vanilla code, untouched; battle RAM at entry identical to Rev 1 (same frames) |
| 4 | selected-fighter setup | Terra / Wedge / Vicks each render and fight exactly as in Rev 1 (29–49 distinct rendered battle frames identical to Rev 1 per combination) |
| 5 | v0.7.1 C3 hooks before battle launch | the menu path runs them in all receptionist runs; results byte-identical to Rev 1; extended items show as blank, unselectable lines (v0.7.1 M3) |
| 6 | v0.7.1 C2 battle-init hooks | run in every Colosseum battle; identical battle frames/results to Rev 1; C4 (QA items equipped) keeps all three extended items |
| 7 | JSR/JSL register/flag preservation | no crash/hang in 39 battles + 3 cancels; identical results to Rev 1 |
| 8 | relocated helpers during setup | no difference observable at any compared point |
| 9 | stack/return corruption | event stack returns correctly to the caller in every run (harness `party_step` executes; field control returns) |
| 10 | vs Rev 1 / v0.6.x | v0.6.0 production and v0.7.2 production give the same frames and inventory as Rev 1, via both the script and the real receptionist |

## 4. Fix (v0.7.2)
`events/qa_access_v071/events.evt`: the harness's Colosseum entry now **calls the vanilla receptionist branch itself**:
```
@QaColo7                   ; QA menu "Colosseum (full battle)"
dlg qa7_colo               ; Colosseum (vanilla script) / Fight (wager list) / Get wager kit / Cancel
choice QaColoFight7, QaColoKit7, QaCancel6
@QaColoFight7
call VanillaColosseum      ; B2 D9 78 01 -> CB:78D9 (fade_out, $9A, $AF battle or fade_in)
party_step RIGHT 1
return
@QaColoKit7                ; a New Game has no items: vanilla wagers for the user test
give_item $EE x3, $F0 x3, $04, $09   ; Elixir, Fenix Down (vs Cactrot: Rename Card / Magicite), ThiefKnife, ValiantKnife
```
`VanillaColosseum = CB:78D9` is declared in `patches/map_v04.py VANILLA_EXTERNALS`. The builder asserts the Rev 1 bytes
at CB:78D9, CB:796C and CB:7972 (`VANILLA_ASSERTS`) before it emits the call. Nothing is written there.
QA prompt text: `TECH v0.7.2 QA ACCESS`. The menu entry is renamed `Colosseum (full battle)`.

Production and celes-tech differ from v0.7.1 only in the build-metadata version byte and the SNES checksum (3 bytes
each). The engine is byte-identical to v0.7.1 (`PATCH_TABLE_v0.7.2.md`, delta section).

## 5. Test-method note (no ROM change)
The battle seeds its random number generator from the game clock's frame byte (C2:2440 `lda $021e / asl / asl /
sta $be`). The emulator test's setup (New Game boot plus four event `$80` item gives) does not take the same number of
frames in v0.7.x as in Rev 1. Event `$80` scans the 256 slots through the extended-slot mask, which costs about one
frame per newly given item (KNOWN_RISKS R16). So without care, an un-POKEd fight would compare two different random
seeds. The test therefore sets the clock `$021B-$021E` to the same value in every ROM before each Colosseum entry.
With identical seeds every ROM gives identical battles and results.
