# App Store & Google Play data — one table for both stores

Two collectors, deliberately similar output, so a cross-platform app table is a merge and not a
project:

- [`app_store_apps`](https://quanticdata.io/collectors/app-store-scraper-api/) — search by term
  **or** fetch by id (numeric id, bundle id, or a store URL). Returns app id, bundle id, title,
  developer + developer URL, category and full category list, rating, review count, rating for
  the current version, price (number **and** formatted), currency, version, release and update
  dates, content rating, download size, icon, screenshots, description and URL. **$0.0008 per app.**
- [`google_play_apps`](https://quanticdata.io/collectors/google-play-scraper-api/) — fetch by
  package name. Returns package, title, developer, category, description, rating, reviews, price,
  currency, content rating, OS requirement, install band, icon and URL. **$0.003 per app.**

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here

python3 search_apps.py "podcast player" --country us --max 40 --out apps.csv
python3 compare_stores.py apps.json --out cross-store.csv
python3 version_watch.py apps.json --state versions.json   # release cadence, from cron
```

## Files

| File | What it does |
|---|---|
| [`stores.py`](stores.py) | both collectors behind one normalised row |
| [`search_apps.py`](search_apps.py) | App Store search → CSV, with the price/rating breakdown |
| [`compare_stores.py`](compare_stores.py) | the same app on both stores, side by side |
| [`version_watch.py`](version_watch.py) | track versions and update dates — a shipping-cadence signal |

## The normalised row

```jsonc
{ "store": "app_store",            // or "google_play"
  "id": "324684580",               // app_id, or the package name on Play
  "title": "Spotify",
  "developer": "Spotify Ltd.",
  "category": "Music",
  "rating": 4.8, "reviews": 28412991,
  "price": 0, "currency": "USD",
  "version": "9.0.16", "updated_at": "2026-08-14",
  "content_rating": "12+",
  "installs": null,                // Play only
  "url": "https://apps.apple.com/us/app/id324684580" }
```

`installs` is a **band** on Play ("100M+"), never a number, and Apple publishes no equivalent at
all. Any cross-store "downloads" comparison is an estimate someone else invented; this repo does
not pretend otherwise.

## Two things the data actually supports

**Release cadence.** `version` and `updated_at` on a schedule tell you how often a competitor
ships. That is a real, verifiable signal, and `version_watch.py` builds it from a JSON state file.

**Rating trajectory per version.** App Store exposes `rating_current_version` alongside the
lifetime rating. When the current-version rating sits well below the lifetime one, the last
release went badly — which is visible days before it shows up in the headline number.

## Cross-store gotchas

- **Categories do not map.** Apple's "Productivity" and Play's "Productivity" contain different
  apps; treat category as a per-store label, not a join key.
- **Same app, different ids.** Match on developer + title, then verify by hand. `compare_stores.py`
  takes an explicit pairing file for exactly this reason.
- **Prices are per storefront** — pass `country` and store it with the row.

## Related

- [App Store scraper API](https://quanticdata.io/collectors/app-store-scraper-api/) · [Google Play scraper API](https://quanticdata.io/collectors/google-play-scraper-api/)
- [All 31 collectors](https://quanticdata.io/collectors/) · [Market research data](https://quanticdata.io/market-research-data/)
- [Documentation](https://quanticdata.io/docs/)

MIT licensed.
