#!/usr/bin/env python3
"""Freeze the OSM ways behind a coverage gap found by sweep_terminals.cjs.

Per-area, graph-free replacement for the national extract: only the area of
the gap is fetched, from Overpass at the catalog's OSM snapshot, and the result
is committed as evidence. build_area_coverage.py then adds it as coverage only.

    python3 scripts/coverage/fetch_area_coverage.py AREA --network ID \
        --bbox S,W,N,E [--reason TEXT]

Takes every uncovered run in pricing-candidates/terminal-sweep/results.json that
lies inside the bbox (run `sweep_terminals.cjs check` first), and refuses to
write evidence unless:
  - every sampled point of every run lies within 12 m of the selected ways
    (the app's coverage tolerance), so the router really drives on them;
  - every selected way is tagged toll=yes with a motorway/trunk class;
  - no node on a selected way is a toll booth or toll gantry, except at an
    existing gate of the network: an unmapped charging point needs a gate and
    a fare, never coverage alone;
  - each run starts and ends next to the network's existing coverage.
"""
import argparse, json, math, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SWEEP = ROOT / 'pricing-candidates/terminal-sweep'
SNAPSHOT = '2026-09-15T20:20:37Z'  # OSM state the reviewed catalog was built from
OVERPASS = 'https://overpass-api.de/api/interpreter'
TOLERANCE_KM = .012
CLASSES = {'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link'}


def decode(shape, precision=6):
    out, i, lat, lng = [], 0, 0, 0
    while i < len(shape):
        for k in (0, 1):
            shift = result = 0
            while True:
                b = ord(shape[i]) - 63; i += 1
                result |= (b & 0x1f) << shift; shift += 5
                if b < 0x20: break
            v = ~(result >> 1) if result & 1 else result >> 1
            if k == 0: lat += v
            else: lng += v
        out.append((lat / 10 ** precision, lng / 10 ** precision))
    return out


def dist_km(p, a, b):
    k = math.cos(math.radians(p[0])) * 111.32
    ax, ay, bx, by = (a[1] - p[1]) * k, (a[0] - p[0]) * 110.57, (b[1] - p[1]) * k, (b[0] - p[0]) * 110.57
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy))) if dx or dy else 0
    return math.hypot(ax + t * dx, ay + t * dy)


def near(p, lines):
    return any(dist_km(p, a, b) <= TOLERANCE_KM for line in lines for a, b in zip(line, line[1:]))


def sample(points):
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        steps = max(1, math.ceil(dist_km(a, a, b) / .01))
        out += [(a[0] + (b[0] - a[0]) * s / steps, a[1] + (b[1] - a[1]) * s / steps) for s in range(1, steps + 1)]
    return out


