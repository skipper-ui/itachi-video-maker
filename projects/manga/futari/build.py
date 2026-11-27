"""Builds script.json for FUTARI, a standalone ~15-minute "manga dub" story video (16:9), part 1.

Run: python3 projects/manga/futari/build.py
Original story and characters (story idea by the channel owner): Ren sees his girlfriend Hikari at the mall holding
another man's arm on the day she said she was visiting her parents. Too scared to ask, he disappears to his grandmother's
orange orchard on an island. Six months later she finds him, and there are two of her: Hikari and Akari are identical
twins who both fell for him and took turns dating him. The misunderstanding is cleared up, but Ren's hurt is not, and the
twins set out to win him back. Part 1 ends there.
In the flashback, each line of "the girlfriend" is voiced by the twin who was really there, as a hidden clue.
Same format as HOSHIZORA: one illustrated panel per beat, Ren narrating in first person in a white box at the top, the
other characters speaking in white boxes near the bottom, every line acted with ElevenLabs v3.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = "narrator"

TWIN_FACE = ("a 25-year-old Japanese woman with long straight chestnut-brown hair, big warm amber eyes and a soft "
             "round face")
# Fixed character descriptions, repeated in every prompt; the key before "_" names the reference portrait used.
# All three TWIN entries share one portrait, so the twins have exactly the same face.
C = {
    "REN": "Ren (a 26-year-old Japanese man with short neat dark brown hair, gentle tired eyes and a slim build, "
           "wearing a white shirt under a navy cardigan)",
    "REN_FARM": "Ren (a 26-year-old Japanese man with short neat dark brown hair, gentle tired eyes and a slim build, "
                "lightly tanned, wearing a plain white t-shirt, khaki work trousers and a towel around his neck)",
    "TWIN": f"his girlfriend ({TWIN_FACE}, her hair worn down with a small yellow sunflower hairpin, "
            "wearing a cream knit sweater and a long beige pleated skirt)",
    "TWIN_AKARI": f"Akari ({TWIN_FACE}, her hair tied up in a high ponytail, a bright confident grin, "
                  "wearing a yellow t-shirt and denim overalls)",
    "TWIN_HIKARI": f"Hikari ({TWIN_FACE}, her hair worn down with a small yellow sunflower hairpin, a shy gentle smile, "
                   "wearing a white blouse and a light blue cardigan)",
    "KAITO": "Kaito (a tall 27-year-old Japanese man with wavy black hair and a friendly grin, wearing a black leather jacket)",
    "DAISUKE": "Daisuke (a 26-year-old Japanese office worker with spiky orange-dyed hair and an expressive face, "
               "wearing a white shirt with a loosened tie)",
    "GRANDMA": "Grandma Fumi (a tiny 78-year-old Japanese grandmother with white hair in a bun and a big toothy smile, "
               "wearing a purple apron over a flowered blouse)",
    "HOST": "Hana (a cute cheerful anime girl, a young woman with long pastel pink hair in twin tails tied with red ribbons, "
            "big sparkling violet eyes and rosy cheeks, wearing a pastel pink hoodie with little cat ears on the hood)",
}
REFS = {k: k.split("_")[0].lower() for k in C}
STYLE = ("modern Japanese anime illustration, manga dub video style, clean thin black line art, flat cel shading, "
         "soft muted colors, detailed simple background, 2D anime, 16:9 widescreen composition, "
         "no text, no letters, no speech bubbles, no watermark")
PORTRAIT = "character reference portrait, waist-up front view of {who}, neutral expression, plain white background, " + STYLE

CAST = {
    "narrator": "TX3LPaxmHKxFdv7VOQHJ",   # Liam: Ren telling his own story
    "ren": "TX3LPaxmHKxFdv7VOQHJ",        # Liam
    "hikari": "EXAVITQu4vr4xnSDxMaL",     # Sarah: soft and shy
    "akari": "cgSgspJ2msm6clMCkdW9",      # Jessica: bright and bubbly
    "kaito": "bIHbv24MWmeRgasZH58o",      # Will
    "daisuke": "IKne3meq5aSn9XLyUdCD",    # Charlie
    "grandma": "vFLqXa8bgbofGarf6fZh",    # Grandma Oxley (ElevenLabs voice library)
    "host": "vGQNBgLaiM3EdZtxIiuY",       # Aerisita (ElevenLabs voice library): the outro host
}
# Local placeholder voices (Kokoro), used only if ElevenLabs can't voice a line.
KOKORO = {"narrator": "am_michael", "ren": "am_michael", "hikari": "af_sky", "akari": "af_nicole", "kaito": "am_puck",
          "daisuke": "am_echo", "grandma": "bf_emma", "host": "af_sky"}


def L(who, text, tone=None):
    return [who, text, {"tone": tone}] if tone else [who, text]


def S(image, *lines, pos=None, buttons=None, sfx=None):
    """One panel. pos="ren:l,hikari:r" puts those speakers' boxes on that side (default: bottom centre)."""
    lines = [l if isinstance(l, list) else L(*l) for l in lines]  # (who, text, tone) tuples -> the same form as L()
    sc = {"image": image.format(**C) + ", " + STYLE, "lines": [list(l) for l in lines],
          "refs": sorted({REFS[k] for k in re.findall(r"\{(\w+)\}", image)})}
    if pos:
        sc["pos"] = dict(p.split(":") for p in pos.split(","))
    if buttons:
        sc["buttons"] = buttons
    if sfx:
        sc["sfx"] = sfx
    return sc


