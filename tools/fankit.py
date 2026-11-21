"""Search and download official art from Supercell's Fan Kit (fankit.supercell.com).

  uv run tools/fankit.py search "town hall 19" [--limit 40]      # list matching assets
  uv run tools/fankit.py fetch projects/<name>/fankit.json       # download a project's art

A project's fankit.json maps names to assets:
  {"library": 338, "assets": {"th19": {"id": 168064, "title": "th19_default_2k", "width": 1600}}}
Files land in projects/<name>/fankit/<name>.png (gitignored: Supercell's files are shown in our
videos under the Fan Content Policy, but are not redistributed in this repository).

Fan Content Policy: don't modify the art itself (moving, scaling and animating it is fine), credit
it with the disclaimer in the video description, and never use leaked or pre-release material.
"""
import argparse
import json
import pathlib
import sys
import urllib.parse
import urllib.request

API = "https://fankit.supercell.com/api/assets/search/{library}?limit={limit}&page={page}&order=NEWEST&q={q}"
CLASH_OF_CLANS = 338  # library id of the Clash of Clans "Game assets" page
DISCLAIMER = ("This material is unofficial and is not endorsed by Supercell. For more information see "
              "Supercell's Fan Content Policy: www.supercell.com/fan-content-policy.")


def search(q, library=CLASH_OF_CLANS, limit=40, page=1):
    url = API.format(library=library, limit=limit, page=page, q=urllib.parse.quote(q))
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def find(asset_id, title, library):
    """The API has no lookup by id, so search by title and match the id."""
    page = 1
    while True:
        d = search(title, library, limit=100, page=page)
        for a in d["data"]:
            if a["id"] == asset_id:
                return a
        if not d.get("hasMore") or page >= 10:
            raise LookupError(f"asset {asset_id} ({title}) not found")
        page += 1


def fetch(manifest_path):
    manifest = json.loads(pathlib.Path(manifest_path).read_text())
    library = manifest.get("library", CLASH_OF_CLANS)
    out = pathlib.Path(manifest_path).parent / "fankit"
    out.mkdir(exist_ok=True)
    for name, spec in manifest["assets"].items():
        dest = out / f"{name}.png"
        if dest.exists():
            continue
        a = find(spec["id"], spec["title"], library)
        width = min(spec.get("width", a["width"]), a["width"])
        url = a["generic_url"].replace("{width}", str(width))
        with urllib.request.urlopen(url, timeout=120) as r:
            dest.write_bytes(r.read())
        print(f"  {name}: {a['title']} ({width}px, {dest.stat().st_size // 1024} KB)")
    print(f"Art in {out}/. Put this in the video description:\n  {DISCLAIMER}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=40)
    s.add_argument("--library", type=int, default=CLASH_OF_CLANS)
    f = sub.add_parser("fetch")
    f.add_argument("manifest")
    a = ap.parse_args()
    if a.cmd == "search":
        d = search(a.query, a.library, a.limit)
        print(f"{d['total']} matches")
        for x in d["data"]:
            print(f"  {x['id']:>7}  {x['width']}x{x['height']}  {x['created'][:10]}  {x['title']}")
    else:
        fetch(a.manifest)


if __name__ == "__main__":
    try:
        main()
    except (LookupError, OSError) as e:
        sys.exit(str(e))
