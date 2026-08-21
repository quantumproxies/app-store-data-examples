"""Both app-store collectors behind one normalised row."""
from __future__ import annotations

import os
import time
from typing import Any

import requests

BASE = "https://api.quanticdata.io/v1"
_s = requests.Session()


def _h() -> dict[str, str]:
    key = os.environ.get("QUANTICDATA_API_KEY")
    if not key:
        raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
    return {"Authorization": f"Bearer {key}"}


def collect(slug: str, **input_: Any) -> list[dict]:
    body = {k: v for k, v in input_.items() if v not in (None, "", [], False)}
    r = _s.post(f"{BASE}/scraper/collectors/{slug}/run", json=body, headers=_h(), timeout=300)
    data = r.json()
    if data.get("type") == "error" or not r.ok:
        raise RuntimeError(f"{slug} ({r.status_code}): {data.get('message')}")

    run = data.get("payload", {})
    while run.get("status") in ("queued", "running"):
        time.sleep(3)
        run = _s.get(f"{BASE}/scraper/collectors/runs/{run['run_id']}",
                     headers=_h(), timeout=60).json().get("payload", {})
    return run.get("results") or []


def normalise_apple(row: dict) -> dict:
    return {
        "store": "app_store",
        "id": row.get("app_id"),
        "bundle_id": row.get("bundle_id"),
        "title": row.get("title"),
        "developer": row.get("developer"),
        "category": row.get("category"),
        "rating": row.get("rating"),
        "rating_current_version": row.get("rating_current_version"),
        "reviews": row.get("reviews"),
        "price": row.get("price"),
        "currency": row.get("currency"),
        "version": row.get("version"),
        "updated_at": row.get("updated_at"),
        "released_at": row.get("released_at"),
        "content_rating": row.get("content_rating"),
        "size_bytes": row.get("size_bytes"),
        "installs": None,
        "url": row.get("url"),
    }


def normalise_play(row: dict) -> dict:
    return {
        "store": "google_play",
        "id": row.get("package"),
        "bundle_id": row.get("package"),
        "title": row.get("title"),
        "developer": row.get("developer"),
        "category": row.get("category"),
        "rating": row.get("rating"),
        "rating_current_version": None,
        "reviews": row.get("reviews"),
        "price": row.get("price"),
        "currency": row.get("currency"),
        "version": None,
        "updated_at": None,
        "released_at": None,
        "content_rating": row.get("content_rating"),
        "size_bytes": None,
        "installs": row.get("installs"),
        "url": row.get("url"),
    }


ROW_FIELDS = ["store", "id", "title", "developer", "category", "rating",
              "rating_current_version", "reviews", "price", "currency", "version",
              "updated_at", "released_at", "content_rating", "installs", "url"]


def apple_search(term: str, country: str = "us", lang: str = "en", limit: int = 20) -> list[dict]:
    return [normalise_apple(r) for r in
            collect("app_store_apps", term=term, country=country, lang=lang, max_results=limit)]


def apple_by_id(ids: list[str], country: str = "us") -> list[dict]:
    return [normalise_apple(r) for r in
            collect("app_store_apps", app_ids=ids, country=country, max_results=len(ids))]


def play_by_package(packages: list[str], country: str = "us", lang: str = "en") -> list[dict]:
    return [normalise_play(r) for r in
            collect("google_play_apps", packages=packages, country=country, lang=lang,
                    max_results=len(packages))]
