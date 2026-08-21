"""App Store search → CSV, with the breakdown you would otherwise compute by hand.

    python3 search_apps.py "podcast player" --country us --max 40 --out apps.csv
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter

from stores import ROW_FIELDS, apple_search


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("term")
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--out", default="apps.csv")
    args = ap.parse_args()

    rows = apple_search(args.term, args.country, args.lang, args.max)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    paid = [r for r in rows if (r.get("price") or 0) > 0]
    rated = [r for r in rows if r.get("rating")]
    print(f"{len(rows)} apps for {args.term!r} in {args.country.upper()} → {args.out}\n")
    print(f"free {len(rows) - len(paid)} / paid {len(paid)}"
          + (f", paid median {statistics.median([r['price'] for r in paid]):.2f} "
             f"{paid[0].get('currency') or ''}" if paid else ""))
    if rated:
        print(f"rating median {statistics.median([r['rating'] for r in rated]):.2f} "
              f"over {len(rated)} rated apps")

    print("\ncategories")
    for category, n in Counter(r.get("category") for r in rows).most_common(8):
        print(f"  {n:>3}  {category}")

    print("\nby review volume")
    for row in sorted(rows, key=lambda r: -(r.get("reviews") or 0))[:12]:
        slipping = ""
        current, lifetime = row.get("rating_current_version"), row.get("rating")
        if current and lifetime and current < lifetime - 0.3:
            slipping = f"   ⚠ current version {current} vs lifetime {lifetime}"
        print(f"  {(row.get('reviews') or 0):>10,} reviews  {str(row.get('rating') or '-'):>4}★  "
              f"{(row.get('title') or '')[:36]:<38}{row.get('developer') or ''}{slipping}")


if __name__ == "__main__":
    main()
