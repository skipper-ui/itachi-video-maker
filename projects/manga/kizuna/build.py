"""Builds script.json for KIZUNA, a ~27-minute "manga dub" story video (16:9), episode 1.

Run: python3 projects/manga/kizuna/build.py
Original story and characters (story idea by the channel owner): when their parents die, 18-year-old Haruto quits school
and works three part-time jobs to raise his 6-year-old sister Mio. Her smile is enough to wash away every hard day.
Sixteen years later Mio lands her dream job at a company's new headquarters in New York. A charming, cunning executive,
Kaname Saijo, talks her into going, and promises her that her brother will be looked after; every month she sends money
home through him. Years pass, the company becomes the biggest in the world, and Mio, buried in work, stops calling.
When she finally does, her brother's number is dead. She flies home: he left their apartment a year ago because he
couldn't pay the rent. Saijo tells her Haruto gambled all her money away, and in her anger she lets him go. A year later,
a boy carrying his little sister in a park sends her to a private investigator, who finds the truth: not one yen ever
reached Haruto. An accident left him with a limp he couldn't afford to fix, and he lived alone on what he could earn.
Mio races to his last address, but he disappeared days before. Episode 1 ends there.
Same format as FUTARI: one illustrated panel per beat, adult Mio narrating in first person in a white box at the top,
the other characters in oval speech bubbles (blue for male speakers, pink for female ones), every line acted with
ElevenLabs v3.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = "narrator"

HARUTO_FACE = "a Japanese man with short messy black hair, kind gentle dark eyes and a lean build"
# Fixed character descriptions, repeated in every prompt; the key before "_" names the reference portrait used.
C = {
    "HARUTO": f"Haruto (18 years old, {HARUTO_FACE}, wearing a black high school gakuran uniform)",
    "HARUTO_WORK": f"Haruto ({HARUTO_FACE}, wearing a worn navy work jacket over a gray hoodie)",
    "HARUTO_HOME": f"Haruto ({HARUTO_FACE}, wearing a plain gray t-shirt and a faded blue apron)",
    "HARUTO_SUIT": f"Haruto ({HARUTO_FACE}, wearing a slightly too-big old black suit and a white shirt)",
    "HARUTO_OLD": (f"Haruto (36 years old, {HARUTO_FACE}, thinner, with light stubble and tired eyes, wearing a faded "
                   "gray hoodie and old work trousers, leaning on a wooden cane)"),
    "MIOCHILD": ("little Mio (a 6-year-old Japanese girl with short black hair in two small pigtails, a small yellow star "
                 "hair clip, big round dark eyes, wearing a yellow dress)"),
    "MIOTEEN": ("Mio (a 15-year-old Japanese girl with shoulder-length straight black hair, a small yellow star hair clip, "
                "big dark eyes, wearing a navy sailor school uniform)"),
    "MIO": ("Mio (a 22-year-old Japanese woman with long straight black hair, a small yellow star hair clip, big dark "
            "eyes and a bright smile, wearing a white blouse and a beige cardigan)"),
    "MIO_EXEC": ("Mio (a 27-year-old Japanese woman with long black hair in a low ponytail, a small yellow star hair "
                 "clip, sharp confident dark eyes, wearing a tailored charcoal-gray business suit)"),
    "SAIJO": ("Kaname Saijo (a handsome 36-year-old Japanese businessman with slicked-back black hair, thin "
              "silver-rimmed glasses, a charming smile and cold narrow eyes, wearing an expensive navy three-piece suit)"),
    "KIRISHIMA": ("Ms. Kirishima (a sharp 45-year-old Japanese woman private investigator with a short black bob "
                  "haircut and calm serious eyes, wearing a beige trench coat over a black turtleneck)"),
    "TANAKA": ("Mrs. Tanaka (a small kind 75-year-old Japanese landlady with gray curly hair and round glasses, "
               "wearing a green cardigan)"),
    "GONDO": ("Mr. Gondo (a gruff 65-year-old Japanese ramen shop owner with a shaved head, thick gray eyebrows and a "
              "white towel tied around his head, wearing a white cook's jacket)"),
    "MORI": ("Mr. Mori (a 50-year-old Japanese high school teacher with neat gray hair and glasses, wearing a brown "
             "suit)"),
    "AUNT": ("Aunt Yoko (a 50-year-old Japanese woman with permed brown hair and a stern face, wearing a black "
             "mourning dress)"),
    "HOST": "Hana (a cute cheerful anime girl, a young woman with long pastel pink hair in twin tails tied with red ribbons, "
            "big sparkling violet eyes and rosy cheeks, wearing a pastel pink hoodie with little cat ears on the hood)",
}
REFS = {k: k.split("_")[0].lower() for k in C}
STYLE = ("modern Japanese anime illustration, manga dub video style, clean thin black line art, flat cel shading, "
         "soft muted colors, detailed simple background, 2D anime, 16:9 widescreen composition, "
         "no text, no letters, no speech bubbles, no watermark")
PORTRAIT = "character reference portrait, waist-up front view of {who}, neutral expression, plain white background, " + STYLE

CAST = {
    "narrator": "XrExE9yKIg1WjnnlVkGX",   # Matilda: grown-up Mio telling the story
    "mio": "XrExE9yKIg1WjnnlVkGX",        # Matilda
    "miochild": "cgSgspJ2msm6clMCkdW9",   # Jessica, acted small and young: Mio as a little girl
    "haruto": "iP95p4xoKVk53GoZ742B",     # Chris
    "saijo": "N2lVS1w4EtoT3dr4eOWO",      # Callum
    "kirishima": "Xb7hH8MSUJpSbSDYk0k2",  # Alice
    "tanaka": "vFLqXa8bgbofGarf6fZh",     # Grandma Oxley (ElevenLabs voice library)
    "gondo": "pqHfZKP75CvOlQylNhV4",      # Bill
    "mori": "JBFqnCBsd6RMkjVDRZzb",       # George
    "aunt": "FGY2WhTYpPnrIDTdsKH5",       # Laura
    "kid": "cgSgspJ2msm6clMCkdW9",        # Jessica: the boy in the park
    "host": "vGQNBgLaiM3EdZtxIiuY",       # Aerisita (ElevenLabs voice library): the outro host
}
MALE = ["haruto", "saijo", "gondo", "mori", "kid"]
FEMALE = ["mio", "miochild", "kirishima", "tanaka", "aunt", "host"]
# Local placeholder voices (Kokoro), used only if ElevenLabs can't voice a line.
KOKORO = {"narrator": "af_sarah", "mio": "af_sarah", "miochild": "af_sky", "haruto": "am_michael", "saijo": "bm_george",
          "kirishima": "bf_emma", "tanaka": "bf_emma", "gondo": "am_echo", "mori": "bm_lewis", "aunt": "af_nicole",
          "kid": "af_sky", "host": "af_sky"}


def L(who, text, tone=None):
    return [who, text, {"tone": tone}] if tone else [who, text]


def S(image, *lines, pos=None, buttons=None, sfx=None):
    """One panel. pos="haruto:l,mio:r" puts those speakers' bubbles on that side (default: bottom centre)."""
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


APT = "inside a tiny old one-room Japanese apartment with a tatami floor, a low wooden table and a small kitchen corner, warm lamp light"
APT_NIGHT = "inside a tiny old one-room Japanese apartment at night, tatami floor, a low wooden table, one dim lamp"
RAMEN = "inside a small old ramen shop with a wooden counter, steam and red paper lanterns, at night"
SCHOOL = "inside a Japanese high school classroom in the afternoon, sunlight through the windows"
OFFICE = "inside a bright modern Tokyo startup office with glass walls and laptops"
NY = "inside a sleek glass corner office high above New York City, the Manhattan skyline through floor-to-ceiling windows"
NY_NIGHT = "inside a sleek glass corner office high above New York City at night, the city lights through the windows"
OLD_STREET = "on a narrow old residential street in an old Tokyo neighborhood, small apartment buildings and power lines"
CAFE = "inside a quiet dim old coffee shop with wooden booths, rain on the window"