MALL = "inside a bright modern shopping mall atrium in Tokyo on a Saturday afternoon, crowds of shoppers"
BOOKS = "inside a cozy cluttered secondhand bookstore with tall wooden shelves, rain on the windows, warm light"
ORCHARD = "in a sunny mikan orchard (rows of green citrus trees with dark green leaves and small round orange fruits) on a hillside above a sparkling blue sea, Japanese island countryside, summer"
HOUSE = "inside an old wooden Japanese farmhouse with tatami mats and open sliding doors, summer"
PORCH = "on the wooden porch of an old Japanese farmhouse overlooking an orange orchard and the sea, summer"
TWINS = "identical twin sisters with exactly the same face"
scenes = [
    # ---- Cold open: the lie ----
    S("{REN} standing alone on a dark train platform at night with a suitcase, looking down sadly, city lights behind",
      (N, "Three years. That's how long I loved her.", "quiet"),
      (N, "And on the day I found out she was lying to me... I didn't ask her a single question. I just ran.", "bitter, quiet")),
    S("{REN} smiling hopefully with his phone to his ear in his small sunny Tokyo apartment, two movie tickets on the table",
      (N, "It started on a Saturday morning. Two movie tickets, and a girlfriend I wanted to surprise.", "warm"),
      L("ren", "Hey, Hikari! Are you free this afternoon? There's a three o'clock showing of that movie you wanted to see!", "cheerful, hopeful")),
    S("{TWIN} talking on the phone in a cozy family living room, smiling apologetically",
      L("hikari", "Ah, sorry, Ren! I'm visiting my parents today. Let's go next week, okay?", "apologetic, sweet"),
      L("ren", "Oh. Sure. Say hi to them for me.", "a little disappointed")),
    S("{REN} walking alone through a bright shopping mall holding two movie tickets, a little lonely, " + MALL,
      (N, "So I went to the mall alone. I thought I'd at least buy her birthday present early.", "wry")),
    S("view from far across a crowded mall atrium: {TWIN} laughing happily and holding the arm of {KAITO} as they walk "
      "into a jewelry shop together, " + MALL,
      (N, "And that's when I saw her.", "stunned, quiet"),
      (N, "Same long hair. The same sunflower hairpin I gave her. Laughing... and holding another man's arm.", "shocked, hollow")),
    S("close-up of {REN} frozen in shock in the mall, two movie tickets slipping from his fingers, " + MALL,
      (N, "She was supposed to be at her parents' house. Two hours away.", "numb")),
    S("close-up of a smartphone screen in a man's hand showing a short chat with a smiling emoji and a photo of a strawberry cake",
      (N, "I sent her one message. Where are you right now?", "tense"),
      (N, "She replied a minute later. At my parents'! Mom made cake. Miss you!", "hollow, bitter")),
    S("{REN} sitting alone on a park bench at night with his head in his hands under a streetlight",
      (N, "She lied. Easily. With a smiley face.", "hurt"),
      (N, "And suddenly, a hundred little things I'd ignored came back to me.", "slow, realizing")),
    S("a small boy standing alone at the door of an empty apartment holding a teddy bear, watching a woman with a suitcase walk away, faded memory",
      (N, "When I was eight, my mom left with a suitcase and a smile. She said she'd be back on Sunday.", "quiet, distant"),
      (N, "She never came back. I waited at the door every Sunday for a year.", "quiet, hurt")),
    S("{TWIN} sitting at a cafe table looking at two cups of coffee, one black and one with a pile of sugar cubes beside it",
      (N, "Some days she drank her coffee black. Other days, with four sugars.", "thoughtful"),
      (N, "Some days she remembered every word I'd ever said. Other days she forgot what we did last weekend, and just laughed it off.", "uneasy")),
    S("{DAISUKE} leaning over {REN}'s desk in a busy Tokyo office, worried, both in office clothes",
      L("daisuke", "Dude, just ask her! Maybe there's an explanation!", "worried, pushy"),
      L("ren", "And if there isn't? If I ask her... and she says it's true?", "quiet, scared"), pos="daisuke:l,ren:r"),
    S("close-up of {REN} in a dark apartment at night lit only by his phone screen, a tear on his cheek",
      (N, "I couldn't do it. Hearing it from her would make it real.", "shaky"),
      (N, "So I did the most cowardly thing I've ever done. I sent one message. Let's end this. Thank you for everything.", "ashamed, quiet")),
    S("{REN} walking away from an apartment building with a suitcase in the grey early morning, not looking back",
      (N, "Then I blocked her number, quit my job, and left Tokyo without telling anyone where I was going.", "flat")),
    S("{TWIN} sitting on the floor of a dark room staring at her phone in shock, tears streaming down her face",
      L("hikari", "Ren...? Why? What did I do?", "heartbroken, trembling")),

    # ---- Flashback: how we met ----
    S("a cozy secondhand bookstore on a narrow street in Shimokitazawa on a rainy afternoon, umbrellas outside, warm light in the windows",
      (N, "We met three years ago, in a little secondhand bookstore, on a rainy afternoon.", "soft, nostalgic")),
    S("{REN} and {TWIN} reaching for the same old photography book on a shelf at the same moment, their hands touching, "
      "both surprised, " + BOOKS,
      L("hikari", "Oh! S-sorry! You take it!", "flustered, shy"),
      L("ren", "No, no. You found it first.", "gentle, smiling"), pos="ren:l,hikari:r"),
    S("close-up of {TWIN} blushing and hugging an old photography book to her chest, smiling shyly, " + BOOKS,
      L("hikari", "Then... maybe we could share it? Over coffee? Next Sunday?", "shy, hopeful"),
      (N, "Her name was Hikari. She talked about old photographs like they were treasure.", "fond")),
    S("{REN} sitting alone at a cafe table checking his watch, rain on the window, two untouched glasses of water",
      (N, "That Sunday, I waited at the cafe for twenty minutes. I was sure she wasn't coming.", "wry")),
    S("{TWIN} bursting in through a cafe door out of breath and laughing, waving energetically, rain behind her",
      L("akari", "Sorry, sorry! I'm here! The train was a total disaster!", "bubbly, breathless")),
    S("{TWIN} laughing loudly at a cafe table with three empty cake plates in front of her, {REN} laughing with her",
      (N, "She was nothing like the shy girl from the bookstore. She was loud and funny, and she ate three slices of cake.", "amused"),
      (N, "I thought she'd just been nervous the first time. I never thought about it again.", "fond")),
    S("{REN} and {TWIN} standing in front of a huge glowing blue aquarium tank full of fish, seen from the side, both faces with normal warm skin tones, her eyes quiet and amazed",
      L("hikari", "Ren, look... it's like they're flying.", "soft, amazed")),
    S("{REN} lying sick in bed with a cold and a towel on his forehead while {TWIN} sits beside him gently feeding him rice porridge with a spoon",
      L("hikari", "Say ah. It's my grandmother's recipe. Ginger and a little egg.", "gentle, caring"),
      (N, "When I caught a cold, she nursed me all day without saying a word about it.", "warm")),
    S("{TWIN} bursting into a small bedroom the next morning holding a bag full of energy drinks, singing loudly, {REN} in bed covering his ears",
      L("akari", "Good morning, patient! I brought twelve energy drinks and my best singing voice!", "loud, cheerful"),
      (N, "The next morning, she came back and sang to me until my fever gave up out of fear.", "amused")),
    S("{REN} and {TWIN} sharing one small umbrella in the rain on a quiet street, her shoulder getting wet, both smiling",
      L("hikari", "I only brought one umbrella. On purpose.", "shy, teasing"),
      (N, "She always forgot her umbrella. Or... half the time she did.", "fond")),
    S("{REN} and {TWIN} in summer yukata at a fireworks festival, she points at the sky and cheers with her mouth wide open, "
      "fireworks bursting overhead",
      L("akari", "Tamaya! Come on, Ren, shout with me! Tamayaaa!", "excited, loud")),
    S("{TWIN} proudly holding out a plate with a burnt lumpy omelet in a small apartment kitchen, {REN} smiling bravely",
      L("akari", "Ta-da! My famous omelet! ...It's a little crispy.", "proud, sheepish"),
      (N, "One week she made me a burnt omelet. The next week, a perfect one. Soft and golden. She said she'd been practicing.", "fond, amused")),
    S("{REN} and {TWIN} on a bridge over a river at sunset, she holds his sleeve and looks up at him seriously with red cheeks",
      (N, "Three months later, on a bridge at sunset...", "soft"),
      L("hikari", "Ren... I like you. I really, really like you. Will you go out with me?", "shy, trembling, sincere")),
    S("close-up of {REN} blushing with a stunned happy smile, sunset behind him",
      L("ren", "...I was going to say that. Yes. Of course, yes.", "overjoyed, shy")),
    S("{REN} gently clipping a small yellow sunflower hairpin into {TWIN}'s hair under cherry blossoms in a park, she smiles with teary eyes",
      (N, "On our first anniversary, I gave her a sunflower hairpin. Because she was like sunshine.", "warm"),
      (N, "Some days bright and loud. Some days soft and warm. She wore it every single day.", "warm")),
    S("{REN} and {TWIN} sitting close together on a small apartment balcony at night sharing earphones, city lights below",
      (N, "She never let me meet her family. She said it was complicated, and I didn't push.", "thoughtful"),
      (N, "For three years, I was the happiest I'd ever been.", "fond, then sad")),
    S("close-up of a tiny metal hair clip decorated with a small yellow sunflower ornament (a hair accessory, not a real flower) lying alone on an empty table in a dark room, moonlight",
      (N, "Which is why, when I thought I'd lost her... I couldn't stay in the same city.", "sad, quiet")),

    # ---- Present: the island ----
    S("wide view of a mikan orchard (rows of green citrus trees with dark green leaves and small round orange fruits) on a hillside above a sparkling blue sea, a small old wooden farmhouse, "
      "small islands on the horizon, bright summer day",
      (N, "Six months later. A little island in Ehime, on the Seto Inland Sea.", "calm"),
      (N, "My grandmother's orange orchard.", "calm")),
    S("{REN_FARM} carrying a basket full of oranges between the trees, sweating, calm face, " + ORCHARD,
      (N, "I picked oranges, fixed fences, and went to bed at nine. Nobody here knew me. It was quiet.", "calm, tired")),
    S("{GRANDMA} cheerfully waving a towel from the porch at {REN_FARM} in the orchard below, " + PORCH,
      L("grandma", "Ren! Lunch! And smile a little, will you? You'll scare the oranges!", "cheerful, teasing"),
      L("ren", "The oranges are fine, Grandma.", "dry, amused"), pos="grandma:l,ren:r"),
    S("{GRANDMA} and {REN_FARM} eating rice balls and drinking tea side by side, " + PORCH,
      L("grandma", "Six months, and you still haven't told me why you ran away from Tokyo.", "gentle, prying"),
      L("ren", "I didn't run away. I just... left.", "defensive, quiet"), pos="grandma:l,ren:r"),
    S("close-up of {GRANDMA} looking sideways with a knowing little smile, holding a teacup, " + PORCH,
      L("grandma", "Mm-hm. Only two things make a young man leave the city like that. Debt, or a girl.", "knowing"),
      L("grandma", "And you've got no debt.", "playful, sly")),
    S("a narrow coastal road along the sea with a small country bus driving away in the summer heat haze, "
      "a lone figure with a big suitcase standing at the bus stop",
      (N, "Then one afternoon in August, the bus from the port stopped at the bottom of our hill.", "calm, ominous")),
    S("{TWIN_AKARI} standing at the wooden orchard gate with a big suitcase, sweaty and out of breath, tears in her eyes, " + ORCHARD,
      L("akari", "I found you... I finally found you!", "breathless, emotional")),
    S("close-up of {REN_FARM} frozen in shock, a basket tipping over and oranges rolling on the ground, " + ORCHARD,
      L("ren", "Hikari...? How did you...", "shocked, whispering")),
    S("close-up of {TWIN_AKARI} wiping her tears with a serious, guilty and determined face, " + ORCHARD,
      L("akari", "I'm not Hikari.", "serious, emotional"),
      L("akari", "My name is Akari.", "firm")),
    S("close-up of {REN_FARM} confused with furrowed eyebrows, " + ORCHARD,
      L("ren", "What...? What kind of joke is this—", "confused, getting angry")),
    S("{TWIN_HIKARI} running up a dusty country road holding a sun hat, out of breath, calling out, the sea behind her",
      L("hikari", "Akari! You can't just run ahead like that!", "breathless, worried")),
    S("{TWIN_AKARI} and {TWIN_HIKARI} standing side by side at the wooden orchard gate, " + TWINS + ", one with a ponytail and "
      "one with her hair down, both looking nervously at the viewer, " + ORCHARD,
      (N, "There were two of them.", "stunned"),
      (N, "Same face. Same eyes. Same voice... almost.", "stunned, slow")),
    S("{REN_FARM} sitting down hard on the ground among spilled oranges with his mouth hanging open, comedic shock, " + ORCHARD,
      L("ren", "There's... two of you.", "dazed")),
    S("{GRANDMA} peeking out from behind a sliding door of the farmhouse with wide delighted eyes and a hand over her mouth",
      L("grandma", "Oh my. Ren... you never told me there were two of them!", "delighted, scandalized")),

    # ---- The truth ----
    S("{TWIN_AKARI} and {TWIN_HIKARI} kneeling formally side by side on the tatami with their heads bowed, {REN_FARM} sitting "
      "across from them with his arms crossed, glasses of barley tea untouched between them, tense, " + HOUSE,
      (N, "Ten minutes later, the three of us sat in Grandma's living room. Nobody touched the tea.", "tense"),
      L("hikari", "We're identical twins. Hikari and Akari Shirakawa.", "quiet, nervous")),
    S("close-up of {TWIN_HIKARI} looking down shyly with her hands on her knees, " + HOUSE,
      L("hikari", "The girl you met at the bookstore was me. But on the day of our coffee date, I had a high fever.", "shy, guilty")),
    S("close-up of {TWIN_AKARI} scratching her cheek with a guilty grin, " + HOUSE,
      L("akari", "She was crying so much about standing you up... so I went instead. As Hikari. Just to explain.", "guilty, sheepish"),
      L("akari", "But you were so easy to talk to. I forgot to explain. And then I... kind of fell for you too.", "embarrassed, honest")),
    S("close-up of {TWIN_HIKARI} gripping her cardigan with teary eyes, " + HOUSE,
      L("hikari", "And I'd already fallen for you at the bookstore. Neither of us could give you up. And neither of us wanted to hurt the other.", "teary, sincere")),
    S("close-up of {REN_FARM} with a stunned pale face, " + HOUSE,
      L("ren", "So you... took turns?", "stunned, slow"),
      L("akari", "...We took turns.", "small, guilty")),
    S("close-up of {REN_FARM} alone, the only person in the picture, glancing sideways at someone off-screen, troubled, " + HOUSE,
      L("ren", "The bridge. The day someone told me they liked me. Which one of you was that?", "quiet, shaky"),
      L("hikari", "Me. But Akari wrote half of what I said. We practiced it all night.", "soft, honest")),
    S("close-up of two hands that look exactly the same passing a small yellow sunflower hairpin from one to the other at a "
      "train station ticket gate",
      L("hikari", "We traded your hairpin at the station every time we switched.", "quiet"),
      L("akari", "Every time we tried to tell you, we got scared you'd leave.", "sad")),
    S("close-up of {REN_FARM} with a bitter, hurt smile, " + HOUSE,
      L("ren", "And then I left anyway.", "bitter")),
    S("{REN_FARM} standing up angrily with clenched fists, " + HOUSE,
      L("ren", "Then who was at the mall? Holding that man's arm? On the day you said you were at your parents'?", "angry, hurt")),
    S("{TWIN_AKARI} waving both hands in panic with wide eyes, " + HOUSE,
      L("akari", "That was me! And that was our cousin Kaito! From Osaka!", "panicked")),
    S("{TWIN_AKARI} kneeling on the tatami and holding her smartphone out toward the viewer with both hands, an eager grin; the phone screen faces the viewer and shows a small photo of {KAITO} smiling inside a watch shop, the photo stays inside the phone screen, " + HOUSE,
      L("akari", "Hikari really was at our parents'. I was buying your birthday present with Kaito. He's the only one in the family with good taste.", "flustered, rushing")),
    S("close-up of {TWIN_AKARI} holding out a small open gift box with a silver wristwatch inside, eyes teary, " + HOUSE,
      L("akari", "This was for your birthday. We've carried it around for six months.", "teary")),
    S("close-up of a silver wristwatch lying face down on a tatami mat, a short engraving on its back",
      (N, "On the back, there was an engraving. To Ren. From both of us.", "quiet"),
      (N, "Back then, I would've thought it meant from her and me.", "quiet, bitter")),
    S("{REN_FARM} sitting cross-legged on the tatami running a hand through his hair, with {TWIN_AKARI} and {TWIN_HIKARI} kneeling beside him watching him anxiously, " + HOUSE,
      L("ren", "How did you even find me? I didn't tell anyone.", "tired"),
      L("akari", "Daisuke. We bought him lunch every day for a month until he cracked.", "sheepish")),
    S("{DAISUKE} eating a huge bowl of ramen alone in a Tokyo ramen shop, looking guilty, sweating",
      (N, "Daisuke. Of course.", "dry")),
    S("{TWIN_AKARI} running through a crowded Tokyo street at night holding up a phone with a photo of a man, asking strangers, exhausted",
      L("akari", "I went to every place you ever took us. Every station. Every cafe. For months.", "tired, emotional")),
    S("{TWIN_HIKARI} sitting at a desk at night writing a letter by lamplight, a pile of sealed letters beside her, a tear falling on the paper",
      L("hikari", "And I wrote you a letter every night. One hundred and eighty-two letters. I didn't know where to send them.", "soft, trembling")),
    S("close-up of {REN_FARM} looking away with a pained face, his jaw tight, " + HOUSE,
      (N, "I didn't know what to say. So I said nothing.", "quiet")),

    # ---- The hurt doesn't go away ----
    S("{REN_FARM} sitting alone on the porch at night looking out at the dark sea, his back to the viewer, moonlight",
      (N, "So she never cheated on me. She never even lied about her parents.", "quiet"),
      (N, "The misunderstanding was gone. But the pain wasn't.", "heavy")),
    S("close-up of {REN_FARM} gazing at the moonlit sea with sad, tired eyes",
      (N, "For six months, I woke up every morning believing the person I loved most had thrown me away.", "raw"),
      (N, "You can't switch that off just because someone tells you it was a mistake.", "quiet, firm")),
    S("{GRANDMA} sitting down beside {REN_FARM} on the moonlit porch with two cups of tea, gentle smile",
      L("grandma", "You know, I almost didn't marry your grandfather.", "gentle"),
      L("ren", "...Why not?", "quiet"), pos="grandma:l,ren:r"),
    S("an old faded photograph of a young Japanese couple standing in front of an orange orchard in the 1960s, sepia tones",
      L("grandma", "Because I was scared. Scared that if I loved him, one day he'd leave. So I tried to leave first.", "soft, nostalgic"),
      L("grandma", "He followed me all the way to the port. Fifty-two years, and he never let me forget it.", "fond, laughing softly")),
    S("close-up of {GRANDMA} patting {REN_FARM}'s hand, moonlight",
      L("grandma", "Running away doesn't protect your heart, Ren. It just makes it lonely.", "wise, kind")),
    S("{TWIN_HIKARI} on the left and {TWIN_AKARI} on the right, standing side by side on a farmhouse porch at night under the moon, both looking at the viewer, hesitant",
      L("hikari", "Ren... can you ever forgive us?", "quiet, hopeful")),
    S("{REN_FARM} looking back over his shoulder with a tired, serious face, on a farmhouse porch at night, a round full moon in a clear night sky",
      L("ren", "I don't know. I don't even know who I fell in love with.", "tired, honest"),
      L("ren", "Go home. Please. The first bus leaves at seven.", "firm, tired")),
    S("{TWIN_AKARI} and {TWIN_HIKARI} asleep sitting up on the farmhouse porch at dawn, leaning against each other under one blanket, their suitcases beside them",
      (N, "I didn't sleep that night. At dawn, I found them on the porch. They'd waited outside all night.", "soft, surprised"),
      (N, "Leaning on each other. Just like they must have done for the last six months.", "soft")),

    # ---- They don't go home ----
    S("{REN_FARM} stepping out of the farmhouse at sunrise mid-yawn, freezing at the sight of {TWIN_AKARI} in a straw hat "
      "holding a basket full of oranges and grinning, " + ORCHARD,
      L("akari", "Morning, Ren! Your grandma hired me! Room and board, and all the oranges I can eat!", "bright, cheeky")),
    S("close-up of {REN_FARM} with a twitching eye in total disbelief, " + ORCHARD,
      L("ren", "Grandma!", "exasperated, shouting")),
    S("{GRANDMA} sipping tea innocently and looking away, " + PORCH,
      L("grandma", "What? We need help with the harvest. She works hard. And she's cute.", "innocent, sly")),
    S("{TWIN_HIKARI} standing in front of a tiny old wooden village library next to a bus stop, holding a stack of books, smiling shyly",
      (N, "And Hikari? She got a job at the tiny village library.", "dry"),
      (N, "Open three days a week. Right next to the bus stop I used every day.", "dry, amused")),
    S("{TWIN_HIKARI} smiling and waving shyly at {REN_FARM} through a library window, morning sun",
      L("hikari", "Good morning, Ren. I saved you the newspaper.", "shy, sweet"),
      L("ren", "...Morning.", "awkward"), pos="hikari:l,ren:r"),
    S("{TWIN_AKARI} proudly holding out an open bento box with a slightly burnt omelet in it to {REN_FARM} under the trees at noon, " + ORCHARD,
      L("akari", "Lunch! I made it myself! The omelet's only a little crispy this time!", "proud")),
    S("close-up of {REN_FARM} holding up a piece of slightly burnt omelet with chopsticks, a strange nostalgic expression, " + ORCHARD,
      (N, "I took a bite. It was the same omelet from three years ago.", "quiet, nostalgic"),
      L("ren", "...So the burnt omelet was you.", "realizing"),
      L("akari", "It's crispy! There's a difference!", "pouting")),
    S("{TWIN_AKARI} pouting with puffed cheeks while {REN_FARM} tries hard not to smile, " + ORCHARD,
      L("ren", "And the perfect one?", "curious"),
      L("akari", "Hikari's. She's better at everything. It's so annoying.", "grumbling, fond"), pos="ren:l,akari:r"),
    S("{TWIN_HIKARI} and {REN_FARM} sitting on a seawall at sunset with a small gap between them, an old photography book open on her lap",
      (N, "In the evenings, Hikari sat on the seawall with the same photography book from the bookstore.", "soft"),
      L("hikari", "Page forty-two. You said this photo looked lonely. I always thought it looked like someone waiting.", "soft")),
    S("close-up of {REN_FARM} looking at {TWIN_HIKARI} in surprise, warm sunset light on the sea",
      (N, "I'd said that three years ago. Once. I'd forgotten it myself.", "surprised, soft"),
      (N, "So the one who remembered everything... was her.", "realizing")),
    S("{TWIN_AKARI} and {TWIN_HIKARI} tugging a basket of oranges back and forth between them, {REN_FARM} sighing between them, " + ORCHARD,
      L("akari", "I'm carrying it! I'm stronger!", "competitive"),
      L("hikari", "You dropped twelve oranges yesterday.", "calm, deadpan"), pos="akari:l,hikari:r"),
    S("{GRANDMA} laughing on the porch and fanning herself while watching the orchard, " + PORCH,
      L("grandma", "Hohoho! This orchard hasn't been this lively in forty years!", "delighted")),
    S("{GRANDMA} leaning close to {REN_FARM} on the porch with a sly grin, whispering behind her hand, evening, " + PORCH,
      L("grandma", "So? Which one do you like better?", "sly, whispering"),
      L("ren", "Grandma! It's not like that!", "flustered"), pos="grandma:l,ren:r"),
    S("{TWIN_AKARI} slipping and falling backwards off a wooden ladder in the orchard, {REN_FARM} rushing to catch her, oranges flying, " + ORCHARD,
      L("akari", "Whoa, whoa, whoa!", "panicked")),
    S("{REN_FARM} holding {TWIN_AKARI} in his arms after catching her, both frozen and blushing, faces close, " + ORCHARD,
      L("akari", "...Hi.", "breathless, embarrassed"),
      L("ren", "You're heavier than you look.", "deadpan, flustered"), pos="akari:l,ren:r"),
    S("{TWIN_AKARI} hitting {REN_FARM}'s chest with both fists, red-faced and furious, while he laughs for the first time, " + ORCHARD,
      L("akari", "Ren! You can't say that to a girl!", "outraged, embarrassed"),
      (N, "I laughed. For the first time in six months, I really laughed.", "surprised, warm")),
    S("{TWIN_HIKARI} standing under the roof of a small country bus stop in sudden heavy rain, no umbrella, looking up at the sky",
      (N, "A few days later, it rained. And there she was at the bus stop, without an umbrella.", "soft")),
    S("{REN_FARM} holding a small umbrella over {TWIN_HIKARI} at the rainy bus stop, she looks up at him in surprise",
      L("ren", "You forgot your umbrella again.", "gentle"),
      L("hikari", "...I didn't forget it.", "shy, soft"), pos="ren:l,hikari:r"),
    S("{REN_FARM} lying awake on a futon under a mosquito net at night, staring at the ceiling, moonlight through the sliding door",
      (N, "Every day, I learned something new. The girl I'd loved for three years wasn't a lie.", "thoughtful"),
      (N, "She was two people. And somehow, that made it harder to stay angry.", "wry, soft")),
    S("{DAISUKE} talking on the phone in a messy Tokyo apartment at night, rubbing the back of his head guiltily",
      L("daisuke", "Ren, I'm sorry I told them. But man... they cried in that ramen shop every single day.", "guilty, sincere"),
      L("daisuke", "Whatever they did, those two really love you. Both of them. That's the weird part.", "honest, awkward")),
    S("close-up of {REN_FARM} on the porch at night holding two old crumpled movie tickets from his wallet, thoughtful",
      (N, "In my wallet, I still had those two movie tickets. I'd never thrown them away.", "soft"),
      (N, "Maybe a part of me had never stopped waiting either.", "soft, realizing")),

    # ---- The festival: their declaration ----
    S("a small seaside village summer festival at night, paper lanterns and food stalls along the harbor, warm glowing light",
      (N, "On the night of the island's summer festival, they found me by the sea.", "soft")),
    S("{TWIN_AKARI} in a summer yukata triumphantly holding up a bag with a goldfish at a goldfish scooping stall, festival lanterns",
      L("akari", "Ha! Five goldfish! Ren, I'm naming them all after you!", "triumphant, loud")),
    S("{TWIN_HIKARI} in a summer yukata shyly holding out a red candy apple to {REN_FARM} in a yukata at a festival stall, lanterns glowing",
      L("hikari", "You always bought the candy apple. Every festival. I remember.", "shy, warm"),
      (N, "Loud and bright. Quiet and warm. The two halves of the person I'd loved.", "warm, thoughtful")),
    S("{TWIN_AKARI} and {TWIN_HIKARI} in summer yukata standing side by side on a moonlit beach, " + TWINS + ", festival lanterns "
      "glowing behind them, serious determined faces",
      L("hikari", "Ren. We're not asking you to forgive us tonight.", "calm, determined"),
      L("akari", "And we're done lying. No more switching. No more hiding.", "firm"), pos="akari:l,hikari:r"),
    S("close-up of {TWIN_AKARI} in a summer yukata grinning confidently with one fist raised, moonlit beach",
      L("akari", "So this time, we're going to make you fall in love again. Honestly. As ourselves.", "confident, bright")),
    S("close-up of {TWIN_HIKARI} in a summer yukata blushing but looking straight ahead bravely, moonlit beach",
      L("hikari", "And this time... you get to choose.", "shy, brave")),
    S("close-up of {REN_FARM} in a summer yukata flustered and wide-eyed with a light pink blush on his cheeks, sweating a little, the first fireworks bursting in the sky behind him",
      L("ren", "Choose?! Wait, wait. I never said I—", "flustered")),
    S("fireworks exploding over the sea, {TWIN_AKARI} and {TWIN_HIKARI} in yukata each hugging one of {REN_FARM}'s arms on the beach, "
      "all three seen from behind against the fireworks",
      L("akari", "Ready or not!", "playful, loud"),
      L("hikari", "Here we come.", "soft, playful"), pos="akari:l,hikari:r"),
    S("{TWIN_AKARI} and {TWIN_HIKARI} in yukata shaking hands firmly and grinning at each other like rivals before a match, sparks between their eyes, beach at night, comedic",
      L("akari", "And Hikari? I'm not losing to you this time.", "competitive, playful"),
      L("hikari", "Neither am I.", "calm, competitive"), pos="akari:l,hikari:r"),
    S("{REN_FARM} in a summer yukata smiling helplessly with a red face, fireworks behind him",
      (N, "I came to this island for a quiet life. To forget.", "wry"),
      (N, "Looks like that's over.", "amused, warm"), pos="narrator:b"),
    S("{TWIN_AKARI} and {TWIN_HIKARI} in yukata smiling at the viewer side by side, " + TWINS + ", fireworks and lanterns behind them",
      (N, "Hikari, or Akari? Who do you think I'll fall for? Tell me in the comments.", "warm, inviting"), pos="narrator:b"),

    # ---- Outro: the channel's host girl ----
    S("{HOST} waving happily at the viewer with both hands and a big smile, sparkles and little pink hearts floating around her, "
      "bright pastel pink and lavender background with soft bokeh lights, upper body",
      L("host", "Thanks for watching~!", "cheerful, cute, sing-song"),
      L("host", "If Ren's story made your heart race, please like, subscribe, and tap the bell, so you never miss the next one!", "bubbly, excited"),
      pos="host:t", buttons=[
          {"text": "LIKE", "line": 1, "delay": 1.4, "x": 0.27, "y": 0.84, "fill": "#3EA6FF"},
          {"text": "SUBSCRIBE", "line": 1, "delay": 1.9, "x": 0.53, "y": 0.84, "press": 1.6, "pressed": "SUBSCRIBED"},
          {"icon": "bell", "line": 1, "delay": 2.9, "x": 0.76, "y": 0.84}],
      sfx=[{"sound": "pop", "at": "line:1+1.4", "volume": 0.5}, {"sound": "pop", "at": "line:1+1.9", "volume": 0.5},
           {"sound": "tap", "at": "line:1+3.5", "volume": 0.6}, {"sound": "ding", "at": "line:1+2.9", "volume": 0.45}]),
    S("{HOST} winking playfully and making a heart shape with both hands, floating hearts and sparkles, "
      "bright pastel pink background with soft bokeh lights, upper body",
      L("host", "Oh! And if you want Part 2, where the twins make their move, comment FUTARI down below!", "playful, excited, winking"),
      L("host", "See you in the next story! Bye-bye!", "sweet, cheerful"),
      pos="host:t", buttons=[{"text": 'COMMENT "FUTARI" FOR PART 2!', "line": 0, "delay": 2.6, "x": 0.5, "y": 0.84,
                              "fill": "#FFD43B", "ink": "#141414"}],
      sfx=[{"sound": "pop", "at": "line:0+2.6", "volume": 0.5}, {"sound": "chime", "at": "line:1", "volume": 0.35}]),
]

