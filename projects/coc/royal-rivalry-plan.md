# The Royal Rivalry: series plan (12 episodes)

A Clash of Clans fan comic built from official Supercell Fan Kit art. Every episode ends on a cliffhanger
and a comment prompt.

**Format (current):** full episodes of about 10 minutes, 16:9 (1920x1080), voiced by a local Kokoro cast
(narrator plus a voice per character, narrator-only subtitles; character lines acted with emotion by
Chatterbox in their Kokoro voice, see tools/emotive_tts.py), each with a ~1-minute vertical promo Short
voiced with ElevenLabs premade voices.
- Full episodes: `projects/coc/royal-rivalry-full-ep<NN>/` (build.py writes script.json)
- Promos: `projects/coc/royal-rivalry-full-ep<NN>-promo/`
- Page helpers and casts: `projects/coc/rivalry.py`; page engine: `motion/coc/comicpage.js`
- The earlier vertical Shorts (`royal-rivalry-ep1..3`) were the pilot of the same story.

**Main cast:** Barbarian King and Archer Queen (rivals), Grand Warden (mentor), the Goblin from Ep 1
(comic relief, later a guide), Barbarians and Archers (the two factions), Healer.
**Villain:** the Electro Titan, a storm sorceress who wants the kingdom's Elixir to power her storm.
**Her forces:** Electro Dragons, a P.E.K.K.A guard. **Late allies:** Royal Champion, Dragons, Balloons.

## The secrets (what the audience doesn't know yet)
Every reveal is set up by clues already on screen, so a rewatch pays off.
- **The traitor is the Wizard.** The Sorceress promised to pull the lightning out of the dying Warden if he helps her.
  Clues: his "clear skies all week" report (Ep 2); he is always near the Elixir when it fizzes (Ep 2, 3);
  his "wrong spell" on the fire (Ep 3); he's the one who rings the alarm a beat too late.
- **The Warden lied.** The Sorceress was his apprentice. He didn't defeat her: he tricked her, sealed her away
  and took the valley's Elixir to found the kingdom. Clue: "You didn't tell them everything" (Ep 3).
- **The goblin is a spy, then a double agent.** He sells the heroes out in Ep 7, because the Sorceress holds the
  Goblin Boss prisoner; he turns back in Ep 9. Clue: the map he "drops" in Ep 3 is bait.
- **The Healer is the Sorceress's granddaughter** (season 2 hook). Clue: "My grandmother told me stories...
  she never, ever forgot a face" (Ep 3).

## Arc 1: The Storm
1. **Who Is the Greatest?** (full episode + promo done): the rivalry, the Warden's contest, the goblin collision, eyes in the dark.
2. **The Storm Arrives** (full episode + promo done): an Electro Dragon attacks, the heroes sabotage each other, the Warden falls.
3. **Picking Up the Pieces** (full episode + promo done): the Healer saves the Warden; near-teamwork at the falling tower;
   the goblin escapes with a map showing the storm mark; the Warden tells the legend of the Storm Sorceress.
   Cliffhanger: a castle made of storm, and eyes looking back.
4. **The Storm Sorceress** (full episode + promo done): the Electro Titan appears in a storm vision and demands the kingdom's Elixir. That night
   three dragons strike, but the attack is a distraction: the Elixir storage is emptied *from inside*, and the
   gate was unbarred with a key. **Twist: there is a traitor in the kingdom.** Everyone suspects the goblin.

## Arc 2: Divided
5. **Two Paths:** the King and Queen set out alone to hunt the Titan, and both fail badly. She visits each of them in
   the storm with the same offer: bring her the Warden's Eternal Tome, and she will make you the only hero the
   kingdom remembers. The King refuses at once. **Cliffhanger: the Queen says, "Tell me more."**
6. **The Goblin Who Knew Too Much:** the heroes catch the goblin; he swears he isn't the traitor and offers to guide
   them to the citadel. The King sees the Queen meeting someone in secret and suspects her.
   **Twist: that night, the Queen steals the Eternal Tome and vanishes.**
7. **The Bridge of Trust:** the King chases her to a broken canyon bridge; they fight, then have to work together to
   cross (King throws, Queen anchors with arrows). **Reveal: the Queen's "deal" was a bluff to get inside the
   citadel.** Then the real betrayal: the goblin guide snatches the Tome and hands it to the Titan's dragons.

## Arc 3: United
8. **Ambush in the Clouds:** dragons ambush the heroes; the Barbarians and Archers arrive *together* to save them.
   The goblin confesses: the Titan holds the Goblin Boss prisoner. **Episode-ending twist: in the citadel, the
   Titan thanks her spy for the gate key, and the spy steps into the light. It's the Wizard.**
9. **The Champion's Return:** the Royal Champion, who left the kingdom long ago, shows up, apparently serving the
   Titan; she's undercover. The Wizard's motive comes out: the Titan promised to save the Warden, who is dying
   from the lightning inside him. The goblin turns double agent to free his Boss.
10. **Siege of the Storm Citadel:** Balloons and Dragons lead the assault; a P.E.K.K.A guards the gate.
    **The biggest twist: the Titan tells the truth about the Warden.** She was his apprentice; he tricked her and
    took the valley's Elixir. The Warden admits it. The heroes have to decide whether they're on the right side.
11. **Clash of Storms:** the final battle. The Wizard turns back and breaks his own spell; the goblin frees the Boss;
    the Warden uses the last of the Tome's power to shield everyone, and apologises to his old apprentice.
    The King and Queen combine strength and aim to break the storm: they stop the Titan without destroying her,
    and she leaves with her Elixir returned.
12. **The Greatest Hero:** the kingdom rebuilt; the Wizard forgiven (and banned from weather reports); the Warden
    crowns *both* heroes; a statue of the two together. They argue over whose side is taller.
    **Final scene: the Healer, alone, and her eyes crackle blue.** Season 2 tease.

## Rules
- Official Fan Kit art only, scaled / moved / cropped / faded (no recolouring or redrawing characters);
  effects, bubbles and scenery are drawn on top.
- Each video description carries Supercell's Fan Content Policy disclaimer.
- Clash videos use the Clash sound set (not the softened Wuthering Waves set).
