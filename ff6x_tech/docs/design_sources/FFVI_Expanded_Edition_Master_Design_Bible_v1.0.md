# FINAL FANTASY VI — EXPANDED EDITION
## Master Design Bible v1.0

**Target baseline:** Final Fantasy VI / Final Fantasy III (SNES/SFC design rules)
**Genre:** story-expansion ROM hack
**Narrative position:** canon-compatible expansion, primarily World of Ruin
**Primary rule:** preserve the original ending, character identities, and the disappearance of magic.

---

# 1. PROJECT PILLARS

1. **Do not rewrite FFVI. Expand what it deliberately leaves unsaid.**
2. **World of Ruin is about reconstruction, not merely collecting the party.** Every major character quest should leave a visible mark on the world.
3. **No resurrection that cheapens a canonical death.** Leo, Rachel, Darill, Baram, Elayne and Owain remain dead.
4. **No redemption rewrite for Kefka.** New material may explain the Magitek program and his deterioration, but never excuse him.
5. **Shadow/Relm remains understated.** The mod can bring their story to emotional closure without a melodramatic explicit confession.
6. **No new permanent playable character in v1.0.** The existing 14-character ensemble is already the heart of FFVI; new characters are NPCs/guests/bosses.
7. **No new living Esper after the ending.** Optional ancient magic content occurs before Kefka falls. Magic still disappears in the ending.
8. **New rewards are sidegrades or character-specialized upgrades.** Lightbringer, Ragnarok, Ultima Weapon, Paladin Shield, Master's Scroll etc. remain meaningful.
9. **All major added content is optional.** A player may still finish FFVI with nearly the original route.
10. **Dialogue style:** short SNES-era lines, subtext over exposition, humor used sparingly, no modern slang, no lore-dump monologues.

---

# 2. HIGH-LEVEL STRUCTURE

## World of Balance — Seeding Layer
Three short optional additions seed later content without damaging the original pacing.

### WOB-A — Research Annex
During the Magitek Research Facility escape, an optional side room contains records of early Magitek infusion trials. It establishes that Kefka was an early unstable subject and that Celes was processed later under a safer protocol.

### WOB-B — Old Thamasa Shrine
After the burning-house sequence, a sealed basement can be opened with Strago. It contains murals showing human mages fighting alongside Espers before the War of the Magi collapsed into factional warfare.

### WOB-C — Darill's Token
After obtaining the Blackjack, speaking to Setzer at a specific rest point triggers a short scene about Darill and a brass race token. This token becomes the key to Setzer's World of Ruin quest.

## World of Ruin — Expansion Layer
The Falcon unlocks eight major arcs and several minor reconstruction quests.

1. **Celes — Echoes of the Empire**
2. **Terra — Children of the Ruined World**
3. **Cyan — The Last Kingdom of Doma**
4. **Shadow & Relm — The Man Behind the Mask**
5. **Edgar & Sabin — Two Sons of Figaro**
6. **Setzer — The Last Race**
7. **War of the Magi — The Forgotten Age**
8. **Endgame — The First Magi**

Each completed major arc sets one permanent **Hope Flag**. The game never shows a numerical Hope meter. Flags are used for NPC changes, rebuilt map states, optional scenes and the expanded ending.

---

# 3. LEVEL / BALANCE BANDS

New content is divided into four intended bands.

| Band | Recommended party level | Typical normal enemy HP | Typical boss HP | Reward tier |
|---|---:|---:|---:|---|
| A | 26–32 | 1,800–5,500 | 24,000–38,000 | strong WoR midgame |
| B | 32–38 | 3,000–8,500 | 34,000–48,000 | late-WoR sidegrade |
| C | 38–45 | 5,000–12,000 | 42,000–60,000 | near-endgame specialized |
| D | 45+ | 7,000–18,000 | 55,000–65,000 per phase | superboss / prestige |

**SNES HP rule:** no single boss phase is designed above 65,535 HP. Superbosses use scripted phase transitions, formation swaps or hidden revive/state changes.

---

# 4. MAJOR ARC 1 — CELES: ECHOES OF THE EMPIRE

## Purpose
Give Celes closure with the Empire and reveal the Magitek-human experimentation program without softening Kefka.

## Unlock
- Falcon obtained.
- Celes in party.
- Visit Vector ruins via a new landing point south-east of Kefka's Tower debris field.

## New maps
1. **Vector Ruins — Outer Ward**
2. **Imperial Research Annex B2**
3. **Infusion Theater**
4. **Records Vault**

## Quest flow
1. Celes recognizes an old officer insignia in the ruins.
2. Party finds survivors led by former Imperial medic **Dr. Edrin Vale**.
3. Vale refuses to enter the Annex. Celes remembers fragments of childhood training.
4. Inside are failed Magitek infusion chambers and records identifying Kefka as an early subject.
5. A dormant autonomous weapon interprets Celes as a deserter and activates the Annex defenses.
6. Boss: **Magitek Praetor**.
7. In the Records Vault Celes finds that General Leo repeatedly petitioned to halt human trials.
8. Vale admits he participated as a junior physician and asks Celes what should be done with the research.
9. Player receives a choice with no gameplay penalty:
   - Burn the records.
   - Preserve them in Figaro so the crimes are remembered.
10. Either choice sets **Hope Flag: Empire**; dialogue and ending vignette differ.

## Key dialogue — entering the Annex

**Celes:** I know this corridor.

**Locke:** You were stationed here?

**Celes:** No.

**Locke:** ...Celes?

**Celes:** I woke up here.

**Edgar:** Then we do this at your pace.

**Celes:** No. We do it once.

## Record scene

**Terminal:** SUBJECT K-01. INFUSION RESPONSE: EXTREME.

**Terminal:** COGNITIVE INSTABILITY: PROGRESSIVE.

**Sabin:** K-01... Kefka?

**Celes:** Keep reading.

**Terminal:** SUBJECT C-07. REVISED PROCEDURE SUCCESSFUL.

**Terminal:** MILITARY APTITUDE: EXCEPTIONAL.

**Locke:** C...

**Celes:** I said keep reading.

## Leo record

**Terminal:** GENERAL LEO CHRISTOPHE: REQUEST DENIED.

**Terminal:** SUBJECTS ARE SOLDIERS OF THE EMPIRE.

**Terminal:** PROJECT DIRECTIVE REMAINS IN EFFECT.

**Celes:** ...He knew.

**Edgar:** And he tried to stop it.

**Celes:** Not soon enough.

**Edgar:** No. But he tried.

## End choice

**Vale:** Burn it, and no one can repeat our work.

**Celes:** Or prove it ever happened.

**Vale:** I don't deserve to choose.

**Celes:** No. You don't.

### Choice A — Burn
**Celes:** Some knowledge has already cost enough lives.

### Choice B — Preserve
**Celes:** Figaro will seal it. Names, orders, everything.

