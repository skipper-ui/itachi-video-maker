"""Builds script.json for HOSHIZORA, a standalone ~17-minute "manga dub" story video (16:9).

Run: python3 projects/manga/hoshizora/build.py
Original story and characters (school-reunion revenge): Sota, bullied as "Bento Boy" in high school, is now the faceless
star chef of Hoshizora in Ginza, and his old bullies book his restaurant for their ten-year reunion.
Same format as FURUSATO: one illustrated panel per beat, the hero narrating in first person in a white box at the top,
the other characters speaking in white boxes near the bottom, every line acted with ElevenLabs v3.
Images are drawn locally with FLUX.2 klein (tools/flux_local.py) from the scene prompt plus the reference portraits of
the characters in it, so faces and outfits stay the same from panel to panel.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = "narrator"

# Fixed character descriptions, repeated in every prompt; the key before "_" names the reference portrait used.
C = {
    "SOTA": "Sota (a 28-year-old Japanese man with short slightly messy black hair, calm sharp eyes and a lean build, "
            "wearing a plain navy knit sweater and dark jeans)",
    "SOTA_CHEF": "Sota (a 28-year-old Japanese man with short slightly messy black hair, calm sharp eyes and a lean build, "
                 "wearing a crisp white double-breasted chef's jacket and a black apron)",
    "TEENSOTA": "teenage Sota (a thin 17-year-old Japanese boy with black hair and long bangs falling over his eyes, "
                "wearing a black high-collared Japanese school uniform)",
    "TEENSOTA_KITCHEN": "young Sota (a thin 19-year-old Japanese man with black hair and long bangs, "
                        "wearing a plain white cook's apron over a white t-shirt, a white bandana on his head)",
    "RYUJI": "Ryuji (a tall broad-shouldered 28-year-old Japanese man with short bleached blond hair and a cocky grin, "
             "wearing a shiny dark blue suit with an open collar and a gold bracelet)",
    "TEENRYUJI": "teenage Ryuji (a tall broad-shouldered 17-year-old Japanese boy with short spiky black hair and a cocky grin, "
                 "wearing a black Japanese school uniform with the collar open and a red baseball wristband)",
    "MIKA": "Mika (a 28-year-old Japanese woman with long wavy ash-blonde hair, heavy glamorous makeup and long nails, "
            "wearing a white off-shoulder dress, always holding a smartphone in a pink case)",
    "TEENMIKA": "teenage Mika (a 17-year-old Japanese girl with long wavy brown hair and a pink hair clip, "
                "wearing a navy Japanese sailor school uniform, holding a smartphone in a pink case)",
    "GORO": "Goro (a chubby 28-year-old Japanese man with a buzz cut and a nervous face, wearing an ill-fitting grey suit)",
    "TEENGORO": "teenage Goro (a chubby 17-year-old Japanese boy with a buzz cut, wearing a black Japanese school uniform)",
    "NANAMI": "Nanami (a 28-year-old Japanese woman with black hair in a low ponytail, warm gentle eyes and a kind smile, "
              "wearing a light blue blouse and a navy cardigan)",
    "TEENNANAMI": "teenage Nanami (a 17-year-old Japanese girl with black hair in a high ponytail and determined eyes, "
                  "wearing a navy Japanese sailor school uniform)",
    "FUJITA": "Mr. Fujita (a thin 62-year-old Japanese man with thinning grey hair and glasses, wearing a brown tweed jacket)",
    "KURODA": "Chef Kuroda (a stern 70-year-old Japanese man, bald with a short white goatee, "
              "wearing a traditional white Japanese chef's coat and a white headband)",
    "MOM": "Mom (a gentle 55-year-old Japanese woman with short permed black hair streaked with grey, "
           "wearing a green apron over a beige sweater)",
    "KENJI": "Kenji (a 30-year-old Japanese sous chef with short spiky dark hair and an energetic grin, wearing a white chef's jacket)",
    "ARAI": "Ms. Arai (a composed 40-year-old Japanese woman restaurant manager with her hair in a neat bun, "
            "wearing a black vest over a white shirt)",
    "WAITER": "a young waiter (a slim 20-year-old Japanese man with neat short hair, wearing a black vest and a bow tie)",
    "MORI": "Director Mori (a stern 60-year-old Japanese executive with slicked-back grey hair and a hard face, wearing a dark suit)",
    "HOST": "Hana (a cute cheerful anime girl, a young woman with long pastel pink hair in twin tails tied with red ribbons, "
            "big sparkling violet eyes and rosy cheeks, wearing a pastel pink hoodie with little cat ears on the hood)",
}
REFS = {k: k.split("_")[0].lower() for k in C}
STYLE = ("modern Japanese anime illustration, manga dub video style, clean thin black line art, flat cel shading, "
         "soft muted colors, detailed simple background, 2D anime, 16:9 widescreen composition, "
         "no text, no letters, no speech bubbles, no watermark")
PORTRAIT = "character reference portrait, waist-up front view of {who}, neutral expression, plain white background, " + STYLE

CAST = {
    "narrator": "cjVigY5qzO86Huf0OWal",   # Eric: Sota telling his own story
    "sota": "cjVigY5qzO86Huf0OWal",       # Eric
    "teensota": "cjVigY5qzO86Huf0OWal",   # Eric
    "ryuji": "N2lVS1w4EtoT3dr4eOWO",      # Callum
    "teenryuji": "N2lVS1w4EtoT3dr4eOWO",  # Callum
    "mika": "cgSgspJ2msm6clMCkdW9",       # Jessica
    "teenmika": "cgSgspJ2msm6clMCkdW9",   # Jessica
    "goro": "IKne3meq5aSn9XLyUdCD",       # Charlie
    "teengoro": "IKne3meq5aSn9XLyUdCD",   # Charlie
    "nanami": "pFZP5JQG7iQjIQuC4Bku",     # Lily
    "teennanami": "pFZP5JQG7iQjIQuC4Bku", # Lily
    "fujita": "JBFqnCBsd6RMkjVDRZzb",     # George
    "kuroda": "pqHfZKP75CvOlQylNhV4",     # Bill
    "mom": "XrExE9yKIg1WjnnlVkGX",        # Matilda
    "kenji": "iP95p4xoKVk53GoZ742B",      # Chris
    "arai": "FGY2WhTYpPnrIDTdsKH5",       # Laura
    "waiter": "bIHbv24MWmeRgasZH58o",     # Will
    "mori": "nPczCjzI2devNBz1zQrb",       # Brian
    "classmate": "CwhRBWXzGAHq8TQ4Fs17",  # Roger
    "classmate2": "EXAVITQu4vr4xnSDxMaL", # Sarah
    "host": "vGQNBgLaiM3EdZtxIiuY",       # Aerisita (ElevenLabs voice library): the outro host
}
# Local placeholder voices (Kokoro), used only if ElevenLabs can't voice a line.
KOKORO = {"narrator": "am_michael", "sota": "am_michael", "teensota": "am_michael", "ryuji": "am_puck",
          "teenryuji": "am_puck", "mika": "af_nicole", "teenmika": "af_nicole", "goro": "am_echo", "teengoro": "am_echo",
          "nanami": "af_sky", "teennanami": "af_sky", "fujita": "bm_george", "kuroda": "am_onyx", "mom": "bf_emma",
          "kenji": "am_fenrir", "arai": "af_bella", "waiter": "am_liam", "mori": "bm_daniel", "classmate": "bm_fable",
          "classmate2": "af_heart", "host": "af_sky"}


def L(who, text, tone=None):
    return [who, text, {"tone": tone}] if tone else [who, text]


def S(image, *lines, pos=None, buttons=None, sfx=None):
    """One panel. pos="ryuji:l,sota:r" puts those speakers' boxes on that side (default: bottom centre)."""
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