spec = {
    "title": "My Girlfriend Lied to Me, So I Disappeared... Then TWO of Her Showed Up | Manga Dub",
    "character": "", "style": "",
    "width": 1920, "height": 1080, "title_card": False,
    "tts": "kokoro", "cast": KOKORO, "speed": 0.95, "scene_pad": 0.7,
    "emotive": {"engine": "eleven_v3", "cast": CAST, "skip": [], "fallback": True,
                "priority": ["narrator", "ren", "hikari", "akari", "grandma", "daisuke", "kaito"]},
    "caption": {"mode": "boxes", "font": "Comic Neue", "fonts_dir": "assets/fonts",
                # dialogue in oval bubbles: blue words for male speakers, pink for female ones
                "bubbles": {"male": ["ren", "kaito", "daisuke"], "female": ["hikari", "akari", "grandma", "host"]}},
    "images": {"provider": "local", "upscale": True},
    "characters": {REFS[k]: PORTRAIT.format(who=C[k]) for k in C if "_" not in k},
    "music": {"sound": "music_dream", "volume": 0.03},
    "sources": ["Original story and characters. Artwork drawn with AI (FLUX.2 klein, run locally)."],
    "scenes": [{"fx": [], **sc} for sc in scenes],
}
for sc in spec["scenes"]:
    sc["image"] = sc["image"].replace("{", "(").replace("}", ")")  # make_video formats prompts; keep them brace-free
for k in spec["characters"]:
    spec["characters"][k] = spec["characters"][k].replace("{", "(").replace("}", ")")

(HERE / "script.json").write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
lines = [l for sc in spec["scenes"] for l in sc["lines"]]
words = sum(len(l[1].split()) for l in lines)
chars = sum(len(l[1]) + (len(l[2]["tone"]) + 3 if len(l) > 2 else 0) for l in lines)
print(f"{len(spec['scenes'])} scenes, {len(lines)} lines, {words} words (~{words / 150:.1f} min of speech), "
      f"~{chars} ElevenLabs characters")