**Celes:** If the world rebuilds, it rebuilds knowing what we did.

## Boss — Magitek Praetor
- Level 36
- HP 47,800
- MP 9,000
- Speed 45
- Battle Power 34
- Defense 165
- Magic Defense 150
- Magic Power 13
- Weak: Lightning
- Null: Poison
- Absorb: none
- Immune: Doom, Petrify, Confuse
- AI:
  - Opening: Magitek Barrier (Protect + Shell)
  - Rotation: Magitek Laser / Missile / Tek Beam / physical
  - At 70% HP: launches two **Suppressor Bits**
  - At 40% HP: Barrier overload; loses Defense, gains Haste
  - If hit by Lightning three times: uses Grounding Field, temporarily nulls Lightning for 3 turns
- Reward: **Runic Crest** relic

## Arc reward
### Runic Crest — Relic, Celes only
- Magic +5
- M.Evade +20%
- When Runic absorbs a spell, restores 20% more MP than normal. *(ASM extension; fallback version: Magic +5/M.Evade +20 only.)*

---

# 5. MAJOR ARC 2 — TERRA: CHILDREN OF THE RUINED WORLD

## Purpose
Continue Terra's Mobliz story: love is not only protection but building a future.

## Unlock
- Terra recruited from Mobliz.
- Return to Mobliz with Terra.

## New maps
1. **Mobliz Rebuilt State 1**
2. **Collapsed Shelter**
3. **Buried Magitek Depot**
4. **Mobliz Rebuilt State 2**

## Quest flow
1. Children are sick because Mobliz's well has become contaminated.
2. Terra refuses to abandon the village but asks the party to investigate.
3. Beneath the shelter is a forgotten Imperial supply depot broken open by the cataclysm.
4. Old Magitek coolant is leaking into groundwater.
5. The depot's life-support system has fused with an escaped magical specimen.
6. Boss: **Magi-Eater**.
7. The party shuts down the leak and restores the well.
8. Terra decides Mobliz needs more than her strength; it needs farmers, carpenters and teachers.
9. Side objectives recruit three survivor NPCs from Tzen, Nikeah and Maranda.
10. Mobliz visibly rebuilds: repaired roof tiles, crops, new shop, children outdoors.

## Key dialogue

**Duane:** We can move them again.

**Terra:** To where?

**Duane:** Anywhere safer than this.

**Terra:** We keep saying that.

**Katarin:** Terra...

**Terra:** I thought protecting them meant standing between them and monsters.

**Terra:** Maybe it also means giving them somewhere they don't have to run from.

## After recruiting the carpenter

**Child:** Miss Terra! Look!

**Terra:** A door?

**Child:** Our door.

**Terra:** ...It's beautiful.

## Boss — Magi-Eater
- Level 34
- HP 39,600
- MP 12,000
- Speed 38
- Battle Power 28
- Defense 145
- Magic Defense 175
- Magic Power 15
- Weak: Holy
- Absorb: Fire, Ice, Lightning one at a time; affinity rotates every 3 turns
- Special mechanic: each absorbed element raises Magic Power by 2 until phase reset
- Uses: Drain, Osmose, Bio, Gravity, elemental -aga spell matching current affinity
- At 25% HP: **Starved Core** removes elemental absorption but gains double speed
- Reward: **Maduin's Locket**

### Maduin's Locket — Relic, Terra only
- Magic +6
- Stamina +3
- Trance duration +25% *(ASM extension; fallback: MP +25% via existing relic flag if reused.)*

---

# 6. MAJOR ARC 3 — CYAN: THE LAST KINGDOM OF DOMA

## Purpose
Turn Cyan's personal healing into a decision about whether Doma should live again.

## Unlock
- Cyan recruited.
- Cyan's Dream completed.

## New maps
1. **Doma Courtyard — Reclaimed**
2. **Doma Aqueduct**
3. **Eastern Refugee Camp**
4. **Doma Throne Hall — Restored State**

## Quest flow
1. Survivors have returned but the water system is poisoned and monsters infest the aqueduct.
2. Cyan initially believes Doma should remain a tomb.
3. A young survivor named **Ren** challenges him: the dead did not ask the living to die with them.
4. Party enters the aqueduct.
5. Boss: **Miasma Regent**, a monster spawned from poison and magical residue.
6. Water is restored.
7. Cyan finds the royal standard and considers taking command.
8. He refuses kingship; Doma will become a council-led settlement.
9. Cyan remains its guardian, not its ruler.

## Key dialogue

**Ren:** Sir Cyan. We need the eastern gate opened.

**Cyan:** This castle is a grave.

**Ren:** It was our home first.

**Cyan:** Thou knowest not what happened here.

**Ren:** I was here.

*(pause)*

**Ren:** I lost my mother in the hall below us.

**Ren:** I still want a roof.

## After boss

**Cyan:** I did mistake remembrance for duty.

**Sabin:** Meaning?

**Cyan:** I thought to honor the dead, Doma must remain as they left it.

**Cyan:** Yet a kingdom is not stone.

**Cyan:** It is its people.

## Boss — Miasma Regent
- Level 38
- HP 49,200
- MP 8,200
- Speed 36
- Battle Power 36
- Defense 170
- Magic Defense 142
- Magic Power 12
- Weak: Fire, Holy
- Absorb: Poison
- Starts with Sap aura applied to all characters without Poison immunity
- Uses: Bio, Acid Rain, Venomist, physical
- Every 4 turns summons two **Tainted Retainers**
- At low HP: casts Reflect on itself and begins bouncing Bio/Drain
- Reward: **Doma Crest**

### Doma Crest — Relic, Cyan only
- Vigor +5
- Stamina +5
- Speed +2
- Bushido charge time reduced by one step *(ASM extension; fallback: Auto-Haste effect is too strong and should NOT be used.)*

---

# 7. MAJOR ARC 4 — SHADOW & RELM: THE MAN BEHIND THE MASK

## Purpose
Resolve the Clyde/Relm subplot without breaking FFVI's restraint.

## Unlock
- Shadow survived Floating Continent and is recruited.
- Relm recruited.
- At least four Shadow dream sequences viewed.
- Enter Thamasa with Shadow + Relm.

## New maps
1. **Old Thamasa Outskirts**
2. **Burned Cottage**
3. **Bandit's Hollow**
4. **Cliff of Ash**

## Quest flow
1. Interceptor leaves the party and runs toward an abandoned cottage.
2. Relm finds a locked box carrying her mother's initials.
3. Shadow demands that she leave it.
4. The key is in Bandit's Hollow, an old smuggler cache once used by Clyde and Baram.
5. The cave projects illusionary memories through residual magic.
6. Boss: **Guiltshade**, not Baram's literal ghost, but a magical entity taking forms from Shadow's memory.
7. The box contains letters never sent to Clyde.
8. Relm confronts Shadow.
9. Shadow never explicitly says “I am your father.”
10. He leaves Relm her mother's ring and remains recruitable.

