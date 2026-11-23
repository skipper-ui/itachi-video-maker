"""Builds script.json for the 1-minute vertical promo of The Royal Rivalry, full Episode 2: The Storm Arrives.

Run: python3 projects/coc/royal-rivalry-full-ep02-promo/build.py
Page helpers and the ElevenLabs promo cast: projects/coc/rivalry.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rivalry import A, B, Cap, S, P, page, N, promo_spec, write  # noqa: E402

pages = [
    page([(N, "Last time, two heroes lost the gold. This time, they could lose everything.")], "1",
         [P("dark", under=["stars"], fx=["bolt:0.15,0,0.3,0.45,0.8@1.2", "bolt:0.85,0,0.7,0.4,0.8@1.6", "eyes:0.5,0.3,0.06,120,210,255@2"])],
         titles=[{"text": "THE ROYAL RIVALRY", "y": 0.5, "size": 96, "at": "lineend:0-0.4"}, {"text": "THE STORM ARRIVES", "y": 0.58, "size": 64, "at": "lineend:0+0.1", "style": "white"}]),
    page([("wizard", "Clear skies all week. Not a single cloud."), (N, "High above the hills, a cloud disagreed.")], "2v",
         [P("day", art=[A("th19", .25, .7, .62), A("wizard", .72, .64, .86, enter="right")], bubbles=[B(0, .34, .24, [.62, .4], w=460)]),
          P("storm", under=["smoke:0.5,0.4,80"], fx=["bolt:0.6,0,0.5,0.6,0.8@line:1+1.2", "flash@line:1+1.2"], at="line:1-0.3",
            sfx=[S("RUMBLE...", .5, .8, "line:1+1", style="zap", size=80)])]),
    page([(N, "Then the sky split open. An Electro Dragon. The biggest anyone had ever seen.")], "1",
         [P("storm", fx=["bolt:0.05,0,0.2,0.4,0.6@1.2", "bolt:0.95,0,0.8,0.45,0.6@2"], art=[A("edrag_lvl10", .5, .5, .55, enter="down", at=1.0, bob=18)],
            sfx=[S("KRRRZZZT!", .5, .14, "lineend:0-1.2", style="zap", size=120)])], shake=["lineend:0-1.2"]),
    page([("king", "Stand back. This dragon is MINE."), ("queen", "You can't punch something that flies.")], "2v",
         [P("burst:orange", art=[A("king_charge", .32, .6, .9, enter="left")], bubbles=[B(0, .7, .26, [.45, .4], shout=True, w=420)]),
          P("burst:purple", art=[A("queen_aim", .7, .6, .9, enter="right")], bubbles=[B(1, .3, .26, [.6, .4], w=460)], at="line:1-0.4")]),
    page([(N, "The Barbarians threw their swords. The swords came back down."), ("barbarians", "Ow. Ow. OW.")], "2v",
         [P("storm", art=[A("barbarian", .3, .66, .85), A("edrag_2", .78, .3, .45, bob=12)], sfx=[S("WHOOSH!", .55, .2, 1.2, style="white", size=80)]),
          P("burst:red", art=[A("barb_emote_set_3", .35, .6, .85)], bubbles=[B(1, .72, .26, [.5, .4], size=40, w=360)], sfx=[S("BONK!", .75, .7, "line:1-0.2", style="red", size=80)], at="line:1-0.5")]),
    page([(N, "He missed by forty feet. She hit his helmet instead."),
          ("king", "MY HELMET!"), ("queen", "Your head was in my shot.")], "1/2",
         [P("storm", art=[A("king_charge", .25, .78, .5, move=[.5, .3], moveAt=0.3, moveEnd=1.8, rot=-0.3), A("edrag_3", .8, .22, .32, bob=12)],
            sfx=[S("SPLOOSH!", .5, .8, 2.0, style="zap", size=90), S("CLANG!", .5, .45, "line:1-0.3", style="red", size=110)]),
          P("burst:red", art=[A("bk_emote", h=.8)], bubbles=[B(1, .5, .16, [.5, .32], shout=True, size=36, w=380)], at="line:1-0.3"),
          P("burst:purple", art=[A("aq_emote", h=.8)], bubbles=[B(2, .5, .16, [.5, .32], size=32, w=400)], at="line:2-0.3")], shake=["line:1-0.3"]),
    page([(N, "And lightning loves a crowd.")], "1",
         [P("storm", art=[A("barbarian", .25, .72, .4), A("archer", .5, .72, .38, flip=True), A("barbarian", .75, .72, .38), A("edrag_1", .75, .2, .3, bob=10)],
            fx=["bolt:0.75,0.25,0.25,0.65,1,14@0.3", "bolt:0.25,0.65,0.5,0.65,1,12@0.6", "bolt:0.5,0.65,0.75,0.65,1,12@0.9", "flash:150,210,255@0.3"],
            sfx=[S("ZAP! ZAP! ZAP!", .5, .45, 0.3, style="zap", size=100)])], shake=[0.3, 0.9]),
    page([("warden", "STOP! Together, or not at all!"), (N, "But they were too busy shouting to hear him.")], "1",
         [P("gold", under=["glow:0.5,0.5,700"], art=[A("warden", .5, .62, .7), A("eq_tome", .78, .72, .2, bob=8)],
            fx=["ring:0.5,0.5,900@0.8", "ring:0.5,0.5,900@1.8"], bubbles=[B(0, .5, .14, [.5, .3], shout=True, w=560)])], shake=[0.4]),
    page([(N, "The dragon struck. The golden shield shattered. And the Grand Warden fell.")], "1",
         [P("storm", under=["glow:0.5,0.5,600"], art=[A("edrag_1", .3, .25, .35, flip=True, bob=10), A("warden", .62, .7, .5)],
            fx=["bolt:0.35,0.3,0.6,0.62,1,22@2.2", "flash:150,210,255@2.2", "ring:0.6,0.65,800@3.4", "darken:0.6@lineend:0-1"],
            sfx=[S("SHATTER!", .5, .45, 3.4, style="white", size=110)])], shake=[2.2, 3.4]),
    page([("queen", "Do you think he'll wake up?"), ("king", "He has to. Who else is going to yell at us?")], "1",
         [P("night", under=["stars", "rain"], art=[A("king_point", .25, .7, .5), A("queen_stand", .75, .7, .52, flip=True)],
            bubbles=[B(0, .7, .2, [.75, .45], w=440), B(1, .3, .34, [.25, .5], w=460)])]),
    page([(N, "Someone sent that dragon. Episode two, The Storm Arrives. Watch the full episode now, on the channel.")], "1",
         [P("dark", under=["stars"], fx=["sigil:0.5,0.3,150@0.8", "bolt:0.1,0,0.25,0.4,0.8@0.6"])],
         titles=[{"text": "FULL EPISODE", "y": 0.5, "size": 110, "at": "lineend:0-3.2"}, {"text": "ON THE CHANNEL", "y": 0.6, "size": 80, "at": "lineend:0-2.6", "style": "white"}]),
]

write(__file__, promo_spec("The Royal Rivalry, Episode 2: The Storm Arrives (promo)", pages))
