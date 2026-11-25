"""Builds script.json for FURUSATO, a standalone ~18-minute "manga dub" story video (16:9).

Run: python3 projects/manga/furusato/build.py
Original story and characters, in the style of office-drama manga dubs: one illustrated panel per beat, the hero
narrating in first person in a white box at the top, the other characters speaking in white boxes near the bottom.
Every line is acted with ElevenLabs v3 (the narrator is Haruto himself, in his own voice).
Images are drawn locally with FLUX.2 klein (tools/flux_local.py), each from the scene prompt plus the reference
portraits of the characters in it, so faces and outfits stay the same from panel to panel.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = "narrator"

# Fixed character descriptions, repeated in every prompt; the key before "_" names the reference portrait used.
C = {
    "HARUTO": "Haruto (a 28-year-old Japanese man with short neat black hair, kind dark eyes and a slim build, "
              "wearing a navy business suit, white shirt and dark blue tie)",
    "HARUTO_HOME": "Haruto (a 28-year-old Japanese man with short neat black hair, kind dark eyes and a slim build, "
                   "wearing a plain grey hoodie and dark trousers)",
    "DAICHI": "Daichi (a tall 28-year-old Japanese man with styled wavy light-brown hair and a confident smirk, "
              "wearing a light grey slim-fit suit, maroon tie and a silver wristwatch)",
    "ERIKA": "Erika (a 27-year-old Japanese woman with long wavy chestnut-brown hair and red lipstick, "
             "wearing a cream silk blouse, beige skirt and gold earrings)",
    "SAKI": "Saki (a 25-year-old Japanese woman with shoulder-length dark brown hair with a small hair clip, round glasses "
            "and a gentle face, wearing a light pink cardigan over a white blouse)",
    "OKABE": "Section Chief Okabe (a chubby balding 55-year-old Japanese man with a thin mustache and a stern face, "
             "wearing a brown suit)",
    "MIO": "Mio (a cheerful 20-year-old Japanese woman with long black hair in a high ponytail, "
           "wearing an oversized yellow hoodie)",
    "DAD": "Dad (a 58-year-old Japanese man with short grey hair, thick eyebrows and glasses pushed up on his forehead, "
           "wearing a dark green work jacket)",
    "MOM": "Mom (a warm 55-year-old Japanese woman with black hair in a low bun and a kind smile, "
           "wearing a lavender sweater and a white apron)",
    "PRESIDENT": "President Shiraishi (a dignified 65-year-old Japanese man with slicked-back white hair, "
                 "wearing a black three-piece suit)",
}
REFS = {k: k.split("_")[0].lower() for k in C}
STYLE = ("modern Japanese anime illustration, manga dub video style, clean thin black line art, flat cel shading, "
         "soft muted colors, detailed simple background, 2D anime, 16:9 widescreen composition, "
         "no text, no letters, no speech bubbles, no watermark")
PORTRAIT = "character reference portrait, waist-up front view of {who}, neutral expression, plain white background, " + STYLE

CAST = {
    "narrator": "TX3LPaxmHKxFdv7VOQHJ",   # Liam: Haruto telling his own story
    "haruto": "TX3LPaxmHKxFdv7VOQHJ",     # Liam
    "daichi": "iP95p4xoKVk53GoZ742B",     # Chris
    "erika": "FGY2WhTYpPnrIDTdsKH5",      # Laura
    "saki": "EXAVITQu4vr4xnSDxMaL",       # Sarah
    "okabe": "N2lVS1w4EtoT3dr4eOWO",      # Callum
    "mio": "cgSgspJ2msm6clMCkdW9",        # Jessica
    "dad": "pqHfZKP75CvOlQylNhV4",        # Bill
    "mom": "XrExE9yKIg1WjnnlVkGX",        # Matilda
    "president": "nPczCjzI2devNBz1zQrb",  # Brian
    "engineer": "bIHbv24MWmeRgasZH58o",   # Will
    "kitano": "CwhRBWXzGAHq8TQ4Fs17",     # Roger
    "anchor": "onwK4e9ZLuTAKqWW03F9",     # Daniel
}
# Local placeholder voices (Kokoro), used only if ElevenLabs can't voice a line.
KOKORO = {"narrator": "am_michael", "haruto": "am_michael", "daichi": "am_puck", "erika": "af_nicole", "saki": "af_sky",
          "okabe": "am_onyx", "mio": "af_bella", "dad": "bm_george", "mom": "bf_emma", "president": "bm_daniel",
          "engineer": "am_echo", "kitano": "am_fenrir", "anchor": "bm_fable"}


def L(who, text, tone=None):
    return [who, text, {"tone": tone}] if tone else [who, text]


def S(image, *lines, pos=None):
    """One panel. pos="daichi:l,erika:r" puts those speakers' boxes on that side (default: bottom centre)."""
    lines = [L(*l) for l in lines]  # (who, text, tone) tuples -> the same form as L()
    sc = {"image": image.format(**C) + ", " + STYLE, "lines": [list(l) for l in lines],
          "refs": sorted({REFS[k] for k in re.findall(r"\{(\w+)\}", image)})}
    if pos:
        sc["pos"] = dict(p.split(":") for p in pos.split(","))
    return sc