CLASS = "in a Japanese high school classroom at lunchtime, desks and a blackboard, afternoon sunlight"
RESTO = "inside an elegant modern Japanese fine-dining restaurant in Ginza at night, warm amber lighting, dark wood and glass"
KITCHEN = "in a gleaming professional restaurant kitchen with steel counters and copper pans"
scenes = [
    # ---- Cold open ----
    S("{SOTA_CHEF} carefully plating a beautiful dish with tweezers " + KITCHEN + ", intense focus, flames from a stove behind him",
      (N, "Ten years ago, my classmates threw my lunch on the floor and called me Bento Boy.", "quiet, bitter"),
      (N, "Ten years later, they walked into my restaurant for our class reunion... and none of them knew who was cooking.", "cold, confident")),
    S("exterior of an elegant small restaurant with a wooden facade and soft lanterns on a quiet street in Ginza at night",
      (N, "My name is Sota Kanzaki. I'm twenty-eight years old, and this is Hoshizora. My restaurant.", "calm"),
      (N, "But to understand why that reunion night mattered so much... I have to start at the beginning.", "reflective")),

    # ---- High school ----
    S("{MOM} packing colorful bento boxes at dawn in a tiny cramped bento shop kitchen, {TEENSOTA} watching sleepily at the counter",
      (N, "My mother ran a tiny bento shop in our neighborhood. Every morning at five, she made a hundred lunches... and one more, for me.", "warm"),
      L("mom", "Eat every bite, Sota. Food made with care gives people strength.", "gentle, loving")),
    S("{TEENSOTA} happily opening a beautiful handmade bento box at his desk " + CLASS + ", rolled omelet, little octopus-shaped sausages and star-shaped rice",
      (N, "Her bentos were beautiful. Rolled omelet. Little octopus sausages. Rice shaped like a star.", "fond"),
      (N, "For me, it was the best part of the day.", "fond")),
    S("{TEENRYUJI} standing and holding a stolen bento box up high out of reach, grinning cruelly, {TEENSOTA} sitting at his desk looking up at him upset and helpless, {TEENGORO} laughing behind them, " + CLASS,
      L("teenryuji", "Whoa, look at this! Bento Boy's mommy made him star-shaped rice!", "mocking, loud"),
      L("teengoro", "Ha! What are you, five years old?", "laughing"), pos="teenryuji:l,teengoro:r"),
    S("{TEENMIKA} holding up her smartphone to record and giggling, " + CLASS,
      L("teenmika", "Ryuji, do it again! I wasn't recording!", "giggling, cruel")),
    S("a bento box falling upside down, rolled omelet, sausages and white rice scattering across a classroom floor, the star-shaped rice broken",
      (N, "Ryuji Takeda. Captain of the baseball team, and king of our class.", "quiet"),
      (N, "He turned my lunch upside down. Almost every day, for three years.", "hollow")),
    S("{TEENSOTA} on his knees picking rice off the classroom floor with a sad face, {TEENRYUJI} standing tall over him with his hands in his pockets sneering down, blurred classmates laughing in the background",
      L("teenryuji", "Pick it up, Bento Boy. Wouldn't want to waste mommy's love.", "sneering")),
    S("{TEENSOTA} finding his desk covered in scribbles and crumpled trash, his indoor shoes sticking out of a trash bin, empty classroom in the morning",
      (N, "Some days it was my lunch. Some days it was my desk. Some days my shoes ended up in the trash.", "flat, tired")),
    S("{TEENNANAMI} stepping in front of {TEENSOTA} with her arms spread, glaring up at {TEENRYUJI}, " + CLASS,
      L("teennanami", "Stop it, Ryuji! That's his lunch! What is wrong with you?", "angry, brave"),
      L("teenryuji", "Relax, Class Rep. It's just a joke.", "dismissive"), pos="teennanami:l,teenryuji:r"),
    S("{FUJITA} standing at the classroom door looking down at papers in his hands and pretending not to notice, students in the background",
      (N, "Our homeroom teacher, Mr. Fujita, saw everything.", "quiet"),
      (N, "He always seemed to find something very interesting to read.", "bitter, dry")),
    S("{TEENNANAMI} kneeling on the classroom floor beside {TEENSOTA}, offering him half of her rice ball with a small smile",
      L("teennanami", "Here. Take half of mine. Don't let them win, okay?", "soft, kind"),
      (N, "Nanami Yuki. The only person in that classroom who ever helped me.", "warm")),
    S("{TEENNANAMI} sitting alone at her desk while a group of girls whisper and turn their backs on her, " + CLASS,
      (N, "After that, half the class stopped talking to Nanami too. She never once complained about it.", "quiet, grateful")),
    S("{TEENSOTA} sitting alone on a school rooftop at sunset eating what is left of his bento, city in the distance",
      (N, "I ate whatever was left up on the roof, alone. It still tasted like home.", "quiet")),
    S("a lively school festival food stall, {TEENGORO} proudly selling golden curry bread in a white apron, {TEENSOTA} helping fry bread beside him, smiling",
      (N, "Strangely, the happiest memory I have from high school involves Goro Saeki, Ryuji's shadow.", "wry"),
      (N, "At the school festival, we were put on the same cooking team. His curry bread sold out in an hour.", "fond")),
    S("{TEENSOTA} standing alone behind a school festival food stall holding a tray of curry bread, looking sadly after {TEENGORO} who walks away toward {TEENRYUJI} waving impatiently in the distance, only these three people",
      L("teenryuji", "Goro! Stop playing chef with the loser and come on!", "impatient"),
      (N, "Then Ryuji called him, and Goro went. He always went.", "sad")),
    S("{TEENSOTA} with grains of rice and a brown curry sauce smudge on his school uniform sleeve, turning away awkwardly, {MOM} looking at him with worry, tiny bento shop at night",
      L("mom", "Sota... is something wrong at school?", "worried"),
      L("teensota", "No. Everything's fine. Your omelet was really good today.", "forced cheerful"),
      (N, "I never told her. I didn't want her to stop making them.", "soft"), pos="mom:l,teensota:r"),
    S("{TEENSOTA} standing alone under cherry blossom trees holding a graduation diploma tube, classmates taking selfies far behind him, nobody looking at him",
      (N, "On graduation day, nobody asked for a photo with me. And I didn't look back.", "quiet")),
    S("{MOM} handing {TEENSOTA} an old kitchen knife wrapped in a white cloth in the bento shop, both serious",
      L("mom", "This was your grandfather's knife. If you want to cook, then cook for real. Cooking is how we take care of people.", "gentle, serious"),
      L("teensota", "I'll make you proud, Mom. I promise.", "determined"), pos="mom:l,teensota:r"),

    # ---- Training in Kyoto ----
    S("{TEENSOTA_KITCHEN} bowing deeply in front of {KURODA} in a traditional Kyoto restaurant kitchen with wooden counters",
      (N, "I went to Kyoto and begged the strictest chef in the city to take me in. Chef Kuroda.", "determined"),
      L("kuroda", "Hah. You want to cook? First you wash dishes. For one year. Then we'll talk.", "gruff")),
    S("{TEENSOTA_KITCHEN} washing a huge mountain of dishes alone late at night in a traditional kitchen, exhausted, sleeves rolled up, soap suds everywhere",
      (N, "So I washed dishes. Then I peeled vegetables. Then I scaled fish until I couldn't feel my fingers.", "tired")),
    S("{KURODA} wrapping a clean white bandage around {TEENSOTA_KITCHEN}'s hand that has a small pink burn mark, stern but caring, traditional kitchen",
      L("kuroda", "Burns heal. Regret doesn't. Back to the stove.", "gruff, caring")),
    S("{TEENSOTA_KITCHEN} talking on an old phone in a tiny dark dormitory room at night, smiling tiredly",
      L("mom", "Are you eating properly, Sota? You sound so tired.", "worried, warm"),
      L("teensota", "I'm fine, Mom. I'm cooking every day. I'm happy.", "tired, sincere")),
    S("{KURODA} pouring a bowl of soup into the sink in front of {SOTA_CHEF}, traditional Kyoto kitchen, tense",
      L("kuroda", "Again. This soup has no heart. Tell me, who are you cooking for?", "stern"),
      L("sota", "...For the person eating it.", "thinking"), pos="kuroda:l,sota:r"),
    S("{SOTA_CHEF} alone in a kitchen at dawn practicing a Japanese rolled omelet in a square pan, dozens of omelets lined up on the counter",
      (N, "Every night after closing, I practiced my mother's rolled omelet. A thousand times. Maybe more.", "quiet, determined")),
    S("{KURODA} tasting a slice of rolled omelet with chopsticks and giving a rare small smile, {SOTA_CHEF} waiting nervously",
      L("kuroda", "...Now that's food. Seven years, kid. Took you long enough.", "gruff, proud")),
    S("{SOTA_CHEF} standing in an empty bare new restaurant space with exposed walls, holding a set of keys, morning light",
      (N, "At twenty-six, with every yen I'd saved and a loan that terrified me, I opened Hoshizora in Ginza.", "hopeful")),
    S("{SOTA_CHEF}, {KENJI} and {ARAI} celebrating in the restaurant kitchen, Kenji holding up a phone excitedly",
      (N, "Two years later, we earned a star in the most famous restaurant guide in the country.", "proud, quiet"),
      L("kenji", "Chef! The reporters are calling again. They want a photo of you!", "excited"),
      L("sota", "No photos. The food is what matters. Not my face.", "calm"), pos="kenji:l,sota:r"),
    S("{ARAI} smiling knowingly while holding a tablet, " + RESTO,
      L("arai", "The mysterious faceless chef of Ginza. The magazines love it, you know.", "amused"),
      (N, "I never showed my face. Partly because I'm shy... and partly because I never wanted people staring at me again.", "honest")),

    # ---- The invitation ----
    S("{SOTA} sitting on a sofa in a simple apartment at night, his phone lighting up with many notifications",
      (N, "Then one night, my phone buzzed. A group chat I'd forgotten even existed. Class 3-B.", "curious")),
    S("close-up of a smartphone screen showing a group chat full of colorful message bubbles and party emojis",
      L("ryuji", "Ten-year reunion, guys! I booked Hoshizora in Ginza. The one with the star. Company card, so don't worry about money!", "bragging, loud"),
      L("mika", "Oh my god, Ryuji, you're amazing! I'll stream the whole thing for my followers!", "gushing")),
    S("close-up of {SOTA} staring at his phone in shock, the screen light on his face",
      (N, "Ryuji had booked my restaurant. For our reunion.", "stunned")),
    S("close-up of a smartphone screen showing a group chat with laughing emojis",
      L("goro", "Should we invite Kanzaki too?", "nervous"),
      L("ryuji", "Sure, invite Bento Boy! He's probably stacking shelves at a convenience store. We could use a laugh.", "mocking"),
      L("mika", "Bento Boy! I bet he still eats his mommy's lunches!", "mocking")),
    S("{SOTA} gripping his phone tightly, then a calm cold smile spreading across his face, apartment at night",
      (N, "Ten years. And they hadn't changed at all.", "cold"),
      (N, "I typed two words. I'll come.", "calm, cold")),
    S("{SOTA_CHEF} talking to {KENJI} and {ARAI} " + KITCHEN + ", Kenji looking shocked",
      L("sota", "The Takeda reservation next Saturday. Forty guests. It's my high school reunion.", "calm"),
      L("kenji", "Wait, they don't know this is your restaurant?", "surprised"),
      L("sota", "No. And don't tell them. That night, I'm just a guest.", "calm, firm"), pos="kenji:r,sota:l"),
    S("{ARAI} raising an eyebrow with a knowing smile, {SOTA_CHEF} beside her, " + KITCHEN,
      L("arai", "Understood, Chef. And who's cooking?", "amused"),
      L("sota", "I'll prepare everything in the afternoon. Kenji will plate. And for the final course... I'll come back to my kitchen.", "determined")),
    S("{MORI} sitting behind a large desk glaring at {RYUJI} who stands at attention, a flashy real estate company office",
      L("mori", "Takeda. The building on Namiki Street. Whoever controls Hoshizora controls that lease. Get their signature by the end of the month, or don't bother coming back.", "cold, stern"),
      L("ryuji", "Leave it to me, Director! I'm throwing a party there on Saturday. I'll charm the owner myself!", "overconfident"),
      pos="mori:l,ryuji:r"),
    S("{RYUJI} grinning confidently to himself in an office corridor, adjusting his gold bracelet",
      (N, "I found out later that Ryuji had his own plan for that night. And it depended entirely on me. He just didn't know it yet.", "dry")),

    # ---- Reunion night ----
    S("well-dressed young adults arriving at the entrance of an elegant Ginza restaurant at night, {RYUJI} at the door greeting people like a host, {MIKA} filming with her phone",
      (N, "Saturday night. Forty classmates in their best clothes, and Ryuji standing at the door like he owned the place.", "dry")),
    S("{RYUJI} pointing and laughing at {SOTA} who just walked in, restaurant entrance at night",
      L("ryuji", "No way! Bento Boy actually came! Look at that sweater! Did you get lost on your way to work?", "mocking, loud"),
      pos="ryuji:l"),
    S("{MIKA} holding her phone close to {SOTA}'s face to film him, fake smile, " + RESTO,
      L("mika", "Hi everyone! This is Bento Boy, the class loser I told you about! Say hi to my two hundred thousand followers!", "fake cheerful"),
      L("sota", "...Hello.", "calm"), pos="mika:l,sota:r"),
    S("{GORO} awkwardly patting {SOTA} on the shoulder, sweating nervously, " + RESTO,
      L("goro", "H-hey, Kanzaki. Long time. Ryuji's paying, so, uh... just enjoy it, I guess.", "awkward"),
      (N, "Goro Saeki. Ryuji's shadow in high school. Apparently, he still was. He worked under Ryuji at the same company.", "dry"),
      pos="goro:l"),
    S("{NANAMI} waving and smiling warmly at {SOTA} across the room, " + RESTO,
      L("nanami", "Sota! You came! I'm so glad. You look really well.", "warm, happy"),
      (N, "And then there was Nanami. Ten years later, she still had the kindest smile in the room.", "soft")),
    S("{NANAMI} and {SOTA} sitting side by side at the end of a long dinner table, talking quietly, other guests chatting, " + RESTO,
      L("nanami", "I'm a teacher now. Third grade. I keep thinking about our class... and I tell my kids never to look away.", "thoughtful"),
      L("sota", "You never did. Not once.", "gentle"), pos="nanami:l,sota:r"),
    S("a friendly classmate in a suit leaning across the table to talk to {SOTA}, {RYUJI} listening nearby with a smirk, " + RESTO,
      L("classmate", "So, Kanzaki, what do you do these days?", "friendly"),
      L("sota", "I cook.", "calm"),
      L("ryuji", "A cook! Like at a family restaurant? Flipping burgers? Ha! Fits you perfectly!", "mocking, laughing")),
    S("{FUJITA} sitting stiffly at the dinner table holding a menu in front of his face, avoiding eye contact, " + RESTO,
      (N, "Mr. Fujita had come too. He looked at me once... and then found his menu very interesting.", "dry")),
    S("{RYUJI} showing off a gold watch to a group of impressed classmates at the table, " + RESTO,
      L("ryuji", "This? Just a little reward from my company. Top salesman three years in a row. I'm about to close the biggest deal of my life.", "boastful")),
    S("{RYUJI} standing and raising a wine glass to toast loudly, guests looking up at him, " + RESTO,
      L("ryuji", "Everyone! Tonight's on me! Order whatever you want. When you're as successful as me, money is nothing!", "boastful, loud")),
    S("{RYUJI} rudely snapping his fingers at {WAITER} who rushes over with a menu, " + RESTO,
      L("ryuji", "Hey, you! Bring us your most expensive wine. And hurry up, I'm paying your salary tonight!", "rude"),
      L("waiter", "Y-yes, sir. Right away.", "nervous"), pos="ryuji:l,waiter:r"),
    S("{WAITER} accidentally spilling a few drops of water near {RYUJI}'s sleeve, Ryuji jumping up furious, " + RESTO,
      L("ryuji", "Are you an idiot?! This suit costs more than you make in a month!", "shouting, furious"),
      L("waiter", "I'm so sorry, sir!", "frightened"), pos="ryuji:l,waiter:r"),
    S("close-up of {SOTA}'s calm face with cold angry eyes, his hand gripping the edge of the table",
      (N, "My staff. In my restaurant.", "cold anger"),
      L("sota", "Ryuji. It was an accident. He apologized. That's enough.", "calm, firm")),
    S("{RYUJI} leaning over {SOTA} and sneering down at him, {MIKA} laughing and filming behind, " + RESTO,
      L("ryuji", "Oh? Bento Boy's giving me orders now? You probably can't even afford the water here.", "mocking"),
      L("mika", "Oh, burn! Chat is loving this!", "laughing"), pos="ryuji:l,mika:r"),
    S("close-up of {SOTA} quietly speaking to {WAITER} near the wall, the waiter looking relieved, " + RESTO,
      L("sota", "You did nothing wrong. Take a five-minute break. Tell Ms. Arai I said so.", "quiet, kind"),
      L("waiter", "...Thank you, sir.", "relieved, confused")),
    S("close-up of a smartphone livestream screen held in a hand with long nails, floating hearts and a stream of comments",
      (N, "Mika's livestream had thousands of viewers. She was sure it made Ryuji look like a king.", "dry")),
    S("elegant dishes being served on a long table: sea bream sashimi with yuzu, grilled wagyu on charcoal, delicate soup in lacquer bowls, guests amazed, " + RESTO,
      (N, "The first courses came out. Sea bream with yuzu. Wagyu grilled over charcoal. A clear soup I'd simmered since morning.", "proud"),
      (N, "The room went quiet, the way it always does when people taste something real.", "satisfied")),
    S("{NANAMI} tasting soup with her eyes closed and a moved expression, {SOTA} watching her, " + RESTO,
      L("nanami", "This is incredible. It tastes... warm. Like someone made it just for me.", "moved"),
      L("sota", "That's the best compliment a cook can get.", "soft"), pos="nanami:l,sota:r"),
    S("{RYUJI} whispering to {GORO} with a scheming grin, Goro looking nervous, " + RESTO,
      L("ryuji", "Watch this, Goro. I'll call the owner out here, get that lease signed in front of everyone, and get promoted by Monday.", "scheming"),
      L("goro", "R-Ryuji, maybe not tonight...", "nervous"), pos="ryuji:l,goro:r"),
    S("{RYUJI} arrogantly waving {ARAI} over to the table, " + RESTO,
      L("ryuji", "You, manager! Tell the owner to come out here. Takeda Real Estate wants a word.", "arrogant"),
      L("arai", "Certainly, sir. The chef will greet everyone with the final course.", "polite, faintly amused"), pos="ryuji:l,arai:r"),
    S("{SOTA} quietly standing up from the table and placing his napkin down, {RYUJI} laughing at him, " + RESTO,
      L("sota", "Excuse me for a moment.", "calm"),
      L("ryuji", "Bathroom break, Bento Boy? Don't steal the towels!", "mocking")),
    S("{SOTA_CHEF} buttoning a white chef's jacket " + KITCHEN + ", {KENJI} grinning and holding out a black apron",
      L("kenji", "Ready, Chef?", "excited"),
      L("sota", "Ready. Let's serve the last course.", "calm, determined"), pos="kenji:l,sota:r"),

    # ---- The reveal ----
    S("the dining room lights dimming, a spotlight on the kitchen door, {ARAI} standing beside it formally, guests turning to look, " + RESTO,
      L("arai", "Ladies and gentlemen, the owner and head chef of Hoshizora... Chef Sota Kanzaki.", "formal, proud")),
    S("{SOTA_CHEF} walking out through the kitchen door in a spotlight carrying a black lacquered bento box, {KENJI} and staff behind him carrying more",
      (N, "I walked out of my own kitchen, in my own chef's jacket.", "calm, powerful")),
    S("a long dinner table of shocked well-dressed classmates with jaws dropped and wide eyes, " + RESTO,
      L("classmate", "Wait... Kanzaki?! Bento Boy is the chef?!", "shocked"),
      L("classmate2", "The faceless chef from the magazines... is him?", "stunned")),
    S("{RYUJI} frozen in shock with a wine glass slipping from his fingers, " + RESTO,
      L("ryuji", "N-no way... that's impossible...", "stammering")),
    S("{MIKA} pale and panicking while staring at her phone screen full of exploding comments, " + RESTO,
      L("mika", "W-wait, chat, this is... um...", "panicked"),
      (N, "Mika's live chat exploded. Thousands of people had just watched her call the chef a loser.", "dry")),
    S("{SOTA_CHEF} calmly placing black lacquered bento boxes in front of each guest at the long table, " + RESTO,
      L("sota", "Tonight's final course. A bento.", "calm"),
      L("sota", "Rolled omelet. Little octopus sausages. And rice shaped like a star.", "calm, meaningful")),
    S("close-up of a luxurious lacquered bento box with golden rolled omelet, octopus-shaped sausages, seasonal vegetables and star-shaped rice",
      (N, "My mother's bento. The one they threw on the floor almost every day for three years.", "quiet, emotional"),
      (N, "Made with the finest ingredients I could find.", "quiet, proud")),
    S("classmates staring down at their bento boxes with guilty faces, one woman with tears in her eyes, " + RESTO,
      L("classmate2", "This is... the lunch from back then...", "quiet, guilty")),
    S("{MOM} wearing a nice dress, sitting at the restaurant's wooden chef's counter as guest of honor, smiling proudly with teary eyes",
      (N, "And at the counter sat my guest of honor. My mother.", "warm"),
      L("mom", "It's even better than mine, Sota.", "moved, proud")),

    # ---- Ryuji ----
    S("{RYUJI} rushing up to {SOTA_CHEF} with a huge fake smile and bowing repeatedly, " + RESTO,
      L("ryuji", "Sota! Buddy! Ha ha, you got me good! We were always friends, right? Listen, about the building lease...", "fake friendly, desperate"),
      pos="ryuji:l"),
    S("{SOTA_CHEF} looking calmly down at {RYUJI} who is sweating and wringing his hands, " + RESTO,
      L("sota", "The building on Namiki Street?", "calm"),
      L("ryuji", "Yes! If you sign with Takeda Real Estate, I'll make it worth your while! Anything you want!", "desperate"),
      pos="sota:r,ryuji:l"),
    S("close-up of {SOTA_CHEF} speaking calmly with quiet strength, restaurant background",
      L("sota", "I don't control the lease, Ryuji.", "calm"),
      L("sota", "I bought the building. Last month.", "calm, final")),
    S("close-up of {RYUJI} turning pale white and sweating heavily, mouth open in shock",
      (N, "Ryuji's face went the color of my rice.", "dry")),
    S("{RYUJI} answering his ringing phone with a trembling hand, " + RESTO,
      L("mori", "Takeda. I'm watching a livestream. You're screaming at a waiter in the restaurant we've been trying to win over for six months.", "cold fury"),
      L("ryuji", "D-Director, I can explain...", "panicked")),
    S("{MORI} on the phone in a dark office at night, furious, a laptop showing a livestream in front of him",
      L("mori", "The owner of that building just declined all further talks with our company. You'll explain that on Monday. In my office. With your resignation letter.", "icy")),
    S("{RYUJI} slumped on his knees on the restaurant floor with his phone fallen beside him, guests staring, " + RESTO,
      (N, "Ten years ago, Ryuji made me kneel on a classroom floor.", "quiet"),
      (N, "Tonight, nobody made him do anything.", "quiet, final")),
    S("{RYUJI} pointing at {SOTA_CHEF} and shouting in desperation, {ARAI} stepping forward calmly, " + RESTO,
      L("ryuji", "This is fake! He's just a cook in a costume!", "desperate, shouting"),
      L("arai", "Sir, Chef Kanzaki owns this restaurant. And this building. Please lower your voice. There are other guests tonight.", "cool, polite"),
      pos="ryuji:l,arai:r"),

    # ---- Mika ----
    S("{MIKA} rushing to {SOTA_CHEF} holding up her phone with a forced sweet smile, " + RESTO,
      L("mika", "Sota! Let's do a collab! 'Famous chef reunites with his high school friends!' My followers would love it!", "fake sweet"),
      pos="mika:l"),
    S("{SOTA_CHEF} gently pushing down {MIKA}'s phone with one hand, calm and firm, " + RESTO,
      L("sota", "Mika. You filmed me picking rice off the floor for three years.", "calm"),
      L("sota", "My kitchen isn't a backdrop for your stream. Please put your phone away.", "firm")),
    S("{MIKA} staring at her phone in horror as angry comments flood in, mascara running, " + RESTO,
      (N, "By the next morning, three of Mika's sponsors had quietly dropped her.", "dry")),

    # ---- Goro ----
    S("{GORO} bowing deeply in front of {SOTA_CHEF}, trembling, " + RESTO,
      L("goro", "Kanzaki... I'm sorry. I held your arms while Ryuji did it. I laughed because I was scared I'd be next.", "ashamed, shaky"),
      L("goro", "I've followed him my whole life. I'm so tired of it.", "broken")),
    S("{SOTA_CHEF} looking thoughtfully at {GORO}, " + RESTO,
      L("sota", "Goro. Do you remember the school festival? Your curry bread sold out in an hour.", "thoughtful"),
      L("goro", "...You remember that?", "surprised"), pos="sota:r,goro:l"),
    S("{SOTA_CHEF} holding out his hand to {GORO} who stares at it with teary eyes, " + RESTO,
      L("sota", "If you're serious about changing, come to my kitchen on Monday. You'll start by washing dishes. Like I did.", "calm, kind"),
      L("goro", "...Yes, Chef!", "tearful, determined"), pos="sota:r,goro:l"),

    # ---- Mr. Fujita ----
    S("{FUJITA} approaching {SOTA_CHEF} and bowing low, ashamed, " + RESTO,
      L("fujita", "Kanzaki... I saw what they did to you. Every day. And I pretended I didn't. I'm truly sorry.", "ashamed, old"),
      pos="fujita:l"),
    S("{SOTA_CHEF} answering {FUJITA} calmly, {NANAMI} watching in the background, " + RESTO,
      L("sota", "Thank you for saying it, Mr. Fujita.", "calm"),
      L("sota", "Nanami teaches her students never to look away. Maybe you could learn that from her too.", "gentle, firm")),

    # ---- Nanami ----
    S("{NANAMI} and {SOTA_CHEF} standing on a restaurant rooftop terrace at night with the Tokyo city lights behind them",
      L("nanami", "You know, back then, I always wanted to taste your mom's bento. It looked so beautiful.", "shy"),
      L("sota", "Then this one was made for you.", "warm"), pos="nanami:l,sota:r"),
    S("close-up of {NANAMI} tasting a piece of rolled omelet with chopsticks, tears in her eyes and a smile, rooftop at night",
      L("nanami", "It's sweet... and a little salty. Like crying and laughing at the same time.", "moved")),
    S("{SOTA_CHEF} smiling shyly and rubbing the back of his neck, rooftop at night with city lights",
      L("sota", "Nanami. You shared your rice ball with me when nobody else would. I never forgot.", "soft"),
      L("sota", "Would you come back next Sunday? The restaurant's closed. I'd like to cook just for you.", "shy")),
    S("close-up of {NANAMI} blushing with a happy smile, city lights sparkling behind her",
      L("nanami", "...I'd love that.", "happy, shy")),

    # ---- Epilogue ----
    S("{GORO} in a white apron and cap earnestly washing dishes " + KITCHEN + ", {KENJI} watching with an approving grin",
      (N, "One month later. Goro shows up an hour early every day.", "amused"),
      (N, "He's already better at curry bread than I am.", "amused, fond")),
    S("{RYUJI} in a worn blue work uniform carrying heavy cardboard boxes into a moving truck, tired and sweating, daytime street",
      (N, "Ryuji lost his job. I heard he's carrying boxes for a moving company now.", "neutral"),
      (N, "Honest work. Maybe it'll be good for him.", "neutral")),
    S("{MIKA} without makeup sitting in front of a phone on a tripod in her bedroom, recording a tearful apology video",
      (N, "Mika posted an apology video. To be fair... it was the most honest thing she'd ever posted.", "dry")),
    S("a cozy renovated little bento shop with a long line of happy customers outside in the morning, {MOM} handing bentos over the counter, {SOTA} helping beside her",
      (N, "And my mother's little bento shop? We rebuilt it. Now there's a line out the door every morning.", "warm"),
      L("mom", "A hundred lunches... and one more, for you.", "warm, teasing")),
    S("{SOTA_CHEF} cooking at the counter of an empty restaurant on a sunny afternoon while {NANAMI} sits at the counter laughing, cozy warm light",
      (N, "Every Sunday, the restaurant is closed. And every Sunday, I cook for one very special guest.", "warm")),
    S("{SOTA} smiling warmly at the viewer, soft evening light, restaurant lanterns behind him",
      (N, "They called me Bento Boy to make me feel small. I turned it into the thing I'm proudest of.", "warm, proud"),
      (N, "If someone who bullied you showed up asking for a favor... what would you do? Tell me in the comments.", "warm, inviting")),

    # ---- Outro: the channel's host girl ----
    S("{HOST} waving happily at the viewer with both hands and a big smile, sparkles and little pink hearts floating around her, "
      "bright pastel pink and lavender background with soft bokeh lights, upper body",
      L("host", "Thanks for watching~!", "cheerful, cute, sing-song"),
      L("host", "If Sota's story made you hungry, please like, subscribe, and tap the bell, so you never miss the next one!", "bubbly, excited"),
      pos="host:t", buttons=[
          {"text": "LIKE", "line": 1, "delay": 1.4, "x": 0.27, "y": 0.84, "fill": "#3EA6FF"},
          {"text": "SUBSCRIBE", "line": 1, "delay": 1.9, "x": 0.53, "y": 0.84, "press": 1.6, "pressed": "SUBSCRIBED"},
          {"icon": "bell", "line": 1, "delay": 2.9, "x": 0.76, "y": 0.84}],
      sfx=[{"sound": "pop", "at": "line:1+1.4", "volume": 0.5}, {"sound": "pop", "at": "line:1+1.9", "volume": 0.5},
           {"sound": "tap", "at": "line:1+3.5", "volume": 0.6}, {"sound": "ding", "at": "line:1+2.9", "volume": 0.45}]),
    S("{HOST} winking playfully and making a heart shape with both hands, floating hearts and sparkles, "
      "bright pastel pink background with soft bokeh lights, upper body",
      L("host", "Oh! And if you want to see Sota and Nanami's Sunday dinner, comment HOSHIZORA down below!", "playful, excited, winking"),
      L("host", "See you in the next story! Bye-bye!", "sweet, cheerful"),
      pos="host:t", buttons=[{"text": 'COMMENT "HOSHIZORA" FOR PART 2!', "line": 0, "delay": 2.6, "x": 0.5, "y": 0.84,
                              "fill": "#FFD43B", "ink": "#141414"}],
      sfx=[{"sound": "pop", "at": "line:0+2.6", "volume": 0.5}, {"sound": "chime", "at": "line:1", "volume": 0.35}]),
]

spec = {
    "title": "They Called Me 'Bento Boy' for 3 Years... 10 Years Later, They Booked My Restaurant for Our Reunion [Manga Dub]",
    "character": "", "style": "",
    "width": 1920, "height": 1080, "title_card": False,
    "tts": "kokoro", "cast": KOKORO, "speed": 0.95, "scene_pad": 0.7,
    "emotive": {"engine": "eleven_v3", "cast": CAST, "skip": [], "fallback": True,
                "priority": ["narrator", "sota", "ryuji", "mika", "nanami", "goro", "mom", "kuroda", "arai", "mori"]},
    "caption": {"mode": "boxes", "font": "Comic Neue", "fonts_dir": "assets/fonts"},
    "images": {"provider": "local", "upscale": True},
    "characters": {REFS[k]: PORTRAIT.format(who=C[k]) for k in C if "_" not in k},
    "music": {"sound": "music_strategy", "volume": 0.03},
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