## Key dialogue — cottage

**Relm:** Interceptor? What's gotten into you?

**Shadow:** Leave him.

**Relm:** He brought us here.

**Shadow:** Then he made a mistake.

**Relm:** Funny. You always say that when you want somebody to stay away.

## Finding the letter

**Relm:** “Clyde...”

**Shadow:** Put it back.

**Relm:** Who was he?

**Shadow:** A coward.

**Relm:** Mom wrote to him.

**Shadow:** ...

**Relm:** She waited for him.

**Shadow:** Enough.

## Final scene

**Relm:** You knew her.

**Shadow:** Yes.

**Relm:** Better than Grandpa did?

**Shadow:** In a different life.

**Relm:** Then look at me.

*(Shadow turns.)*

**Relm:** Was Clyde my father?

*(long pause)*

**Shadow:** Your mother deserved better than the man he was.

**Relm:** Maybe.

**Relm:** But that wasn't what I asked.

*(Shadow removes a ring.)*

**Shadow:** She wore this.

**Relm:** ...

**Shadow:** Keep it safe.

**Relm:** You could do that yourself.

**Shadow:** No.

**Relm:** Coward.

**Shadow:** ...Yeah.

*(Interceptor walks to Relm and sits.)*

## Boss — Guiltshade
- Level 40
- HP 44,000 phase 1 / 26,000 phase 2
- MP 20,000
- Phase 1 appears as shifting masked silhouette.
- Phase 2 changes palette/form after scripted “Baram” illusion breaks.
- Weak: Holy in phase 2 only
- Immune: instant death, Stop, Confuse
- AI emphasizes Image, Vanish, Throw-like attacks, Doom countdown and counterattacks
- If Shadow is in active party, unique battle event cancels one fatal attack once: Interceptor blocks it.
- Reward: **Memento Ring II** / named **Keepsake Ring**

### Keepsake Ring — Relic, Shadow/Relm
- Prevents Doom, Zombie and instant death
- Magic +3
- Speed +3
- Does not replace original Memento Ring narratively; it is the mother's paired ring.

---

# 8. MAJOR ARC 5 — EDGAR & SABIN: TWO SONS OF FIGARO

## Purpose
Resolve the brothers' different ideas of duty and rebuild Figaro's infrastructure.

## Unlock
- Edgar and Sabin recruited.
- Visit Figaro Castle with both.

## New maps
1. **Figaro Foundry**
2. **Collapsed Sand Intake**
3. **Royal Archive**
4. **Duncan's High Path**

## Quest flow
1. Figaro Castle's subterranean drive system is failing due to post-cataclysm sand pressure.
2. Edgar hides the severity from civilians.
3. Sabin accuses him of carrying everything alone, just like after their father's death.
4. Party enters the Sand Intake and destroys a giant machine-beast nest.
5. Boss: **Brass Colossus**.
6. Royal Archive contains the real two-headed coin their father gave Edgar as a joke gift years before the succession.
7. Sabin realizes Edgar had planned the coin toss to free him.
8. Edgar admits he wanted Sabin to choose freely because he could not.
9. Optional second stage: Duncan requests Sabin prove he has learned when *not* to strike.
10. Boss/trial: **Master's Echo**.

## Coin scene

**Sabin:** You still have it?

**Edgar:** Of course.

**Sabin:** Two heads.

**Edgar:** Very observant.

**Sabin:** You cheated.

**Edgar:** I was king. It was practically a job requirement.

**Sabin:** Edgar.

**Edgar:** ...I knew what you'd choose if I gave you the chance.

**Sabin:** You gave up yours.

**Edgar:** Someone had to stay.

**Sabin:** You could've told me.

**Edgar:** And you would've stayed.

*(pause)*

**Sabin:** Yeah.

**Edgar:** Exactly.

## Boss — Brass Colossus
- Level 37
- HP 52,000
- MP 4,000
- Speed 30
- Battle Power 42
- Defense 190
- Magic Defense 125
- Weak: Water, Lightning
- Absorb: Fire
- Mechanics:
  - Alternates **Siege Mode** (high Def) and **Vent Mode** (low Def, powerful fire attacks)
  - Drill/Chainsaw bypass normal defenses but trigger Counterweight counter once per cycle
  - Sabin Blitz attacks build hidden stagger; after 3 Blitzes it loses a turn
- Reward: **Royal Gear** armor

## Trial boss — Master's Echo
- Level scales to Sabin's level +2, capped 50
- HP 36,000
- No EXP
- Uses Blitz-like attacks
- Cannot be defeated efficiently by brute force; final 25% phase counters repeated command types
- Teaches upgraded **Phantom Rush** animation only; no damage increase required unless engine allows safe custom skill slot.

### Royal Gear — Body armor, Edgar/Sabin
- Def 84
- MDef 60
- Vigor +4
- Speed +2
- Stamina +3
- Nullifies Fire
- Positioned below Snow Scarf defensively but excellent for the Figaro brothers.

---

# 9. MAJOR ARC 6 — SETZER: THE LAST RACE

## Purpose
Give Darill an identity and let Setzer choose life rather than merely survive it.

## Unlock
- Setzer recruited.
- Darill's Tomb completed.
- WOB Darill's Token flag optional; if missed, token can be found in Falcon cabin.

## New maps
1. **Sky Graveyard** — floating debris accessible by Falcon
2. **Wreck of the Vagrant Queen**
3. **Race Beacon Tower**

## Quest flow
1. Falcon receives an old mechanical beacon signal.
2. Setzer recognizes it as Darill's private racing frequency.
3. The party finds pieces of a second airship from Darill's last race.
4. Flashback sequences let the player briefly control Setzer walking aboard Blackjack, not piloting action gameplay.
5. The wreck reveals Darill intentionally diverted to save a civilian transport during a storm.
6. A predatory sky monster has nested around the beacon.
7. Boss: **Sky Reaver**.
8. Setzer repairs the beacon and turns it into a navigation light for survivors.

## Key dialogue

**Celes:** You thought she crashed because she pushed too hard.

**Setzer:** Darill always pushed too hard.

**Celes:** That's not what happened.

**Setzer:** No.

**Celes:** Does that help?

**Setzer:** ...Ask me when it stops hurting.

**Celes:** It may not.

**Setzer:** Then I guess I'll keep flying anyway.

## Boss — Sky Reaver
- Level 39
- HP 54,500
- MP 7,500
- Speed 52
- Battle Power 38
- Defense 150
- Magic Defense 155
- Weak: Ice
- Absorb: Wind
- Starts Float
- Uses Aero, Wing Sabre, Cyclonic, Dive
- Every 5th action targets Falcon systems: party gets a battle message; failure to deal 8,000 damage within two turns causes permanent Haste on boss for rest of battle
- Reward: **Darill's Coin**

