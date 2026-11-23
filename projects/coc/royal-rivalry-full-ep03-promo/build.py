"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 3: Picking Up the Pieces.

Run: python3 projects/coc/royal-rivalry-full-ep03-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, HJ, promo_spec, write  # noqa: E402

RUINS = HJ + "@0.5,0.6,1.6"

pages = [
    page([(N, "The dragon is gone. The Warden is down. And somebody in this kingdom is keeping secrets.")], "1",
         [P(RUINS, under=["smoke:0.3,0.5,90", "smoke:0.7,0.45,80"], fx=["darken:0.45@0", "sigil:0.5,0.3,120@2.5"])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.62, "size": 96, "at": "lineend:0-0.6"}, {"text": "PICKING UP THE PIECES", "y": 0.7, "size": 60, "at": "lineend:0-0.1", "style": "white"}]),
    page([(N, "Golden light. And the Warden opened his eyes."),
          ("warden", "Is the fountain still standing?")], "2v",
         [P("gold", under=["glow:0.5,0.5,600"], art=[A("healer", .5, .62, .9, bob=10)], fx=["ring:0.5,0.55,700@1.5", "flash:255,230,160@3"]),
          P("gold", under=["glow:0.5,0.45,460"], art=[A("warden", .5, .62, .9)], bubbles=[B(1, .5, .25, [.5, .4], w=520)], at="line:1-0.4")]),
    page([(N, "Then the tower fell."),
          ("king", "Little help... would be... NICE!")], "1",
         [P("red", under=["speed:0.5,0.5"], art=[A("king_army", .5, .7, .55), A("archer_tower", .52, .38, .32, rot=-0.4)],
            bubbles=[B(1, .5, .14, [.5, .3], shout=True, w=520)], sfx=[S("CRASH!", .5, .55, 1.2, style="fire", size=120)])], shake=[1.2]),
    page([(N, "Three arrows. Three ropes."),
          ("queen", "Don't you dare drop it!")], "2v",
         [P("cool", under=["speed:0.2,0.5"], art=[A("queen_aim", .5, .62, .9)], sfx=[S("THUNK! THUNK! THUNK!", .5, .2, 1.2, style="gold", size=70)]),
          P("warm", art=[A("king_army", .5, .66, .8), A("archer_tower", .5, .28, .4, rot=-0.4)], bubbles=[B(1, .5, .86, w=560)], at="line:1-0.4")]),
    page([(N, "Burned into the stones, a mark. Still crackling."),
          ("queen", "Lightning doesn't leave a signature. Unless someone wants you to know who sent it.")], "1",
         [P("ash", art=[A("queen_stand", .5, .74, .5)], fx=["sigil:0.5,0.3,200@0.8", "bolt:0.3,0.3,0.4,0.15,0.5@2", "bolt:0.7,0.3,0.6,0.45,0.5@2.6"],
            bubbles=[B(1, .5, .52, w=640)])]),
    page([("goblin", "Ooh. Shiny."),
          (N, "He grabbed a dragon scale, and ran.")], "2v",
         [P("ash", art=[A("wall", .5, .85, .5), A("goblin_07", .5, .7, .55, enter="up", at=0.2)], bubbles=[B(0, .5, .26, [.5, .42], w=360)]),
          P("warm", under=["speed:0.5,0.5"], art=[A("king_charge", .38, .66, .8, rot=-0.3), A("queen_leap", .66, .66, .8, rot=0.35, flip=True)],
            fx=["dizzy:0.5,0.35@lineend:1-0.6"], sfx=[S("BONK!", .5, .2, "lineend:1-0.8", style="fire", size=120)], at="line:1-0.3")],
         shake=["lineend:1-0.8"]),
    page([(N, "He dropped a map, with the same mark on it."),
          (N, "Almost as if someone wanted it to be found.")], "1",
         [P("paper", art=[A("goblin_07", .2, .78, .25, alpha=0.6)], fx=["sigil:0.62,0.32,110@1.5"],
            caps=[Cap("THE MAP", at=0, size=40), Cap("THE HILLS", at=1, x=.4, y=.5, size=44), Cap("THE KINGDOM", at=1, x=.12, y=.86, size=38)])]),
    page([("healer", "You didn't tell them everything, did you?"), ("warden", "No. Not yet.")], "2v",
         [P("dusk", under=["glow:0.5,0.4,360"], art=[A("healer", .5, .62, .9, bob=6)], bubbles=[B(0, .5, .25, [.5, .4], w=520)]),
          P("gloom", art=[A("warden", .5, .62, .9, flip=True)], bubbles=[B(1, .5, .25, [.5, .4], w=360)], at="line:1-0.4")]),
    page([(N, "At midnight, the Elixir began to glow. And the Wizard was already there."),
          ("wizard", "Oh no. It's fizzing again!")], "2v",
         [P("purple", art=[A("elixir_collector", .32, .64, .7), A("elixir_storage", .72, .68, .6)],
            fx=["glow:0.5,0.5,520,200,120,255", "bolt:0.3,0.3,0.7,0.35,0.6@2"], sfx=[S("HMMMMMM...", .5, .16, 1, style="purple", size=70)]),
          P("burst:red", art=[A("wizard", .5, .62, .88)], bubbles=[B(1, .5, .25, [.5, .4], shout=True, w=440)], at="line:1-0.4")]),
    page([(N, "Beyond the hills, a castle made of storm. And two eyes, looking back."),
          (N, "Episode three. Watch the full episode now, on the channel.")], "1",
         [P("dark", under=["stars", "smoke:0.5,0.35,130"], fx=["bolt:0.1,0,0.25,0.4,0.8@1", "bolt:0.9,0,0.75,0.35,0.8@1.5", "eyes:0.5,0.3,0.06,120,210,255@line:0+3"])],
         titles=[{"text": "FULL EPISODE", "y": 0.5, "size": 110, "at": "line:1+2.2"}, {"text": "ON THE CHANNEL", "y": 0.6, "size": 80, "at": "line:1+2.8", "style": "white"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 3: Picking Up the Pieces (promo)", pages))
