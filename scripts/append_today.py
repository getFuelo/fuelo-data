#!/usr/bin/env python3
"""Append today's price aggregate to history-<c>.json.

Run by the refresh workflow after the fresh stations-<c>.json lands. Computes
the per-fuel summary from the current snapshot and appends one row dated today
(UTC), replacing any existing row for today so same-day re-runs update rather
than duplicate.

Usage: python3 scripts/append_today.py [es fr ad ...]
"""
import json
import os
import sys
from datetime import datetime, timezone

from aggregate import fuel_stats


def append(country, date):
    spath = f"stations-{country}.json"
    if not os.path.exists(spath):
        print(f"{country}: no {spath}, skipping", file=sys.stderr)
        return
    stats = fuel_stats(json.load(open(spath)))
    if not stats:
        print(f"{country}: no usable fuels, skipping", file=sys.stderr)
        return
    hpath = f"history-{country}.json"
    hist = (
        json.load(open(hpath))
        if os.path.exists(hpath)
        else {"country": country.upper(), "fuels": [], "series": {}}
    )
    series = hist.setdefault("series", {})
    for fuel, st in stats.items():
        rows = [r for r in series.get(fuel, []) if r["date"] != date]
        rows.append({"date": date, **st})
        rows.sort(key=lambda r: r["date"])
        series[fuel] = rows
    hist["country"] = country.upper()
    hist["fuels"] = sorted(series)
    with open(hpath, "w") as f:
        json.dump(hist, f, separators=(",", ":"))
    print(f"{country}: appended {date} ({sorted(stats)})")


if __name__ == "__main__":
    countries = sys.argv[1:] or ["es", "fr", "ad", "pt"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for c in countries:
        append(c, today)
