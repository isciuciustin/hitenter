#!/usr/bin/env python3
"""Snapshot GitHub release download totals into public/stats.json.

GitHub only keeps all-time totals per file, so we store one snapshot per UTC
day; the site shows daily downloads as the difference between snapshots.
"""
import datetime, json, os, urllib.request

REPO = os.environ.get("REPO", "isciuciustin/hitenter")
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "stats.json")
PLATFORMS = {".zip": "windows", ".exe": "windows", ".msi": "windows",
             ".dmg": "macos", ".deb": "linux", ".appimage": "linux", ".rpm": "linux"}

def totals():
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases?per_page=100",
                                 headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    out = {}
    for rel in json.load(urllib.request.urlopen(req)):
        counts = {"windows": 0, "macos": 0, "linux": 0}
        for a in rel["assets"]:
            ext = os.path.splitext(a["name"])[1].lower()
            if ext in PLATFORMS:
                counts[PLATFORMS[ext]] += a["download_count"]
        out[rel["tag_name"]] = counts
    return out

def main():
    try:
        with open(OUT) as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {"days": []}
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    stats["days"] = [d for d in stats["days"] if d["date"] != today]
    stats["days"].append({"date": today, "totals": totals()})
    stats["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(OUT, "w") as f:
        json.dump(stats, f, indent=1)
        f.write("\n")

if __name__ == "__main__":
    main()
