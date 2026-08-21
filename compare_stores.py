"""The same apps on both stores, side by side.

Pairing is explicit on purpose: automatic matching across stores is wrong often
enough that a wrong row is worse than no row.

    python3 compare_stores.py apps.json --country us --out cross-store.csv
    # apps.json: [{"name":"Spotify","app_id":"324684580","package":"com.spotify.music"}, …]
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib

from stores import apple_by_id, play_by_package

FIELDS = ["name", "apple_title", "play_title", "developer",
          "apple_rating", "play_rating", "apple_reviews", "play_reviews",
          "apple_price", "play_price", "currency", "apple_version", "apple_updated_at",
          "play_installs", "apple_url", "play_url"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--country", default="us")
    ap.add_argument("--out", default="cross-store.csv")
    args = ap.parse_args()

    pairs = json.loads(args.file.read_text(encoding="utf-8"))
    app_ids = [p["app_id"] for p in pairs if p.get("app_id")]
    packages = [p["package"] for p in pairs if p.get("package")]

    apple = {r["id"]: r for r in apple_by_id(app_ids, args.country)} if app_ids else {}
    play = {r["id"]: r for r in play_by_package(packages, args.country)} if packages else {}

    rows = []
    for pair in pairs:
        a = apple.get(str(pair.get("app_id")), {})
        p = play.get(pair.get("package"), {})
        rows.append({
            "name": pair.get("name"),
            "apple_title": a.get("title"), "play_title": p.get("title"),
            "developer": a.get("developer") or p.get("developer"),
            "apple_rating": a.get("rating"), "play_rating": p.get("rating"),
            "apple_reviews": a.get("reviews"), "play_reviews": p.get("reviews"),
            "apple_price": a.get("price"), "play_price": p.get("price"),
            "currency": a.get("currency") or p.get("currency"),
            "apple_version": a.get("version"), "apple_updated_at": a.get("updated_at"),
            "play_installs": p.get("installs"),
            "apple_url": a.get("url"), "play_url": p.get("url"),
        })

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} apps → {args.out}\n")
    print(f"{'app':<22}{'apple':>16}{'play':>16}  note")
    for row in rows:
        apple_cell = f"{row['apple_rating'] or '-'}★ {(row['apple_reviews'] or 0):,}"
        play_cell = f"{row['play_rating'] or '-'}★ {(row['play_reviews'] or 0):,}"
        note = ""
        if row["apple_rating"] and row["play_rating"]:
            gap = row["apple_rating"] - row["play_rating"]
            if abs(gap) >= 0.4:
                note = f"{'iOS' if gap > 0 else 'Android'} rates it {abs(gap):.1f}★ higher"
        print(f"{str(row['name'])[:21]:<22}{apple_cell:>16}{play_cell:>16}  {note}")

    print("\nInstall bands are Play-only and are bands, not counts. There is no comparable "
          "Apple figure — do not build a 'downloads' column.")


if __name__ == "__main__":
    main()
