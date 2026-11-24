"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 1: Who Is the Greatest?

Run: python3 projects/coc/royal-rivalry-full-ep01-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
Hype only: it sets up the heroes, the statue and the contest, and cuts away before anything is decided.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, HJ, promo_spec, write  # noqa: E402

pages = [
    page([(N, "Two heroes. One kingdom. And room for only one statue.")], "1",
         [P(HJ + "@0.5,0.5,1.6", art=[A("king_charge", .3, .7, .55, enter="left", at=0.2), A("queen_leap", .72, .7, .55, flip=True, enter="right", at=0.9)],
            sfx=[S("VS", .5, .5, 1.6, style="red", size=150)])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.2, "size": 96, "at": "lineend:0-0.4"}]),
    page([("king", "Plans are for people who can't punch!"),
          ("queen", "Eleven thousand bullseyes. But who's counting? Me. I am counting.")], "2v",
         [P("burst:orange", art=[A("king_point", .32, .6, .9, enter="left")], bubbles=[B(0, .7, .27, [.42, .4], shout=True, w=440)], caps=[Cap("The Barbarian King", y=.86)]),
          P("burst:purple", art=[A("queen_aim", .7, .6, .9, enter="right")], bubbles=[B(1, .3, .27, [.6, .4], w=480)], caps=[Cap("The Archer Queen", y=.86)], at="line:1-0.4")]),
    page([("king", "Morning, Your Majesty."), ("queen", "Morning. You have breakfast in your beard.")], "2v",
         [P("warm", art=[A("king_point", .32, .6, .9)], bubbles=[B(0, .7, .26, [.45, .4], w=400)]),
          P("cool", art=[A("queen_stand", .68, .6, .9, flip=True)], bubbles=[B(1, .3, .26, [.55, .4], w=440)], at="line:1-0.4")]),
    page([("wizard", "The council proposes a statue of the kingdom's greatest hero!"),
          ("king", "Obviously, that's me."), ("queen", "Obviously, it's me.")], "1/2",
         [P(HJ + "@0.55,0.5,1.4", art=[A("wizard", .72, .66, .8, enter="right")], bubbles=[B(0, .36, .27, [.62, .45], w=560)], caps=[Cap("The town council", y=.88)]),
          P("burst:gold", art=[A("bk_emote", h=.8)], bubbles=[B(1, .5, .16, [.5, .32], shout=True, size=36, w=420)], at="line:1-0.3"),
          P("burst:purple", art=[A("aq_emote", h=.8)], bubbles=[B(2, .5, .16, [.5, .32], shout=True, size=36, w=420)], at="line:2-0.3")]),
    page([("king", "I could beat you with one hand!"), ("queen", "You'd need the other one to find your sword.")], "2v",
         [P("red", under=["speed:0.5,0.5"], art=[A("king_point", .32, .6, .9)], bubbles=[B(0, .7, .26, [.45, .4], shout=True, w=420)]),
          P("cool", under=["speed:0.5,0.5"], art=[A("queen_aim", .68, .6, .9, flip=True)], bubbles=[B(1, .3, .26, [.55, .4], w=440)], at="line:1-0.4")]),
    page([("barbarians", "KING! KING! KING!"), ("archers", "Queen. Obviously.")], "2v",
         [P("burst:gold", art=[A("barb_emote_set_1", .5, .6, .8)], bubbles=[B(0, .5, .2, [.5, .35], shout=True, size=40, w=440)]),
          P("burst:green", art=[A("archer_emote", .5, .6, .8)], bubbles=[B(1, .5, .2, [.5, .35], size=40, w=420)], at="line:1-0.4")]),
    page([("warden", "ENOUGH!")], "1",
         [P("gloom", art=[A("warden", .5, .62, .8, enter="up")], fx=["speed:0.5,0.5", "flash@line:0"], bubbles=[B(0, .5, .16, [.5, .3], shout=True, size=80)])],
         shake=["line:0"]),
    page([("warden", "The next time goblins raid this kingdom, whoever stops them, alone, will be named its greatest hero.")], "1",
         [P("paper", art=[A("warden", .5, .66, .7)], fx=["crown:0.5,0.3,1.2@lineend:0-1.5"], caps=[Cap("THE CONTEST", at=0.3, size=48, y=.9)],
            bubbles=[B(0, .5, .16, [.5, .32], w=640)])]),
    page([("king", "Done! Start carving my nose."), ("queen", "Carve mine smaller. And prettier.")], "2v",
         [P("warm", art=[A("king_point", .32, .6, .9)], bubbles=[B(0, .7, .26, [.45, .4], w=400)]),
          P("cool", art=[A("queen_stand", .68, .6, .9, flip=True)], bubbles=[B(1, .3, .26, [.55, .4], w=420)], at="line:1-0.4")]),
    page([("boss", "Tonight, we hit the gold storage."), ("king", "MINE!"), ("queen", "MINE!")], "1/2",
         [P("night", under=["stars", "moon:0.82,0.2"], art=[A("goblin_02", .5, .64, .85)], bubbles=[B(0, .5, .2, [.5, .4], w=520)]),
          P("warm", under=["speed:0.8,0.5"], art=[A("king_charge", .5, .62, .9)], bubbles=[B(1, .5, .16, [.5, .32], shout=True, size=44)], at="line:1-0.2"),
          P("cool", under=["speed:0.2,0.5"], art=[A("queen_leap", .5, .62, .9, flip=True)], bubbles=[B(2, .5, .16, [.5, .32], shout=True, size=44)], at="line:2-0.2")]),
    page([(N, "Who will be the greatest? And what is watching from the storm?")], "1",
         [P("dark", under=["stars"], fx=["bolt:0.15,0,0.3,0.5,0.8@1.2", "bolt:0.85,0,0.7,0.45,0.8@1.6", "eyes:0.5,0.32,0.06,120,210,255@lineend:0-1.5"])]),
    page([(N, "Episode one, Who Is the Greatest. Full episode now, on the channel. Like and subscribe!")], "1",
         [P("dark", under=["stars"], fx=["eyes:0.5,0.32,0.06,120,210,255@0"])],
         titles=[{"text": "FULL EPISODE", "y": 0.44, "size": 110, "at": 1.2}, {"text": "ON THE CHANNEL", "y": 0.52, "size": 80, "at": 1.8, "style": "white"},
                 {"text": "LIKE & SUBSCRIBE", "y": 0.62, "size": 70, "at": "lineend:0-1.4"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 1: Who Is the Greatest? (promo)", pages))
