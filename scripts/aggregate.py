"""Shared price-aggregation core for the history pipeline.

No value-range filtering: the app trusts raw prices as-is, so the history must
too. We only require a present numeric value per fuel.
"""

FUELS = ["diesel", "dieselPremium", "gasoline95", "gasoline98", "lpg"]
MIN_SAMPLE = 10  # too few stations to be a meaningful distribution


def pct(sorted_vals, p):
    """Linear-interpolation percentile (numpy-style), p in 0..100."""
    n = len(sorted_vals)
    if n == 0:
        return None
    if n == 1:
        return round(sorted_vals[0], 3)
    k = (n - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, n - 1)
    if f == c:
        return round(sorted_vals[f], 3)
    return round(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f), 3)


def fuel_stats(stations):
    """Per-fuel percentile summary over a list of station dicts."""
    out = {}
    for fuel in FUELS:
        vals = sorted(
            p
            for s in stations
            if isinstance((p := s.get("prices", {}).get(fuel)), (int, float))
        )
        if len(vals) < MIN_SAMPLE:
            continue
        out[fuel] = {
            "count": len(vals),
            "min": round(vals[0], 3),
            "p1": pct(vals, 1),
            "p5": pct(vals, 5),
            "p25": pct(vals, 25),
            "median": pct(vals, 50),
            "p75": pct(vals, 75),
            "p95": pct(vals, 95),
            "max": round(vals[-1], 3),
        }
    return out