scenes = [
    # ---- Cold open ----
    S("{MIO_EXEC} standing frozen in the rain on a narrow old Tokyo street at night, holding a thick brown envelope, "
      "shocked and pale, her umbrella fallen at her feet",
      (N, "For five years, I sent my brother money. Every single month.", "quiet, shaken"),
      (N, "And tonight I found out that not one yen of it ever reached him.", "breaking")),
    S("close-up of {MIO_EXEC} in the rain at night, tears mixing with the rain on her face, eyes wide",
      (N, "While I was building a life on the other side of the world... he was alone. In pain. Waiting for a sister who never came.", "heavy, trembling")),
    S("an old faded family photo on a wooden shelf: a smiling Japanese couple in their 40s, an 18-year-old boy with "
      "messy black hair, and a little 6-year-old girl with pigtails on his shoulders, warm nostalgic light",
      (N, "My name is Mio Aoyama. And this is the story of my brother, Haruto.", "soft, steady"),
      (N, "The person who gave up everything... for me.", "soft")),

    # ---- The day everything changed ----
    S("{MIOCHILD} sitting on a tatami floor drawing with crayons while {HARUTO} does homework at a low table, both "
      "smiling, a cozy family living room in the evening",
      (N, "I was six years old. My brother was eighteen. Twelve years apart.", "warm, nostalgic"),
      (N, "Our parents used to joke that I was the surprise of their lives.", "warm, a little laugh")),
    S("a cozy family living room in the evening, rain on the window, a landline telephone ringing on a side table, "
      "a family photo next to it, ominous mood",
      (N, "That night, it was raining. Mom and Dad had gone to pick up a cake for my birthday.", "slowing down, quiet"),
      (N, "Then the phone rang.", "hushed")),
    S("{HARUTO} holding a landline phone to his ear, his face draining of color, eyes wide in shock, rain on the window behind him",
      L("haruto", "...Yes. This is their son. ...What? Which hospital?", "confused, then horrified")),
    S("{MIOCHILD} looking up from her drawing at her brother with a worried innocent face, a crayon in her hand",
      L("miochild", "Onii-chan? Who was that? Are Mom and Dad coming home soon?", "small, innocent, childlike voice")),
    S("{HARUTO} kneeling down and hugging {MIOCHILD} tightly, his face hidden in her shoulder, shaking, rain outside",
      L("haruto", "Mio... let's put on your coat, okay? We have to go somewhere.", "trying to keep his voice steady, failing")),
    S("a long empty hospital corridor at night with cold fluorescent lights and a row of plastic chairs, a small girl "
      "asleep across two chairs under a boy's school jacket",
      (N, "A truck had slid on the wet road. They were gone before the ambulance arrived.", "heavy, quiet"),
      (N, "I didn't understand. I fell asleep in that hallway, waiting for them to come out.", "small, sad")),
    S("{HARUTO} sitting alone on a hospital bench at night, elbows on his knees, staring at the floor with empty red eyes",
      (N, "My brother sat there all night. He didn't cry. Not in front of me.", "soft"),
      (N, "Years later, I learned he cried every night for a month. In the bathroom, with the water running, so I wouldn't hear.", "aching")),

    # ---- The funeral ----
    S("a quiet Japanese funeral hall with white chrysanthemums and two framed photos of a smiling couple, relatives in "
      "black clothes, incense smoke",
      (N, "At the funeral, relatives I'd never met filled the room.", "quiet")),
    S("{AUNT} and two other relatives in black clothes whispering in a corner of a funeral hall, cold faces",
      L("aunt", "We can't take her. We have our own children. And the boy is barely an adult.", "cold, low"),
      L("aunt", "There are facilities for children like her. It's the sensible thing.", "cold, matter-of-fact")),
    S("{MIOCHILD} hiding behind a pillar at a funeral hall, clutching a stuffed rabbit, tears in her eyes, overhearing",
      (N, "I didn't know what a facility was. But I knew it meant I'd be sent away.", "small, scared")),
    S("{HARUTO_SUIT} stepping between the relatives and a frightened little girl, his face firm and angry, funeral hall",
      L("haruto", "She's not going anywhere.", "firm, low")),
    S("close-up of {HARUTO_SUIT} with fierce determined eyes, facing the relatives",
      L("aunt", "Haruto, be realistic. You're eighteen. You're still in school. How will you feed her?", "sharp"),
      L("haruto", "I'll figure it out. She stays with me. She's my sister.", "steady, absolute")),
    S("{HARUTO_SUIT} kneeling and hugging {MIOCHILD}, who clings to his neck crying, white funeral flowers behind them",
      L("miochild", "Onii-chan, don't leave me... please don't leave me too...", "sobbing, childlike"),
      L("haruto", "Never. I'm right here, Mio. I'm not going anywhere. I promise.", "gentle, choked")),

    # ---- He quits school ----
    S("{MORI} sitting across a desk from {HARUTO} in an empty school staff room, an envelope of withdrawal papers on the desk",
      L("mori", "Haruto, you're top of your class. You have a university scholarship waiting for you.", "pleading, serious"),
      L("mori", "If you quit now, you're throwing your whole future away.", "earnest")),
    S("close-up of {HARUTO} smiling sadly at his teacher, sunlight from a window, staff room",
      L("haruto", "My future can wait, sensei. My sister's dinner can't.", "calm, sad smile")),
    S("{HARUTO} bowing deeply to {MORI} in a school hallway, the teacher looking heartbroken",
      L("haruto", "Thank you for everything.", "respectful, quiet"),
      (N, "He left school two months before graduation. He never got to wear his diploma.", "quiet, aching")),

    # ---- Three jobs ----
    S("{HARUTO_WORK} riding an old bicycle loaded with newspapers through a dark empty street at 4 a.m., his breath "
      "white in the cold, streetlights",
      (N, "From that day, my brother worked three jobs.", "steady"),
      (N, "Newspaper delivery at four in the morning.", "steady")),
    S("{HARUTO_WORK} carrying heavy cardboard boxes in a busy warehouse, sweating, wearing work gloves",
      (N, "A warehouse during the day.", "steady")),
    S("{HARUTO_HOME} washing a tall stack of bowls at the sink of a small ramen shop, steam rising, late at night, " + RAMEN,
      (N, "And dishes at a ramen shop until midnight.", "steady")),
    S("{GONDO} glaring at {HARUTO_HOME} across the counter of a ramen shop with his arms crossed, " + RAMEN,
      L("gondo", "You're the kid who keeps showing up at four a.m. with newspapers, aren't you? When do you sleep?", "gruff"),
      L("haruto", "On the train, sir. Fifteen minutes. It's enough.", "polite, tired smile")),
    S("{GONDO} sliding a big bowl of ramen across the counter to {HARUTO_HOME} with a gruff expression, " + RAMEN,
      L("gondo", "Eat. Then take this home for your sister. Don't argue with me.", "gruff, kind underneath"),
      L("haruto", "...Thank you, sir.", "moved, quiet")),

    # ---- Life together ----
    S("a tiny old one-room apartment with a tatami floor, two futons, a small low table and a children's drawing taped "
      "to the wall, warm evening light",
      (N, "We moved into a tiny apartment by the train tracks. One room. Two futons.", "warm"),
      (N, "To me, it was a palace.", "warm, smiling")),
    S("{HARUTO_HOME} clumsily trying to tie {MIOCHILD}'s hair into pigtails in the morning, both laughing, one pigtail "
      "much higher than the other, " + APT,
      L("miochild", "Onii-chan, they're crooked again!", "giggling, childlike"),
      L("haruto", "Crooked is the style now. All the cool girls have crooked pigtails.", "playful")),
    S("close-up of an open lunchbox with little octopus-shaped sausages, a rolled omelet and a smiling face made of "
      "seaweed on rice, on a small wooden table",
      (N, "He learned to cook from library books. Every day, my lunch had octopus sausages.", "warm"),
      (N, "His own lunch was usually rice and nothing else.", "softer")),
    S("{MIOCHILD} proudly showing her lunchbox to classmates at a little elementary school desk, other kids leaning in amazed",
      L("miochild", "My onii-chan made it! He's the best cook in the whole world!", "proud, childlike")),
    S("{HARUTO_WORK} running across an elementary school sports field in his dirty work clothes, waving, out of breath, "
      "parents and children watching, sunny sports day with flags",
      (N, "On sports day, every other kid had two parents cheering. I had my brother.", "warm"),
      (N, "He ran there straight from the warehouse. He was late, and covered in dust, and the loudest one there.", "laughing softly")),
    S("{MIOCHILD} running in a children's race with a huge smile while {HARUTO_WORK} cheers wildly behind the rope, "
      "sunny sports day",
      L("haruto", "Go, Mio! Go! That's my sister! That's my sister!", "shouting, overjoyed")),
    S("{MIOCHILD} asleep at a low table with her head on a picture book, while {HARUTO_HOME} gently covers her with a "
      "blanket, late at night, " + APT_NIGHT,
      (N, "Some nights he came home so tired that he fell asleep sitting up.", "soft"),
      (N, "But every night, before he slept, he checked on me.", "soft")),
    S("close-up of {HARUTO_HOME}'s rough cracked hands holding a small cup of tea under a dim lamp, bandages on two fingers",
      (N, "His hands were always cracked. In winter they bled.", "quiet"),
      (N, "When I asked, he'd say, it's nothing. Just dry skin.", "quiet")),
    S("{MIOCHILD} running into the apartment and hugging {HARUTO_WORK} around the waist as he comes home exhausted at "
      "night, he smiles down at her, " + APT_NIGHT,
      L("miochild", "Welcome home, onii-chan!", "bright, childlike")),
    S("close-up of {HARUTO_WORK} looking down with a tired but completely happy smile, warm lamp light",
      (N, "He told me once that no matter how bad the day was... when I smiled and said welcome home, it all washed away.", "tender"),
      L("haruto", "I'm home, Mio. ...Yeah. I'm home.", "warm, tired, happy")),

    # ---- The birthday ----
    S("{HARUTO_WORK} counting coins on the counter of a small bakery, a tiny strawberry shortcake in a box, the baker "
      "watching kindly",
      (N, "On my seventh birthday, he counted coins at the bakery for ten minutes.", "warm, sad")),
    S("{MIOCHILD} gasping with joy at a tiny strawberry shortcake with one candle on a low table, {HARUTO_HOME} grinning "
      "beside her, " + APT_NIGHT,
      L("haruto", "Happy birthday, Mio! Make a wish!", "warm, excited"),
      L("miochild", "Onii-chan, you eat the strawberry! You never eat cake!", "insistent, childlike")),
    S("{HARUTO_HOME} gently clipping a small yellow star hair clip into {MIOCHILD}'s hair, she beams, " + APT_NIGHT,
      L("haruto", "And this is from me. A star. Because you're my lucky star.", "gentle, a little shy"),
      (N, "It cost a hundred yen. I've worn it every day of my life.", "soft, emotional")),
    S("{MIOCHILD} handing her brother a crayon drawing of a boy in a red cape holding a little girl's hand, " + APT_NIGHT,
      L("miochild", "I made you a present too! It's you! You're a superhero!", "proud, childlike")),
    S("close-up of {HARUTO_HOME} holding a child's crayon drawing, tears running down his face, smiling",
      L("haruto", "...This is the best present I've ever gotten.", "crying, laughing"),
      (N, "That was the first time I saw my brother cry. He said it was the onions. There were no onions.", "fond, teary")),
    S("a child's crayon drawing taped to an old apartment wall: a boy in a red cape holding a little girl's hand, with "
      "a sun and hearts around them",
      (N, "He taped it to the wall. It stayed there for sixteen years.", "warm")),
    S("{HARUTO_WORK} walking {MIOCHILD} to the gate of an elementary school in spring, she wears a big red school "
      "backpack, cherry blossoms, other children with their parents",
      (N, "On my first day of school, every other child came with a mother or a father.", "soft"),
      L("miochild", "Onii-chan... the other kids all have moms.", "small, uncertain")),
    S("{HARUTO_WORK} crouching down to {MIOCHILD}'s eye level at a school gate, straightening her backpack straps with a big grin",
      L("haruto", "And you have me. That's way cooler. I can carry you on my back and I can make octopus sausages.", "playful, warm"),
      L("miochild", "...Yeah! That's way cooler!", "giggling, childlike")),
    S("{HARUTO_WORK} running through a dark rainy street at night carrying {MIOCHILD} wrapped in a blanket, her face "
      "flushed with fever, desperate",
      (N, "When I was eight, I got a terrible fever in the middle of the night.", "tense"),
      (N, "We had no car. No money for a taxi. So he ran. Two kilometers, in the rain, with me on his back.", "intense")),
    S("{HARUTO_WORK} soaking wet, sitting on a hospital chair beside a small bed where {MIOCHILD} sleeps, holding her "
      "small hand in both of his, night",
      L("haruto", "Please... she's all I have. Please let her be okay.", "whispering, praying")),
    S("{MIOCHILD} wobbling on a small old bicycle on a riverside path at sunset while {HARUTO_HOME} runs behind holding the seat",
      L("haruto", "Keep pedaling! I've got you! I won't let go!", "encouraging")),
    S("{MIOCHILD} riding a bicycle alone along a riverside path at sunset, laughing, while {HARUTO_HOME} stands far "
      "behind with his hands empty, smiling",
      L("miochild", "Onii-chan, I'm doing it! Don't let go!", "excited, childlike"),
      L("haruto", "I let go ages ago, Mio! That's all you!", "proud, laughing")),
    S("a tiny tabletop Christmas tree made of a branch with paper decorations on a low table in a small apartment, "
      "{MIOCHILD} opening a small wrapped present with joy, {HARUTO_HOME} watching, night",
      (N, "Our Christmas tree was a branch from the park, decorated with origami.", "warm, fond"),
      (N, "Every year he gave me a present. Every year he said Santa had dropped it off at the ramen shop.", "fond laugh")),
    S("{HARUTO_HOME} and {MIOCHILD} with their hands pressed together, praying in front of a family grave stone with "
      "flowers and incense, autumn",
      L("haruto", "Mom. Dad. Mio learned her times tables this year. She's smarter than me already.", "gentle, proud"),
      L("miochild", "And onii-chan burned the rice three times!", "teasing, childlike")),

    # ---- Hard times ----
    S("{HARUTO_HOME} sitting at the low table at night with a pile of bills and a calculator, his head in his hand, "
      "a single dim lamp, " + APT_NIGHT,
      (N, "Of course, it wasn't always warm.", "quiet"),
      (N, "Some months, the bills piled up faster than he could pay them.", "quiet")),
    S("{MIOCHILD} eating a bowl of rice and miso soup at the low table while {HARUTO_HOME} sits across from her with "
      "nothing, smiling, " + APT_NIGHT,
      L("miochild", "Onii-chan, aren't you eating?", "curious, childlike"),
      L("haruto", "I already ate at work. I'm so full. Eat up.", "light, casual lie")),
    S("close-up of {HARUTO_HOME} alone at night drinking a glass of tap water at the sink, his stomach empty, a tired face",
      (N, "He hadn't eaten. He never ate on those nights. I only figured it out years later.", "aching")),
    S("{HARUTO_WORK} kneeling in the doorway of a cramped apartment, bowing his head low to an angry man in a suit "
      "holding a paper, night",
      (N, "When the landlord came for late rent, he bowed until his forehead touched the floor.", "quiet, pained")),
    S("{HARUTO_WORK} kneeling with a fever, flushed and sweating, pulling on his work shoes at dawn while {MIOCHILD} tugs "
      "his sleeve with a worried face, " + APT,
      L("miochild", "You're hot, onii-chan! You have a fever! Stay home!", "worried, childlike"),
      L("haruto", "If I stay home, we don't eat. Don't worry. Big brothers don't get sick.", "weak smile")),
    S("{HARUTO_WORK} collapsed asleep on the floor just inside the apartment door still wearing his shoes, {MIOCHILD} "
      "covering him with her small blanket, night",
      (N, "That night he came home and collapsed in the doorway. I covered him with my blanket and sat with him until morning.", "soft, sad")),

    # ---- Mio grows up ----
    S("{MIOTEEN} studying hard at the low table late at night with textbooks and notes, a small yellow star hair clip, " + APT_NIGHT,
      (N, "Years passed. I grew up.", "steady"),
      (N, "And the older I got, the more I understood what he'd given up.", "thoughtful")),
    S("two snobby teenage girls in school uniforms laughing and pointing in a school hallway, {MIOTEEN} turning around angrily",
      (N, "In middle school, some girls found out my brother washed dishes for a living.", "cool")),
    S("{MIOTEEN} facing two teenage girls in a school hallway with her fists clenched and a fierce proud face",
      L("mio", "Yes, my brother washes dishes. And delivers newspapers. And works in a warehouse.", "fierce"),
      L("mio", "He's done three jobs a day since he was eighteen so I could stand here. What have you ever done?", "fierce, proud")),
    S("{HARUTO_WORK} standing outside a school gate at sunset, waving shyly at {MIOTEEN} who runs to him smiling",
      (N, "That evening I took his arm and walked home with him the long way. I wanted everyone to see.", "warm, proud")),
    S("{MIOTEEN} standing in the apartment holding a part-time job flyer, facing {HARUTO_HOME} with determination, " + APT,
      L("mio", "Onii-chan, I'm fifteen now. I can work part-time too. Let me help.", "determined, teenage"),
      L("haruto", "Absolutely not.", "firm")),
    S("{HARUTO_HOME} gently tapping {MIOTEEN}'s forehead with one finger, smiling, " + APT,
      L("haruto", "Your job is to study. Mine is to worry about money. Don't steal my job.", "gentle, teasing"),
      L("mio", "...You're so stubborn.", "pouting, fond")),
    S("{MIOTEEN} at a desk in a library late in the evening, surrounded by books, studying with fierce focus",
      (N, "So I studied. Harder than anyone. If he wouldn't let me pay him back with money... I'd pay him back with my future.", "determined")),
    S("{MIOTEEN} looking at an expensive cram school brochure with a sad face, then hiding it in a drawer, " + APT_NIGHT,
      (N, "I wanted to go to cram school for the entrance exams. I knew we couldn't afford it, so I never asked.", "quiet")),
    S("{HARUTO_HOME} handing {MIOTEEN} an envelope with a big grin, she looks shocked, " + APT,
      L("haruto", "Cram school fees. For the whole year. Don't ask where I got it. I won the lottery.", "proud, casual"),
      L("mio", "Onii-chan... we can't...", "shocked, emotional")),
    S("close-up of an old gold wristwatch in a pawn shop display case with a price tag, dim light",
      (N, "Years later, I found the pawn shop receipt. He'd sold Dad's watch. The only thing he had left of our father.", "aching")),
    S("{MIOTEEN} holding an acceptance letter in front of a mailbox, gasping with tears of joy",
      (N, "At eighteen, I got a full scholarship to the best university in Tokyo.", "excited")),
    S("{MIOTEEN} running into a ramen shop waving a letter while {HARUTO_HOME} drops a bowl in shock, {GONDO} grinning "
      "behind the counter, " + RAMEN,
      L("mio", "Onii-chan! I got in! Full scholarship!", "overjoyed, breathless"),
      L("haruto", "You... you did it? You really did it?!", "stunned, overjoyed")),
    S("{GONDO} laughing and banging the counter while {HARUTO_HOME} lifts {MIOTEEN} off the ground in a hug, " + RAMEN,
      L("gondo", "Free ramen for everyone tonight! The kid's sister is a genius!", "booming, delighted")),

    # ---- Graduation ----
    S("a Japanese university graduation ceremony outdoors under cherry blossoms, graduates in suits and hakama, "
      "families taking photos",
      (N, "Four years later, I graduated top of my class.", "proud")),
    S("{HARUTO_SUIT} standing among the parents at a graduation ceremony under cherry blossoms, beaming with pride, "
      "his old suit a little too big",
      (N, "My brother came in the same black suit he wore to our parents' funeral. It was the only one he owned.", "tender")),
    S("{MIO} in a graduation hakama hugging {HARUTO_SUIT} under cherry blossoms, both laughing with tears",
      L("mio", "This is yours too, onii-chan. Every bit of it.", "emotional"),
      L("haruto", "No. It's all you. I just made the lunches.", "proud, teary laugh")),
    S("{MIO} and {HARUTO_SUIT} posing for a photo together under cherry blossoms, she holds up her diploma, he gives an "
      "awkward peace sign",
      (N, "He'd never gotten his own diploma. That day, he held mine like it was the most precious thing in the world.", "soft")),

    # ---- Stellaris and Saijo ----
    S("{MIO} at a laptop in a bright modern startup office, colleagues around her, focused and energetic, " + OFFICE,
      (N, "I joined a small tech company called Stellaris. Fifty employees, and a big dream.", "bright")),
    S("{MIO} presenting confidently in front of a glass whiteboard covered in charts to a small team, " + OFFICE,
      (N, "Within a year, my project became the company's biggest success.", "proud")),
    S("{SAIJO} leaning on the glass doorway of a meeting room, watching with a charming smile and narrow calculating eyes, " + OFFICE,
      (N, "That's when Kaname Saijo noticed me.", "neutral, a hint of ominous")),
    S("{SAIJO} shaking hands with {MIO} with a dazzling smile, she looks surprised and flattered, " + OFFICE,
      L("saijo", "Ms. Aoyama. Kaname Saijo, head of overseas expansion. Your project was brilliant.", "smooth, charming")),
    S("{SAIJO} sitting across from {MIO} in a glass meeting room, sliding a folder toward her",
      L("saijo", "We're opening our new headquarters in New York. I want you to lead the launch team.", "smooth, confident")),
    S("close-up of {MIO} staring at a folder with a photo of the New York skyline, stunned",
      L("mio", "New York...? Me?", "stunned, breathless"),
      (N, "It was everything I'd ever dreamed of. And I couldn't say yes.", "conflicted")),
    S("{MIO} looking down at her hands, hesitant and torn, in a glass meeting room",
      L("mio", "I'm honored. But... I have a brother. He raised me alone. I can't just leave him.", "hesitant, quiet")),
    S("{SAIJO} leaning forward with a warm understanding smile, his eyes cold behind silver glasses",
      L("saijo", "Ms. Aoyama. Think about it. What does your brother want more than anything?", "gentle, persuasive")),
    S("close-up of {SAIJO} smiling gently, his glasses glinting",
      L("saijo", "For you to succeed. And with a New York salary, you could finally give him the life he gave you.", "smooth"),
      L("saijo", "He could quit those jobs. He could rest. Isn't that the best way to thank him?", "silky, persuasive")),
    S("{MIO} biting her lip, thinking hard, sunlight through the glass walls of a meeting room",
      (N, "He knew exactly which words would work on me.", "bitter, knowing")),
    S("{MIO} looking up at {SAIJO} with serious determined eyes across a meeting table",
      L("mio", "Then I have one condition.", "firm")),
    S("close-up of {MIO} with a determined face, a small yellow star hair clip in her hair",
      L("mio", "Promise me my brother will be taken care of. That every month, my money reaches him. That he's okay.", "serious, firm")),
    S("{SAIJO} smiling warmly and placing a hand on his chest like a promise",
      L("saijo", "You have my word. The company has a family support program. I'll handle the transfers myself.", "warm, sincere-sounding"),
      L("saijo", "And I'll check on him personally. You just focus on your work.", "smooth")),
    S("{SAIJO} and {MIO} shaking hands over a signed contract on a glass table, he smiles, she looks hopeful",
      (N, "I believed him. I had no reason not to.", "quiet, regretful")),

    # ---- Telling Haruto ----
    S("{HARUTO_HOME} cheerfully serving two plates of curry rice at the low table, {MIO} sitting nervously, " + APT_NIGHT,
      L("haruto", "Curry tonight! Extra potatoes, the way you like it.", "cheerful")),
    S("{MIO} holding a spoon without eating, looking down nervously at the table, her brother noticing, " + APT_NIGHT,
      L("haruto", "...Mio? What's wrong? You haven't touched it.", "concerned, gentle")),
    S("{MIO} looking up at her brother with nervous eyes, " + APT_NIGHT,
      L("mio", "Onii-chan... the company wants to send me to New York. To lead the new headquarters.", "nervous, quiet"),
      L("mio", "It would be for a long time. Years, maybe.", "quiet")),
    S("close-up of {HARUTO_HOME} freezing with his spoon halfway to his mouth, his eyes widening, a flicker of fear",
      (N, "For one second, I saw it on his face. The fear of being alone.", "aching")),
    S("{HARUTO_HOME} putting his spoon down and smiling the widest smile, eyes shining, " + APT_NIGHT,
      L("haruto", "New York? Mio, that's incredible! That's your dream!", "overjoyed, slightly too bright")),
    S("{MIO} reaching across the table for her brother's hand, worried, " + APT_NIGHT,
      L("mio", "But you'll be alone. Who'll make sure you eat? Who'll say welcome home?", "worried, emotional")),
    S("{HARUTO_HOME} laughing softly and ruffling {MIO}'s hair across the low table, " + APT_NIGHT,
      L("haruto", "Hey. I'm the big brother here. I'll be fine.", "warm, reassuring"),
      L("haruto", "Go. Go and shine, Mio. That's all I ever wanted.", "tender")),
    S("{HARUTO_HOME} standing alone at the small sink at night washing two plates, his back to the room, shoulders "
      "trembling slightly, " + APT_NIGHT,
      (N, "That night, I heard the water running in the kitchen for a very long time.", "soft, aching")),
    S("{HARUTO_HOME} kneeling beside an open suitcase at night carefully packing snacks, socks and a sealed letter, "
      "{MIO} asleep on a futon nearby, " + APT_NIGHT,
      (N, "The night before I left, he stayed up packing my suitcase. Snacks. Warm socks. And a letter.", "soft")),

    # ---- The airport ----
    S("a busy international airport departure hall in Tokyo, big windows and planes outside, travelers with suitcases",
      (N, "Three weeks later, he took me to the airport.", "quiet")),
    S("{HARUTO_SUIT} holding out a small red omamori good-luck charm to {MIO}, who has a suitcase, airport departure gate",
      L("haruto", "Here. A charm for safe travels. I got it at the shrine by our old house.", "gentle")),
    S("{MIO} clutching a small red omamori charm to her chest, tears in her eyes, airport",
      L("mio", "I'll send you money every month. Quit at least one job, okay? Promise me. Sleep more. Eat real food.", "tearful, insistent")),
    S("{HARUTO_SUIT} smiling and nodding at the airport, his eyes glistening",
      L("haruto", "Yeah, yeah. Don't worry about me. Worry about New York pizza.", "teasing, holding back tears")),
    S("{MIO} hugging {HARUTO_SUIT} tightly at the airport departure gate, crying, other travelers passing by",
      L("mio", "Thank you, onii-chan. For everything. For my whole life.", "sobbing")),
    S("{HARUTO_SUIT} waving at the airport gate with a big smile as she walks away, seen from behind her",
      L("haruto", "Mio! Make lots of friends! Call me when you land!", "calling out, cheerful")),
    S("close-up of {HARUTO_SUIT} alone at the airport after she has gone, his smile slowly falling, his hand still half-raised",
      (N, "I didn't look back. If I had, I would have seen his face.", "regretful, quiet")),
    S("{MIO} in an airplane window seat at night reading a handwritten letter, tears running down her face, clouds outside",
      L("haruto", "Mio. You were never a burden. Not for one day. You were the reason I got up every morning.", "gentle, letter being read")),
    S("close-up of a handwritten letter held in shaking hands on an airplane tray table, a small red omamori beside it",
      L("haruto", "So go and be happy. Don't look back. That's the only thing I'll ever ask of you. Your big brother, Haruto.", "gentle, smiling through tears")),
    S("close-up of {MIO} pressing a letter to her chest on an airplane at night, crying, the window dark",
      (N, "I cried across the whole Pacific Ocean.", "tearful, small laugh")),

    # ---- New York ----
    S("wide view of the New York City skyline on a bright morning, yellow taxis, busy streets, skyscrapers",
      (N, "New York was everything I'd imagined. Loud, fast, and impossible.", "energetic")),
    S("{MIO_EXEC} walking confidently into a huge glass office lobby in New York with a coffee and a laptop bag",
      (N, "I worked like my brother had taught me. Earlier than everyone. Later than everyone.", "determined")),
    S("{MIO_EXEC} leading a meeting of international colleagues around a long table, pointing at a big screen, " + NY,
      (N, "My team grew from five people to five hundred.", "proud")),
    S("{MIO_EXEC} at a laptop late at night alone in a glass office, setting up a bank transfer, a small red charm on "
      "her desk, " + NY_NIGHT,
      (N, "And every month, on payday, I sent half my salary home. Through Mr. Saijo's family support program, just as he'd promised.", "warm, trusting")),
    S("{SAIJO} on a video call on a laptop screen, smiling reassuringly, {MIO_EXEC} listening, " + NY,
      L("saijo", "Your brother's doing wonderfully. He quit two of his jobs. He even moved to a bigger place.", "smooth, warm")),
    S("close-up of {MIO_EXEC} smiling with relief at a laptop",
      L("mio", "Really? Oh, thank goodness. Thank you, Mr. Saijo.", "relieved, grateful")),
    S("a laptop screen in a glass office showing a blurry photo of a man seen from behind standing outside a nice new "
      "apartment building, a coffee cup beside the laptop",
      L("saijo", "Here's a photo I took last week. Nice place, isn't it? He didn't want his picture taken, of course. Shy as ever.", "smooth, chuckling"),
      (N, "It was blurry, and from behind. I was too happy to notice.", "quiet, regretful")),
    S("close-up of a smartphone screen showing a short chat message with a smiling emoji, a desk in a glass office behind it",
      (N, "At first, my brother and I talked every week.", "warm")),
    S("{MIO_EXEC} laughing on the phone in a glass office at night, kicking off her heels, " + NY_NIGHT,
      L("mio", "Onii-chan, guess what? They gave me my own team! Five people!", "excited")),
    S("{HARUTO_WORK} on an old phone at the low table of the small apartment, smiling with tears in his eyes, night",
      L("haruto", "Five people? My sister's a boss! Are you eating? Are you sleeping?", "proud, warm")),
    S("{MIO_EXEC} on the phone in a busy office, distracted by colleagues waving papers at her, " + NY,
      L("mio", "Sorry, onii-chan, I have a meeting. I'll call you this weekend, okay?", "rushed, apologetic")),
    S("{MIO_EXEC} on the phone at her desk in New York, frowning slightly while typing on her laptop at the same time, " + NY,
      (N, "About a year after I left, I called him one night. His voice sounded strange. Thin.", "uneasy")),
    S("{HARUTO_WORK} lying on a futon in a dark small apartment with a cast on his leg, holding an old phone to his ear, "
      "smiling painfully, night",
      L("mio", "Onii-chan? You sound tired. Are you okay?", "slightly worried, distracted"),
      L("haruto", "Me? I'm fine. Just a little cold. Don't worry about me. How's work?", "forcing cheer")),
    S("close-up of {MIO_EXEC} on the phone while reading an email on her laptop, distracted",
      L("mio", "Busy! Super busy. Okay, rest up. Love you. Bye!", "rushed, cheerful"),
      (N, "I hung up in under a minute. I didn't hear what he wasn't saying.", "regretful")),
    S("{MIO_EXEC} asleep at her desk at night, surrounded by documents, the phone face down beside her, " + NY_NIGHT,
      (N, "Then every two weeks. Then every month. Then...", "slowing, regretful")),
    S("a smartphone on a desk with an unread message notification, unanswered, in a dark glass office",
      (N, "I always meant to call back. I always thought there would be time.", "heavy, regretful")),

    # ---- The company grows ----
    S("{MIO_EXEC} on a big stage giving a presentation to a huge audience, a giant screen behind her, spotlights",
      (N, "Stellaris exploded. Our product changed the industry.", "proud, intense")),
    S("a tall skyscraper in New York with a glowing star-shaped company logo shape on top, at dusk, no letters",
      (N, "Within three years, we were one of the leading companies in the world.", "proud")),
    S("{MIO_EXEC} in a corner office looking out over New York at sunset, holding a small red omamori charm, " + NY,
      (N, "I was promoted to director. My name was in business magazines.", "proud, hollow")),
    S("{SAIJO} raising a glass of champagne at a glamorous party in a penthouse, smiling coldly at the crowd",
      (N, "Mr. Saijo was promoted too. Vice president. He was always smiling.", "neutral, uneasy")),

    # ---- The unreachable number ----
    S("{MIO_EXEC} alone in a dark office at night, looking at a family photo on her phone, the city lights behind her, " + NY_NIGHT,
      (N, "One evening, four years after I left Japan, I realized I hadn't heard my brother's voice in over a year.", "quiet, guilty")),
    S("{MIO_EXEC} smiling softly with a phone to her ear, " + NY_NIGHT,
      (N, "I wanted to surprise him.", "soft")),
    S("close-up of a smartphone screen showing a call failing, a red icon, dark background",
      L("mio", "...'The number you have dialed is not in service'?", "confused")),
    S("{MIO_EXEC} calling again and again, frowning at her phone, " + NY_NIGHT,
      (N, "I tried again. And again. Ten times. Twenty.", "growing worry")),
    S("{MIO_EXEC} on the phone with a worried face, " + NY_NIGHT,
      L("mio", "Mr. Saijo, I can't reach my brother. His number's been disconnected. Has something happened?", "worried, tense")),
    S("{SAIJO} on the phone in a dark luxury apartment, his face calm but his eyes cold, a glass of wine in his hand",
      L("saijo", "Ah, he probably just changed carriers. There's nothing to worry about.", "smooth, light"),
      L("saijo", "I'll look into it. You've got the board meeting tomorrow. Focus on that.", "smooth")),
    S("close-up of {SAIJO} lowering his phone with a cold expression, his smile completely gone, dark room",
      (N, "He said there was nothing to worry about.", "uneasy")),
    S("{MIO_EXEC} lying awake in bed in a dark New York apartment, staring at the ceiling, city light through the curtains",
      (N, "But I couldn't sleep. Something was wrong. I could feel it.", "uneasy")),
    S("{MIO_EXEC} rushing through an airport terminal at night with a small suitcase, determined and anxious",
      (N, "Two days later, I was on a plane to Tokyo.", "urgent")),

    # ---- The empty apartment ----
    S("an old two-story wooden apartment building by train tracks in Tokyo at dusk, a small for-rent sign on one door, "
      "a train passing",
      (N, "The building by the tracks looked exactly the same.", "quiet, nervous")),
    S("{MIO_EXEC} knocking on the door of an old apartment with a nervous hopeful smile, a gift bag in her hand",
      L("mio", "Onii-chan? It's me! Surprise!", "nervous, hopeful")),
    S("{MIO_EXEC} looking through a dusty window into an empty one-room apartment with bare tatami and no furniture, shocked",
      (N, "The room was empty. No futons. No table. No drawing on the wall.", "hollow, stunned")),
    S("{TANAKA} coming out of a neighboring door with a watering can, peering at the visitor through round glasses",
      L("tanaka", "Oh my... is that little Mio? Haruto's Mio? Look how grown up you are!", "surprised, warm")),
    S("{MIO_EXEC} hurrying toward {TANAKA} on the outdoor walkway of an old apartment building",
      L("mio", "Mrs. Tanaka! Where's my brother? Did he move?", "anxious")),
    S("close-up of {TANAKA} looking sad and uncomfortable, holding a watering can",
      L("tanaka", "He left about a year ago, dear. He couldn't afford the rent anymore.", "gentle, sad"),
      L("tanaka", "I told him he could pay late, but he wouldn't hear of it. Said he didn't want to be a burden.", "sad")),
    S("close-up of {MIO_EXEC} frozen in shock on the walkway, her gift bag slipping from her fingers",
      L("mio", "Couldn't... afford the rent? That's impossible.", "stunned, whispering")),
    S("{MIO_EXEC} gripping the walkway railing, shaking, the train tracks behind her",
      (N, "I'd sent him half my salary every month for four years. He should have had more money than he could spend.", "confused, rising panic")),
    S("{MIO_EXEC} on her phone on the old apartment walkway at dusk, her face tense",
      L("mio", "Mr. Saijo. I'm in Tokyo. My brother lost his apartment a year ago. Where has my money been going?", "sharp, shaking")),
    S("{SAIJO} on the phone in a dark office with a regretful expression that does not reach his cold eyes",
      L("saijo", "...Ms. Aoyama. I was hoping you'd never have to find out.", "sighing, regretful")),
    S("close-up of {SAIJO} on the phone, speaking slowly with fake sympathy, glasses glinting",
      L("saijo", "Your brother started gambling. Pachinko. Horse racing. It got worse every month.", "slow, grave"),
      L("saijo", "He spent everything you sent. Then he borrowed more. He begged me not to tell you.", "fake sympathy")),
    S("close-up of {MIO_EXEC} with her eyes wide and her face pale, the phone against her ear",
      L("mio", "No... no. Onii-chan would never...", "disbelief, breaking")),
    S("{SAIJO} on the phone, looking at a sheet of paper with a faint smile",
      L("saijo", "I have the loan documents, if you want to see them. I'm so sorry. I tried to help him.", "smooth")),
    S("{MIO_EXEC} sitting on the outdoor stairs of the old apartment at night, staring at nothing, the phone in her lap",
      (N, "The brother who wouldn't let me work part-time. Who skipped dinner so I could eat.", "hollow")),
    S("close-up of {MIO_EXEC} with angry tears in her eyes, jaw clenched, at night",
      (N, "He'd thrown it all away? Everything I worked for? On gambling?", "rising anger")),
    S("{MIO_EXEC} standing up from the stairs, wiping her eyes hard, her face turning cold, at night",
      L("mio", "Fine. If that's what he wanted... then he can have it.", "cold, hurt")),
    S("{MIO_EXEC} walking away down a dark old street without looking back, her heels clicking, a train passing behind",
      (N, "I didn't look for him. I didn't want to see him. I went back to New York that same week.", "cold, regretful")),
    S("{MIO_EXEC} at her desk in New York putting a small red omamori charm into a drawer and closing it, cold face, " + NY,
      (N, "And I put his charm in a drawer.", "quiet")),

    # ---- One more year ----
    S("{MIO_EXEC} on a huge stage receiving an award under bright spotlights, applause, a giant screen behind her",
      (N, "One more year passed. Stellaris became the number one company in the world.", "flat, empty")),
    S("{MIO_EXEC} alone in a vast empty penthouse at night, looking out over the city, a glass of water in her hand",
      (N, "I had everything. Money. A title. A view of the whole city.", "hollow")),
    S("close-up of {MIO_EXEC}'s reflection in a dark window, her face tired and lonely",
      (N, "And no one to say welcome home to.", "aching, quiet")),

    # ---- The park ----
    S("a sunny afternoon in Central Park in New York, autumn trees, families walking on the paths",
      (N, "One Sunday, I was walking in Central Park.", "calm")),
    S("a little girl of about five falling down on a park path and crying, holding her scraped knee, autumn park",
      (N, "A little girl tripped on the path and started crying.", "calm")),
    S("a boy of about nine kneeling next to a crying little girl in a park, wiping her tears with his sleeve, autumn park",
      L("kid", "Hey, hey. Don't cry. Big brother's here. Come on, get on my back.", "young boy, gentle")),
    S("a boy of about nine carrying his little sister piggyback down a park path, she is smiling through tears, "
      "golden autumn light",
      (N, "He was small. She was almost too heavy for him. But he carried her anyway, all the way down the path.", "softening")),
    S("{MIO_EXEC} standing frozen on a park path watching two children walk away, her hand over her mouth, autumn trees",
      (N, "And suddenly, I was six years old again.", "trembling")),
    S("{HARUTO} carrying {MIOCHILD} piggyback down a sunset street, she is asleep on his back, warm nostalgic orange light",
      (N, "My brother carried me home like that every time I fell asleep somewhere. Every single time.", "tearful, warm")),
    S("{HARUTO_HOME} smiling and saying something gently, warm nostalgic flashback light, soft focus",
      L("haruto", "Don't cry, Mio. Big brother's here. I'm always here.", "gentle, echoing memory")),
    S("{MIO_EXEC} sitting on a park bench crying into her hands, autumn leaves falling around her",
      (N, "I sat on a bench and cried for the first time in years.", "breaking")),
    S("close-up of {MIO_EXEC} lifting her tearful face from her hands, her eyes slowly hardening with doubt, park",
      (N, "And for the first time, a question I'd been too angry to ask came up.", "slowly")),
    S("close-up of {MIO_EXEC} thinking hard, a park bench, tears drying",
      L("mio", "Onii-chan skipped dinner for twelve years so I could eat... and he'd gamble away my money?", "slow, doubting")),
    S("{MIO_EXEC} standing up from the park bench with determination, pulling out her phone, autumn park",
      L("mio", "...No. That's not my brother.", "firm, quiet")),

    # ---- The investigator ----
    S("{MIO_EXEC} on a phone call in a dark office, speaking in a low secretive voice, door closed, " + NY_NIGHT,
      (N, "I didn't tell Mr. Saijo. I don't know why. Something told me not to.", "cautious")),
    S("{KIRISHIMA} listening on the phone in a small cluttered detective office with file cabinets, a cup of coffee, Tokyo at night",
      L("kirishima", "Kirishima Investigations.", "calm, professional"),
      L("mio", "I need you to find someone. My brother. Haruto Aoyama. I want to know everything.", "low, urgent")),
    S("close-up of {KIRISHIMA} writing a name in a notebook with a pen, a serious face",
      L("kirishima", "Everything can be hard to hear, Ms. Aoyama.", "calm, careful"),
      L("mio", "I know. Find him anyway.", "firm")),
    S("{MIO_EXEC} sitting in a glass office staring at her phone, waiting, days passing, papers piling up, " + NY,
      (N, "Three weeks passed. They were the longest three weeks of my life.", "tense")),
    S("{MIO_EXEC} hurrying into a quiet old coffee shop in Tokyo on a rainy evening, shaking water from her coat, " + CAFE,
      (N, "Then she called. She wouldn't tell me over the phone. So I flew to Tokyo again.", "tense")),
    S("{KIRISHIMA} sitting in a wooden booth in a dim coffee shop with a thick brown envelope on the table, a serious face, " + CAFE,
      L("kirishima", "Sit down, Ms. Aoyama.", "calm, grave")),
    S("{KIRISHIMA} opening the brown envelope and taking out bank statements, across the table from {MIO_EXEC}, " + CAFE,
      L("kirishima", "I'll start with the money. Every month, you sent money to an account in your brother's name.", "measured")),
    S("close-up of {KIRISHIMA} looking straight across the table, serious, " + CAFE,
      L("kirishima", "Your brother never opened that account. He never knew it existed.", "flat, grave")),
    S("close-up of {MIO_EXEC} going pale in a coffee shop booth",
      L("mio", "...What?", "barely a whisper")),
    S("close-up of bank statements on a wooden table with columns of numbers and a pen circling them, coffee cup beside them",
      L("kirishima", "Every transfer left that account within a day. Not one yen of it ever reached him.", "grave"),
      L("kirishima", "Where it went, I'm still tracing. Someone was very careful.", "grim")),
    S("{MIO_EXEC} gripping the edge of the table with both hands, shaking, in a dim coffee shop",
      L("mio", "Then the gambling... the loans...", "shaking")),
    S("{KIRISHIMA} shaking her head slowly in a coffee shop booth",
      L("kirishima", "I asked everyone. Every pachinko parlor near every place he lived.", "firm"),
      L("kirishima", "Nobody had ever seen him. Your brother never gambled a single yen in his life.", "firm, certain")),
    S("close-up of {MIO_EXEC} with her hand over her mouth, eyes filling with tears, coffee shop",
      (N, "Mr. Saijo had told me... he'd shown me papers...", "confused, breaking")),

    # ---- What really happened ----
    S("{KIRISHIMA} sliding a photo across the table, her expression heavy, " + CAFE,
      L("kirishima", "After you left, your brother kept working. The same three jobs. He lived only on what he earned.", "measured, heavy")),
    S("{HARUTO_WORK} riding an old bicycle loaded with newspapers in the dark before dawn, rain falling, flashback",
      (N, "He never quit. He never even knew there was money to quit with.", "aching")),
    S("a dark wet street at night, headlights glaring, a bicycle swerving to avoid a small child who ran into the road, "
      "dramatic flashback",
      L("kirishima", "One year after you left, he was delivering on his bicycle at night. A child ran into the street.", "grave")),
    S("a fallen bicycle and scattered newspapers on a wet road at night, a truck stopped with its headlights on, a "
      "frightened child safe on the sidewalk, flashback",
      L("kirishima", "He swerved to miss her. The truck didn't miss him.", "heavy")),
    S("{MIO_EXEC} gasping with both hands over her mouth in a coffee shop booth, tears falling",
      L("mio", "No...", "broken whisper")),
    S("{HARUTO_WORK} lying in a hospital bed with his leg in a cast, a doctor showing him papers, his face worried, flashback",
      L("kirishima", "His leg was badly broken. The doctors recommended surgery to fix it properly.", "grave"),
      L("kirishima", "He couldn't afford it. Or the weeks off work. So he chose the cheaper treatment.", "heavy")),
    S("close-up of {HARUTO_WORK} in a hospital bed forcing a smile at a doctor, flashback",
      L("haruto", "It's fine, doctor. Just set it. I need to get back to work.", "forced cheer, flashback")),
    S("{HARUTO_OLD} walking slowly down an old street with a wooden cane, limping, carrying a plastic shopping bag",
      L("kirishima", "The bone healed wrong. He's walked with a limp ever since. He can't stand for long. He can't run.", "heavy")),
    S("{HARUTO_OLD} being handed an envelope by a foreman at a warehouse, apologetic faces, flashback",
      L("kirishima", "He lost the warehouse job. Then the newspaper route.", "measured")),
    S("{GONDO} sitting on a stool in his ramen shop, older, his arms crossed, speaking sadly, " + RAMEN,
      L("kirishima", "I spoke to a Mr. Gondo, the owner of a ramen shop. He kept your brother on as long as he could.", "measured")),
    S("close-up of {GONDO} with his eyes wet, looking down, his towel in his hands, " + RAMEN,
      L("gondo", "That kid washed dishes sitting on a stool because his leg couldn't hold him up. Never complained once. Not once.", "gruff, emotional")),
    S("{HARUTO_OLD} sitting on a stool washing dishes in a ramen shop kitchen, smiling at Gondo, flashback, " + RAMEN,
      L("gondo", "Every day he'd tell me, my sister's doing amazing things in America. She's going to change the world.", "gruff, choked")),
    S("an old shop wall covered in neatly cut newspaper and magazine clippings about a tech company and a young "
      "businesswoman, pinned carefully, warm light",
      L("gondo", "He cut out every article about you. Every one. Pinned them up in the back of my shop.", "emotional")),
    S("close-up of {MIO_EXEC} sobbing in a coffee shop booth, both hands pressed to her face",
      (N, "He was proud of me. The whole time I was angry at him... he was proud of me.", "sobbing")),
    S("{KIRISHIMA} looking down at her notes with a grim face, " + CAFE,
      L("kirishima", "There's more. After the accident, his phone was cut off. He couldn't pay the bill.", "careful")),
    S("{KIRISHIMA} turning a page in her notebook, her voice careful, " + CAFE,
      L("kirishima", "Do you remember a phone call, about a year after you left? You said he sounded tired.", "careful")),
    S("close-up of {MIO_EXEC} going still in a coffee shop booth, remembering, horror dawning",
      L("mio", "...He said it was a cold.", "whispering")),
    S("close-up of {KIRISHIMA} nodding slowly, grave, " + CAFE,
      L("kirishima", "That was four days after the accident. He called you from the hospital hallway, on crutches.", "grave"),
      L("kirishima", "He asked the nurses to keep quiet so you wouldn't hear the announcements.", "heavy")),
    S("{MIO_EXEC} bent over the coffee shop table, her forehead on her hands, shoulders shaking",
      (N, "Under a minute. I'd hung up in under a minute.", "devastated")),
    S("{HARUTO_OLD} at an old green public pay phone in the rain, holding the receiver with hope, flashback",
      L("kirishima", "Mr. Gondo says your brother called your company in New York once. From a pay phone.", "careful")),
    S("close-up of {HARUTO_OLD} at a pay phone in the rain, his hopeful face slowly falling, flashback",
      L("kirishima", "Someone told him you were too busy. That you'd asked not to be contacted by family.", "heavy")),
    S("close-up of {MIO_EXEC} with her eyes wide in horror, coffee shop",
      L("mio", "I never said that! Nobody ever told me he called! Who... who told him that?!", "horrified, shouting")),
    S("{KIRISHIMA} meeting {MIO_EXEC}'s eyes steadily across the table, " + CAFE,
      L("kirishima", "That's what I'd like to know too.", "quiet, pointed")),
    S("{HARUTO_OLD} sitting alone on the floor of a tiny bare room at night, looking at an old crayon drawing in his "
      "hands, a single bare bulb, flashback",
      L("gondo", "After that call, he never talked about you again. But he never stopped buying the newspapers.", "sad, gruff")),
    S("{GONDO} wiping down an empty ramen counter, older, with a sad tired face, a for-sale sign on the shop door, " + RAMEN,
      L("kirishima", "Last year, Mr. Gondo closed the shop. His health. After that, your brother had almost nothing.", "measured")),
    S("{HARUTO_OLD} sitting on the floor of a tiny bare room folding stacks of advertising flyers into envelopes by "
      "lamplight, flashback",
      L("kirishima", "He folded flyers at home for a few yen a stack. Sometimes he sorted bottles at a recycling center.", "quiet")),
    S("{HARUTO_OLD} sitting on the step of a run-down boarding house sharing a piece of bread with a skinny stray cat, "
      "evening, flashback",
      L("kirishima", "The other tenants said he was quiet. Polite. He shared his bread with a stray cat.", "soft")),
    S("{HARUTO_OLD} alone at a tiny table in a bare room with a very small strawberry shortcake and one candle, "
      "smiling sadly, flashback, night",
      L("kirishima", "And once a year, he bought a small strawberry cake. Just one. Always on the same day.", "soft, heavy")),
    S("close-up of {MIO_EXEC} in a coffee shop booth, her lips trembling",
      L("mio", "...March fourteenth.", "barely a whisper"),
      L("kirishima", "Your birthday.", "quiet")),
    S("{HARUTO_OLD} alone in a dark bare room singing softly to a tiny cake with one candle, his eyes wet, flashback",
      L("haruto", "Happy birthday, dear Mio... happy birthday to you.", "soft, singing alone, breaking")),

    # ---- The last address ----
    S("{KIRISHIMA} writing an address on a piece of paper and sliding it across the table, " + CAFE,
      L("kirishima", "This is his most recent address. A boarding house by the river. I found it four days ago.", "urgent")),
    S("{MIO_EXEC} grabbing the paper and running out of the coffee shop into the rainy night, coat flying",
      (N, "I didn't even say goodbye. I just ran.", "breathless")),
    S("{MIO_EXEC} running through rainy Tokyo streets at night, soaked, neon reflections on the wet pavement",
      (N, "I kept thinking about what I'd say. I'm sorry. I'm so sorry. I was wrong. I'm home.", "breathless, crying")),
    S("a small run-down two-story boarding house beside a dark river at night, rain, one dim light in a window",
      (N, "The boarding house by the river was old and small. One light was on.", "breathless, hopeful")),
    S("{MIO_EXEC} pounding on a thin wooden door in a dim boarding house hallway, soaked from the rain",
      L("mio", "Onii-chan! Onii-chan, it's me! It's Mio! Please open the door!", "desperate, crying")),
    S("an old man in a cardigan opening the door of the next room in a dim boarding house hallway, surprised and sad",
      L("tanaka", "...You're looking for the young man with the cane? Oh, dear...", "sad, gentle")),
    S("an elderly woman landlady with gray curly hair and round glasses, holding a key in a dim boarding house hallway, "
      "looking sorry",
      L("tanaka", "He left three days ago. Paid his last rent in coins, cleaned the room spotless... and just left.", "sad")),
    S("close-up of {MIO_EXEC} soaked and frozen in a dim hallway, her face blank with shock",
      L("mio", "Left...? Where? Where did he go?", "barely breathing")),
    S("an elderly landlady shaking her head sadly in a dim boarding house hallway",
      L("tanaka", "He didn't say. He didn't take much. Just a small bag... and an old picture, rolled up.", "sad")),
    S("a tiny empty boarding house room with bare tatami at night, cleaned spotless, a single folded note left on the "
      "floor under a bare bulb",
      (N, "The room was empty. Except for one note, left for the landlady.", "hushed")),
    S("close-up of a folded handwritten note held in a woman's shaking hands, dim light, rain sounds",
      L("haruto", "Thank you for everything. If anyone ever comes looking for me... please don't tell my sister.", "quiet, gentle, a letter being read")),
    S("{MIO_EXEC} collapsing to her knees on the tatami of an empty room, clutching a small note to her chest, sobbing",
      L("mio", "Why...? Why, onii-chan...?", "sobbing, broken")),
    S("close-up of {MIO_EXEC} crying on the floor of an empty room, her yellow star hair clip catching the light",
      (N, "Even then. Even after everything. He was still trying to protect me.", "sobbing, aching")),

    # ---- Cliffhanger ----
    S("{MIO_EXEC} standing alone at the edge of a dark river at night in the rain, the city lights far away, small and lost",
      (N, "That's how I found out the truth.", "quiet, shaken")),
    S("close-up of a small yellow star hair clip in a woman's palm, rain drops on it",
      (N, "My brother had been alone, and hurt, and hungry... while I was angry at him from the top of a skyscraper.", "bitter, breaking")),
    S("a dark luxurious New York penthouse office at night, a man in a navy three-piece suit seen from behind, standing "
      "at the window with a glass of wine, his face hidden in shadow",
      (N, "And somewhere on the other side of the world, someone had been very, very careful.", "cold, ominous")),
    S("close-up of {MIO_EXEC} in the rain at night lifting her head, her tearful eyes turning fierce and determined",
      L("mio", "Onii-chan. Wait for me. This time... I'll find you.", "fierce, tearful vow")),
    S("{HARUTO_OLD} seen from behind, limping alone with a cane down a long empty country road at dawn, a small bag over "
      "his shoulder, mist",
      (N, "Where is my brother now? Is he even alive?", "haunted"),
      (N, "And where did five years of money go?", "cold")),
    S("close-up of {MIO_EXEC} at dawn with determined eyes, holding a small red omamori charm, a small yellow star hair "
      "clip in her hair, a city skyline behind her",
      (N, "What would you do if you were me? Tell me in the comments.", "intimate, direct"),
      (N, "Because I'm going to find him. Whatever it takes.", "determined"), pos="narrator:b"),

    # ---- Host outro ----
    S("close-up of {HOST} with teary sparkling eyes, smiling softly, holding a tissue, soft pink sparkly background",
      L("host", "Waaah... thanks for watching~! Haruto, you deserve the whole world!", "teary, sweet")),
    S("{HOST} pointing at the viewer with a determined wink, soft pink sparkly background",
      L("host", "Want to see Mio find her brother... and find out who took the money? Comment ONII-CHAN for episode two!", "energetic, playful")),
]

spec = {
    "title": "My Brother Gave Up Everything to Raise Me... For 5 Years, Not One Yen I Sent Reached Him | Manga Dub",
    "character": "", "style": "",
    "width": 1920, "height": 1080, "title_card": False,
    "tts": "kokoro", "cast": KOKORO, "speed": 0.95, "scene_pad": 0.7,
    "emotive": {"engine": "eleven_v3", "cast": CAST, "skip": [], "fallback": True,
                "priority": ["narrator", "mio", "haruto", "miochild", "saijo", "kirishima", "gondo", "tanaka", "mori",
                             "aunt", "kid"]},
    "caption": {"mode": "boxes", "font": "Comic Neue", "fonts_dir": "assets/fonts",
                # dialogue in oval bubbles: blue words for male speakers, pink for female ones
                "bubbles": {"male": MALE, "female": FEMALE}},
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
