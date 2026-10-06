# FINAL FANTASY VI — EXPANDED EDITION
## Scenario Script v1.0

This document is the **narrative master script** for all newly added story content in the v1.0 expansion design. It is intentionally written before ROM compression. Final line breaks, control codes, speaker tokens and text-bank allocation must be decided during implementation.

Conventions:
- `[EVENT]` = map/event action.
- `[CHOICE]` = player choice.
- `[IF X]` = conditional dialogue.
- `[NPC STATE]` = persistent NPC line.
- `...` is used sparingly and intentionally.

---

# WOB-A — RESEARCH ANNEX

## Trigger
Optional door in Magitek Research Facility after the party gains access to the upper laboratory section.

### Scene WOB-A01 — Sealed Door

[EVENT: Locke checks door.]

**Locke:** Locked.

**Edgar:** Imperial lock?

**Locke:** Worse. New Imperial lock.

**Sabin:** So... locked?

**Locke:** For about ten seconds.

[EVENT: click.]

**Locke:** Nine.

### Scene WOB-A02 — Observation Room

[EVENT: party enters; tanks visible behind glass.]

**Terra:** What is this place?

**Edgar:** Not part of the main facility.

**Locke:** There's a terminal here.

**Terminal:** MAGITEK INFUSION ANNEX.

**Terminal:** AUTHORIZED PERSONNEL ONLY.

**Sabin:** Little late for that.

### Terminal records

**Record 01:** SUBJECT K-01.

**Record 01:** MAGIC RESPONSE: EXTREME.

**Record 01:** BEHAVIORAL INSTABILITY: PROGRESSIVE.

**Record 01:** FURTHER INFUSION APPROVED.

**Terra:** K...?

**Edgar:** Keep reading.

**Record 02:** SUBJECTS K-02 THROUGH K-06.

**Record 02:** PROCEDURE FAILURE.

**Record 02:** SURVIVAL: ZERO.

**Locke:** ...

**Record 03:** REVISED PROTOCOL AUTHORIZED.

**Record 03:** SUBJECT C-07 SELECTED.

**Record 03:** AGE: MINOR.

**Sabin:** They used a kid?

**Edgar:** The Empire has done worse.

**Terra:** Who was C-07?

[EVENT: no answer; party hears distant alarm.]

**Locke:** We can wonder later. Move!

---

# WOB-B — OLD THAMASA SHRINE

## Trigger
After burning-house rescue, return to Strago's home before leaving for the Esper meeting.

### Scene WOB-B01 — Hidden Stair

**Relm:** Grandpa! You left the cellar open!

**Strago:** I most certainly did not.

**Relm:** Then your floor did.

[EVENT: cracked floor reveals stair.]

**Strago:** ...That seal.

**Terra:** You know it?

**Strago:** I know enough to wish I didn't.

### Scene WOB-B02 — Murals

[EVENT: murals show humans and Espers together.]

**Locke:** I thought the War of the Magi was humans against Espers.

**Strago:** That's the version frightened people teach their children.

**Terra:** Then what happened?

**Strago:** Humans fought humans. Espers fought Espers.

**Strago:** Alliances shifted. Fear grew faster than wisdom.

**Relm:** So everybody was stupid.

**Strago:** ...A concise historical summary.

### Inscription 1

**Inscription:** WE SHARED FIRE.

**Inscription:** THEN WE NAMED IT OURS.

### Inscription 2

**Inscription:** THREE POWERS STOOD ABOVE US.

**Inscription:** MEN KNELT, THEN ARGUED OVER WHERE TO KNEEL.

### Scene WOB-B03 — Exit

**Terra:** Did Espers ever trust humans again?

**Strago:** Some did.

**Terra:** How do you know?

**Strago:** Because you're standing here.

---

# WOB-C — DARILL'S TOKEN

## Trigger
After recruiting Setzer and before Floating Continent, speak to him during a rest stop on Blackjack.

### Scene WOB-C01

**Setzer:** You're going to wear a hole in my deck.

**Celes:** I couldn't sleep.

**Setzer:** Dangerous habit. Gives you time to think.