### Darill's Coin — Relic, Setzer only
- Speed +5
- M.Evade +20%
- Slots “bad result” probability reduced *(ASM extension)*
- Fallback without ASM: Speed +5, Magic +2, M.Evade +20%

---

# 10. MAJOR ARC 7 — WAR OF THE MAGI: THE FORGOTTEN AGE

## Purpose
Explore ancient history without over-explaining the Warring Triad.

## Unlock
Complete any four Hope Flags and obtain:
- Alexander
- Odin or Raiden
- Valigarmanda

Three ancient seals appear on the world map.

## Dungeon 1 — Sanctuary of Concord
Theme: a place where humans and Espers once cooperated.

### New mobs
- Pact Keeper
- Aether Wolf
- Crystal Wisp
- Fallen Evoker

### Boss — Concord Sentinel
- Lv 41
- HP 45,000
- Alternates physical and magical immunity every two turns
- Reward: **Concord Sigil**

## Dungeon 2 — Field of Cinders
Theme: preserved battlefield from the War of the Magi.

### New mobs
- Ash Knight
- War Chimera
- Cinder Wraith
- Magebreaker

### Boss — Empyreal Chimera
- Lv 43
- HP 58,000
- Three heads: Fire/Ice/Lightning; killing a head changes formation and AI
- Reward: **Cinder Sigil**

## Dungeon 3 — Shrine of the Silent Three
Theme: humans who worshiped the Warring Triad before understanding what the gods' conflict would do.

### New mobs
- Stone Cantor
- Triune Eye
- Oathbound
- Null Priest

### Boss — Triune Sentinel
- Three-target formation
- Body A HP 24,000; Body B 24,000; Body C 24,000
- Their affinities rotate when one dies.
- Killing all three within one cycle prevents revival.
- Reward: **Triune Sigil**

## Lore conclusion
The three sigils open a hidden chamber containing journals of **Vael**, one of the earliest human Magi. The texts do not say the Warring Triad were created by humans; they describe the gods as already existing powers whose conflict human factions exploited.

Vael attempted to end the war by sealing magic itself, but the spell failed because magic was bound to living Espers.

His final chamber remains closed until eight Hope Flags are set.

---

# 11. MAJOR ARC 8 — THE FIRST MAGI

## Purpose
Create an endgame superboss whose ideology mirrors Kefka without simply repeating him.

## Premise
Vael survived as a magical imprint sealed into a crystal engine. When the statues were moved and the world broke, the seal awakened. He observes the new world and concludes that as long as mortals possess magic, the War of the Magi will repeat.

Unlike Kefka, Vael does not believe life is meaningless. He believes magic must die so life can continue.

This creates a moral conflict: Vael's conclusion resembles what will naturally happen after Kefka dies, but his method requires destroying every remaining Magicite now, including those sustaining lives and protecting settlements.

## Unlock
- All eight Hope Flags
- Eight Dragons defeated
- Deathgaze defeated
- Before final Kefka battle

## New map
**Cradle of Silence** — four-floor endgame dungeon beneath an ancient fault line.

## Final dialogue

**Vael:** I watched one war consume the world.

**Terra:** So did we.

**Vael:** And still you carry its embers.

**Celes:** We carry weapons. That isn't the same as wanting war.

**Vael:** Every age says that before the first fire.

**Edgar:** Then teach the next age better.

**Vael:** I tried.

**Terra:** No. You tried to choose for them.

**Vael:** And you would gamble the world on hope?

**Terra:** Yes.

**Vael:** Why?

**Terra:** Because that's what a future is.

## Superboss — Vael, First Magi

### Phase 1 — Vael
- Lv 52
- HP 62,000
- MP 30,000
- Speed 48
- Battle Power 42
- Defense 170
- Magic Defense 170
- Magic Power 16
- No elemental weakness
- AI: Flare, Holy, Quake, Stop, Dispel, physical staff attack
- Every third magic cast creates **Arcane Debt**: next spell of same element/type used by party is countered.

### Phase 2 — Seal Engine
Formation swap after scripted scene.
- Core HP 48,000
- Left Seal HP 22,000
- Right Seal HP 22,000
- Core invulnerable while both seals live.
- Left Seal suppresses physical commands intermittently.
- Right Seal suppresses magic commands intermittently.
- Destroying one strengthens the other.

### Phase 3 — Vael Unbound
- HP 65,000
- Speed 58
- Defense 145
- Magic Defense 150
- Magic Power 20
- Opens with **Silence of Ages**: removes buffs and drains 25% current MP from party.
- At 75%: elemental cycle begins.
- At 50%: uses dual-action turns.
- At 25%: stops using status attacks and enters pure damage race.
- Final scripted attack **Last Edict** leaves party at critical HP rather than instant kill if at least six Hope Flags are complete; with all eight, surviving reconstructed-world NPC prayers/messages appear as battle text before the party's next turn. This is cosmetic/emotional, not a raw stat buff.

## Reward
### Legacy of the Magi — Relic
- Equip: Terra, Celes, Relm, Strago, Gogo
- Magic +7
- M.Evade +30%
- MP +25%
- Does **not** teach Ultima or invalidate Soul of Thamasa.

### Optional trophy item
**Broken Seal** — key item, no combat effect; adds expanded ending scene.

---

# 12. MINOR RECONSTRUCTION QUESTS

These are short 5–15 minute quests attached to the major arcs.

| Quest | Location | Objective | Permanent world change | Reward |
|---|---|---|---|---|
| Seeds for Tomorrow | Mobliz/Maranda | deliver hardy seeds | Mobliz gains crops | Gaia Tonic x3 |
| The Empty Forge | Narshe | find surviving smith | weapon shop reopens | Tempered Edge |
| A Road Through Sand | Figaro | clear burrowers | merchant route returns | discount flag |
| Letters Home | Doma | deliver three survivor letters | new NPC families | Hero Ring |
| The Bell of Thamasa | Thamasa | repair warning bell | new children/NPC scene | Ether Bundle |
| Light on the Coast | Nikeah | relight beacon | new ferry flavor NPC | Gale Pin |
| The Last Classroom | Mobliz | recover books from ruined house | school room appears | Growth Egg fragment / alternative reward |
| Graves Without Names | Vector ruins | identify soldiers/civilians | memorial appears | Memorial Band |

---

# 13. NEW NORMAL ENEMY ROSTER

Values are target design numbers for SNES balancing and should be playtested against actual damage formulas.

