"""Shared helpers for The Royal Rivalry full episodes and promos (build.py in each episode folder).

A page is one scene: its spoken lines ([speaker, text]) and the comic page that plays under them.
Panel coordinates are fractions of the panel; "line:N" / "lineend:N" times refer to the page's Nth line.
The page format is drawn by motion/coc/comicpage.js.
"""
import json
import re
from pathlib import Path

N = "narrator"
HJ = "img:bg_2026_hammerjam_backgroundonly"

# Kokoro voices for the full episodes.
KOKORO_CAST = {
    "narrator": "bm_george", "king": "am_fenrir", "queen": "af_bella", "warden": "bm_fable", "wizard": "bm_lewis",
    "goblin": "am_puck", "goblin2": "am_echo", "boss": "am_onyx", "barbarians": "am_eric", "archers": "af_kore", "healer": "af_sky",
    "titan": "bf_emma",  # the Storm Sorceress (Electro Titan)
}
# ElevenLabs premade voices for the 1-minute promos (library voices need a paid plan).
ELEVEN_CAST = {
    "narrator": "IKne3meq5aSn9XLyUdCD",  # Charlie, the channel's Shorts narrator
    "king": "nPczCjzI2devNBz1zQrb",      # Brian
    "queen": "Xb7hH8MSUJpSbSDYk0k2",     # Alice
    "warden": "JBFqnCBsd6RMkjVDRZzb",    # George
    "wizard": "onwK4e9ZLuTAKqWW03F9",    # Daniel
    "goblin": "SOYHLrjzK2X1ezoPC6cr",    # Harry
    "boss": "N2lVS1w4EtoT3dr4eOWO",      # Callum
    "healer": "EXAVITQu4vr4xnSDxMaL",    # Sarah
    "barbarians": "CwhRBWXzGAHq8TQ4Fs17",  # Roger
    "titan": "pFZP5JQG7iQjIQuC4Bku",     # Lily, the Storm Sorceress
}
SOURCES = ["Original fan story. Characters and art: official Supercell Fan Kit (https://fankit.supercell.com), "
           "used under Supercell's Fan Content Policy: unofficial, not endorsed by Supercell."]


def A(name, x=.5, y=.62, h=.85, **kw): return {"name": name, "x": x, "y": y, "h": h, **kw}
def B(line, x=.5, y=.18, tail=None, **kw): return {"line": line, "x": x, "y": y, **({"tail": tail} if tail else {}), **kw}
def Cap(text, at=0, **kw): return {"text": text, "at": at, **kw}
def S(text, x, y, at, **kw): return {"text": text, "x": x, "y": y, "at": at, **kw}
def P(bg, art=(), bubbles=(), caps=(), sfx=(), fx=(), under=(), at=None, **kw):
    d = {"bg": bg, "art": list(art), "bubbles": list(bubbles), "caps": list(caps), "sfx": list(sfx), "fx": list(fx), "under": list(under), **kw}
    if at is not None: d["at"] = at
    return d
def page(lines, layout, panels, **kw): return {"lines": [list(l) for l in lines], "page": {"layout": layout, "panels": panels, **kw}}


# Sound design from the pages themselves: a pop as each later panel appears, a matching sound for each
# sound-effect word, an impact on every screen shake, a stamp for big titles. Pages can add their own "extra_sfx".
SFX_SOUND = {"zap": "magic", "fire": "impact", "green": "tap", "red": "thud", "gold": "ding", "white": "whoosh", "purple": "magic"}


def add_cues(pages):
    for pg in pages:
        cues, P_ = [], pg["page"]
        for k, panel in enumerate(P_["panels"]):
            if k and "at" in panel:
                cues.append({"sound": "pop", "at": panel["at"], "offset": 0.05, "volume": 0.28})
            for sfx in panel.get("sfx", []):
                cues.append({"sound": sfx.get("sound") or SFX_SOUND.get(sfx.get("style", "fire"), "impact"), "at": sfx["at"], "volume": 0.42})
        for at in P_.get("shake", []):
            cues.append({"sound": "impact", "at": at, "volume": 0.45})
        for tt in P_.get("titles", []):
            cues.append({"sound": "stamp", "at": tt["at"], "volume": 0.4})
        cues += pg.pop("extra_sfx", [])
        for c in cues:
            if isinstance(c["at"], str) and c["at"].startswith("word:"):
                m = re.match(r"^([^+\-#]+)(?:#\d+)?([+-][\d.]+)?$", c.pop("at")[5:])
                c["word"] = m.group(1); c["offset"] = c.get("offset", 0) + float(m.group(2) or 0)
            elif isinstance(c["at"], str) and c["at"].startswith("end"):
                c["at"] = 0.0
        pg["sfx"] = cues
    return pages


def full_episode_spec(title, pages):
    return {
        "title": title, "series": "The Royal Rivalry (Clash of Clans fan comic), full episodes",
        "visuals": "motion", "title_card": False, "width": 1920, "height": 1080,
        "tts": "kokoro", "cast": KOKORO_CAST, "speed": 0.92, "scene_pad": 1.0,
        # Narrator on Kokoro; every character line acted with emotion by Chatterbox in the same voice.
        "emotive": {"skip": ["narrator"]},
        "caption": {"max_chars": 46, "max_words": 8, "size": 0.046, "margin": 0.03},
        "music": {"sound": "music_strategy", "volume": 0.10},
        "sources": SOURCES, "scenes": add_cues(pages),
    }


def promo_spec(title, pages):
    return {
        "title": title, "series": "The Royal Rivalry (Clash of Clans fan comic), full-episode promos",
        "visuals": "motion", "title_card": False, "width": 1080, "height": 1920,
        "tts": "elevenlabs", "cast": ELEVEN_CAST, "scene_pad": 0.45,
        "caption": {"max_chars": 18, "max_words": 4, "size": 0.05, "margin": 0.185},
        "music": {"sound": "music_strategy", "volume": 0.18},
        "sources": SOURCES, "scenes": add_cues(pages),
    }


def write(build_file, spec):
    out = Path(build_file).with_name("script.json")
    out.write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    lines = [l for p in spec["scenes"] for l in p["lines"]]
    words, chars = sum(len(l[1].split()) for l in lines), sum(len(l[1]) for l in lines)
    print(f"{len(spec['scenes'])} pages, {len(lines)} lines, {words} words, {chars} characters -> {out}")
