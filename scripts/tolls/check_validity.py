#!/usr/bin/env python3
"""Fail when a network's tariff has expired or expires within 60 days.

The app refuses an expired tariff (the journey becomes unavailable), so a new
year's fares or a concession end date must be in the catalog before it bites.
"""
import datetime, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WARN_DAYS = 60


def main():
    today = datetime.date.today()
    catalog = json.loads((ROOT / 'tolls-es-reviewed.json').read_text())
    late = []
    for n in catalog['pricing']:
        until = datetime.date.fromisoformat(n['validThrough'])
        days = (until - today).days
        if days < WARN_DAYS:
            late.append((days, n['id'], n['validThrough']))
    for days, nid, until in sorted(late):
        print(f"{nid}: valid through {until} ({'EXPIRED' if days < 0 else f'{days} days left'})")
    print(f"{len(catalog['pricing'])} networks checked, {len(late)} expired or expiring within {WARN_DAYS} days")
    sys.exit(1 if late else 0)


if __name__ == '__main__':
    main()