| Enemy | Lv | HP | MP | BP | Def | MDef | Mag | Spd | Weak | Absorb/Null | EXP | GP | Notable behavior |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---|
| Rust Hound | 30 | 2800 | 200 | 29 | 125 | 105 | 8 | 44 | Ice | Poison null | 1300 | 700 | Pack Howl = Haste allies |
| Annex Guard | 31 | 3400 | 350 | 31 | 140 | 120 | 8 | 38 | Lightning | — | 1450 | 900 | Magitek Laser |
| Suppressor Bit | 33 | 2200 | 1200 | 20 | 155 | 150 | 11 | 50 | Water | Lightning null | 1200 | 500 | Reflect support |
| Failed Infused | 34 | 5200 | 1800 | 34 | 135 | 135 | 12 | 36 | Holy | Poison absorb | 1900 | 900 | random elemental spells |
| Mire Leech | 30 | 2600 | 500 | 26 | 110 | 125 | 9 | 33 | Fire | Poison absorb | 1100 | 600 | Drain/Osmose |
| Depot Slime | 32 | 4100 | 900 | 22 | 90 | 160 | 12 | 28 | Holy | Ice absorb | 1500 | 800 | split at low HP |
| Tek Scavenger | 33 | 4700 | 600 | 35 | 145 | 120 | 9 | 42 | Lightning | — | 1650 | 1000 | steals item then flees |
| Tainted Retainer | 35 | 5200 | 900 | 36 | 155 | 125 | 10 | 36 | Fire | Poison absorb | 1800 | 1100 | counter physical |
| Plague Crow | 34 | 3600 | 650 | 28 | 120 | 130 | 11 | 53 | Ice | Poison null | 1500 | 850 | Sap + Blind |
| Doma Revenant | 36 | 6500 | 1000 | 39 | 165 | 130 | 10 | 32 | Holy | Poison absorb | 2200 | 1200 | undead |
| Smuggler Shade | 36 | 4800 | 1500 | 35 | 130 | 145 | 13 | 49 | Holy | Dark-themed status resist | 1950 | 1200 | Vanish/Image |
| Ash Spider | 35 | 4400 | 400 | 31 | 120 | 115 | 8 | 46 | Ice | Fire absorb | 1700 | 900 | Stop web |
| Masked Memory | 38 | 6900 | 2200 | 36 | 145 | 150 | 14 | 45 | Holy | — | 2450 | 1400 | copies last spell |
| Sand Maw | 34 | 6100 | 300 | 42 | 175 | 105 | 7 | 29 | Water | Earth absorb | 2050 | 1500 | Swallow-style temporary remove |
| Gear Wasp | 35 | 3900 | 700 | 32 | 130 | 135 | 10 | 58 | Lightning | — | 1750 | 1100 | fast status needles |
| Foundry Golem | 37 | 8200 | 800 | 44 | 185 | 115 | 8 | 25 | Water | Fire absorb | 2600 | 1600 | heavy physical |
| Sky Manta | 36 | 5600 | 900 | 36 | 125 | 145 | 12 | 55 | Ice | Wind absorb | 2200 | 1400 | Aero |
| Beacon Wisp | 38 | 4200 | 2600 | 20 | 110 | 175 | 15 | 48 | Holy | Lightning null | 2050 | 1300 | magic-heavy |
| Wreck Raider | 38 | 7200 | 300 | 43 | 150 | 120 | 8 | 47 | Poison | — | 2500 | 1800 | strong steal/drop table |
| Pact Keeper | 40 | 7600 | 3500 | 40 | 160 | 165 | 15 | 42 | none | Holy null | 3000 | 1800 | swaps Protect/Shell |
| Aether Wolf | 40 | 6800 | 1600 | 45 | 145 | 135 | 12 | 58 | Ice | — | 2850 | 1700 | pounces low HP |
| Crystal Wisp | 41 | 5100 | 5000 | 18 | 100 | 190 | 17 | 50 | physical | elements resist | 2950 | 1500 | magic counters |
| Fallen Evoker | 41 | 8400 | 4200 | 35 | 145 | 170 | 17 | 39 | Holy | — | 3300 | 1900 | summons minor mobs |
| Ash Knight | 41 | 9000 | 900 | 48 | 180 | 135 | 10 | 38 | Ice | Fire absorb | 3400 | 2200 | Cover allies |
| War Chimera | 42 | 11200 | 3000 | 45 | 165 | 155 | 16 | 43 | variable | Fire/Ice/Lightning resist | 4200 | 2600 | 3-element pattern |
| Cinder Wraith | 42 | 6900 | 3600 | 30 | 120 | 180 | 18 | 52 | Holy | Fire absorb | 3500 | 2100 | undead mage |
| Magebreaker | 43 | 9800 | 1200 | 50 | 175 | 155 | 12 | 45 | Poison | — | 4100 | 2800 | Runic-like absorb |
| Stone Cantor | 42 | 8700 | 3200 | 35 | 175 | 170 | 16 | 32 | Water | Earth absorb | 3600 | 2300 | Quake/Slowga |
| Triune Eye | 43 | 7200 | 4500 | 26 | 135 | 185 | 18 | 49 | none | rotating null | 3800 | 2400 | scans party weakness |
| Oathbound | 44 | 12000 | 1800 | 52 | 185 | 145 | 12 | 40 | Holy | Doom immune | 4700 | 3200 | revenge counter |
| Null Priest | 44 | 7600 | 6200 | 24 | 140 | 190 | 19 | 41 | physical | many magic resists | 4400 | 2800 | Dispel/Osmose |
| Seal Hound | 46 | 10800 | 1200 | 52 | 175 | 150 | 13 | 58 | Ice | — | 5200 | 3300 | Haste + bite |
| Arcane Husk | 47 | 13500 | 5800 | 44 | 175 | 185 | 20 | 42 | Holy | status immune | 6200 | 3900 | Flare/Gravity |
| Silence Knight | 48 | 15000 | 2400 | 58 | 195 | 165 | 14 | 44 | Lightning | — | 7000 | 4500 | Silence + physical |
| Seal Seraph | 49 | 17200 | 9000 | 42 | 170 | 195 | 22 | 51 | none | Holy absorb | 8200 | 5000 | endgame elite caster |

---

# 14. NEW BOSS TABLE

| Boss | Arc | Lv | HP structure | Key mechanic | Main reward |
|---|---|---:|---:|---|---|
| Magitek Praetor | Celes | 36 | 47,800 | barrier/bit phases | Runic Crest |
| Magi-Eater | Terra | 34 | 39,600 | rotating absorption | Maduin's Locket |
| Miasma Regent | Cyan | 38 | 49,200 | poison aura/summons | Doma Crest |
| Guiltshade | Shadow/Relm | 40 | 44k + 26k | illusion phase | Keepsake Ring |
| Brass Colossus | Figaro | 37 | 52,000 | siege/vent | Royal Gear |
| Master's Echo | Sabin trial | scale | 36,000 | repeated-command counters | prestige/animation |
| Sky Reaver | Setzer | 39 | 54,500 | damage check/beacon attack | Darill's Coin |
| Concord Sentinel | Magi | 41 | 45,000 | immunity swap | Concord Sigil |
| Empyreal Chimera | Magi | 43 | 58,000 | removable heads | Cinder Sigil |
| Triune Sentinel | Magi | 44 | 24k x3 | synchronized kill | Triune Sigil |
| Archive Guardian | Magi | 45 | 61,000 | spell-memory counter | Magister Robe |
| Vael Phase 1 | Endgame | 52 | 62,000 | Arcane Debt | — |
| Seal Engine | Endgame | 53 | 48k + 22k + 22k | command suppression | — |
| Vael Unbound | Endgame | 55 | 65,000 | 3-stage escalation | Legacy of the Magi |

