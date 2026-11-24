"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 2: The Storm Arrives.

Run: python3 projects/coc/royal-rivalry-full-ep02-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
Hype only: the squabble, the warning signs and the dragon's arrival. It cuts away before the battle is decided,
and keeps the Warden's fate and the "Titan" clue secret.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, HJ, promo_spec, write  # noqa: E402

pages = [
    page([(N, "Last time, they lost the gold. This time, something much worse is coming.")], "1",
         [P("dark", under=["stars"], fx=["bolt:0.15,0,0.3,0.45,0.8@1.2", "bolt:0.85,0,0.7,0.4,0.8@1.6", "eyes:0.5,0.3,0.06,120,210,255@2"])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.5, "size": 96, "at": 1.0}, {"text": "THE STORM ARRIVES", "y": 0.58, "size": 64, "at": 1.6, "style": "white"}]),
    page([("warden", "You lost the gold together. So together, you will rebuild this wall."),
          ("king", "With HER?"), ("queen", "With HIM?")], "1/2",
         [P(HJ + "@0.5,0.6,1.5", art=[A("warden", .5, .64, .8)], bubbles=[B(0, .5, .2, [.5, .4], w=600)]),
          P("burst:orange", art=[A("bk_emote", h=.8)], bubbles=[B(1, .5, .16, [.5, .32], shout=True, size=36)], at="line:1-0.3"),
          P("burst:purple", art=[A("aq_emote", h=.8)], bubbles=[B(2, .5, .16, [.5, .32], shout=True, size=36)], at="line:2-0.3")]),
    page([("queen", "Your half is leaning."), ("king", "My half is NOT leaning!"), ("wizard", "It's leaning a little.")], "2v",
         [P("warm", art=[A("wall", .55, .8, .5, rot=-0.18), A("king_point", .3, .6, .85)], bubbles=[B(1, .7, .24, [.45, .4], shout=True, w=400)]),
          P("cool", art=[A("queen_stand", .7, .6, .9, flip=True), A("wizard", .22, .72, .5, at="line:2-0.3")], bubbles=[B(0, .3, .24, [.55, .4], w=380), B(2, .3, .24, [.25, .45], w=380)])]),
    page([("wizard", "Clear skies all week. Not a single cloud."), ("barbarians", "Then what's that cloud?")], "2v",
         [P("day", art=[A("th19", .25, .7, .6), A("wizard", .72, .64, .86, enter="right")], bubbles=[B(0, .34, .24, [.62, .4], w=460)]),
          P("storm", under=["smoke:0.5,0.4,80"], fx=["bolt:0.6,0,0.5,0.6,0.8@line:1+1", "flash@line:1+1"], at="line:1-0.3",
            bubbles=[B(1, .5, .26, [.5, .45], w=440)], sfx=[S("RUMBLE...", .5, .8, "line:1+0.8", style="zap", size=80)])]),
    page([("wizard", "The Elixir is fizzing. Elixir does not fizz!")], "1",
         [P("purple", art=[A("elixir_collector", .3, .66, .5), A("elixir_storage", .72, .7, .45), A("wizard", .5, .36, .35, at=0.4)],
            fx=["glow:0.5,0.6,520,200,120,255", "bolt:0.3,0.55,0.7,0.6,0.5@1.5"], bubbles=[B(0, .5, .12, [.5, .22], shout=True, w=560)],
            sfx=[S("FIZZ! FIZZ!", .5, .88, 1, style="purple", size=80)])]),
    page([("boss", "Boys, pack up. When goblins run away from something, everybody else should too.")], "1",
         [P("dusk", art=[A("goblin_02", .5, .66, .7)], bubbles=[B(0, .5, .16, [.5, .32], w=620)])]),
    page([(N, "Then the sky split open. An Electro Dragon. The biggest anyone had ever seen.")], "1",
         [P("storm", fx=["bolt:0.05,0,0.2,0.4,0.6@0.4", "bolt:0.95,0,0.8,0.45,0.6@0.8", "flash:150,210,255@0.9"], art=[A("edrag_lvl10", .5, .5, .55, enter="down", at=0.6, bob=18)],
            sfx=[S("KRRRZZZT!", .5, .14, "lineend:0", style="zap", size=120)])], shake=["lineend:0"]),
    page([("wizard", "DRAGON! Big one! Very sparkly! Everybody panic!")], "1",
         [P("burst:red", art=[A("wizard", .5, .62, .75)], bubbles=[B(0, .5, .14, [.5, .3], shout=True, w=600)], sfx=[S("DING! DING! DING!", .5, .88, 0.4, style="gold", size=70)])]),
    page([("king", "Stand back. This dragon is MINE."), ("queen", "You can't punch something that flies.")], "2v",
         [P("burst:orange", art=[A("king_charge", .32, .6, .9, enter="left")], bubbles=[B(0, .7, .26, [.45, .4], shout=True, w=420)]),
          P("burst:purple", art=[A("queen_aim", .7, .6, .9, enter="right")], bubbles=[B(1, .3, .26, [.6, .4], w=460)], at="line:1-0.4")]),
    page([("warden", "STOP! Both of you! Together, or not at all!")], "1",
         [P("gold", under=["glow:0.5,0.5,700"], art=[A("warden", .5, .62, .7), A("eq_tome", .78, .72, .2, bob=8)],
            fx=["ring:0.5,0.5,900@0.6", "ring:0.5,0.5,900@1.4"], bubbles=[B(0, .5, .14, [.5, .3], shout=True, w=560)])], shake=[0.4]),
    page([(N, "Will they listen in time? Episode two, The Storm Arrives. Full episode now, on the channel. Like and subscribe!")], "1",
         [P("dark", under=["stars"], fx=["bolt:0.1,0,0.25,0.4,0.8@0.6", "eyes:0.5,0.3,0.06,120,210,255@0.3"])],
         titles=[{"text": "FULL EPISODE", "y": 0.44, "size": 110, "at": "lineend:0-4.2"}, {"text": "ON THE CHANNEL", "y": 0.52, "size": 80, "at": "lineend:0-3.6", "style": "white"},
                 {"text": "LIKE & SUBSCRIBE", "y": 0.62, "size": 70, "at": "lineend:0-1.4"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 2: The Storm Arrives (promo)", pages))
