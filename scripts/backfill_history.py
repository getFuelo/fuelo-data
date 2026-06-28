#!/usr/bin/env python3
"""Backfill per-fuel daily price history from the git history of stations-<c>.json.

Walks every commit that touched the country's station snapshot, computes robust
per-fuel percentiles (p5/p25/median/p75/p95 + min/max/count) over all stations
selling that fuel, and writes history-<c>.json (one row per day, newest last).

The 6-hourly refresh workflow appends today's row going forward; this script
seeds the file from the ~month of snapshots already in git.

Usage: python3 scripts/backfill_history.py [es fr ad ...]   (default: all three)
"""
import json
import subprocess
import sys

from aggregate import fuel_stats


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def commits_for(path):
    """(sha, YYYY-MM-DD) for every commit touching path, oldest first."""
    out = git("log", "--format=%H|%cd", "--date=format:%Y-%m-%d", "--", path)
    rows = [line.split("|") for line in out.strip().splitlines() if line]
    return list(reversed(rows))  # oldest -> newest


def stats_at(sha, path):
    """Per-fuel stats from the snapshot at a given commit."""
    return fuel_stats(json.loads(git("show", f"{sha}:{path}")))


def backfill(country):
    path = f"stations-{country}.json"
    commits = commits_for(path)
    by_day = {}  # day -> stats (last commit of the day wins)
    for sha, day in commits:
        try:
            by_day[day] = stats_at(sha, path)
        except Exception as e:
            print(f"  ! {country} {day} {sha[:8]}: {e}", file=sys.stderr)
    # Reshape to per-fuel series, one row per day.
    series = {}
    for day in sorted(by_day):
        for fuel, st in by_day[day].items():
            series.setdefault(fuel, []).append({"date": day, **st})
    result = {"country": country.upper(), "fuels": sorted(series), "series": series}
    out_path = f"history-{country}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, separators=(",", ":"))
    print(f"{country}: {len(by_day)} days, fuels={sorted(series)} -> {out_path}")
    return result


def spread_report(result):
    """Print p25-p75 vs p5-p95 widths so we can judge whether the outer band matters."""
    c = result["country"]
    for fuel in ("diesel", "gasoline95"):
        rows = result["series"].get(fuel, [])
        if not rows:
            continue
        iqr = [r["p75"] - r["p25"] for r in rows]
        outer = [r["p95"] - r["p5"] for r in rows]
        first, last = rows[0], rows[-1]
        print(f"\n[{c} {fuel}] {len(rows)} days  ({first['date']} -> {last['date']})")
        print(f"  median: {first['median']:.3f} -> {last['median']:.3f}")
        print(
            f"  p25-p75 width: avg {sum(iqr)/len(iqr):.3f}  "
            f"(min {min(iqr):.3f}, max {max(iqr):.3f})"
        )
        print(
            f"  p5-p95  width: avg {sum(outer)/len(outer):.3f}  "
            f"(min {min(outer):.3f}, max {max(outer):.3f})"
        )
        print(
            f"  outer/inner ratio: {(sum(outer)/len(outer))/(sum(iqr)/len(iqr)):.2f}x  "
            f"(latest: p5={last['p5']:.3f} p25={last['p25']:.3f} "
            f"med={last['median']:.3f} p75={last['p75']:.3f} p95={last['p95']:.3f})"
        )


if __name__ == "__main__":
    countries = sys.argv[1:] or ["es", "fr", "ad", "pt"]
    for c in countries:
        spread_report(backfill(c))