---

# 15. NEW WEAPONS

All values are intentionally below or sideways to the strongest canonical endgame options.

| Weapon | User | Atk | Extra stats/effect | Source |
|---|---|---:|---|---|
| Tempered Edge | Terra/Celes/Edgar/Locke | 188 | Vigor +2, Eva +10 | Narshe forge quest |
| Imperial Saber | Celes | 205 | Mag +3, M.Eva +20 | Vector Annex chest |
| Leo's Blade | Terra/Celes/Edgar/Locke | 218 | Vig +3, Sta +3, Holy element | rare Celes arc reward branch |
| Raider Knife | Locke | 198 | Spd +5, steal-on-hit property | reconstruction chain |
| Sandpiercer | Edgar/Mog | 210 | Wind element, Spd +2 | Figaro Foundry |
| Duncan Claw | Sabin | 214 | Vig +5, Sta +3 | Master's Echo |
| Moonless | Shadow | 216 | Spd +7, Eva +30 | Bandit's Hollow |
| Doma Edge | Cyan | 222 | Vig +5, Sta +4 | Doma rebuilt smith |
| Darill's Dirk | Setzer/Locke | 202 | Spd +4, Eva +20 | Sky Graveyard |
| Magister Rod | Strago/Relm | 190 | Mag +7, M.Eva +20 | Forgotten Age |
| Concord Brush | Relm | 184 | Mag +7, Spd +3 | Sanctuary of Concord |
| Gale Lance | Mog/Edgar | 218 | Wind element, Spd +4 | beacon quest |
| Echo Dagger | Gogo | 200 | Vig +3, Mag +3, Spd +3 | Cradle of Silence |

---

# 16. NEW ARMOR / HELMETS / SHIELDS

| Equipment | Slot | Users | Def | MDef | Extra |
|---|---|---|---:|---:|---|
| Royal Gear | Body | Edgar/Sabin | 84 | 60 | Vig +4, Spd +2, Sta +3, Fire null |
| Imperial Mantle | Body | Celes/Terra | 78 | 72 | Mag +4, M.Eva +20 |
| Magister Robe | Body | Terra/Celes/Relm/Strago/Gogo | 70 | 82 | Mag +6, MP-oriented sidegrade |
| Ashen Mail | Body | Edgar/Cyan/Setzer | 88 | 52 | Fire absorb, Ice weak |
| Concord Vest | Body | Locke/Shadow/Gau/Mog/Gogo | 76 | 62 | Spd +4, Eva +20 |
| Doma Plate | Body | Cyan/Edgar/Celes/Terra | 92 | 58 | Sta +5 |
| Falcon Jacket | Body | Setzer/Locke/Shadow | 74 | 60 | Spd +5, Wind resist |
| Child's Ribbon | Head | Terra/Relm/Celes | 34 | 38 | Mag +3, Sta +3, status resist subset |
| Doma Kabuto | Head | Cyan | 42 | 32 | Vig +4, Sta +4 |
| Engineer Goggles | Head | Edgar/Setzer | 36 | 30 | Blind immunity, Spd +2 |
| Magi Circlet | Head | magic users | 36 | 44 | Mag +5, M.Eva +10 |
| Concord Shield | Shield | broad | 54 | 48 | Eva +20, M.Eva +20, Holy resist |
| Ashguard | Shield | heavy users | 58 | 42 | Fire absorb, Ice weakness |

---

# 17. NEW RELICS

| Relic | User | Effect |
|---|---|---|
| Runic Crest | Celes | Mag +5, M.Eva +20; enhanced Runic with ASM |
| Maduin's Locket | Terra | Mag +6, Sta +3; longer Trance with ASM |
| Doma Crest | Cyan | Vig +5, Sta +5, Spd +2; faster Bushido with ASM |
| Keepsake Ring | Shadow/Relm | blocks Doom/Zombie/instant death; Mag +3, Spd +3 |
| Darill's Coin | Setzer | Spd +5, M.Eva +20; improved Slots table with ASM |
| Memorial Band | all | Sta +4, protects from Berserk/Confuse |
| Gale Pin | all | Spd +3, Wind resistance |
| Beastheart | Gau | Vig +4, Sta +4; Rage enhancement reserved for ASM phase |
| Painter's Lens | Relm | Mag +5, Sketch accuracy increase |
| Elder's Seal | Strago | Mag +5, MP +12.5%, Silence immunity |
| Engineer's Badge | Edgar | Vig +3, Spd +3; Tools +10% damage with ASM |
| Master's Cord | Sabin | Vig +5, Sta +5; Blitz +10% damage with ASM |
| Legacy of the Magi | Terra/Celes/Relm/Strago/Gogo | Mag +7, M.Eva +30, MP +25% |

**Balance rule:** character-specific relic bonuses that require assembly work are optional enhancement patches. Every quest must still function with a data-only fallback effect.

---

# 18. NEW CONSUMABLES / KEY ITEMS

| Item | Type | Effect |
|---|---|---|
| Gaia Tonic | consumable | heals 1,500 HP + Regen one ally |
| Aether Flask | consumable | restores 100 MP |
| Phoenix Ash | rare consumable | revives one ally at 50% HP |
| Null Dust | battle item | Dispel one target |
| Iron Ration | field/battle | heals 600 HP, cheap reconstruction-shop item |
| Remedy+ | rare | cures normal status + Zombie |
| Beacon Flare | battle | Fire damage to all + reveals invisible enemies |
| Magitek Cell | battle | Lightning non-elemental hybrid damage; limited quantity |
| Darill's Token | key | unlocks Last Race |
| Concord Sigil | key | First Magi gate |
| Cinder Sigil | key | First Magi gate |
| Triune Sigil | key | First Magi gate |
| Broken Seal | key | expanded ending condition |

---

# 19. SHOP / ECONOMY CHANGES

The mod should not shower the player with top-tier gear. Reconstructed settlements unlock practical shops rather than ultimate equipment.

## Rebuilt Mobliz
- Iron Ration
- Remedy
- Phoenix Down
- Gaia Tonic
- Gaia Gear

## Rebuilt Doma
- Ashigaru-style existing gear
- Doma Edge only after quest and at very high price if a second copy is allowed
- consumable scrolls

## Reopened Narshe Forge
- Tempered Edge
- elemental blades from base game
- shields

## Figaro Foundry
- Tools remain canonical
- sells limited Magitek Cell after Celes arc

**Gil sink target:** 150,000–250,000 gil across all reconstruction purchases, optional. This gives late-game gil a purpose without making farming mandatory.

