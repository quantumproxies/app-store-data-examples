"""Track versions and update dates — how often does a competitor actually ship?

App Store publishes the current version and its update date. Sampling that on a
schedule builds a release history nobody publishes, and the gaps between releases
are the signal.

    python3 version_watch.py apps.json --state versions.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from datetime import date, datetime

from stores import apple_by_id


def parse_day(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--state", type=pathlib.Path, default=pathlib.Path("versions.json"))
    ap.add_argument("--country", default="us")
    args = ap.parse_args()

    pairs = json.loads(args.file.read_text(encoding="utf-8"))
    app_ids = [str(p["app_id"]) for p in pairs if p.get("app_id")]
    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}

    rows = apple_by_id(app_ids, args.country)
    today = date.today().isoformat()

    print(f"{'app':<28}{'version':<12}{'updated':<12}{'cadence':>10}  status")
    for row in rows:
        history = state.setdefault(str(row["id"]), {"title": row.get("title"), "releases": []})
        releases = history["releases"]

        version, updated = row.get("version"), row.get("updated_at")
        is_new = not releases or releases[-1]["version"] != version
        if is_new and version:
            releases.append({"version": version, "updated_at": updated, "seen_at": today})

        days = [parse_day(r["updated_at"]) for r in releases]
        days = [d for d in days if d]
        gaps = [(b - a).days for a, b in zip(days, days[1:]) if (b - a).days > 0]
        cadence = f"{statistics.median(gaps):.0f}d" if gaps else "—"

        status = "NEW RELEASE" if is_new and len(releases) > 1 else ""
        last = parse_day(updated)
        if last and (date.today() - last).days > 180:
            status = status or f"quiet {(date.today() - last).days}d"

        print(f"{str(row.get('title'))[:27]:<28}{str(version or '-'):<12}"
              f"{str(updated or '-')[:10]:<12}{cadence:>10}  {status}")

    args.state.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"\nstate → {args.state} "
          f"({sum(len(v['releases']) for v in state.values())} releases recorded)")


if __name__ == "__main__":
    main()
