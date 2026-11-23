"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 1.

Run: python3 projects/coc/royal-rivalry-full-ep01-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, HJ, promo_spec, write  # noqa: E402

pages = [
    page([(N, "Two heroes. One statue. And absolutely zero chill.")], "1",
         [P(HJ + "@0.5,0.5,1.6", art=[A("king_charge", .3, .7, .55, enter="left", at=0.2), A("queen_leap", .72, .7, .55, flip=True, enter="right", at=1.0)],
            sfx=[S("VS", .5, .5, 1.6, style="red", size=150)])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.2, "size": 96, "at": "lineend:0-0.2"}]),
    page([("king", "Plans are for people who can't punch!"),
          ("queen", "Eleven thousand bullseyes. But who's counting? Me. I am counting.")], "2v",
         [P("burst:orange", art=[A("king_point", .32, .6, .9, enter="left")], bubbles=[B(0, .7, .27, [.42, .4], shout=True, w=440)], caps=[Cap("The Barbarian King", y=.86)]),
          P("burst:purple", art=[A("queen_aim", .7, .6, .9, enter="right")], bubbles=[B(1, .3, .27, [.6, .4], w=480)], caps=[Cap("The Archer Queen", y=.86)], at="line:1-0.4")]),
    page([(N, "There was exactly one pancake left."),
          ("king", "That pancake is mine."), ("queen", "I hit twenty bullseyes. Before breakfast."),
          (N, "The pancake did not survive.")], "1",
         [P("warm", under=["speed:0.5,0.6"], art=[A("king_point", .22, .72, .5), A("queen_stand", .78, .72, .52, flip=True), A("snack_pancakes", .5, .5, .22, at=0.3)],
            bubbles=[B(1, .25, .13, [.22, .45], w=420), B(2, .72, .26, [.78, .45], w=420)],
            sfx=[S("SPLAT!", .5, .45, "line:3-0.35", style="fire", size=150)], fx=["burst:0.5,0.5@line:3-0.35"])],
         shake=["line:3-0.35"]),
    page([("wizard", "The council proposes a statue of the kingdom's greatest hero."),
          ("king", "Obviously, that's me."), ("queen", "Obviously, it's me.")], "1/2",
         [P(HJ + "@0.55,0.5,1.4", art=[A("wizard", .72, .66, .8, enter="right")], bubbles=[B(0, .36, .27, [.62, .45], w=560)], caps=[Cap("The town council", y=.88)]),
          P("burst:gold", art=[A("bk_emote", h=.8)], bubbles=[B(1, .5, .16, [.5, .32], shout=True, size=36, w=420)], at="line:1-0.3"),
          P("burst:purple", art=[A("aq_emote", h=.8)], bubbles=[B(2, .5, .16, [.5, .32], shout=True, size=36, w=420)], at="line:2-0.3")]),
    page([(N, "So they made it a contest. Whoever guards the gold best, wins."),
          ("boss", "Tonight, we hit the gold storage.")], "2v",
         [P("warm", art=[A("gold_full", .5, .62, .75), A("king_point", .14, .72, .55, at=1.0), A("queen_stand", .86, .72, .56, flip=True, at=1.6)], caps=[Cap("The contest")]),
          P("night", under=["stars", "moon:0.82,0.2"], art=[A("goblin_02", .4, .62, .9), A("goblin_05", .82, .7, .5, at="line:1+0.6")],
            bubbles=[B(1, .58, .26, [.45, .45], w=520)], caps=[Cap("Meanwhile, beyond the walls...", y=.86)], at="line:1-0.4")]),
    page([("king", "This one is MINE!"), ("queen", "Get your own goblin!"), (N, "They met in the middle. Hard.")], "1",
         [P("warm", under=["speed:0.5,0.55"], art=[A("king_charge", .2, .55, .5, move=[.4, .55], moveAt="line:0", moveEnd="lineend:1"),
                                                   A("queen_leap", .8, .55, .5, flip=True, move=[.6, .55], moveAt="line:0", moveEnd="lineend:1"), A("goblin_03", .5, .82, .2)],
            bubbles=[B(0, .25, .12, [.22, .3], shout=True, w=400), B(1, .75, .12, [.78, .3], shout=True, w=400)],
            sfx=[S("BONK!", .5, .4, "lineend:1", style="fire", size=180)], fx=["flash@lineend:1", "dizzy:0.5,0.25@line:2"])], shake=["lineend:1"]),
    page([("goblin", "Thanks for the gold! Same time next week?"),
          ("warden", "Two heroes. Twenty goblins. And not a single one caught.")], "2v",
         [P("night", under=["stars"], art=[A("goblin_07", .62, .62, .85, move=[.85, .62], moveAt="line:0+1")], bubbles=[B(0, .3, .25, [.5, .4], w=460)]),
          P("gloom", art=[A("warden", .5, .62, .88)], bubbles=[B(1, .5, .24, [.5, .42], w=600)], at="line:1-0.4")]),
    page([(N, "And far beyond the walls, something in the storm was watching."),
          (N, "Episode one, Who Is the Greatest. Watch the full episode now, on the channel.")], "1",
         [P("dark", under=["stars"], fx=["bolt:0.15,0,0.3,0.5,0.8@line:0+1.5", "bolt:0.85,0,0.7,0.45,0.8@line:0+2", "eyes:0.5,0.32,0.06,120,210,255@line:0+2.4"])],
         titles=[{"text": "FULL EPISODE", "y": 0.5, "size": 110, "at": "line:1+1.8"}, {"text": "ON THE CHANNEL", "y": 0.6, "size": 80, "at": "line:1+2.4", "style": "white"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 1: Who Is the Greatest? (promo)", pages))