[EVENT: metallic token falls from Setzer's hand.]

**Celes:** What's that?

**Setzer:** A bad bet.

**Celes:** Looks like a race marker.

**Setzer:** Darill's.

**Celes:** The pilot you mentioned?

**Setzer:** The only one who could make me feel slow.

**Celes:** What happened to her?

**Setzer:** She won.

**Celes:** Won what?

**Setzer:** The right not to answer questions tonight.

[EVENT: Setzer pockets token.]

---

# ARC 1 — CELES: ECHOES OF THE EMPIRE

## Scene C01 — Vector Ruins Landing

[EVENT: Falcon lands among broken Imperial masonry.]

**Locke:** Didn't think there'd be anything left.

**Celes:** There shouldn't be.

**Edgar:** You recognize this district?

**Celes:** Officers' quarter. Research wing to the east.

**Sabin:** Research as in Magitek?

**Celes:** Research as in don't touch anything.

## NPC — Former Imperial Medic Vale

**Vale:** Stop!

**Celes:** ...Vale?

**Vale:** General Celes.

**Celes:** Don't call me that.

**Vale:** Old habit.

**Locke:** Friend of yours?

**Celes:** No.

**Vale:** She's right.

### Scene C02 — Vale's confession

**Vale:** We thought the Annex was buried when the earth split.

**Edgar:** What was in it?

**Vale:** Records. Infusion chambers. Failed subjects.

**Sabin:** You worked there.

**Vale:** I carried instruments. Wrote temperatures. Held people still.

**Celes:** And now?

**Vale:** Now I wake up remembering their names.

**Celes:** Good.

**Locke:** Celes...

**Celes:** He should remember.

## Scene C03 — Annex entrance

**Vale:** I can't go farther.

**Celes:** Can't?

**Vale:** Won't.

**Celes:** Then wait here.

**Vale:** You're not afraid?

**Celes:** Of course I am.

**Celes:** Open the door.

## Scene C04 — Infusion Theater

[EVENT: lights flicker; empty restraint platform.]

**Celes:** I know this room.

**Locke:** You were stationed here?

**Celes:** No.

**Locke:** ...Celes?

**Celes:** I woke up here.

**Edgar:** Then we do this at your pace.

**Celes:** No. We do it once.

## Terminal C-A

**Terminal:** SUBJECT K-01.

**Terminal:** INFUSION RESPONSE: EXTREME.

**Terminal:** COGNITIVE INSTABILITY: PROGRESSIVE.

**Terminal:** EMOTIONAL INHIBITION: FAILED.

**Terminal:** FURTHER INFUSION AUTHORIZED BY IMPERIAL DECREE.

**Sabin:** Kefka.

**Celes:** Probably.

**Locke:** “Probably?”

**Celes:** I won't turn a monster into an excuse because a file has his initial.

## Terminal C-B

**Terminal:** SUBJECT C-07.

**Terminal:** REVISED INFUSION PROTOCOL: SUCCESSFUL.

**Terminal:** MILITARY APTITUDE: EXCEPTIONAL.

**Terminal:** MEMORY RESPONSE: WITHIN ACCEPTABLE RANGE.

**Locke:** C-07...

**Celes:** Keep reading.

**Terminal:** RECOMMEND IMMEDIATE OFFICER-TRACK TRAINING.

**Terminal:** AGE EXCEPTION APPROVED.

**Sabin:** How old were you?

**Celes:** Old enough to remember the ceiling.

## Scene C05 — Leo petitions

**Terminal:** GENERAL LEO CHRISTOPHE: REQUEST TO HALT HUMAN INFUSION DENIED.

**Terminal:** GENERAL LEO CHRISTOPHE: SECOND REQUEST DENIED.

**Terminal:** GENERAL LEO CHRISTOPHE: FORMAL PROTEST ENTERED.

**Celes:** ...He knew.

**Edgar:** And he tried to stop it.

**Celes:** Not soon enough.

**Edgar:** No.

**Edgar:** But he tried.

## Scene C06 — Praetor activation

**System:** BIOMETRIC MATCH.

**System:** CELES CHERE.

**System:** STATUS: DESERTER.

**Celes:** Of course.

**System:** SENTENCE: IMMEDIATE.

**Sabin:** The Empire really loved paperwork.

[BOSS: MAGITEK PRAETOR]

## Scene C07 — After boss

**Locke:** You all right?

**Celes:** No.

**Locke:** ...All right.

**Celes:** That's it?

**Locke:** You said no.

**Celes:** Hm.

## Scene C08 — Records decision

[EVENT: Vale enters Records Vault.]

**Vale:** There are enough names here to bury Vector twice.

**Edgar:** Medical logs. Orders. Signatures.

**Vale:** Burn it.

**Celes:** Why?

**Vale:** So no one can repeat it.

**Celes:** Or prove it happened.

**Vale:** I don't deserve to choose.

**Celes:** No. You don't.

[CHOICE]
- Preserve the records.
- Burn the records.

### Preserve

**Celes:** Figaro will seal them.

**Edgar:** Every page.

**Celes:** Names, orders, failures.

**Vale:** Mine too?

**Celes:** Especially yours.

**Vale:** ...Good.

**Celes:** If the world rebuilds, it rebuilds knowing what we did.

### Burn

**Celes:** Some knowledge has already cost enough lives.

**Edgar:** You're certain?

**Celes:** Keep the names.

**Celes:** Burn the procedure.

**Vale:** And my record?

**Celes:** You don't get to disappear with the notes.

[EVENT: documents burn.]

## NPC STATES — Vector survivors

### Before quest
**Survivor 1:** Nothing grows here. Maybe nothing should.

**Survivor 2:** We were clerks, cooks, mechanics. Not everyone in Vector carried a sword.

### After preserve
**Survivor 1:** Figaro took the records. Strange... seeing soldiers guard paper instead of people.

**Survivor 2:** My brother's name was in there. At least now somebody knows.

### After burn
**Survivor 1:** Smoke again. Vector always ends in smoke.

**Survivor 2:** They kept the list of names. That's enough for me.

---

# ARC 2 — TERRA: CHILDREN OF THE RUINED WORLD

## Scene T01 — Sick child

**Child:** Terra... my stomach hurts.

**Terra:** Again?

**Katarin:** Three more this morning.

**Duane:** It's the water.

**Terra:** The well?

**Duane:** Smells like metal.

**Terra:** Nobody drinks from it until we know why.

**Child 2:** But I'm thirsty.

**Terra:** I know.

**Terra:** We'll fix it.

## Scene T02 — Duane wants to leave

**Duane:** We can move them again.

**Terra:** To where?

**Duane:** Anywhere safer than this.

**Terra:** We keep saying that.

**Katarin:** Terra...

**Terra:** I thought protecting them meant standing between them and monsters.

**Terra:** Maybe it also means giving them somewhere they don't have to run from.

## Scene T03 — Shelter discovery

**Sabin:** This wall's hollow.

**Edgar:** Imperial concrete.

**Terra:** Under Mobliz?

**Edgar:** Supply depot, perhaps. Hidden before the occupation.

**Terra:** Then whatever is poisoning the water may be ours to clean up.

## Scene T04 — Depot terminal

**Terminal:** MAGITEK COOLANT RESERVOIR.

**Terminal:** BIOHAZARD SEAL FAILURE.

**Locke:** There's our well problem.

**Terra:** Can we stop it?

**Edgar:** If the controls still work.

**System:** CONTAINMENT ORGANISM ACTIVE.

**Sabin:** “Containment organism?”

**Edgar:** I preferred “controls.”

[BOSS: MAGI-EATER]

## Scene T05 — Well restored

[EVENT: water runs clear.]

**Child:** Can I drink it now?

**Terra:** Wait.

[EVENT: Terra tastes water.]

**Terra:** Now.

**Child:** You drank first!

**Terra:** That's what grown-ups are for.

**Sabin:** Nobody told me that.

## Scene T06 — Rebuilding plan

**Katarin:** The well's fixed. But the roof over the west house won't last another storm.

**Duane:** And we're almost out of seed.

**Terra:** Then we'll find people who know roofs and seeds.

**Duane:** You mean leave?

**Terra:** For a little while.

**Duane:** The children need you.

**Terra:** They need more than me.

### Recruit: Carpenter in Tzen

**Carpenter:** Mobliz? Thought the place was gone.

**Terra:** It isn't.

**Carpenter:** Got lumber?

**Terra:** Some.

**Carpenter:** Nails?

**Terra:** Fewer.

**Carpenter:** Food?

**Terra:** Enough to share.

**Carpenter:** Hmph. Sounds like a town to me.

### Recruit: Farmer in Maranda

**Farmer:** Soil there turned grey after the light hit.

**Terra:** We have clean water now.

**Farmer:** Water isn't soil.

**Terra:** What would make it soil again?

**Farmer:** Time. Compost. Stubbornness.

**Terra:** We have children.

**Farmer:** ...Plenty of stubbornness, then.

### Recruit: Teacher in Nikeah

**Teacher:** Books?

**Terra:** A few survived.

**Teacher:** Desks?

**Terra:** No.

**Teacher:** Chalk?

**Terra:** I don't know what that is.

**Teacher:** You really do need a teacher.

## Scene T07 — Door scene

**Child:** Miss Terra! Look!

**Terra:** A door?

**Child:** Our door.

**Terra:** ...It's beautiful.

**Carpenter:** It's crooked.

**Terra:** It's still beautiful.

## Scene T08 — Terra conclusion

**Katarin:** You could stay here, you know.

**Terra:** I will.

**Duane:** But you're going with them again.

**Terra:** Yes.

**Duane:** Why?

**Terra:** Because I want this place to be here when I come back.

**Child:** You'll come back?

**Terra:** Always.

## NPC STATES — Mobliz

### Child A before
“Are the monsters coming back?”

### During
“Terra says the water's bad. Water can be bad?”

### After
“I planted this one! Don't step on it!”

### Child B after
“We have lessons now. I liked monsters better.”

### Teacher after
“Terra learns faster than the children. She also asks more questions.”

### Duane after
“We stopped planning how to leave.”

### Katarin after
“That's how I knew we'd finally come home.”

---

# ARC 3 — CYAN: THE LAST KINGDOM OF DOMA

## Scene D01 — Return to Doma

**Cyan:** Someone hath lit the eastern lamps.

**Sabin:** You expecting company?

**Cyan:** No living soul.

[EVENT: survivor Ren appears.]

**Ren:** Then you're late, Sir Cyan.

**Cyan:** Thou knowest me?

**Ren:** Everybody from Doma knows you.

## Scene D02 — The argument

**Ren:** We need the eastern gate opened.

**Cyan:** This castle is a grave.

**Ren:** It was our home first.

**Cyan:** Thou knowest not what happened here.

**Ren:** I was here.

[EVENT pause.]

**Ren:** I lost my mother in the hall below us.

**Ren:** I still want a roof.

**Cyan:** ...Forgive me.

## Scene D03 — Poisoned aqueduct

**Ren:** We found water under the old barracks, but anyone who drinks it gets sick.

**Cyan:** Kefka's poison...

**Ren:** After all this time?

**Strago:** Poison leaves. Magic lingers.

**Cyan:** Then we shall cleanse both.

## Scene D04 — Aqueduct memorial

[EVENT: party finds rusted child's sword.]

**Cyan:** Owain had one much like this.

**Sabin:** Want a minute?

**Cyan:** Nay.

**Cyan:** I have had a year of minutes.

## Scene D05 — Boss intro

**Strago:** That thing's been drinking the poison.

**Cyan:** Then it hath feasted long enough.

[BOSS: MIASMA REGENT]

## Scene D06 — Water returns

**Ren:** Clear.

**Cyan:** Taste it not yet.

**Ren:** You sound like my mother.

**Cyan:** I shall take that as an honor.

## Scene D07 — Throne room

**Ren:** People will listen to you.

**Cyan:** That doth not mean they should obey me.

**Ren:** Doma needs someone.

**Cyan:** Doma needs many someones.

**Sabin:** That's not a word.

**Cyan:** Today, it is.

## Scene D08 — Cyan conclusion

**Cyan:** I did mistake remembrance for duty.

**Sabin:** Meaning?

**Cyan:** I thought to honor the dead, Doma must remain as they left it.

**Cyan:** Yet a kingdom is not stone.

**Cyan:** It is its people.

**Ren:** Then help us move some stone.

**Cyan:** Gladly.

## NPC STATES — Doma

### Before completion
**Survivor:** There is nothing here but ghosts.

### After completion
**Survivor:** The ghosts can stay. So can we.

### Ren after
“Sir Cyan keeps asking permission before moving anything in the castle. I keep telling him it's his castle too.”

### Memorial keeper
“We repaired every room but this one. Some things should remain exactly where memory left them.”

---

# ARC 4 — SHADOW & RELM: THE MAN BEHIND THE MASK

## Scene S01 — Interceptor runs

[EVENT: Interceptor barks and leaves Thamasa.]

**Relm:** Interceptor! Hey!

**Shadow:** Leave him.

**Relm:** He brought us here.

**Shadow:** Then he made a mistake.

**Relm:** Funny. You always say that when you want somebody to stay away.

## Scene S02 — Burned cottage

**Relm:** I've never seen this place.

**Strago:** Nor have I.

**Shadow:** There's nothing here.

**Relm:** Then why are you standing in front of the door?

[EVENT: Relm enters.]

## Scene S03 — Box

**Relm:** Locked.

**Shadow:** Good.

**Relm:** You know it.

**Shadow:** No.

**Relm:** You're a terrible liar.

**Shadow:** I'm alive. That makes me good enough.

## Scene S04 — Bandit's mark

**Locke:** This carving... old robber code.

**Shadow:** Forget it.

**Locke:** Baram's mark?

[EVENT: Shadow turns.]

**Shadow:** I said forget it.

**Relm:** Who's Baram?

**Shadow:** Dead.

## Scene S05 — Guilt illusion

**Illusion:** Clyde.

**Shadow:** ...

**Illusion:** Finish it.

**Relm:** Who's Clyde?

**Shadow:** Nobody.

**Illusion:** You ran.

**Shadow:** Shut up.

**Illusion:** You always run.

**Relm:** Shadow!

[BOSS: GUILTSHADE]

## Scene S06 — After boss

**Relm:** That thing knew you.

**Shadow:** It knew memories.

**Relm:** Same difference.

**Shadow:** No.

**Relm:** Then explain it.

**Shadow:** No.

## Scene S07 — Letter

[EVENT: key opens cottage box.]

**Relm:** “Clyde...”

**Shadow:** Put it back.

**Relm:** Who was he?

**Shadow:** A coward.

**Relm:** Mom wrote to him.

**Shadow:** ...

**Relm:** She waited for him.

**Shadow:** Enough.

**Relm:** It says she had a daughter.

**Shadow:** Relm.

**Relm:** It says he never came back.

## Scene S08 — Cliff of Ash

[EVENT: Relm follows Shadow outside.]

**Relm:** You knew her.

**Shadow:** Yes.

**Relm:** Better than Grandpa did?

**Shadow:** In a different life.

**Relm:** Then look at me.

[EVENT: Shadow turns.]

**Relm:** Was Clyde my father?

[EVENT: long pause.]

**Shadow:** Your mother deserved better than the man he was.

**Relm:** Maybe.

**Relm:** But that wasn't what I asked.

[EVENT: Shadow removes ring.]

**Shadow:** She wore this.

**Relm:** ...

**Shadow:** Keep it safe.

**Relm:** You could do that yourself.

**Shadow:** No.

**Relm:** Coward.

**Shadow:** ...Yeah.

[EVENT: Interceptor walks to Relm and sits.]

**Relm:** He's staying with me tonight.

**Shadow:** He decides that.

**Relm:** No. I do.

## Scene S09 — Strago optional

[IF STRAGO IN PARTY]

**Strago:** I knew her mother had secrets.

**Relm:** Grandpa.

**Strago:** Not that many secrets.

**Shadow:** Old man.

**Strago:** Don't “old man” me.

**Strago:** You owe this family years.

**Shadow:** I know.

**Strago:** Good.

## NPC STATE — Relm house after

**Relm:** Don't tell him I kept the ring on.

**Strago:** The man can see.

**Relm:** Then don't tell him I said not to tell him.

## Shadow airship line after

**Shadow:** Some debts don't disappear because you finally face them.

---

# ARC 5 — EDGAR & SABIN: TWO SONS OF FIGARO

## Scene F01 — Engine trouble

[EVENT: Figaro shudders underground.]

**Engineer:** Majesty! Pressure on the southern intake!

**Edgar:** Reduce drive output twelve percent.

**Engineer:** We already did.

**Sabin:** This happen often?

**Edgar:** Define often.

**Sabin:** Edgar.

**Edgar:** No.

## Scene F02 — Brothers argue

**Sabin:** How bad?

**Edgar:** Manageable.

**Engineer:** Your Majesty—

**Edgar:** Manageable.

**Sabin:** You always do this.

**Edgar:** Do what?

**Sabin:** Decide what everybody else can handle.

**Edgar:** That's called ruling.

**Sabin:** That's called being impossible.

## Scene F03 — Foundry

**Engineer:** The intake tunnel's blocked by something alive.

**Sabin:** Finally. A problem I understand.

**Edgar:** Hit the machinery and I will personally exile you.

**Sabin:** See? Impossible.

## Scene F04 — Brass Colossus

**Edgar:** That's one of Father's excavation frames.

**Sabin:** It got bigger.

**Engineer:** It ate the other frames.

**Sabin:** ...I still understand this problem.

[BOSS: BRASS COLOSSUS]

## Scene F05 — Royal Archive

[EVENT: coin falls from old box.]

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

[EVENT pause.]

**Sabin:** Yeah.

**Edgar:** Exactly.

## Scene F06 — Sabin's anger softens

**Sabin:** I spent years thinking I ran away.

**Edgar:** You did run away.

**Sabin:** Thanks.

**Edgar:** So did I. I just ran into a throne room.

**Sabin:** That's the stupidest thing you've ever said.

**Edgar:** You smiled.

**Sabin:** Shut up.

## Scene F07 — Duncan trial

**Duncan:** Strength!

**Sabin:** Master.

**Duncan:** You still strike before you think.

**Sabin:** I've gotten better.

**Duncan:** You broke my gate.

**Sabin:** Your gate attacked me.

**Duncan:** Good! Then fight something that fights back.

[BOSS: MASTER'S ECHO]

## Scene F08 — Duncan conclusion

**Duncan:** Better.

**Sabin:** I won.

**Duncan:** I said better.

**Sabin:** You could say “good.” Once.

**Duncan:** Good students stop asking.

**Sabin:** There it is.

## NPC STATES — Figaro

**Engineer before:** His Majesty says the engine is fine. His face says otherwise.

**Engineer after:** The castle can cross the desert again. His Majesty can stop pretending he wasn't worried.

**Guard after:** Prince Sabin carried a drive shaft by himself. His Majesty complained about the floor afterward.

---

# ARC 6 — SETZER: THE LAST RACE

## Scene R01 — Beacon

[EVENT: Falcon alarm chirps.]

**Setzer:** Turn that off.

**Edgar:** I didn't turn it on.

**Setzer:** Then turn it off anyway.

[EVENT: signal repeats.]

**Setzer:** ...No.

**Celes:** You know it.

**Setzer:** Racing beacon.

**Celes:** Whose?

**Setzer:** Darill's.

## Scene R02 — Sky Graveyard

**Locke:** That's a lot of wreckage.

**Setzer:** Pilots used this storm belt as a shortcut.

**Edgar:** Sensible pilots?

**Setzer:** Those are called passengers.

## Scene R03 — Wreck nameplate

**Celes:** “Vagrant Queen.”

**Setzer:** Civilian courier.

**Celes:** You know it?

**Setzer:** I know every ship that crossed our race route that day.

**Celes:** Why?

**Setzer:** Because I spent years trying to prove the weather killed her.

## Flashback R-F1

**Darill:** You're late.

**Setzer:** I arrived after you. Different thing.

**Darill:** Still counts as losing.

**Setzer:** We'll count when we land.

**Darill:** If you can keep up.

## Flashback R-F2

**Darill:** Storm front's moving north.

**Setzer:** Afraid?

**Darill:** Of getting bored waiting for you.

**Setzer:** First one through Beacon Seven buys dinner.

**Darill:** First one through Beacon Seven never has to listen to you talk about odds again.

## Scene R04 — Truth in log

**Log:** VAGRANT QUEEN ENGINE FAILURE.

**Log:** DISTRESS SIGNAL RECEIVED.

**Log:** UNIDENTIFIED RACER ALTERED COURSE.

**Log:** TOW ESTABLISHED.

**Log:** RACER LOST IN STORM.

**Celes:** She turned back for them.

**Setzer:** ...

**Celes:** You thought she crashed because she pushed too hard.

**Setzer:** Darill always pushed too hard.

**Celes:** That's not what happened.

**Setzer:** No.

## Scene R05 — Sky Reaver

[EVENT: beacon tower shakes.]

**Edgar:** Something is wrapped around the transmitter.

**Setzer:** Then unwrap it.

**Sabin:** Finally, your kind of repair work.

[BOSS: SKY REAVER]

## Scene R06 — Beacon restored

**Celes:** Does knowing help?

**Setzer:** Ask me when it stops hurting.

**Celes:** It may not.

**Setzer:** Then I guess I'll keep flying anyway.

[EVENT: beacon lights.]

**Setzer:** She'd hate that I turned her race marker into a safety light.

**Celes:** She turned around for a broken ship.

**Setzer:** ...Yeah.

**Setzer:** She'd complain first.

## Falcon line after

**Setzer:** Odds are for people who need permission to act.

---

# ARC 7 — THE FORGOTTEN AGE

# Dungeon A — Sanctuary of Concord

## Entrance inscription

**Inscription:** NO BLOOD BEYOND THIS GATE.

**Inscription:** HUMAN AND ESPER ENTER AS GUESTS.

## Scene A01

**Terra:** They lived together here.

**Strago:** For a time.

**Relm:** What ruined it?

**Strago:** If these people knew, they didn't carve it on the door.

## Archive tablet A

**Tablet:** WE BORROWED FLAME FROM THOSE WHO WERE FLAME.

**Tablet:** WE CALLED THE BORROWING FRIENDSHIP.

**Tablet:** THEN WE CALLED IT RIGHT.

## Boss intro — Concord Sentinel

**Sentinel:** PACT STATUS: BROKEN.

**Terra:** We're not here to take anything.

**Sentinel:** ALL WHO CAME AFTER SAID THE SAME.

[BOSS]

## After

**Terra:** It was still guarding an agreement nobody remembered.

**Strago:** Sometimes rules outlive the reason for them.

**Terra:** People too.

---

# Dungeon B — Field of Cinders

## Entrance scene

**Cyan:** I like not this place.

**Sabin:** Because it's haunted?

**Cyan:** Because it is familiar.

## Battlefield memory stones

**Stone 1:** THIRD COMPANY. HUMAN.

**Stone 2:** RED WING. ESPER.

**Stone 3:** FOUGHT TOGETHER. DIED TOGETHER.

**Celes:** So the sides weren't clean even then.

**Edgar:** They never are.

## Boss intro — Empyreal Chimera

**Strago:** War beast.

**Relm:** People made that?

**Strago:** People ordered it.

**Terra:** Same difference.

[BOSS]

## After

**Celes:** A weapon waiting a thousand years for an order.

**Edgar:** Let's make sure it never gets one.

---

# Dungeon C — Shrine of the Silent Three

## Entrance

**Inscription:** POWER ABOVE.

**Inscription:** ORDER BELOW.

**Inscription:** OBEDIENCE BETWEEN.

**Relm:** I don't like this place.

**Strago:** Good.

## Shrine tablet

**Tablet:** THREE GODS SPOKE.

**Tablet:** THREE KINGS CLAIMED TO HEAR THEM BEST.

**Tablet:** THEN THE KILLING BEGAN.

**Cyan:** Men needed no god to teach them pride.

## Boss intro — Triune Sentinel

**Sentinel A:** GODDESS.

**Sentinel B:** FIEND.

**Sentinel C:** DEMON.

**All:** KNEEL.

**Sabin:** Pass.

[BOSS]

## After

**Edgar:** Three statues. Three factions.

**Celes:** And everyone certain they were the chosen one.

**Terra:** Kefka would have liked it here.

---

# VAEL ARCHIVE

## Journal 1

**Vael's Record:** We believed magic made us greater.

**Vael's Record:** Then we learned it merely made our mistakes larger.

## Journal 2

**Vael's Record:** The Espers are not our servants.

**Vael's Record:** Nor are we theirs.

**Vael's Record:** Yet every treaty becomes ownership when fear enters the room.

## Journal 3

**Vael's Record:** I will sever magic from man.

**Vael's Record:** Better one age of loss than another age of fire.

## Journal 4

**Vael's Record:** The seal failed.

**Vael's Record:** Magic does not sit in stone.

**Vael's Record:** It lives.

**Vael's Record:** To remove it, I would have to wound every life it touches.

## Journal 5

**Vael's Record:** I could not do it.

**Vael's Record:** I do not know whether that was mercy or cowardice.

---

# ARC 8 — THE FIRST MAGI

## Scene V01 — Cradle entrance

[EVENT: three sigils react.]

**Strago:** These stones haven't held power for centuries.

**Terra:** Something inside remembers them.

**Celes:** That's comforting.

**Locke:** Your definition of comforting worries me.

## Scene V02 — First projection

**Vael:** Turn back.

**Terra:** Who are you?

**Vael:** One who failed before your ancestors learned my name.

**Strago:** Vael.

**Vael:** Ah.

**Vael:** Someone kept the old mistakes after all.

## Scene V03 — Argument

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

[BOSS PHASE 1]

## Scene V04 — Seal Engine

**Vael:** You mistake survival for wisdom.

**Celes:** And you mistake fear for wisdom.

**Vael:** Fear remembers what hope forgets.

**Cyan:** Then let memory counsel us.

**Cyan:** It shall not rule us.

[BOSS PHASE 2]

## Scene V05 — Vael Unbound

[EVENT: seal shatters; Vael reforms.]

**Vael:** I spared the world once.

**Strago:** No.

**Strago:** You stopped because the price frightened you.

**Vael:** And you would pay it now?

**Strago:** Not with someone else's life.

**Vael:** Then you learned nothing.

**Relm:** Maybe we learned not to let dead old men make all the decisions.

**Strago:** Relm!

**Vael:** ...

**Vael:** Perhaps extinction has improved manners.

**Relm:** See? He's learning already.

[BOSS PHASE 3]

## Hope messages during Last Edict
These appear only if corresponding flags are complete. They are fragments, not literal telepathy.

**Mobliz:** “Our door.”

**Doma:** “A kingdom is its people.”

**Figaro:** “Someone had to stay.”

**Vector:** “Remember the names.”

**Thamasa:** “Keep it safe.”

**Falcon:** “Keep flying anyway.”

**Sanctuary:** “Human and Esper enter as guests.”

**Terra:** “A future is a gamble.”

## Scene V06 — Defeat

**Vael:** If you are wrong...

**Terra:** Then they'll have to choose again.

**Vael:** Again...

**Edgar:** That's the troublesome thing about people.

**Vael:** Hm.

**Vael:** I had forgotten.

[EVENT: Vael dissolves into inert crystal.]

## Scene V07 — Broken Seal

**Celes:** Is he dead?

**Strago:** He was dead a thousand years ago.

**Relm:** That's a yes, then.

**Terra:** No.

**Terra:** It's an ending.

**Locke:** Difference?

**Terra:** I think so.

---

# MINOR QUEST SCRIPT — SEEDS FOR TOMORROW

## Maranda

**Farmer:** These seeds survived ash, drought and one very determined chocobo.

**Terra:** Will they grow in Mobliz?

**Farmer:** Ask them.

**Terra:** ...

**Farmer:** That's farmer humor.

**Terra:** I don't understand it.

**Farmer:** You'll fit right in.

## Mobliz completion

**Child:** Which one grows candy?

**Farmer:** None.

**Child:** We brought the wrong farmer.

---

# MINOR QUEST SCRIPT — THE EMPTY FORGE

## Narshe

**Locke:** Forge is cold.

**Old Smith:** So am I.

**Locke:** You're alive!

**Old Smith:** Disappointing, isn't it?

**Locke:** Depends. Can you still make a sword?

**Old Smith:** Can you still pay for one?

**Locke:** Definitely alive.

## Completion

**Old Smith:** Fire's lit.

**Celes:** Staying?

**Old Smith:** Somebody has to complain when people hold a blade wrong.

---

# MINOR QUEST SCRIPT — A ROAD THROUGH SAND

**Merchant:** Burrowers ate two wagons.

**Sabin:** The whole wagons?

**Merchant:** Wheels and all.

**Edgar:** That's impossible.

**Merchant:** Tell the burrowers.

## Completion

**Merchant:** Road's open!

**Edgar:** Try not to drive over anything with teeth.

**Merchant:** That's most of the desert, Majesty.

---

# MINOR QUEST SCRIPT — LETTERS HOME

## Letter 1 delivery

**Woman:** My son wrote this?

**Cyan:** He did.

**Woman:** Is he...?

**Cyan:** He lived long enough to wish thee home.

**Woman:** Then I will go.

## Letter 2 delivery

**Man:** I thought everyone from Doma was dead.

**Cyan:** So did we all.

**Man:** That's a terrible thing to be wrong about.

**Cyan:** Nay.

**Cyan:** This once, I am glad of it.

---

# MINOR QUEST SCRIPT — THE BELL OF THAMASA

**Strago:** That bell warned us when outsiders approached.

**Relm:** So everybody could pretend not to use magic.

**Strago:** Correct.

**Relm:** We were weird.

**Strago:** We were cautious.

**Relm:** Weird and cautious.

## Completion

[EVENT: bell rings.]

**Child:** What's it warn us about now?

**Strago:** Dinner, if I have anything to say about it.

---

# MINOR QUEST SCRIPT — LIGHT ON THE COAST

**Sailor:** Beacon's dead. Ships hug the shore now.

**Setzer:** Cowards.

**Celes:** Sensible people.

**Setzer:** Same thing at sea.

## Completion

**Sailor:** Light's visible past the reef!

**Setzer:** Good.

**Celes:** No insult?

**Setzer:** I charge extra for those.

---

# MINOR QUEST SCRIPT — THE LAST CLASSROOM

## Ruined house

**Terra:** Books.

**Locke:** Mostly dry, too.

**Terra:** This one is about numbers.

**Locke:** Put it back.

**Terra:** Why?

**Locke:** Monsters I can fight.

## Mobliz

**Teacher:** History, letters, numbers...

**Child:** Do we have to learn all of them?

**Teacher:** Eventually.

**Child:** Kefka was easier.

**Terra:** No.

**Child:** ...I was joking.

**Terra:** Oh.

**Terra:** Was it funny?

---

# MINOR QUEST SCRIPT — GRAVES WITHOUT NAMES

## Vector ruin

**Vale:** These markers have numbers, not names.

**Celes:** Find the roster.

**Vale:** Some were Imperial soldiers.

**Celes:** Find the roster.

**Vale:** Some guarded the Annex.

**Celes:** Vale.

**Vale:** ...I'll find it.

## Memorial completion

**Former Soldier:** You put guards and prisoners on the same wall.

**Celes:** They're all dead.

**Former Soldier:** That's your reason?

**Celes:** It's enough.

---

# AIRSHIP POST-QUEST BARKS

## Terra
“It's strange. I used to wonder where I belonged. Now I wonder how many places can become home.”

## Celes
“I don't need the Empire forgiven. I need it remembered correctly.”

## Locke
“Rebuilding towns is harder than stealing treasure. Less running, more carrying.”

## Edgar
“A kingdom is much easier to rule when it isn't buried in sand.”

## Sabin
“Edgar says I can't help fix the engine anymore. I helped once.”

## Cyan
“Doma soundeth different with hammers in the halls.”

## Shadow
“Keep moving.”

## Relm
“Interceptor likes my room better than his. Don't tell Shadow.”

## Strago
“A thousand years of history, and somehow children still interrupt the important parts.”

## Gau
“Doma people make roof! Gau help! Roof fall once. Only once!”

## Setzer
“A beacon's just a bet that somebody out there wants to get home.”

## Mog
“Everybody's building stuff, kupo! Does that mean I get a house?”

## Gogo
“...”

## Umaro
“Uwao!”

---

# EXPANDED ENDING VIGNETTES

## Ending E01 — Empire / Preserve

[EVENT: Figaro archive. Two guards carry sealed boxes. Celes watches.]

**Archivist:** General?

[EVENT: Celes looks at him.]

**Archivist:** ...Celes. Where should we put the Leo files?

**Celes:** With the others.

**Archivist:** Separate display?

**Celes:** No.

**Celes:** Let the whole story stand together.

[EVENT: Celes leaves.]

## Ending E02 — Empire / Burn

[EVENT: Vector memorial. Ash blows across stones.]

**Celes:** Leo.

[EVENT: she places old insignia.]

**Celes:** We remembered the names.

[EVENT: fade.]

## Ending E03 — Mobliz

[EVENT: children run between crop rows.]

**Child:** Terra! School's over!

[EVENT: camera pans to old room now filled with desks.]

**Terra:** Already?

**Teacher:** Three hours ago.

**Terra:** Oh.

## Ending E04 — Doma

[EVENT: gates open; lumber wagons enter.]

**Ren:** Sir Cyan! We need you at the west wall!

**Cyan:** I am coming!

[EVENT: Cyan pauses at memorial door, bows, then continues.]

## Ending E05 — Shadow/Relm

[EVENT: Relm paints by window. Interceptor sleeps beside her.]

**Relm:** Hold still.

[EVENT: distant ridge. Shadow silhouette briefly visible.]

**Relm:** Not you.

[EVENT: she smiles without looking up.]

## Ending E06 — Figaro

[EVENT: castle emerges beside caravan road.]

**Engineer:** Majesty! The western brace—

**Edgar:** Ask Sabin.

**Sabin:** What?!

**Edgar:** Family responsibility.

**Sabin:** That's not what that means!

## Ending E07 — Setzer

[EVENT: night sky. Beacon flashes. Small airship follows route.]

**Setzer:** Not bad.

**Celes:** For a safety light?

**Setzer:** For a bad bet.

## Ending E08 — Forgotten Age

[EVENT: powerless sigils placed behind simple railing.]

**Strago:** No altar.

**Relm:** Good.

**Strago:** No dramatic inscription.

**Relm:** Better.

**Strago:** No touching.

**Relm:** We'll see.

## Ending E09 — Broken Seal

[EVENT: Terra holds inert shard. Last faint light fades.]

**Terra:** Goodbye.

[EVENT: she opens her hand; shard is ordinary stone.]

**Child:** Are you sad?

**Terra:** A little.

**Child:** Why are you smiling?

**Terra:** Because we're still here.

---

# FINAL STYLE CHECKLIST FOR ROM TEXT PASS

For every line during implementation:
1. Preserve character voice over literal exposition.
2. Remove redundant speaker names if portrait/name box makes them unnecessary.
3. Prefer one thought per text box.
4. Avoid modern therapy vocabulary, memes, slang or self-aware genre jokes.
5. Shadow should have the fewest words possible.
6. Terra should not suddenly explain philosophy at length.
7. Cyan's archaic register must remain readable.
8. Relm may be sharp, not cruel.
9. Kefka-related records remain clinical, not sympathetic.
10. All new lore must remain compatible with the original ending: magic disappears when Kefka/Warring Triad power ends.