OFFICE = "in a bright modern Japanese open-plan office"
scenes = [
    # ---- Cold open ----
    S("{HARUTO} standing alone in the rain at night holding a cardboard box of office belongings, soaked, empty eyes, city lights behind him",
      (N, "In one week, I lost my project, my wife, and my job.", "quiet, bitter"),
      (N, "And the man who took all three... was my best friend.", "slow, bitter")),
    S("exterior of a tall modern glass office building in Tokyo on a sunny morning, salarymen walking in",
      (N, "My name is Haruto Mizuki. I'm twenty-eight, and I work in the product planning department at Hikari Electric, a company that makes small home appliances.")),
    S("{HARUTO} at his desk late at night " + OFFICE + ", only his desk lamp on, a sleek white compact rice cooker prototype and design drawings on the desk, tired but focused",
      (N, "For the past year, I'd poured everything into one project. A compact rice cooker that makes perfect rice in just fifteen minutes."),
      (N, "We called it Project Hinata.", "proud")),
    S("{DAICHI} leaning casually on the side of {HARUTO}'s desk holding two cans of coffee, grinning, " + OFFICE + " at night",
      (N, "And this is Daichi Kurosawa. My best friend since university. He worked in sales, two floors down."),
      L("daichi", "Still here, Haruto? At this rate you're going to marry that rice cooker.", "teasing, laughing"),
      L("haruto", "Very funny. The presentation is on Friday. It has to be perfect.", "tired laugh"), pos="daichi:l,haruto:r"),
    S("close-up of {DAICHI} smiling warmly and holding out his hand, office at night",
      L("daichi", "Relax. If anyone can pull it off, it's you. Hey, send me your files. I'll double-check the sales numbers for you.", "friendly"),
      L("haruto", "Really? Thanks, Daichi. You're a lifesaver.", "grateful")),
    S("{HARUTO} smiling as he clicks send on his laptop, a file transfer progress bar on the screen, office at night",
      (N, "I didn't think twice. Daichi had always been there for me.", "warm"),
      (N, "Or so I thought.", "dark")),
    S("{SAKI} shyly handing a blue folder to {HARUTO} at his desk, she is blushing slightly, " + OFFICE + " in the evening",
      L("saki", "Um, Mizuki-san... I double-checked the cost sheets for Hinata. Everything matches.", "shy, soft"),
      L("haruto", "Thank you, Aoyama-san. You didn't have to stay late for this.", "kind"),
      L("saki", "I wanted to. I... really believe in this project.", "shy"), pos="saki:l,haruto:r"),
    S("close-up of {SAKI} adjusting her round glasses and smiling to herself, office background",
      (N, "Saki Aoyama, from accounting. Quiet, careful, and one of the few people who ever noticed my work.")),
    S("{HARUTO_HOME} entering a modern Tokyo apartment living room at night, {ERIKA} lying on the sofa scrolling her phone and not looking up",
      (N, "At home, my wife Erika was waiting for me. Well... waiting might be the wrong word.", "wry"),
      L("haruto", "I'm home. Sorry I'm late again.", "tired"),
      L("erika", "Mm. There's leftover curry in the fridge.", "uninterested")),
    S("{HARUTO_HOME} sitting at the end of the sofa talking hopefully to {ERIKA} who keeps looking at her phone, apartment at night",
      L("haruto", "The presentation's this Friday. If it goes well, I might get promoted. We could finally take that trip to Okinawa.", "hopeful"),
      L("erika", "Sure. If.", "dismissive"), pos="haruto:l,erika:r"),
    S("close-up of a smartphone lying on a glass coffee table, its screen lit with a new message notification showing a pink heart emoji, dark apartment",
      (N, "Her phone buzzed. She turned it face down before I could see it.", "uneasy"),
      (N, "I told myself it was nothing.", "quiet")),

    # ---- The theft ----
    S("large corporate conference room full of executives in suits around a long table, a projector screen at the front, {OKABE} sitting at the head of the table",
      (N, "Friday came. The whole department gathered in the big conference room. Even the company president was there.")),
    S("{PRESIDENT} sitting at a conference table with his hands folded, calm and observant, executives beside him",
      (N, "President Shiraishi. A man who almost never spoke in meetings. But when he did, everyone listened.")),
    S("{OKABE} standing at the head of the conference table and gesturing toward the door, executives watching",
      L("okabe", "Before Mizuki begins, Kurosawa from sales has asked to present a new product idea.", "pompous")),
    S("{DAICHI} standing confidently in front of a projector screen showing a white compact rice cooker design, presenting to a conference room",
      L("daichi", "Thank you, Chief. Ladies and gentlemen... allow me to introduce Project Hinata.", "confident, showman")),
    S("close-up of {HARUTO} sitting at the conference table frozen in shock, eyes wide, sweat on his face",
      (N, "My slides. My data. My fifteen-minute rice cooker. Every word of it... was mine.", "stunned"),
      L("haruto", "Daichi... what are you doing?", "whispering, shocked")),
    S("{DAICHI} smiling smugly at the projector screen while executives nod approvingly",
      L("daichi", "I came up with the concept while talking to our customers. After all, sales knows what people really want.", "smug")),
    S("{HARUTO} standing up suddenly from his chair in the conference room, slamming his hands on the table, angry, executives turning to look",
      L("haruto", "That's my proposal! I've been working on Hinata for a whole year!", "shouting")),
    S("{OKABE} glaring and pointing at someone across the conference table, angry red face",
      L("okabe", "Mizuki! Sit down! Do you have any proof?", "angry"),
      L("haruto", "The files are on my computer. The timestamps will show...", "desperate")),
    S("{DAICHI} holding up a tablet showing a file list, looking calm and amused, conference room",
      L("daichi", "Funny. My files are dated a whole month before yours.", "smug, calm")),
    S("{HARUTO} sitting back down, pale and trembling, staring at the table, conference room",
      (N, "He'd sent my files to himself and changed the dates. The same files I'd given him to check the sales numbers.", "bitter")),
    S("{PRESIDENT} looking thoughtfully across the room, eyes narrowed, hand on his chin",
      L("president", "...Interesting. We will discuss this later.", "calm, thoughtful"),
      (N, "He said nothing more. But I noticed he was looking at me. Not at Daichi.")),
    S("{HARUTO} grabbing {DAICHI}'s arm in an empty office hallway, Haruto angry and hurt, Daichi turning around",
      L("haruto", "Daichi! Why? We've been friends for ten years!", "hurt, angry"),
      L("daichi", "Friends? Haruto, you were always the smart one. Top of the class. Everyone's favorite. Do you have any idea how that felt?", "bitter"),
      pos="haruto:l,daichi:r"),
    S("close-up of {DAICHI} leaning in with a cold sneer, office hallway, dramatic shadow over his eyes",
      L("daichi", "This time, I win. And Hinata isn't the only thing I'm taking from you.", "cold whisper"),
      L("haruto", "What's that supposed to mean?", "confused")),
    S("{DAICHI} walking away down an office hallway, waving over his shoulder without looking back",
      L("daichi", "You'll find out. Go home early today, buddy.", "mocking")),
    S("{SAKI} standing at the corner of the hallway holding a folder to her chest, looking worried at {HARUTO}",
      L("saki", "Mizuki-san... I know Hinata is yours. I saw you working on it every single night.", "worried, gentle"),
      L("haruto", "Thank you, Aoyama-san. But I don't think anyone else is going to believe that.", "defeated"), pos="saki:l,haruto:r"),

    # ---- The betrayal at home ----
    S("{HARUTO} on a commuter train in the afternoon holding a small white cake box on his lap, a tired hopeful smile",
      (N, "I went home early. It was our third wedding anniversary, so I stopped and bought Erika's favorite strawberry cake.", "soft"),
      (N, "I thought... at least I still had my family.", "sad")),
    S("close-up of an apartment entrance floor with a pair of shiny expensive brown Italian leather men's shoes next to women's red high heels",
      (N, "At the door, there was a pair of shoes I recognized. Expensive Italian leather. Daichi never stopped bragging about them.", "dread")),
    S("{DAICHI} on a living room sofa with his arm around {ERIKA}, both turning toward the doorway, modern apartment, afternoon light",
      L("haruto", "...Erika?", "barely a whisper"),
      L("erika", "Oh. You're early.", "cold, unbothered")),
    S("a white cake box falling and hitting the floor of an apartment hallway, a strawberry cake spilling out, {HARUTO}'s legs in the background",
      L("haruto", "How long?", "trembling"),
      L("erika", "Six months. Maybe seven. Does it matter?", "bored")),
    S("{ERIKA} standing with her arms crossed and looking down at someone with contempt, apartment living room",
      L("erika", "Daichi is going places, Haruto. He's going to be a section chief. And you? You're a man who stays late with rice cookers.", "contemptuous")),
    S("{ERIKA} slapping divorce papers down on a glass coffee table, close-up of her hand with red nails",
      L("erika", "Sign these. I already filled in my part.", "sharp")),
    S("{DAICHI} lounging on the sofa laughing, one arm over the backrest, apartment living room",
      L("daichi", "Told you to go home early, buddy.", "laughing"),
      L("haruto", "Get out. Both of you. Get out of my home!", "furious, shouting")),
    S("{ERIKA} at the apartment door with a rolling suitcase, looking back over her shoulder, {DAICHI} waiting outside",
      L("erika", "Gladly. And my name's on the lease too, so you have until the end of the month.", "sharp, smug")),
    S("{HARUTO_HOME} sitting on the floor of a dark apartment hallway at dawn, knees up, head down, the crushed strawberry cake on the floor beside him",
      (N, "That night, I sat on the floor until the sun came up. The cake was still lying where I'd dropped it.", "hollow")),

    # ---- Fired ----
    S("{OKABE} sitting at his desk and glaring up at {HARUTO} who stands in front of him, a security guard by the door, " + OFFICE,
      L("okabe", "Mizuki. Confidential design data for Hinata was leaked to Kitano Appliances, our biggest competitor. And the leak came from your account.", "stern"),
      L("haruto", "What? I never... I would never do that!", "shocked"), pos="okabe:l,haruto:r"),
    S("{OKABE} slapping a printed access log onto his desk, angry, office background",
      L("okabe", "The access log doesn't lie. You're dismissed, effective immediately. Be grateful we're not pressing charges.", "cold")),
    S("{DAICHI} behind a glass office wall giving a small mocking wave and smirking, office background",
      (N, "Behind the glass wall, Daichi gave me a little wave. That's when I understood.", "realizing"),
      (N, "He knew my password. I'd given it to him years ago, when he helped me fix my laptop.", "bitter")),
    S("{HARUTO} carrying a cardboard box of belongings through the office while coworkers at their desks whisper and look away",
      (N, "I carried five years of work out in a single cardboard box. People I'd worked with every day wouldn't even look at me.", "sad")),
    S("{SAKI} running across an office building lobby toward {HARUTO} who carries a cardboard box, she is out of breath",
      L("saki", "Mizuki-san! Wait!", "calling out, out of breath"),
      L("saki", "I don't believe it. Not for a second. Please... don't give up.", "earnest"),
      L("haruto", "Thank you, Aoyama-san. Take care of yourself.", "forced smile"), pos="saki:l,haruto:r"),
    S("{HARUTO} waiting at a bus stop in heavy rain at night holding a cardboard box, looking at his glowing phone",
      (N, "No job. No wife. Soon, no apartment. My phone had one unread message. It was from my mom.", "numb")),
    S("close-up of a smartphone in a man's wet hand showing a voice message from Mom, raindrops on the screen",
      L("mom", "Haruto, it's Mom. You haven't come home in two years. Your father misses you, even if he won't say it. Come home anytime, okay?", "gentle, voice message")),
    S("close-up of {HARUTO}'s face in the rain, tears mixing with raindrops, a small sad smile",
      L("haruto", "...Yeah. Maybe it's time.", "tearful, soft")),

    # ---- Going home ----
    S("a small local train crossing green rice fields with tall mountains of Nagano behind, bright summer morning",
      (N, "My hometown is a small town in the mountains of Nagano, three hours from Tokyo. Rice fields, old houses, and one convenience store that closes at nine.", "fond")),
    S("an old Japanese countryside house with a tiled roof next to a small wooden machine workshop with a big sliding door, summer, cicadas, blue sky",
      (N, "My family's house sits behind my father's old workshop. For thirty years, he repaired every machine on every farm in the valley.")),
    S("{MOM} hugging {HARUTO_HOME} tightly at the front door of an old Japanese house, she is overjoyed and teary",
      L("mom", "Haruto! Oh, look at you. You're so thin! Are you eating properly?", "overjoyed"),
      L("haruto", "I'm home, Mom.", "emotional")),
    S("{MIO} jumping onto {HARUTO_HOME}'s back from behind with a big grin, entrance of a Japanese house",
      L("mio", "Big brother! You actually came back! Did Tokyo finally kick you out?", "teasing, cheerful"),
      L("haruto", "...Something like that.", "awkward laugh")),
    S("a Japanese family dinner table with rice, miso soup and grilled fish, {HARUTO_HOME} staring at his untouched bowl, {DAD} and {MOM} watching him",
      (N, "At dinner, I tried to act normal. I lasted about five minutes.", "wry")),
    S("{DAD} putting down his chopsticks and looking seriously across the dinner table, traditional Japanese dining room",
      L("dad", "Haruto. Your mother made your favorite and you haven't touched it. Talk.", "gruff")),
    S("{HARUTO_HOME} with his head bowed speaking at the dinner table while {MIO}, {MOM} and {DAD} listen in shock",
      (N, "So I told them everything. The project. Daichi. Erika. The leak. The box in the rain.", "heavy")),
    S("{MIO} slamming both hands on the dinner table, furious, chopsticks flying",
      L("mio", "That snake! I always hated that Daichi guy! He ate all my pudding at New Year's!", "furious")),
    S("{MOM} covering her mouth with her hand, teary eyes, dining room",
      L("mom", "And Erika... after everything you did for her.", "heartbroken")),
    S("{DAD} standing and placing a firm hand on {HARUTO_HOME}'s shoulder, warm lamplight, dining room",
      L("dad", "Listen to me. A man who steals an idea only gets the idea. He doesn't get the head it came from.", "firm, warm"),
      L("dad", "You built that rice cooker once. You can build something better. And this time, you build it for yourself.", "warm")),
    S("close-up of {HARUTO_HOME} looking up with tears in his eyes and a trembling smile",
      L("haruto", "Dad...", "choked up"),
      (N, "For the first time in a week, I felt something besides pain. I felt like I could breathe again.", "relieved")),
    S("{DAD} sliding open the big door of a dusty old machine workshop in morning sunlight, lathe, workbenches, tools on the walls and a small 3D printer, {HARUTO_HOME} behind him",
      L("dad", "The workshop's been empty since I retired. It's yours. Lathe, soldering station, 3D printer... everything.", "proud"),
      L("haruto", "Wait. You have a 3D printer?", "surprised"),
      L("dad", "Your sister made me buy it. I used it once. To print a cup holder.", "deadpan")),
    S("{MIO} sitting cross-legged with a laptop covered in stickers, grinning mischievously, workshop background",
      L("mio", "And don't forget, I study computer science! If you need an app, a website, or someone to hack your ex-best-friend's... I mean, if you need help, I'm here!", "mischievous"),
      L("haruto", "No hacking, Mio.", "laughing"),
      L("mio", "Fine, fine.", "pouting")),

    # ---- Building something better ----
    S("{HARUTO_HOME} sitting at a wooden workbench sketching designs in a notebook, crumpled paper around him, workshop at night",
      (N, "I didn't want to rebuild Hinata. Daichi could keep it. I wanted to make something new.", "determined")),
    S("{MOM} lifting the lid of an old black clay rice pot on a gas stove in a traditional Japanese kitchen, steam rising",
      (N, "The answer came from my mother's kitchen."),
      L("mom", "This old clay pot is slow, but nothing tastes better. The new machines just aren't the same.", "wistful"),
      L("haruto", "Mom... say that again.", "realizing")),
    S("close-up of {HARUTO_HOME} with wide excited eyes, a bright idea glow around his head, kitchen background",
      (N, "Every fast rice cooker, Hinata included, traded flavor for speed. But what if you didn't have to choose?", "excited"),
      L("haruto", "A cooker that heats like a clay pot... but fast enough for a family where everyone works!", "excited")),
    S("{HARUTO_HOME} and {DAD} working side by side at a workbench at night, sparks from a grinder, circuit boards and metal parts, warm workshop light",
      (N, "For three months, my father and I worked in that workshop every day. He knew metal and heat like nobody else. I knew the design and the electronics.")),
    S("{MIO} typing on a laptop surrounded by empty energy drink cans, a cute rice-grain mascot character on the screen, night",
      (N, "Mio wrote an app that let you start the rice from your phone, and learned each family's favorite texture."),
      L("mio", "I named the AI Okome-chan. She's very polite!", "proud")),
    S("a metal rice cooker prototype on a workbench with black smoke pouring out, {DAD} and {HARUTO_HOME} coughing and waving the smoke away",
      (N, "Our first prototype caught fire.", "deadpan"),
      L("dad", "...Well. It's warm.", "deadpan")),
    S("{MOM} tasting rice with chopsticks with an amazed teary expression while {HARUTO_HOME}, {DAD} and {MIO} watch nervously, workshop table",
      (N, "Our seventh prototype cooked rice in eighteen minutes. And when my mother tasted it, she went very quiet."),
      L("mom", "Haruto... this tastes just like my grandmother's rice.", "amazed, tearful")),
    S("{HARUTO_HOME} proudly holding up a beautiful finished rice cooker with a matte white body and a warm wooden lid, workshop background, morning light",
      (N, "We called it Furusato. It means hometown.", "proud, warm")),
    S("{MIO} filming with a smartphone on a tripod while {HARUTO_HOME} stands stiffly next to the wooden-lid rice cooker in the workshop",
      L("mio", "Okay, smile, big brother! We launch the crowdfunding campaign tonight!", "cheerful"),
      L("haruto", "I'm really not good in front of cameras...", "nervous")),

    # ---- Meanwhile, in Tokyo ----
    S("{DAICHI} in a new private office leaning back in a leather chair with his feet up on the desk, smug, city view window",
      (N, "Meanwhile, back in Tokyo, things weren't going so well for Daichi. I only heard about it later.")),
    S("worried young engineers in work uniforms showing {DAICHI} a tablet with a red warning graph, a lab with rice cooker prototypes",
      L("engineer", "Kurosawa-san, the Hinata prototype keeps overheating. What temperature curve did you use in the original design?", "worried"),
      L("daichi", "Uh... just fix it! That's your job, isn't it?", "panicking")),
    S("{DAICHI} alone at night sweating in front of a computer monitor full of technical diagrams, loosened tie",
      (N, "Of course he couldn't answer. He'd copied my slides, but he never understood the engineering behind them.")),
    S("{ERIKA} in a luxury boutique holding up a designer handbag, {DAICHI} beside her with a strained smile holding a credit card",
      L("erika", "Daichi, I want this one. And we should move to a bigger apartment, don't you think?", "spoiled"),
      L("daichi", "Sure, babe. Anything for you.", "strained"), pos="erika:l,daichi:r"),
    S("{DAICHI} staring in horror at a long credit card bill, sitting on the edge of a bed at night",
      (N, "Daichi was spending money he didn't have. And to keep up, he'd made a very dangerous decision.", "ominous")),
    S("{DAICHI} meeting a shady man in a black coat and sunglasses in a dim underground parking garage, an envelope being handed over",
      L("kitano", "Your last data package was useful, Kurosawa. Bring the rest, and you'll get the other half.", "sinister"),
      L("daichi", "Keep your voice down. Nobody can know about this.", "nervous whisper"), pos="kitano:l,daichi:r"),

    # ---- Saki's discovery ----
    S("{SAKI} alone at her desk late at night in a dark office, the glow of two monitors with spreadsheets on her face",
      (N, "But someone in Tokyo hadn't forgotten about me.", "warm")),
    S("close-up of {SAKI} frowning at a computer monitor showing a table of access logs, office at night",
      L("saki", "That's strange... Mizuki-san's account sent the files to Kitano at eleven forty-two P.M. on the fourteenth.", "puzzled, murmuring")),
    S("{SAKI} with her eyes widening in realization, hand on her mouth, a soft memory glow behind her",
      L("saki", "But on the fourteenth, Mizuki-san was with me in accounting until midnight. We were checking the cost sheets. He never went back to his desk!", "realizing")),
    S("a computer monitor showing grainy security camera footage of {DAICHI} sitting at a dark office desk at night using a computer, {SAKI} reflected in the screen",
      (N, "She asked security for the camera footage from that night. And there he was. Daichi. Sitting at my desk.", "tense"),
      L("saki", "Got you.", "quiet determination")),
    S("{SAKI} on the phone in an empty office stairwell, nervous and hopeful, holding a USB drive",
      L("saki", "Mizuki-san? It's Aoyama. I'm sorry to call so suddenly. I found something. I think I can prove you're innocent.", "nervous, hopeful")),
    S("{HARUTO_HOME} holding a phone to his ear in the workshop, shocked and moved",
      L("haruto", "Aoyama-san... why would you go this far for me?", "moved"),
      L("saki", "Because you were the only one who ever said thank you to accounting.", "shy laugh"),
      L("saki", "And because... I miss seeing you at the office.", "very shy, quiet")),
    S("{MIO} peeking around the workshop door with a huge teasing grin, {HARUTO_HOME} blushing red holding a phone",
      L("mio", "Ohhh? Who's Aoyama-san? Big brother's face is all red!", "teasing"),
      L("haruto", "Mio! Go away!", "embarrassed"), pos="mio:l,haruto:r"),

    # ---- Success ----
    S("a laptop on a wooden table showing a crowdfunding page with a progress bar far over one hundred percent and confetti graphics",
      (N, "Then the crowdfunding campaign launched. We hoped to raise one million yen.", "nervous"),
      (N, "In the first twenty-four hours, we raised ten million.", "amazed")),
    S("{MIO} jumping with joy and {MOM} laughing and clapping in a Japanese living room, {DAD} looking confused with his arms crossed",
      L("mio", "Ten million! TEN MILLION! Okome-chan is famous!", "screaming with joy"),
      L("dad", "...Is that a lot?", "confused"),
      L("mom", "Dear. It's a lot.", "laughing")),
    S("a TV screen in a living room showing a news program about a rice cooker with a wooden lid, a news anchor at a desk",
      L("anchor", "A rice cooker built in a small Nagano workshop has become the most funded home appliance in Japanese crowdfunding history.", "news broadcast")),
    S("a shiny black luxury car parked on a gravel road in front of an old wooden workshop in the countryside, {PRESIDENT} stepping out",
      (N, "A week later, a black car pulled up in front of our workshop. And out stepped someone I never expected to see again.", "surprised")),
    S("{PRESIDENT} bowing politely to a surprised {HARUTO_HOME} inside the workshop",
      L("president", "Mizuki-kun. I owe you an apology. I should have trusted my instincts at that meeting.", "sincere"),
      L("haruto", "President Shiraishi?", "stunned"), pos="president:l,haruto:r"),
    S("{PRESIDENT} speaking seriously in the workshop, {SAKI} standing behind him waving shyly",
      L("president", "Hinata has failed every safety test since you left. Whoever invented it doesn't understand it. And Ms. Aoyama from accounting brought me something very interesting.", "knowing"),
      L("saki", "Hello, Mizuki-san.", "shy")),
    S("{PRESIDENT} holding out his hand for a handshake toward {HARUTO_HOME}, workshop with the wooden-lid rice cooker on the bench",
      L("president", "I'd like to make you an offer. Hikari Electric will manufacture Furusato as your partner. Your company. Your design. Your name.", "warm, serious"),
      L("president", "And I'd like you to present it at our shareholders' meeting next month.")),
    S("{DAD} giving a proud firm nod with his arms crossed, workshop background",
      L("dad", "Go on. Finish what you started.", "proud")),
    S("{HARUTO_HOME} shaking hands firmly with {PRESIDENT}, determined expression",
      L("haruto", "I accept. But I have one condition. Daichi Kurosawa must be at that meeting.", "determined"), pos="haruto:l,president:r"),

    # ---- The shareholders' meeting ----
    S("a huge hotel ballroom set up for a corporate shareholders' meeting, hundreds of seated people, a stage with a big screen, cameras",
      (N, "The shareholders' meeting. Two hundred people. Cameras everywhere.", "tense"),
      (N, "And in the front row... Section Chief Daichi Kurosawa, with Erika on his arm.", "cold")),
    S("{DAICHI} and {ERIKA} sitting in the front row of an audience, Daichi's jaw dropping in shock, Erika confused",
      L("daichi", "Haruto?! What is HE doing here?", "shocked"),
      L("erika", "Isn't that your old friend? The failure?", "confused, snide"), pos="daichi:l,erika:r"),
    S("{HARUTO} in a sharp navy suit standing confidently on a stage at a podium with a microphone, a big screen behind him showing the wooden-lid rice cooker",
      L("haruto", "Good afternoon. My name is Haruto Mizuki. Six months ago, I was fired from this company.", "confident"),
      L("haruto", "Today, I'm here as its partner.", "confident")),
    S("a ballroom audience applauding enthusiastically, a big screen on stage showing a rice cooker with a wooden lid",
      (N, "I explained everything about Furusato. The clay-pot heating. Okome-chan. Ten million yen in a single day. The room went silent... and then it burst into applause.")),
    S("{DAICHI} standing up in the audience pointing angrily at the stage, red-faced, people around him staring",
      L("daichi", "This is ridiculous! He's a thief! He leaked our company's data to Kitano! Why is a criminal standing on that stage?", "outraged, shouting")),
    S("{PRESIDENT} standing calmly at the side of the stage with his hands behind his back, icy stare",
      L("president", "Kurosawa-kun. Funny you should mention the leak. Ms. Aoyama, if you would.", "calm, icy")),
    S("{SAKI} standing at a laptop on the stage, a big screen behind her showing grainy night security camera footage of {DAICHI} at an office computer",
      L("saki", "On the night of the leak, Mizuki-san was with me in accounting until midnight. This is the security camera footage from his desk at eleven forty-two.", "steady")),
    S("{DAICHI} pale and sweating, stepping backward, the audience gasping around him",
      L("daichi", "Th-that's fake! That's not me!", "panicking")),
    S("a big screen on a stage showing bank transfer records with large highlighted numbers, {SAKI} pointing at it",
      L("saki", "And these are payments from Kitano Appliances, to an account in your name. Five million yen. In two parts.", "firm")),
    S("{HARUTO} stepping to the front of the stage and looking down calmly, dramatic spotlight",
      L("haruto", "And Daichi... if Hinata was really your idea, tell everyone. What's the heating curve at minute seven?", "calm, cutting")),
    S("close-up of {DAICHI} stammering, eyes darting, sweat dripping",
      L("daichi", "The... the heating... it's... eighty... no, it's...", "stammering")),
    S("close-up of {HARUTO} with a cold calm stare, stage lights",
      L("haruto", "It's a hundred and two degrees, held for ninety seconds. It's on page forty of the design document you stole.", "cold"),
      L("haruto", "You never even read it.", "cold, quiet")),
    S("two security guards approaching {DAICHI} in the ballroom aisle, {PRESIDENT} on stage pointing toward the exit",
      L("president", "Kurosawa Daichi. You are dismissed, effective immediately. Our lawyers will contact you about the stolen data. And the police are waiting outside.", "stern")),
    S("{OKABE} trying to sneak toward a side exit of the ballroom, sweating, being stopped by {PRESIDENT}",
      L("president", "Ah, and Section Chief Okabe. You approved his promotion and signed Mizuki-kun's dismissal without any investigation. We'll be discussing your future as well.", "cold"),
      L("okabe", "P-President, I can explain...", "sweating, panicked")),
    S("{DAICHI} being dragged up the aisle by two security guards, shouting back over his shoulder",
      L("daichi", "Haruto! This isn't over! You hear me?!", "screaming"),
      (N, "It was over. He just didn't know it yet.", "calm")),

    # ---- Erika ----
    S("{ERIKA} running after {HARUTO} down a hotel corridor, desperate, her makeup smudged",
      L("erika", "Haruto! Wait! Haruto, please!", "desperate")),
    S("close-up of {ERIKA} crying and clasping her hands, hotel corridor",
      L("erika", "I made a mistake. Daichi lied to me. He tricked me! I never stopped loving you, Haruto.", "crying, desperate")),
    S("{ERIKA} clutching {HARUTO}'s sleeve with both hands, pleading, hotel corridor",
      L("erika", "We can start over. You and me. With your company... we could have such a good life together!", "pleading"), pos="erika:l,haruto:r"),
    S("{HARUTO} calmly removing {ERIKA}'s hand from his sleeve, his face calm and sad, hotel corridor",
      L("haruto", "Erika. On our anniversary, I dropped a strawberry cake on the floor. You stepped over it on your way out.", "quiet, calm"),
      pos="haruto:r,erika:l"),
    S("close-up of {HARUTO} looking at her with calm, tired eyes",
      L("haruto", "You didn't fall in love with Daichi. You fell in love with what he promised you. And now you want what I have. Not me.", "calm"),
      L("haruto", "Goodbye, Erika. I hope you find what you're looking for.", "gentle, final")),
    S("{ERIKA} kneeling alone on the carpet of an empty hotel corridor crying, {HARUTO} walking away in the distance",
      (N, "I later heard that most of Daichi's credit cards were in both their names.", "dry"),
      (N, "Erika spent the next few years paying off designer bags she'd already sold.", "dry, satisfied")),

    # ---- One year later ----
    S("a new small modern factory building with a wooden facade in a countryside valley, cherry blossom trees in full bloom, spring",
      (N, "One year later, Furusato was the best-selling rice cooker in Japan.", "warm"),
      (N, "My father's old workshop is now a real factory, with thirty employees from our hometown.", "proud")),
    S("{DAD} in a clean factory teaching young workers in caps how to assemble a heating plate, proud and stern",
      L("dad", "Careful with that! The heat plate is the heart of the machine!", "gruff, proud")),
    S("{MIO} in her yellow hoodie spinning in an office chair in front of multiple monitors, a cute rice mascot on screen, modern startup office",
      L("mio", "Official title: Chief Technology Officer. And Okome-chan now speaks four languages!", "proud")),
    S("{MOM} in a bright test kitchen with grandmothers from the village tasting rice from wooden-lid rice cookers, everyone smiling",
      (N, "Mom runs our test kitchen. Every new model has to pass the grandmother test.", "fond")),
    S("{DAICHI} in a convenience store uniform mopping the floor alone at night, tired and unshaven",
      (N, "As for Daichi, he was convicted of corporate espionage. After his sentence, I heard he found work on a night shift somewhere.", "neutral"),
      (N, "I hope he learned something.", "quiet")),
    S("{HARUTO_HOME} and {SAKI} walking side by side under cherry blossom trees by a river, petals falling, she is blushing",
      L("saki", "Mizuki-san... I mean, Haruto. Is it really okay for me to leave Hikari and join your company?", "shy"),
      L("haruto", "Of course. You're the one who saved me, Saki. I'd like you by my side. At work... and outside of work, too.", "warm, a little shy"),
      pos="haruto:l,saki:r"),
    S("close-up of {SAKI} blushing with a happy smile, cherry blossom petals around her",
      L("saki", "...Yes. I'd like that.", "happy, blushing")),
    S("{HARUTO_HOME}, {SAKI}, {MIO}, {MOM} and {DAD} laughing together around a dinner table full of food in a traditional Japanese house, warm evening light",
      (N, "In one week, I lost everything. But when I went back home, I found out what I really had all along.", "warm, moved")),
    S("{HARUTO_HOME} smiling warmly at the viewer, cherry blossom petals falling, soft spring light",
      (N, "If you were in my place... what would you have said to Erika in that hallway? Tell me in the comments.", "warm, inviting"),
      (N, "And like and subscribe for more stories like this.", "warm, smiling")),
]

spec = {
    "title": "My Best Friend Stole My Project, My Wife and My Job... So I Went Home and Built Something Better [Manga Dub]",
    "character": "", "style": "",
    "width": 1920, "height": 1080, "title_card": False,
    "tts": "kokoro", "cast": KOKORO, "speed": 0.95, "scene_pad": 0.7,
    "emotive": {"engine": "eleven_v3", "cast": CAST, "skip": [], "fallback": True,
                "priority": ["narrator", "haruto", "daichi", "erika", "saki", "dad", "mom", "mio", "president", "okabe"]},
    "caption": {"mode": "boxes", "font": "Comic Neue", "fonts_dir": "assets/fonts"},
    "images": {"provider": "local", "upscale": True},
    "characters": {REFS[k]: PORTRAIT.format(who=C[k]) for k in C if "_" not in k},
    "music": {"sound": "music_strategy", "volume": 0.07},
    "sources": ["Original story and characters. Artwork drawn with AI (FLUX.2 klein, run locally)."],
    "scenes": [{**sc, "fx": []} for sc in scenes],
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