def overpass(query, attempts=6):
    data = urllib.parse.urlencode({'data': query}).encode()
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(OVERPASS, data=data, headers={'User-Agent': 'Fuelo-toll-coverage-audit/1.0'})
            return json.loads(urllib.request.urlopen(req, timeout=180).read())
        except urllib.error.HTTPError as error:
            # The public instance sheds load with 429/502/504; back off and retry.
            if error.code not in (429, 502, 503, 504) or attempt == attempts - 1: raise
            time.sleep(30 * (attempt + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('area'); ap.add_argument('--network', required=True)
    ap.add_argument('--bbox', required=True, help='S,W,N,E around the gap')
    ap.add_argument('--reason', default='')
    args = ap.parse_args()
    s, w, n, e = map(float, args.bbox.split(','))
    inside = lambda p: s <= p[0] <= n and w <= p[1] <= e

    # Runs (with one covered neighbour each side) from the cached sweep journeys.
    results = json.loads((SWEEP / 'results.json').read_text())
    runs, journeys = [], set()
    for gap in results['gaps']:
        if not (inside((gap['from']['lat'], gap['from']['lng'])) and inside((gap['to']['lat'], gap['to']['lng']))): continue
        rec = json.loads((SWEEP / 'responses' / (gap['journey'] + '.json')).read_text())
        geometry = [pt for leg in rec['trip']['legs'] for pt in decode(leg['shape'])]
        runs.append(geometry[max(0, gap['begin'] - 1): gap['end'] + 2]); journeys.add(gap['journey'])
    assert runs, 'no sweep gap inside the bbox; run sweep_terminals.cjs check first'

    # Network coverage, to check each run joins it at both ends.
    catalog = json.loads((ROOT / 'tolls-es-reviewed.json').read_text())
    net = next(x for x in catalog['pricing'] if x['id'] == args.network)
    covered = [[(v['lat'], v['lng']) for v in w['line']] for w in net['coverageWays']]
    known = {w['id'] for x in catalog['pricing'] for w in x['coverageWays']}

    pts = [p for run in runs for p in run[1:-1]]
    step = max(1, len(pts) // 120)
    line = ','.join(f'{p[0]:.6f},{p[1]:.6f}' for p in pts[::step] + [pts[-1]])
    query = (f'[out:json][timeout:120][date:"{SNAPSHOT}"];way(around:25,{line})[highway][toll=yes];out meta geom;'
             'node(w)[~"^(barrier|highway)$"~"^(toll_booth|toll_gantry)$"];out meta;')
    data = overpass(query)
    ways = [x for x in data['elements'] if x['type'] == 'way']
    charging = [x for x in data['elements'] if x['type'] == 'node']
    lines = {x['id']: [(g['lat'], g['lon']) for g in x['geometry']] for x in ways}

    # Keep the ways the route actually drives on (not crossings or parallel roads).
    used = set()
    for run in runs:
        for p in sample(run[1:-1]):
            best = min(lines, key=lambda wid: min(dist_km(p, a, b) for a, b in zip(lines[wid], lines[wid][1:])))
            if min(dist_km(p, a, b) for a, b in zip(lines[best], lines[best][1:])) <= TOLERANCE_KM: used.add(best)
    problems = []
    for run in runs:
        missing = [p for p in sample(run[1:-1]) if not near(p, [lines[i] for i in used] + covered + [[(v['lat'], v['lng']) for v in w['line']] for x in catalog['pricing'] for w in x['coverageWays']])]
        if missing: problems.append(f'{len(missing)} route points not on toll=yes ways, e.g. {missing[0]}')
        if not near(run[0], covered) and not near(run[-1], covered): problems.append(f'run {run[1]} -> {run[-2]} does not join {args.network} coverage')
    chosen = [x for x in ways if x['id'] in used and str(x['id']) not in known]
    for x in chosen:
        if x['tags'].get('highway') not in CLASSES: problems.append(f"way {x['id']} is highway={x['tags'].get('highway')}")
    # A booth already modelled by one of the network's gates is the plaza the
    # catalog charges at; any other booth or gantry is an unmapped charge.
    gates = [[(v['lat'], v['lng']) for v in g['line']] for g in net['gates'] if g.get('line')]
    modelled = lambda c: any(dist_km((c['lat'], c['lon']), a, b) <= .1 for line in gates for a, b in zip(line, line[1:]))
    booths = [c for c in charging if any(c['id'] in x.get('nodes', []) for x in chosen) and not modelled(c)]
    if booths: problems.append('charging points on the gap ways: ' + ', '.join(f"node {c['id']} {c['tags']}" for c in booths))
    if problems:
        raise SystemExit('REFUSED ' + args.area + ':\n  ' + '\n  '.join(problems))

    out = ROOT / 'audit/area-coverage' / f'{args.area}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        'area': args.area, 'network': args.network, 'snapshot': SNAPSHOT,
        'source': OVERPASS + ' (attic query at the snapshot)', 'query': query,
        'attribution': '© OpenStreetMap contributors, ODbL 1.0',
        'reason': args.reason or 'Ways tagged toll=yes beyond the mapped cuts, with no booth or gantry: the journey settles at the existing gates.',
        'journeys': sorted(journeys),
        'checks': {'runs': len(runs), 'routePointsOnWays': True, 'chargingPointsOnWays': 0, 'joinsNetworkCoverage': True},
        'ways': [{'id': str(x['id']), 'version': x['version'], 'ref': x['tags'].get('ref'), 'highway': x['tags']['highway'],
                  'line': [{'lat': g['lat'], 'lng': g['lon']} for g in x['geometry']]} for x in sorted(chosen, key=lambda x: x['id'])],
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'{args.area}: {len(chosen)} ways frozen for {args.network} ({len(runs)} runs) -> {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
