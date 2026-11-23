"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 4: The Storm Sorceress.

Run: python3 projects/coc/royal-rivalry-full-ep04-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, promo_spec, write  # noqa: E402

SKY = ["smoke:0.3,0.35,110", "smoke:0.7,0.3,100"]

pages = [
    page([(N, "At noon, the sun went out."), (N, "And the sky grew a face."), ("titan", "Hello, little kingdom.")], "1",
         [P("storm", under=SKY, art=[A("titan5", .5, .55, .7, alpha=0.85, enter="down", at="line:1", bob=10)], fx=["flash:150,210,255@line:1", "bolt:0.1,0,0.3,0.4,0.7@0.6"],
            bubbles=[B(2, .5, .14, [.5, .3], w=520)])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.84, "size": 96, "at": "line:2"}, {"text": "THE STORM SORCERESS", "y": 0.91, "size": 60, "at": "line:2+0.5", "style": "white"}],
         shake=["line:1"]),
    page([("titan", "You have something of mine. Give it back by the full moon."),
          ("king", "Give it BACK? It's ours!")], "2v",
         [P("storm", under=SKY, art=[A("titan_d", .4, .62, .9, alpha=0.9)], bubbles=[B(0, .62, .25, [.45, .4], w=520)]),
          P("red", art=[A("king_point", .32, .6, .9)], bubbles=[B(1, .7, .26, [.45, .4], shout=True, w=400)], at="line:1-0.4")]),
    page([("titan", "Is it? Ask the old man where it came from."), ("titan", "Hello, old teacher.")], "2v",
         [P("storm", art=[A("titan_emote", .5, .6, .8)], bubbles=[B(0, .5, .2, [.5, .35], w=560), B(1, .5, .2, [.5, .35], w=440)]),
          P("gloom", art=[A("warden", .5, .62, .9)], fx=["darken:0.3@0"], at="line:1-0.3", caps=[Cap("Teacher?", y=.86, at="lineend:1")])]),
    page([(N, "On the full moon, three dragons came. And for once, the heroes fought together.")], "1",
         [P("storm", under=["moon:0.5,0.15"], art=[A("edrag_1", .2, .3, .3, bob=12, enter="left", at=0.4), A("edrag_2", .5, .22, .3, bob=12, enter="up", at=0.8),
                                                  A("edrag_3", .8, .3, .3, flip=True, bob=12, enter="right", at=1.2), A("king_charge", .28, .8, .35, enter="left", at=2.2), A("queen_aim", .72, .8, .35, flip=True, enter="right", at=2.5)],
            fx=["flash:150,210,255@0.4"])], shake=[0.4]),
    page([(N, "He threw a boulder. She split it in mid air."),
          ("queen", "That was OUR dragon.")], "1",
         [P("storm", under=["speed:0.5,0.5"], art=[A("queen_aim", .25, .74, .45), A("edrag_2", .72, .3, .35, bob=10)],
            fx=["burst:0.5,0.45@2.2", "flash@2.2"], sfx=[S("KRAKOOM!", .5, .5, 2.2, style="fire", size=120)], bubbles=[B(1, .62, .66, [.35, .6], w=420)])], shake=[2.2]),
    page([(N, "Then the dragons flew home. Too easily."),
          (N, "Because the Elixir storage was empty.")], "2v",
         [P("night", under=["stars", "moon:0.5,0.2"], art=[A("edrag_1", .3, .5, .25, move=[.1, .1], moveAt=0.8, moveEnd=3), A("edrag_3", .7, .5, .25, flip=True, move=[.9, .1], moveAt=0.8, moveEnd=3)]),
          P("gloom", art=[A("elixir_storage", .5, .6, .75)], sfx=[S("...EMPTY.", .5, .16, "line:1+1.5", style="white", size=90)], at="line:1-0.3")]),
    page([("king", "The gate's been opened. Not broken. Opened."),
          ("queen", "Someone in this kingdom is working for her.")], "2v",
         [P("warm", art=[A("king_point", .32, .6, .9)], bubbles=[B(0, .7, .26, [.45, .4], w=420)]),
          P("cool", art=[A("queen_stand", .68, .6, .9, flip=True)], bubbles=[B(1, .3, .26, [.55, .4], w=420)], at="line:1-0.4")]),
    page([("wizard", "I was here the whole time! I didn't hear a thing."),
          (N, "Not a sound. Not a single thing.")], "1",
         [P("purple", art=[A("wizard", .5, .6, .75), A("elixir_storage", .75, .82, .3)], bubbles=[B(0, .5, .14, [.5, .3], w=640)],
            caps=[Cap("Not a single thing.", at="line:1+0.5", y=.92)])]),
    page([(N, "Traitor.")], "1",
         [P("dark", fx=["bolt:0.2,0,0.35,0.6,0.8@0.2", "flash:150,210,255@0.2"])],
         titles=[{"text": "TRAITOR.", "y": 0.5, "size": 170, "at": 0.3}], shake=[0.2]),
    page([(N, "Everyone blamed the goblin. But the goblin was on a hill, talking to a dragon scale."),
          ("goblin", "I did what you asked. Now let my Boss go.")], "2v",
         [P("night", under=["stars", "moon:0.8,0.2"], art=[A("goblin_07", .5, .64, .75)], fx=["glow:0.6,0.55,200,120,210,255"]),
          P("storm", art=[A("goblin_07", .3, .62, .7)], bubbles=[B(1, .66, .26, [.4, .4], w=420)], at="line:1-0.4")]),
    page([(N, "So who opened the gate? Episode four. Watch the full episode now, on the channel.")], "1",
         [P("dark", fx=["glow:0.5,0.3,200,200,120,255@0.4", "sigil:0.5,0.3,130@1"])],
         titles=[{"text": "FULL EPISODE", "y": 0.5, "size": 110, "at": "lineend:0-3.2"}, {"text": "ON THE CHANNEL", "y": 0.6, "size": 80, "at": "lineend:0-2.6", "style": "white"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 4: The Storm Sorceress (promo)", pages))