---

# 20. WORLD STATE CHANGES

## Mobliz
Before: ruined, fearful, children indoors.
After: repaired roofs, crops, school corner, active well, one new shop.

## Doma
Before: silent tomb.
After: eastern courtyard occupied, lamps lit, two survivor families, memorial room preserved untouched.

## Narshe
Before: abandoned.
After forge quest: small survivor group returns to lower district; upper frozen cliffs remain dangerous.

## Figaro
Foundry NPCs and engineers move into previously empty rooms; dialogue changes after the brothers' quest.

## Vector Ruins
A memorial marker appears if records preserved; a burned-out archive appears if destroyed.

## Thamasa
Shadow/Relm quest adds one permanent scene trigger in Relm's house and new Interceptor idle position.

## Falcon
After Setzer arc, a small beacon indicator/object appears in cabin; Setzer gets new idle dialogue.

---

# 21. NPC DIALOGUE STATE EXAMPLES

## Mobliz child
### Before Terra expansion
“Are the monsters coming back?”

### During
“Terra says the water's bad. Water can be bad?”

### After
“I planted this one! Don't step on it!”

## Doma survivor
### Before
“There is nothing here but ghosts.”

### After
“The ghosts can stay. So can we.”

## Figaro engineer
### Before
“His Majesty says the engine is fine. His face says otherwise.”

### After
“The castle can cross the desert again. His Majesty can stop pretending he wasn't worried.”

## Former Imperial soldier
### Before Celes quest
“Don't look at the uniform. I don't wear it anymore.”

### After preserve-records choice
“Put my name in the book too. I followed orders. That's still something I did.”

### After burn-records choice
“No records left? Maybe that's mercy. Maybe it's cowardice.”

---

# 22. EXPANDED ENDING

The canonical ending structure remains intact. Added vignettes are inserted before/among the existing character epilogues depending on flags.

## Empire Hope Flag
- Preserve: Figaro archivists seal Imperial records; Celes watches, then leaves without speaking.
- Burn: wind blows ash over Vector ruins; Celes places Leo's insignia at a stone marker.

## Mobliz Hope Flag
Children run through a field of new crops. Terra's old room is now a classroom.

## Doma Hope Flag
The castle gate opens. Civilians carry lumber through it. Cyan bows once toward the memorial hall and joins them.

## Shadow/Relm Hope Flag
Relm paints at a window. Interceptor lies beside her. A masked figure is visible briefly on a distant ridge, then gone.

## Figaro Hope Flag
Figaro Castle emerges from the sand near a new caravan road. Edgar speaks to engineers while Sabin helps lift a beam.

## Setzer Hope Flag
A small airship follows the Falcon's repaired beacon route at night.

## Forgotten Age Flag
The three sigils, now powerless stones, are placed in a museum-like chamber rather than worshiped.

## Broken Seal Flag
Terra watches the last magical glow leave the stone. She smiles instead of mourning it.

**Final principle:** the world is not restored to the World of Balance. It becomes something new.

---

# 23. EVENT FLAG PLAN

Exact SRAM bit assignment must be chosen only after auditing free event bits in the target ROM.

Logical flags:

- EXP_WOB_RESEARCH_ANNEX
- EXP_WOB_THAMASA_SHRINE
- EXP_WOB_DARILL_TOKEN
- EXP_CELES_STARTED
- EXP_CELES_DONE
- EXP_CELES_RECORDS_PRESERVED
- EXP_TERRA_STARTED
- EXP_TERRA_WELL_FIXED
- EXP_TERRA_CARPENTER
- EXP_TERRA_FARMER
- EXP_TERRA_TEACHER
- EXP_TERRA_DONE
- EXP_CYAN_STARTED
- EXP_CYAN_DONE
- EXP_SHADOW_RELM_STARTED
- EXP_SHADOW_RELM_DONE
- EXP_FIGARO_STARTED
- EXP_FIGARO_DONE
- EXP_SETZER_STARTED
- EXP_SETZER_DONE
- EXP_MAGI_SANCTUARY_DONE
- EXP_MAGI_CINDERS_DONE
- EXP_MAGI_TRIUNE_DONE
- EXP_FIRST_MAGI_UNLOCK
- EXP_FIRST_MAGI_DONE
- EXP_HOPE_01 through EXP_HOPE_08 or equivalent packed bitset

No flag addresses are assigned in this document because that must follow ROM/SRAM conflict audit.

---

# 24. MAP BUDGET

## Fully new maps
1. Vector Ruins Outer Ward
2. Research Annex B2
3. Infusion Theater
4. Records Vault
5. Collapsed Shelter
6. Buried Magitek Depot
7. Doma Aqueduct
8. Eastern Refugee Camp
9. Burned Cottage
10. Bandit's Hollow
11. Cliff of Ash
12. Figaro Foundry
13. Sand Intake
14. Royal Archive
15. Duncan's High Path
16. Sky Graveyard
17. Vagrant Queen Wreck
18. Race Beacon Tower
19. Sanctuary of Concord A
20. Sanctuary of Concord B
21. Field of Cinders A
22. Field of Cinders B
23. Shrine of Silent Three A
24. Shrine of Silent Three B
25. Cradle of Silence 1
26. Cradle of Silence 2
27. Cradle of Silence 3
28. Cradle of Silence Core

## Modified/reused maps
- Mobliz x2 reconstruction states
- Doma x2 states
- Narshe lower town state
- Figaro NPC state
- Thamasa house state
- Falcon cabin state
- Vector ruin landing area

Design target: reuse tilesets aggressively; create new tiles only for signature areas to control ROM/VRAM complexity.

---

# 25. NEW GRAPHICS ASSET LIST

## Boss sprites
1. Magitek Praetor — large armored humanoid/machine hybrid
2. Magi-Eater — organic magical core with cables/tendrils
3. Miasma Regent — decayed crowned sludge/samurai mass
4. Guiltshade — masked shadow with second-phase broken mask
5. Brass Colossus — Figaro industrial golem
6. Master's Echo — martial spirit silhouette
7. Sky Reaver — manta/dragon aerial predator
8. Concord Sentinel — ancient human/Esper guardian construct
9. Empyreal Chimera — 3-headed ancient war beast
10. Triune Sentinel — 3 coordinated statues
11. Archive Guardian — floating mage armor
12. Vael — human mage
13. Seal Engine — multi-part crystal machinery
14. Vael Unbound — same man distorted by accumulated magic, not a godlike angel copy of Kefka

## Normal mobs
35 entries listed above; at least half may be palette/part remixes of existing FFVI graphical language, but signature enemies should receive new art.

## Map objects
- reconstruction scaffolding
- crop tiles
- memorial stones
- Magitek tanks
- ancient sigil doors
- airship wreckage
- beacon machinery

---

# 26. MUSIC PLAN

v1.0 should reuse/recontextualize existing tracks unless a custom music engine is deliberately added later.

