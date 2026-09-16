#!/usr/bin/env python3
"""Probe the legally free AP-53 Santiago/AG-59 movement on both carriageways."""
import gzip
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
with gzip.open(ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz', 'rt') as f:
    graph = json.load(f)
nodes = graph['nodes']

def select(ref, lat, lng, north):
    options = []
    for way in graph['ways']:
        if way['tags'].get('ref') != ref or way['tags'].get('highway') != 'motorway':
            continue
        first, last = [nodes[str(n)] for n in (way['nodes'][0], way['nodes'][-1])]
        if (last[0] > first[0]) != north:
            continue
        for i, node in enumerate(way['nodes'][1:-1], 1):
            p = nodes[str(node)]
            distance = math.hypot(p[0] - lat, (p[1] - lng) * .735)
            a, b = [nodes[str(n)] for n in (way['nodes'][i-1], way['nodes'][i+1])]
            heading = round(math.degrees(math.atan2((b[1]-a[1])*.735, b[0]-a[0])) % 360)
            options.append((distance, node, way['id'], way['version'], {'lat': p[0], 'lon': p[1], 'heading': heading}))
    chosen = min(options)
    assert chosen[0] < .001, chosen
    return chosen

out = ROOT / 'pricing-candidates/ap53-routes'
for north in (False, True):
    name = 'AG59-free-' + ('north' if north else 'south')
    target = out / (name + '.json')
    if target.exists():
        continue
    chosen = [select('AP-53', 42.845, -8.533, north), select('AG-59', 42.824, -8.531, north)]
    if north:
        chosen.reverse()
    body = {'locations': [c[4] for c in chosen], 'costing': 'auto',
            'costing_options': {'auto': {'use_tolls': 1}}, 'directions_options': {'units': 'kilometers'}}
    raw = urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json=' + urllib.parse.quote(json.dumps(body)), timeout=45).read()
    result = json.loads(raw)
    assert result.get('trip'), result
    target.write_bytes(raw)
    (out / (name + '-request.json')).write_text(json.dumps({'request': body, 'expectedCents': 0,
        'sourceNodes': [{'node': c[1], 'way': c[2], 'version': c[3]} for c in chosen],
        'legalSource': 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2008-16770'}, indent=2) + '\n')
    print(name, result['trip']['summary'], flush=True)
    time.sleep(.6)
