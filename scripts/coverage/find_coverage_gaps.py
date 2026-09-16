#!/usr/bin/env python3
"""Locate uncovered toll-maneuver vertices without changing matching tolerance."""
import argparse
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('catalog', type=Path)
parser.add_argument('response', type=Path)
args = parser.parse_args()

def decode(encoded):
    i, lat, lng = 0, 0, 0
    points = []
    while i < len(encoded):
        values = []
        for _ in range(2):
            value, shift = 0, 0
            while True:
                byte = ord(encoded[i]) - 63
                i += 1
                value |= (byte & 31) << shift
                shift += 5
                if byte < 32:
                    break
            values.append(~(value >> 1) if value & 1 else value >> 1)
        lat += values[0]
        lng += values[1]
        points.append((lat / 1e6, lng / 1e6))
    return points

def distance(p, a, b):
    cos = math.cos(math.radians(p[0]))
    ax, ay = (a[1]-p[1])*cos, a[0]-p[0]
    dx, dy = (b[1]-a[1])*cos, b[0]-a[0]
    t = max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx or dy else 0
    return math.hypot(ax+t*dx, ay+t*dy)*111195

catalog = json.loads(args.catalog.read_text())
edges = []
for net in catalog['pricing']:
    for way in net['coverageWays']:
        points = [(p['lat'], p['lng']) for p in way['line']]
        edges.extend(zip(points, points[1:]))
trip = json.loads(args.response.read_text())['trip']
missed = []
for leg in trip['legs']:
    points = decode(leg['shape'])
    indices = set(i for m in leg['maneuvers'] if m.get('toll') for i in range(m['begin_shape_index'], m['end_shape_index']+1))
    for i in sorted(indices):
        if min(distance(points[i], a, b) for a, b in edges) > 12:
            missed.append(points[i])
print(len(missed), 'uncovered vertices (segment interiors require the app check as well)')
if not missed:
    raise SystemExit(0)
with gzip.open(ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz', 'rt') as f:
    graph = json.load(f)
results = {}
for point in missed:
    matches = []
    for way in graph['ways']:
        pts = [graph['nodes'][str(n)] for n in way['nodes']]
        if not (min(p[0] for p in pts)-.0003 <= point[0] <= max(p[0] for p in pts)+.0003 and min(p[1] for p in pts)-.0004 <= point[1] <= max(p[1] for p in pts)+.0004):
            continue
        nearest = min(distance(point, a, b) for a, b in zip(pts, pts[1:]))
        if nearest < 12:
            matches.append((round(nearest, 2), way['id'], way['tags']))
    matches.sort(key=lambda m: m[0])
    key = matches[0][1] if matches else 'unmapped'
    if key not in results:
        results[key] = {'point': point, 'nearest': matches[:2]}
print(json.dumps(results, ensure_ascii=False, indent=2))
