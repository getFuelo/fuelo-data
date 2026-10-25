#!/usr/bin/env python3
"""Widen a main-line plaza gate to span every mapped booth lane.

Gate lines were cut ±8 m around the single booth node on the carriageway. Where
OSM maps the booth lanes as separate ways, a route through an outer lane passes
the end of the line uncrossed and the plaza is not charged (found by
sweep_terminals.cjs as a NEAR MISS). Same per-area, graph-free approach as
fetch_area_coverage.py: only the plaza is fetched, from Overpass at the catalog
snapshot, and frozen as evidence; build_area_coverage.py applies it.

    python3 scripts/coverage/fetch_plaza_gate.py NAME --network ID --gate GATE [--max-lane-gap M]

The line keeps its centre and orientation (so crossing direction semantics are
unchanged) and grows over consecutive lane crossings (gaps of at most 15 m, or
--max-lane-gap where the plaza fans its lanes wider; recorded in the evidence) plus 8 m.
It never shrinks an existing line. Refused if
the widened line would cut any way that is not a motorway/trunk carriageway or
link: a parallel free road must never be charged.
"""
import argparse, json, math
from pathlib import Path
from fetch_area_coverage import ROOT, SNAPSHOT, overpass

MARGIN_M, SEARCH_M, MAX_LANE_GAP_M = 8, 80, 15
LANES = {'motorway', 'motorway_link', 'trunk', 'trunk_link'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name'); ap.add_argument('--network', required=True); ap.add_argument('--gate', required=True)
    ap.add_argument('--max-lane-gap', type=float, default=MAX_LANE_GAP_M)
    args = ap.parse_args()
    catalog = json.loads((ROOT / 'tolls-es-reviewed.json').read_text())
    net = next(n for n in catalog['pricing'] if n['id'] == args.network)
    gate = next(g for g in net['gates'] if g['id'] == args.gate)
    a, b = gate['line']
    c = {'lat': (a['lat'] + b['lat']) / 2, 'lng': (a['lng'] + b['lng']) / 2}
    k = math.cos(math.radians(c['lat'])) * 111320
    to_xy = lambda p: ((p['lng'] - c['lng']) * k, (p['lat'] - c['lat']) * 110570)
    ax, ay = to_xy(b)[0] - to_xy(a)[0], to_xy(b)[1] - to_xy(a)[1]
    norm = math.hypot(ax, ay); ux, uy = ax / norm, ay / norm  # unit vector along the gate line

    query = (f'[out:json][timeout:60][date:"{SNAPSHOT}"];'
             f'way(around:{SEARCH_M},{c["lat"]:.7f},{c["lng"]:.7f})[highway];out meta geom;')
    ways = [e for e in overpass(query)['elements'] if e['type'] == 'way']
    cuts, refused = [], []
    for w in ways:
        pts = [to_xy({'lat': g['lat'], 'lng': g['lon']}) for g in w['geometry']]
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            # Intersect the segment with the gate axis (through the centre).
            s1, s2 = x1 * -uy + y1 * ux, x2 * -uy + y2 * ux  # signed distance to the axis
            if s1 * s2 > 0 or s1 == s2: continue
            t = s1 / (s1 - s2)
            along = (x1 + t * (x2 - x1)) * ux + (y1 + t * (y2 - y1)) * uy
            if abs(along) > SEARCH_M: continue
            cut = {'way': str(w['id']), 'version': w['version'], 'highway': w['tags'].get('highway'), 'ref': w['tags'].get('ref'), 'offsetM': round(along, 1)}
            cuts.append(cut)
            if cut['highway'] not in LANES: refused.append(cut)
    assert cuts, 'no carriageway crosses the gate axis'
    # Grow from the centre over consecutive lane crossings only: booth lanes sit
    # a few metres apart, a separate (possibly free) road lies beyond a gap.
    reach = {}
    for side in (1, -1):
        edge = 0
        for x in sorted((x for x in cuts if x['highway'] in LANES and x['offsetM'] * side >= 0), key=lambda x: abs(x['offsetM'])):
            if abs(x['offsetM']) - edge > args.max_lane_gap: break
            edge = abs(x['offsetM'])
        reach[side] = edge
    previous_half = math.hypot(*(to_xy(b)[i] - to_xy(a)[i] for i in (0, 1))) / 2
    half = max(max(reach.values()) + MARGIN_M, previous_half)
    # Only lanes within the widened span matter; a non-lane way there is refused.
    blocking = [x for x in refused if abs(x['offsetM']) <= half]
    if blocking:
        raise SystemExit(f'REFUSED {args.name}: widened line would cut ' + ', '.join(f"way {x['way']} highway={x['highway']} at {x['offsetM']} m" for x in blocking))
    line = [{'lat': round(c['lat'] + s * uy / 110570, 9), 'lng': round(c['lng'] + s * ux / k, 9)} for s in (-half, half)]
    out = ROOT / 'audit/area-gates' / f'{args.name}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        'name': args.name, 'network': args.network, 'gate': args.gate, 'snapshot': SNAPSHOT,
        'source': 'https://overpass-api.de/api/interpreter (attic query at the snapshot)', 'query': query,
        'attribution': '© OpenStreetMap contributors, ODbL 1.0',
        'reason': 'Booth lanes mapped as separate ways reach beyond the ±8 m line; routes through outer lanes passed the plaza uncrossed.',
        'previousLine': gate['line'], 'line': line, 'halfLengthM': round(half, 1), 'maxLaneGapM': args.max_lane_gap,
        'lanes': sorted([x for x in cuts if abs(x['offsetM']) <= half], key=lambda x: x['offsetM']),
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{args.name}: {args.network}/{args.gate} widened to ±{half:.0f} m over {len([x for x in cuts if abs(x["offsetM"]) <= half])} lane crossings')


if __name__ == '__main__':
    main()
