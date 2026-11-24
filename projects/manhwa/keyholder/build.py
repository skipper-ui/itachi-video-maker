"""Builds script.json for KEYHOLDER, a standalone ~20-minute manhwa-style story video (16:9).

Run: python3 projects/manhwa/keyholder/build.py
Original story and characters. Each scene is one AI image (Pollinations, FLUX.2 klein) under its spoken lines.
Voices are recorded in Speechma: SPEECHMA.md, written alongside, lists every clip; recorded files go in
audio/clip-NNN.mp3 and are used automatically. Any clip not recorded yet is voiced by a local Kokoro placeholder,
so a draft can be rendered at any time.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = "narrator"

# Fixed character descriptions, repeated in every prompt so the art stays consistent from panel to panel.
C = {
    "JIHO": "Yoon Ji-ho, a 20-year-old Korean young man with messy black hair, tired dark eyes, a thin scar on his left cheek, "
            "wearing a worn navy-blue utility jacket with a small brass key badge on the chest",
    "JIHO_GOLD": "Yoon Ji-ho, a 20-year-old Korean young man with messy black hair and glowing golden eyes, a thin scar on his left cheek, "
                 "wearing a worn navy-blue utility jacket with a small glowing brass key badge",
    "YEONAH": "Seo Yeon-ah, a 22-year-old Korean woman with long straight white hair in a high ponytail, ice-blue eyes, "
              "wearing a black and silver armored hunter coat, holding a slender katana",
    "KWON": "Director Kwon, a handsome 45-year-old Korean man with slicked-back grey-streaked hair, thin gold-rimmed glasses, "
            "wearing an immaculate white three-piece suit and a gold ring engraved with a keyhole",
    "MINGYU": "Park Min-gyu, a 23-year-old Korean man with spiky dyed red hair, sharp grin, wearing a red leather hunter jacket and heavy steel gauntlets",
    "JIAH": "Yoon Ji-ah, a 12-year-old Korean girl with a short black bob haircut, pale cheeks, in a light blue hospital gown",
}
STYLE = ("Korean manhwa webtoon art style, clean bold line art, cel shading, dramatic cinematic lighting, vibrant colors, "
         "highly detailed illustration, 16:9 widescreen composition, no text, no letters, no speech bubbles, no watermark")

# Placeholder voices (Kokoro, local) for clips that haven't been recorded in Speechma yet.
KOKORO = {"narrator": "am_michael", "jiho": "am_puck", "yeonah": "af_nicole", "kwon": "am_onyx", "mingyu": "am_fenrir",
          "jiah": "af_sky", "voice": "bm_fable", "official": "am_eric", "anchor": "bm_daniel", "doctor": "bm_george",
          "hunter": "am_echo", "nurse": "af_bella"}
ELEVEN = {
    "jiho": "TX3LPaxmHKxFdv7VOQHJ",     # Liam
    "yeonah": "EXAVITQu4vr4xnSDxMaL",   # Sarah
    "kwon": "cjVigY5qzO86Huf0OWal",     # Eric
    "mingyu": "SOYHLrjzK2X1ezoPC6cr",   # Harry
    "jiah": "cgSgspJ2msm6clMCkdW9",     # Jessica
    "voice": "JBFqnCBsd6RMkjVDRZzb",    # George: the ancient voice of the Key
    "official": "iP95p4xoKVk53GoZ742B", # Chris
    "anchor": "onwK4e9ZLuTAKqWW03F9",   # Daniel
    "doctor": "pqHfZKP75CvOlQylNhV4",   # Bill
    "hunter": "bIHbv24MWmeRgasZH58o",   # Will
    "nurse": "FGY2WhTYpPnrIDTdsKH5",    # Laura
}
NAMES = {"narrator": "Narrator", "jiho": "Ji-ho", "yeonah": "Yeon-ah", "kwon": "Director Kwon", "mingyu": "Min-gyu",
         "jiah": "Ji-ah", "voice": "The Voice", "official": "Association official", "anchor": "News anchor",
         "doctor": "Doctor", "hunter": "Hunter", "nurse": "Nurse"}
SPEECHMA_VOICES = {  # suggested Speechma voices (English, US unless noted), if recording there instead
    "narrator": "a deep, calm male narrator (e.g. Guy or Christopher)", "jiho": "young male (e.g. Brian or Andrew)",
    "yeonah": "young female, cool (e.g. Jenny or Aria)", "kwon": "smooth middle-aged male (e.g. Eric or Davis)",
    "mingyu": "young male, rough (e.g. Roger or Tony)", "jiah": "a child or bright young female (e.g. Ana)",
    "voice": "old British male (e.g. Ryan, UK)", "official": "any male", "anchor": "news-style male (e.g. Thomas, UK)",
    "doctor": "older male", "hunter": "young male", "nurse": "female",
}


def L(who, text, tone=None):
    return [who, text, {"tone": tone}] if tone else [who, text]


def S(image, *lines, fx=None):
    sc = {"image": image.format(**C) + ", " + STYLE, "lines": [list(l) for l in lines]}
    if fx is not None:
        sc["fx"] = fx
    return sc


scenes = [
    # ---- Cold open ----
    S("wide establishing shot of the Seoul skyline at night with dozens of glowing blue and red portal gates floating in the sky above skyscrapers",
      (N, "Seoul. Ten years after the first Gate opened in the sky.")),
    S("hunters in armor fighting a giant horned monster in a ruined Seoul street at night, sparks and blue magic, cars overturned",
      (N, "Monsters poured out of them. Hunters rose to fight back. And when the fighting was over, someone had to close the door.")),
    S("{JIHO} kneeling in the rain with his palm pressed against a small fading blue portal on a ruined street, faint light on his hand, an official in a reflective vest with a clipboard behind him",
      L("jiho", "Seal complete. Gate C-114 is closed.", "tired"),
      L("official", "Sign here, Sealer. You've got six more tonight.", "bored")),
    S("{JIHO} standing alone in the rain under a streetlight, small figure in a huge city, lonely mood",
      (N, "That someone was Yoon Ji-ho. F-rank. The lowest rank a hunter can have. His only skill: closing Gates after real hunters had finished with them.")),
    S("Hunter Association evaluation hall, {JIHO} with his hand on a large crystal orb that glows only very faintly, an official reading a tablet, other hunters laughing in the background",
      L("official", "Yoon Ji-ho. Re-evaluation result: F-rank. Again.", "bored"),
      L("jiho", "Could you check one more time? Maybe the machine's broken.", "hopeful"),
      L("official", "The machine's fine, kid. You're just weak. Next!", "dismissive")),
    S("{MINGYU} snatching a pay envelope out of {JIHO}'s hands in a guild hallway, counting the money with a grin",
      L("mingyu", "Sealer fee, thirty thousand won. Guild cut, twenty-nine thousand.", "smug"),
      L("jiho", "That leaves me one thousand.", "flat"),
      L("mingyu", "Buy yourself some nice gum.", "mocking laugh")),

    # ---- Act 1: the Red Gate ----
    S("bright luxurious guild hall lobby with marble floor and a golden lion emblem, {MINGYU} smirking at {JIHO} who carries a heavy equipment bag",
      L("mingyu", "Look who it is. The janitor. You missed a spot yesterday, Sealer.", "mocking"),
      L("jiho", "Good morning to you too, Min-gyu.", "flat"),
      L("mingyu", "That's Mister B-rank to you.", "smug")),
    S("{KWON} walking down a marble staircase smiling warmly, guild members bowing, golden light from tall windows",
      (N, "The Hwarang Guild. The richest guild in Korea. And its Director, the most beloved man in Seoul."),
      L("kwon", "Now, now, Min-gyu. Every great guild needs someone to close the doors. Ji-ho, you'll join today's raid.", "warm, smooth"),
      L("jiho", "Me? On a Red Gate?", "surprised"),
      L("kwon", "Someone has to seal it afterwards. Who better than our best Sealer?", "smiling")),
    S("hospital room with afternoon light, {JIAH} sitting up in bed smiling, {JIHO} sitting beside her holding a paper bag of snacks",
      L("jiah", "Oppa, you're late again.", "teasing"),
      L("jiho", "Traffic. Monster traffic. Very rude monsters.", "joking"),
      L("jiah", "Liar.", "giggling")),
    S("close-up of a hospital IV drip and a medicine bottle with a very expensive price label on a bedside table, soft sad lighting",
      (N, "Ji-ah had Gate Fever. A sickness that came with the Gates. There was no cure. Only medicine. Very expensive medicine.")),
    S("close-up of a girl's small hand and a young man's hand making a pinky promise above a hospital blanket",
      L("jiah", "Promise you'll come home tonight.", "worried"),
      L("jiho", "I promise. I'm just the Sealer. I stand at the back. Nobody ever looks at the Sealer.", "gentle")),
    S("a huge glowing red portal gate in the middle of an evacuated Seoul plaza, police tape, {YEONAH} standing in front of a squad of armored hunters",
      (N, "Leading the raid was Seo Yeon-ah. S-rank. They called her the Frost Blade."),
      L("yeonah", "Sealer. Stay behind me. Don't touch anything.", "cold"),
      L("jiho", "Yes, ma'am.", "nervous")),
    S("inside a vast red crystal cavern dungeon, glowing red crystals, a squad of hunters walking carefully, {MINGYU} swinging his gauntlets casually",
      L("mingyu", "Easy raid. Easy money.", "cocky"),
      L("yeonah", "Quiet. Something's wrong. It's too quiet.", "tense whisper")),
    S("a swarm of glowing red crystal beetles the size of dogs pouring from the cavern walls, {YEONAH} unleashing a huge frost slash that freezes a wave of them",
      L("hunter", "Contact! Crystal beetles, dozens of them!", "shouting"),
      L("yeonah", "Formation! Shields forward, mages behind me!", "commanding"),
      L("mingyu", "Show-off.", "muttering")),
    S("{JIHO} pulling a wounded young hunter in light armor up from the cavern floor, putting the hunter's arm over his shoulder, {YEONAH} glancing back",
      L("hunter", "My leg! I can't feel my leg!", "panicked"),
      L("jiho", "Hold on. I've got you. Lean on me.", "steady"),
      L("yeonah", "Sealer. I told you to stay back.", "sharp"),
      L("jiho", "He was falling behind. Nobody gets left.", "firm"),
      L("yeonah", "Fine. Then keep him alive.", "after a pause")),
    S("a colossal stone golem forty meters tall rising from the red crystal cavern floor, a glowing red core in its chest, tiny hunters below",
      (N, "The boss of the Gate rose from the floor. A Stone Warden. Forty meters tall."),
      L("mingyu", "That's not a Red Gate boss. That's a calamity!", "panicking")),
    S("{YEONAH} slashing her katana against the giant stone golem's leg, ice shards exploding, but the stone is completely unharmed",
      L("yeonah", "My blade isn't even scratching it.", "shocked")),
    S("the giant stone golem sweeping its arm through a line of armored hunters who are thrown across the red crystal cavern, chaos, dust",
      L("hunter", "It's too strong! We can't hold it!", "terrified"),
      L("yeonah", "Fall back! Everyone to the exit! Now!", "commanding shout"),
      (N, "One by one, the strongest hunters in Korea were thrown aside like toys.")),
    S("{JIHO} pressing his hand against the swirling red exit portal of the cavern, which is shrinking and covered with dark chains",
      L("hunter", "The exit! The Gate's closing behind us!", "screaming"),
      L("jiho", "It's not closing. It's being locked. From the outside.", "stunned")),
    S("close-up of {JIHO} holding a radio earpiece, red light on his face, horrified expression",
      L("kwon", "Sealer. The boss is about to break into the city. Seal the Gate. Now.", "calm, cold"),
      L("jiho", "Director, there are twelve hunters still inside!", "desperate"),
      L("kwon", "Twelve hunters, or ten million citizens. Seal it.", "icy")),
    S("dramatic close-up of {JIHO}'s determined face, red light, sweat, gritted teeth",
      L("jiho", "No.", "firm"),
      L("kwon", "Then you can stay in there with them.", "pleasant, chilling")),
    S("the red exit portal sealing shut with black chains and a black keyhole symbol glowing on it, hunters screaming in the dark cavern",
      (N, "The Gate locked itself behind them. Someone had made the choice for him.")),
    S("{JIHO} dragging the wounded {YEONAH} behind a fallen crystal pillar, her armor cracked, blood on her lip, the stone golem looming",
      L("yeonah", "Why didn't you run?", "weak"),
      L("jiho", "Sealers stay until everyone's out. That's the only rule I've got.", "breathless")),
    S("the giant stone golem raising its huge fist above {JIHO} who shields {YEONAH} with his body, his hand touching a glowing red crystal shard on the ground",
      L("voice", "Keyholder. At last, you have come.", "ancient, echoing whisper")),
    S("a vast white void with an enormous golden floating keyhole in the center, {JIHO} standing small before it, golden particles",
      L("voice", "Every lock has a key. Every key has a holder. Open your eyes, Keyholder.", "solemn"),
      L("jiho", "Who are you?", "awed"),
      L("voice", "Look.", "commanding")),
    S("close-up of {JIHO_GOLD}, his eyes now glowing bright gold, golden keyhole symbols floating in the red cavern around him",
      (N, "Suddenly, he could see them. Keyholes. Glowing gold. On the walls. On the Gate. And on the monster itself.")),
    S("{JIHO_GOLD} leaping up the giant stone golem's arm toward a glowing golden keyhole on its chest core, dynamic action pose",
      L("jiho", "Unlock.", "intense")),
    S("the giant stone golem shattering into hundreds of falling stone pieces, golden light bursting from its chest, {JIHO} falling through the debris",
      (N, "The forty-meter Stone Warden came apart like a broken lock.")),
    S("{JIHO} walking out of the red portal carrying the unconscious {YEONAH} on his back, reporters and camera flashes outside, crowd cheering",
      L("mingyu", "The Frost Blade did it! She killed the boss! She saved us all!", "ecstatic"),
      (N, "Nobody looked at the Sealer. They never did.")),
    S("close-up of {YEONAH} on a stretcher half-conscious, looking at {JIHO} walking away in the crowd",
      L("yeonah", "It wasn't me, was it?", "faint whisper")),

    # ---- Act 2: the Keyholder ----
    S("{JIHO} sitting on the floor of a tiny cramped studio apartment at night, holding his brass key badge which glows gold, moonlight through the window",
      L("voice", "You have opened your first lock. One fragment of nine.", "quiet"),
      L("jiho", "Nine? Nine what?", "confused"),
      L("voice", "Find them. Before he does.", "warning"),
      L("jiho", "Before who? Hello?", "frustrated")),
    S("{JIHO} eating instant ramen in front of a small TV showing a news broadcast of {YEONAH} with a heroic headline graphic",
      L("anchor", "The Hwarang Guild's Red Gate raid ends in triumph, as S-rank hunter Seo Yeon-ah defeats a calamity-class boss single-handedly.", "news broadcast"),
      L("jiho", "Triumph. Sure.", "sarcastic")),
    S("{KWON} warmly gripping {JIHO}'s shoulder in a bright guild office, smiling kindly",
      L("kwon", "Ji-ho! Our brave Sealer. I'm so glad you survived. The radio failed in there, you know. A terrible accident.", "warm, concerned"),
      L("jiho", "The radio didn't fail. I heard every word.", "inner thought, quiet")),
    S("{KWON} sliding an envelope across a polished desk toward {JIHO}, city view behind",
      L("kwon", "I've paid your sister's hospital bills. All of them. Consider it a thank you.", "generous"),
      L("jiho", "You what?", "stunned"),
      L("kwon", "Just stay close to me, Ji-ho. I'd hate to lose you.", "soft, menacing")),
    S("extreme close-up of a gold ring engraved with a keyhole symbol on a man's hand resting on a desk, dramatic lighting",
      (N, "On the Director's finger was a gold ring. Engraved with a keyhole."),
      L("jiho", "That symbol...", "whisper")),
    S("{JIHO_GOLD} standing in front of a vending machine at night, a golden keyhole glowing on it, a can dropping out, comedic",
      L("jiho", "Unlock.", "testing"),
      (N, "Clunk."),
      L("jiho", "Okay. That's useful.", "amused")),
    S("{JIHO} in a small bathroom looking into a cracked mirror, a nosebleed running down his lip, his golden eyes fading back to dark",
      L("voice", "Every lock you open takes something from you. Open too many, and you will be the one who breaks.", "warning"),
      L("jiho", "Great. Fine print. Love it.", "sarcastic, wiping blood")),
    S("{JIHO_GOLD} fighting a pack of small goblin monsters inside a dark low-rank dungeon, golden keyholes glowing on each monster",
      L("jiho", "Unlock. Unlock. Unlock!", "focused"),
      (N, "Every night, he entered the Gates nobody wanted. Every night, he got a little faster.")),
    S("{JIHO_GOLD} raising his hand as a huge wolf monster freezes mid-leap, golden chains wrapping its claws",
      L("voice", "Two fragments of nine. Now learn the other half.", "approving"),
      L("jiho", "Lock.", "commanding"),
      L("jiho", "It can close things too.", "amazed")),
    S("rooftop of a Seoul building at night with city lights, {YEONAH} leaning on the railing waiting, {JIHO} arriving surprised",
      L("yeonah", "You've been entering E-rank Gates alone. At night. An F-rank Sealer.", "cool"),
      L("jiho", "Are you following me?", "defensive"),
      L("yeonah", "You saved my life. I like to know who I owe.", "matter-of-fact")),
    S("{YEONAH} and {JIHO} facing each other on the rooftop at night, wind blowing her white hair, tense",
      L("yeonah", "In the Gate, your eyes turned gold. And the Stone Warden fell apart. I saw it.", "steady"),
      L("jiho", "You were half unconscious.", "nervous laugh"),
      L("yeonah", "Half. Not all.", "dry")),
    S("{YEONAH} drawing her katana and pointing it at {JIHO}, frost mist, a small golden keyhole glowing on the buckle of her armor",
      L("yeonah", "Then show me. Find my weakness.", "challenging"),
      L("jiho", "Unlock.", "smirking"),
      (N, "Her armor's buckle clicked open. Her sword arm dropped.")),
    S("{YEONAH} with a rare small smile, sheathing her sword, city lights behind her",
      L("yeonah", "Impressive. And extremely annoying.", "dry, amused")),
    S("{YEONAH} looking out over the Seoul night skyline from the rooftop, wind in her white hair, sad expression, {JIHO} beside her",
      L("yeonah", "Five years ago, my brother walked into a Hwarang Gate. A simple C-rank. It locked. They called it an accident.", "quiet"),
      L("jiho", "You never believed them.", "gentle"),
      L("yeonah", "I became S-rank so I could find out the truth. I think I'm looking at it.", "steely")),
    S("{YEONAH} sparring with {JIHO} on a moonlit rooftop, her wooden practice sword at his throat, {JIHO} sweating and smiling",
      L("yeonah", "You can see every weakness in the world, and you still leave your left side open.", "unimpressed"),
      L("jiho", "I was letting you win.", "out of breath"),
      L("yeonah", "Again.", "stern"),
      L("jiho", "Can we at least take a water break?", "pleading"),
      L("yeonah", "Monsters don't take water breaks. Again.", "dry")),
    S("{YEONAH} and {JIHO} sitting on the rooftop ledge looking at a map of Seoul covered with gate markers on a tablet",
      L("yeonah", "Gates don't lock themselves. Someone locked ours. From the outside. With a key.", "serious"),
      L("jiho", "Director Kwon wears a ring with a keyhole on it.", "quiet"),
      (N, "Neither of them said anything for a long time.")),
    S("a dark guild archive vault at night lit by a flashlight, {JIHO_GOLD} opening a heavy steel door with a golden keyhole glowing on it, {YEONAH} keeping watch",
      L("jiho", "Unlock.", "whisper"),
      L("yeonah", "Ten years of Gate records. Quickly.", "urgent whisper")),
    S("{JIHO} and {YEONAH} reading stacks of files by flashlight in the archive, red ACCIDENT stamps on the pages",
      L("jiho", "Gate locked. Hunters lost. Accident. Gate locked. Accident. Accident. Accident.", "growing horror"),
      L("yeonah", "Seo Joon-ho. My brother. Gate locked by order of the Director.", "barely holding together"),
      L("jiho", "Yeon-ah...", "soft"),
      L("yeonah", "Don't. Not now. We finish this first.", "trembling, resolute")),
    S("bright hospital room, {JIAH} pointing excitedly at {YEONAH} who stands stiffly by the door, {JIHO} looking embarrassed",
      L("jiah", "Oppa! Is she your girlfriend?", "excited"),
      L("jiho", "No!", "flustered"),
      L("yeonah", "Absolutely not.", "flat"),
      L("jiah", "You both said that really fast.", "giggling")),
    S("{YEONAH} kneeling by the hospital bed placing a small glowing snowflake crystal charm in {JIAH}'s hands, soft warm light",
      L("yeonah", "For luck. It never melts.", "softer than usual"),
      L("jiah", "It's so pretty! Thank you, unni!", "delighted")),
    S("hospital corridor, a worried doctor in a white coat talking to {JIHO}",
      L("doctor", "Her fever spiked the night the Red Gate opened. It happens every time a big Gate opens.", "grave"),
      L("jiho", "Every time?", "alarmed"),
      L("doctor", "It's as if the Gates are feeding on her.", "uneasy")),
    S("{JIAH} in her hospital bed at night, eyes half open, a faint red glow from the window, {JIHO} holding her hand",
      L("jiah", "Oppa. I dreamed of a giant door. Somebody was knocking on it. From the other side.", "sleepy, scared")),

    # ---- Act 3: the black lock ----
    S("guild training gym, {MINGYU} slamming his gauntlet into a wall beside {JIHO}'s head, aggressive",
      L("mingyu", "Nobody walks out of a locked Gate. Nobody. Except you. So what are you, janitor?", "aggressive"),
      L("jiho", "Lucky.", "calm"),
      L("mingyu", "I'm going to find out.", "threatening")),
    S("{MINGYU} standing before {KWON}'s desk in a dark luxury office, {KWON} smiling",
      L("mingyu", "Director, the Sealer's hiding something. Let me take him into a Gate and prove it.", "eager"),
      L("kwon", "What a wonderful idea. Take Gate D-7. I'll handle the paperwork.", "delighted")),
    S("{KWON} alone in his dark office, his gold keyhole ring glowing black, a black keyhole symbol appearing over a gate on a holographic city map",
      L("kwon", "Two problems. One Gate.", "cold whisper")),
    S("{JIHO} and {MINGYU} entering a dim forest dungeon through a small portal, the portal behind them sealing with a black keyhole",
      L("mingyu", "Just you and me, janitor. Show me what you've got.", "cocky"),
      L("jiho", "Min-gyu. The Gate just locked. And this lock isn't gold. It's black.", "alarmed")),
    S("huge mutated black wolves with glowing red eyes surging out of a dark forest dungeon, {MINGYU} punching one with his gauntlet",
      L("mingyu", "This is a D-rank Gate? These are A-rank monsters!", "shouting")),
    S("{MINGYU} wounded and sitting against a tree, his gauntlet cracked, {JIHO} kneeling beside him",
      L("mingyu", "The Director sent me in here. He locked it on me too?", "shocked, hurt"),
      L("jiho", "Welcome to the club.", "grim")),
    S("{MINGYU} and {JIHO} sitting against a tree in the dark dungeon forest, a small fire between them, {MINGYU} looking at the flames",
      L("mingyu", "You know why I hate Sealers? My dad was one. Twenty years closing Gates for rich guilds. Died in one. Nobody even came to the funeral.", "bitter, quiet"),
      L("jiho", "So you became the guy who laughs at Sealers.", "gentle"),
      L("mingyu", "Yeah. Stupid, right?", "rueful"),
      L("jiho", "A little.", "small smile")),
    S("{JIHO_GOLD} touching a black keyhole floating in the air which sparks and burns his hand",
      L("jiho", "Unlock! Why won't it open?", "straining"),
      L("voice", "That lock was not made by you. To open it, you must take its key.", "urgent"),
      L("jiho", "Whose key?", "gasping"),
      L("voice", "The one who made it. It is inside the beast.", "grave")),
    S("a giant black alpha wolf with a black keyhole glowing in its chest lunging at {JIHO_GOLD}, golden chains wrapping its jaws",
      L("jiho", "Lock!", "shouting"),
      L("jiho", "And unlock.", "intense")),
    S("the black alpha wolf dissolving into black smoke, a small black key shard falling into {JIHO}'s hand, the exit portal opening with golden light",
      (N, "The beast came apart. And in Ji-ho's hand, a shard of black key.")),
    S("{JIHO} supporting the injured {MINGYU} with an arm over his shoulder, walking out of a portal into the dawn",
      L("mingyu", "You saved me. After everything I said to you.", "ashamed"),
      L("jiho", "You were annoying. Not evil. There's a difference.", "tired smile"),
      L("mingyu", "I owe you, janitor.", "gruff"),
      L("jiho", "Ji-ho.", "firm"),
      L("mingyu", "Ji-ho.", "grudging respect")),
    S("{MINGYU} talking on a phone in a hospital corridor with a bandaged arm, a cold expression, {JIHO} listening from around a corner",
      L("kwon", "Min-gyu. You're alive. How wonderful. And our Sealer?", "sweet"),
      L("mingyu", "He didn't make it, Director. The wolves got him.", "lying, steady"),
      L("kwon", "What a tragedy. Come and see me tomorrow.", "pleased")),
    S("close-up of a black key shard glowing in {JIHO}'s open palm",
      L("voice", "Three fragments of nine. And now he knows you exist.", "ominous")),
    S("{KWON} in his dark office, his gold ring cracked down the middle, his gentle smile gone, cold furious eyes behind gold glasses",
      L("kwon", "So. There is another Keyholder.", "cold, dangerous")),
    S("a luxurious rooftop restaurant at night, {KWON} pouring wine at a candlelit table, {JIHO} sitting stiffly across from him",
      L("kwon", "Sit, Ji-ho. Eat. You look thin.", "fatherly"),
      L("kwon", "Two Keyholders, working together. Every Gate in the world would answer to us. Money. Power. A cure for your sister.", "persuasive")),
    S("close-up of {KWON} smiling over a wine glass, his cracked keyhole ring visible, {JIHO} gripping the table edge",
      L("jiho", "And the hunters you locked inside?", "controlled anger"),
      L("kwon", "Sacrifices. Every great door needs its keys.", "calm"),
      L("jiho", "No.", "firm"),
      L("kwon", "Think about it. Hospitals can be such dangerous places.", "gentle, threatening")),
    S("a closed noodle restaurant at night, {JIHO}, {YEONAH} and {MINGYU} sitting at a small table with bowls, serious faces",
      L("mingyu", "He's been locking Gates for years. Letting the monsters inside grow. Bigger monster, bigger core. And cores sell for billions.", "angry"),
      L("yeonah", "And the hunters who asked questions never came back.", "quiet")),
    S("{JIHO} staring at his hands at the noodle restaurant table, steam rising, realization on his face",
      L("jiho", "My sister's fever spikes every time one of his locked Gates grows. He's not just killing hunters. He's feeding something.", "horrified")),
    S("{YEONAH} placing a thick folder of archive files on the noodle restaurant table, {MINGYU} and {JIHO} leaning in",
      L("yeonah", "We take the archive records to the Hunter Association. Tomorrow morning.", "decisive"),
      L("mingyu", "And if the Director finds out first?", "uneasy"),
      L("jiho", "Then we'd better hope he doesn't.", "grim")),
    S("a vision of two figures in ancient robes, an old master and a young student, standing before a colossal door made of black stone, golden light",
      L("voice", "There were two Keyholders once. A teacher, and his student. The student wanted to open every door. Even the one that must stay closed.", "sorrowful")),
    S("{JIHO} in the noodle restaurant, eyes glowing gold, whispering, the others staring at him",
      L("jiho", "The Great Gate.", "whisper"),
      L("voice", "Beneath Seoul. And the student's name was Kwon.", "grave")),
    S("giant billboard screens across Seoul at night all showing {KWON} smiling, crowds looking up",
      L("kwon", "Citizens of Seoul. Tonight, the Hwarang Guild opens the door to a new era.", "grand, smiling")),
    S("an enormous black and gold portal gate tearing open in the sky above the entire Seoul skyline, lightning, cars stopped, people screaming",
      (N, "Above Seoul, the largest Gate ever recorded began to open. And this time, it was opening on purpose.")),

    # ---- Act 4: the Great Gate ----
    S("hospital room in chaos, red light, a nurse checking monitors, {JIAH} gasping in bed",
      L("nurse", "Her fever's off the charts!", "panicked"),
      L("jiah", "Oppa. The door is opening.", "faint")),
    S("close-up of {JIHO}'s hand and {JIAH}'s small hand in a pinky promise again, red light from the window",
      L("jiho", "Hold on, Ji-ah. I'm going to close it. I promise.", "determined, tender")),
    S("{JIHO}, {YEONAH} and {MINGYU} standing side by side in a ruined street, facing the colossal black and gold Gate above Seoul, wind and debris",
      L("mingyu", "So the plan is, the F-rank janitor walks into the biggest Gate in history.", "nervous laugh"),
      L("jiho", "Sealer.", "dry"),
      L("yeonah", "And the S-rank and the B-rank keep him alive.", "resolute"),
      L("mingyu", "Great plan. Love it. We're all going to die.", "sarcastic")),
    S("inside the Great Gate, a colossal cathedral of black stone shaped like a giant keyhole, golden chains everywhere, {KWON} standing at the center with glowing black and gold eyes",
      L("kwon", "Ji-ho. My little Sealer. You should have stayed at the back.", "amused")),
    S("{YEONAH} pulling a broken silver sword out of a mass of black chains in the dark cathedral, her hands shaking",
      L("yeonah", "This is Joon-ho's sword.", "breaking"),
      L("kwon", "Your brother asked too many questions too. He made an excellent key.", "pleasant"),
      L("yeonah", "I'm going to end you.", "cold fury")),
    S("{KWON} spreading his arms before an enormous sealed door covered in chains behind him",
      L("kwon", "Do you know what's behind this door? Power. The core of every Gate that has ever opened.", "ecstatic"),
      L("jiho", "And my sister? And every hunter you locked away?", "furious"),
      L("kwon", "Keys for the door. Nothing more.", "dismissive")),
    S("{KWON} looking up at the giant chained door with a strange longing, black and gold light on his face",
      L("kwon", "My teacher gave me one fragment and told me to guard this door. Forever. Alone, in the dark.", "bitter"),
      L("kwon", "So I decided I would rather open it.", "quiet, certain"),
      L("jiho", "He trusted you.", "angry"),
      L("kwon", "He trusted a lock. I am not a lock.", "cold")),
    S("{YEONAH} slicing through swarms of black chain monsters with frost blasts while {MINGYU} smashes through them with his gauntlets, epic battle",
      L("yeonah", "Go, Ji-ho! We've got these!", "shouting"),
      L("mingyu", "Go! Before I change my mind!", "shouting")),
    S("{MINGYU} catching a giant black armored knight's sword with both gauntlets, sparks flying, teeth gritted",
      L("mingyu", "My dad closed Gates for twenty years! You think I'm scared of you?", "roaring"),
      L("mingyu", "Okay, a little scared! But mostly angry!", "straining")),
    S("{KWON} pointing his ringed hand at {JIHO_GOLD}, black chains wrapping and freezing {JIHO} mid-air",
      L("kwon", "Lock.", "cold"),
      L("kwon", "Did you really think you were the only one?", "mocking")),
    S("close-up of {JIHO} frozen in black chains, a black keyhole glowing on his chest, straining",
      L("voice", "A Keyholder cannot unlock himself. He must be opened by another.", "urgent")),
    S("{YEONAH} leaping and slashing her frost katana through the black keyhole on {JIHO}'s chest, ice and gold light exploding",
      L("yeonah", "Then I'll be your key!", "fierce shout")),
    S("{JIHO} inside a dark dream space surrounded by black chains, a small glowing vision of {JIAH} holding the snowflake charm reaching toward him",
      L("jiah", "Oppa. You promised. You always come home.", "echoing, gentle"),
      L("jiho", "I know. I'm coming.", "determined")),
    S("{JIHO_GOLD} landing free from shattered black chains, golden light all around him, facing {KWON}",
      L("kwon", "Impossible!", "shocked"),
      L("jiho", "You taught your student to open every door. You forgot why some doors stay closed.", "steady, powerful")),
    S("{JIHO_GOLD} grabbing {KWON}'s hand, a golden keyhole glowing on the gold ring",
      L("jiho", "Unlock.", "final")),
    S("the gold keyhole ring shattering into pieces, black energy draining out of {KWON} who falls to his knees screaming",
      L("kwon", "No. No! My key!", "anguished scream")),
    S("the enormous sealed door behind the cathedral cracking open, a gigantic glowing eye staring through the gap, tiny figures below",
      (N, "But it was too late. Behind the door, something enormous opened its eye.")),
    S("{JIHO_GOLD} standing before the cracking door, golden light, looking back over his shoulder at {YEONAH} and {MINGYU}",
      L("voice", "To seal the Great Gate, someone must lock it from the inside.", "solemn"),
      L("mingyu", "No. No way. We're not leaving you!", "desperate"),
      L("jiho", "Sealers stay until everyone's out. That's the rule.", "gentle smile")),
    S("{JIHO} pushing {YEONAH} and {MINGYU} through a closing golden portal, {YEONAH} reaching back for him",
      L("yeonah", "Ji-ho!", "screaming")),
    S("{JIHO_GOLD} alone, both hands pressed against a colossal golden keyhole on the giant door, blinding golden light",
      L("jiho", "Lock.", "whisper, final"),
      (N, "And for the first time in ten years, the biggest door in the world closed.")),
    S("the Seoul skyline at dawn, the giant gate in the sky gone, clouds parting, golden sunlight",
      (N, "The sky over Seoul cleared. The Gate was gone.")),
    S("{YEONAH} and {MINGYU} sitting in the rubble at dawn, staring at the empty sky",
      L("mingyu", "He's not coming out, is he?", "broken"),
      L("yeonah", "He's coming out. He promised his sister.", "certain")),
    S("a small golden keyhole appearing in the empty air at dawn, {JIHO} stumbling out of it with a burnt jacket and a tired grin",
      L("jiho", "Did somebody call a Sealer?", "exhausted grin")),
    S("{YEONAH} punching {JIHO}'s arm while smiling with tears, {MINGYU} crying and laughing beside them, dawn light",
      L("mingyu", "Don't scare me like that, janitor!", "crying, laughing"),
      L("jiho", "Ji-ho.", "laughing"),
      L("yeonah", "Idiot.", "tearful smile")),
    S("bright hospital room with morning sun, {JIAH} sitting up healthy and beaming, {JIHO} with bandages hugging her",
      L("jiah", "Oppa! The knocking stopped!", "overjoyed"),
      L("jiho", "Told you. I'm the guy who closes doors.", "warm")),
    S("{JIAH} and {YEONAH} sitting together on the hospital bed laughing, {YEONAH} braiding {JIAH}'s hair, the snowflake charm glowing on the bedside table",
      L("jiah", "Unni, will you teach me to use a sword?", "eager"),
      L("yeonah", "When you're older. And when your brother learns to guard his left side.", "amused"),
      L("jiho", "I heard that!", "from the doorway")),
    S("{KWON} in handcuffs being led away by hunter association officers, cameras flashing, his glasses cracked",
      L("anchor", "Hwarang Guild Director Kwon has been arrested on charges of illegal Gate manipulation.", "news broadcast"),
      L("kwon", "You think it's over? There are still five fragments out there. And others are looking for them.", "unsettling laugh")),
    S("Hunter Association evaluation hall, {JIHO} with his hand on the crystal orb which blazes with blinding golden light, the official's jaw dropped, hunters staring",
      L("official", "Yoon Ji-ho. Re-evaluation result... unmeasurable?", "stammering"),
      L("jiho", "Could you check one more time? Maybe the machine's broken.", "deadpan")),
    S("{JIHO}, {YEONAH} and {MINGYU} standing in front of a tiny old shop front with an empty sign, morning sun, a small brass key hanging above the door",
      L("mingyu", "Every guild in Korea wants you now. So what are you going to do?", "curious"),
      L("jiho", "Start my own. Small. Three people. We close the doors nobody else will.", "content"),
      L("yeonah", "Does it have a name?", "interested"),
      L("jiho", "The Keyholders.", "proud"),
      L("mingyu", "Cheesy.", "grinning"),
      L("yeonah", "I like it.", "smiling")),
    S("{JIHO} on a rooftop at night, his brass key badge glowing gold, across the city several small portals flicker with black keyholes",
      L("voice", "Four fragments of nine, Keyholder. There are other doors.", "ominous whisper")),
    S("{JIHO_GOLD} looking at the camera with a confident smile, wind in his hair, golden keyholes floating around him, city lights",
      (N, "The weakest hunter in Korea had closed the greatest Gate in history. But somewhere out there, other doors were waiting."),
      (N, "Who do you think holds the other keys? Tell me in the comments. And like and subscribe for more stories like this.")),
]

spec = {
    "title": "KEYHOLDER: The F-Rank Sealer Who Can Unlock Anything",
    "series": "Standalone manhwa-style story (original)",
    "character": "", "style": "",
    "width": 1920, "height": 1080, "title_card": False,
    "tts": "kokoro", "cast": KOKORO, "speed": 0.95, "scene_pad": 0.8,
    "clips_dir": "audio",
    "caption_speakers": list(NAMES),
    "caption": {"max_chars": 46, "max_words": 8, "size": 0.046, "margin": 0.05},
    "images": {"provider": "pollinations"},
    "music": {"sound": "music_strategy", "volume": 0.10},
    "sources": ["Original story and characters. Artwork generated with AI (Pollinations, FLUX.2 klein)."],
    "scenes": [{**sc, "fx": sc.get("fx", [])} for sc in scenes],
}
clip = 0
for sc in spec["scenes"]:
    sc["image"] = sc["image"].replace("{", "(").replace("}", ")")  # make_video formats prompts; keep them brace-free
    for line in sc["lines"]:  # number every line: its Speechma recording is audio/clip-NNN.mp3
        clip += 1
        if len(line) < 3:
            line.append({})
        line[2]["clip"] = clip

(HERE / "script.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")

# The same script, clip by clip, for recording in Speechma.
out = ["# KEYHOLDER: voice script for Speechma", "",
       "Make one audio file per clip and name it exactly as shown (e.g. `clip-001.mp3`; .wav or .m4a also work). "
       "The words in brackets are acting notes: pick a voice and speed that fit, but don't type them into Speechma.", "",
       "Send the files back in any batch size: every clip you send replaces its placeholder voice in the video, "
       "the rest keep the placeholder until you record them.", "", "## Voices", ""]
out += [f"- **{NAMES[k]}**: {v}" for k, v in SPEECHMA_VOICES.items()]
n = 0
for i, sc in enumerate(spec["scenes"], 1):
    out += ["", f"## Scene {i}", ""]
    for line in sc["lines"]:
        n += 1
        tone = f" *({line[2]['tone']})*" if line[2].get("tone") else ""
        out.append(f"- `clip-{n:03d}` **{NAMES[line[0]]}**{tone}: {line[1]}")
(HERE / "SPEECHMA.md").write_text("\n".join(out) + "\n")

lines = [l for sc in spec["scenes"] for l in sc["lines"]]
words = sum(len(l[1].split()) for l in lines)
nw = sum(len(l[1].split()) for l in lines if l[0] == N)
print(f"{len(spec['scenes'])} scenes, {len(lines)} lines ({n} clips), {words} words ({nw} narrator)")