Suggested reuse:
- Celes Annex: “The Empire Gestahl” / darker ambient track
- Mobliz reconstruction: “Kids Run Through the City” or “Awakening” depending scene
- Doma: “Cyan's Theme” sparingly
- Shadow/Relm: “Shadow's Theme” only at final scene, not throughout dungeon
- Setzer: “Setzer's Theme” / “Epitaph”
- Ancient Magi dungeons: “The Ancient Castle” tone where appropriate
- Vael: custom track desirable only in Phase 2+ production pass

No music should undermine the existing leitmotif hierarchy.

---

# 27. WRITING RULES PER CHARACTER

## Terra
Quiet, literal, emotionally sincere. She does not suddenly become philosophical or eloquent.

## Celes
Controlled, concise, often defensive. Emotion leaks through what she refuses to say.

## Locke
Uses levity to avoid pain; becomes serious quickly when someone else's guilt resembles his own.

## Edgar
Polished humor, political intelligence, hides burdens. Flirtation should be used less in serious reconstruction scenes.

## Sabin
Direct, warm, emotionally perceptive despite seeming simple. Never write him as stupid.

## Cyan
Formal register, but readable. Use archaic flavor selectively rather than every sentence becoming parody.

## Shadow
Minimal words. Never explains himself when silence can work.

## Relm
Blunt, observant, fearless. Childlike does not mean naive.

## Strago
Experienced, occasionally comic, but becomes grave around War of the Magi history.

## Gau
Short grammar and unusual phrasing, but emotional clarity must remain understandable.

## Setzer
Fatalistic humor, risk language, cards/racing metaphors in moderation.

## Mog
Bright but not mascot-only; can be practical and brave.

## Gogo
Almost no added lore. Mystery is the point.

## Umaro
No expanded verbal dialogue beyond reactions.

## Kefka
No new sympathetic childhood scenes. New records describe procedures, not an excuse or secret tragic hero narrative.

---

# 28. CONTENT THAT MUST NOT BE ADDED

- Leo resurrection
- Rachel permanent resurrection
- Darill surviving secretly
- Baram surviving secretly
- Shadow openly joining Relm as domestic father in the ending
- Kefka redemption
- “true villain behind Kefka”
- retcon that humans created the Warring Triad
- alternate ending where magic remains because the player did enough quests
- a fifteenth permanent hero who steals focus from the cast
- level-99-only mandatory bosses
- equipment clearly stronger than Lightbringer + Paladin Shield in every dimension

---

# 29. TECHNICAL IMPLEMENTATION NOTES — SNES

1. Monster records contain Speed, Battle Power, Hit Rate, Evasion, M.Block, Defense, Magic Defense, Magic Power, two-byte HP, two-byte MP, EXP, GP, level, status/element fields and special data. New monster design can therefore be represented largely within the native data model.
2. Native monster table contains 384 entries. A slot audit is mandatory before deciding whether to reclaim unused/dummy monsters or relocate/expand data.
3. FF6Tools can edit maps, triggers, events, battles, monster AI, dialogue, characters, skills, espers and shops and can relocate/expand data when required.
4. Any relocation must be treated as a baseline-changing operation because it can reduce compatibility with older utilities/patches.
5. Character-specific relic behavior such as faster Bushido, longer Trance or Tools bonuses should be modular ASM patches. Story content must not depend on these extensions.
6. Multi-phase superbosses should use battle events/formation swaps rather than HP overflow hacks.
7. All new dialogue must later receive a dedicated text-budget/relocation pass. The script in this bible is narrative master copy, not final compressed ROM text.

---

# 30. PRODUCTION ORDER

## Milestone 0 — Baseline audit
- choose exact ROM revision
- checksum
- list existing patches
- free space map
- event bit audit
- monster/item slot audit
- map slot audit

## Milestone 1 — Vertical slice
Implement **Celes: Echoes of the Empire** only.
Required:
- 4 maps
- 4 normal mobs
- Magitek Praetor
- Runic Crest fallback version
- complete events/dialogue
- save/load regression
- Kefka Tower progression regression

If this runs safely, it becomes the technical template for every other arc.

## Milestone 2 — Reconstruction trio
- Terra
- Cyan
- Figaro
- world-state map swapping

## Milestone 3 — Character closure
- Shadow/Relm
- Setzer
- minor quests

## Milestone 4 — Ancient Magi
- three dungeons
- three sigils
- lore records

## Milestone 5 — First Magi
- Cradle of Silence
- multi-phase superboss
- ending flags

## Milestone 6 — balance/QA
- low-level party tests
- average casual party tests
- optimized Ultima/Genji/Offering tests
- status exploit tests
- Vanish/Doom behavior audit depending selected bug-fix baseline
- Rage/Sketch/Control interactions
- save compatibility

---

# 31. DEFINITION OF “CONTENT COMPLETE”

The expansion is content-complete when:

- 8 major arcs are playable start-to-finish.
- 8 Hope Flags alter the world and ending.
- 28 new map instances are implemented or equivalently consolidated.
- ~35 new normal enemy designs exist.
- 14 new boss encounters exist including Vael's phases.
- 13+ new weapons, 13+ armor pieces and 13+ relics are implemented or intentionally cut after balance review.
- Every new NPC has before/during/after dialogue states where relevant.
- No original recruitment, Eight Dragons, Deathgaze, Ancient Castle, Phoenix Cave, Fanatics' Tower, Cyan's Dream, Gogo/Umaro or Kefka's Tower event is broken.
- Original ending remains valid without new quests.
- Expanded ending reacts only to completed optional content.
- No added scene contradicts canonical deaths or the disappearance of magic.

---

# 32. FINAL NARRATIVE STATEMENT

The original Final Fantasy VI asks whether life retains meaning after everything is destroyed.

**Expanded Edition adds the next question:**

> If the answer is yes, what do you build afterward?

Kefka can destroy cities, governments, families and even the shape of the world. The expansion should never undo that loss. Instead, every optional arc lets the player create one small piece of a future: a clean well, an open gate, a repaired engine, a remembered crime, a child in a classroom, a light in the sky.

That is why the final reward is not a stronger version of the old world.

It is evidence that people chose to live in the new one.

---

# APPENDIX A — REFERENCE BASELINE NOTES

For balance calibration, canonical SNES/FFVI data places high-end weapons around the 200–255 Attack range, while late optional bosses such as Storm Dragon and Deathgaze operate around 42,500 and 55,555 HP respectively. Native monster HP is stored in two bytes, reinforcing the design choice to use multi-phase battles rather than single enormous HP pools.

Technical references used when drafting this bible:
- StrategyWiki — Final Fantasy VI weapons, armor, enemies, relics, espers and sidequests.
- Data Crystal — FFVI Monster Data Format and ROM/RAM documentation.
- FF6Tools documentation — map/event/battle/monster/dialogue editing and relocation/expansion capabilities.

