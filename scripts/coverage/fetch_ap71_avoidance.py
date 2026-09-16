#!/usr/bin/env python3
"""Real AP-71/N-120 alternatives using app-generated exclusion geometry."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'pricing-candidates/ap71-avoidance'
out.mkdir(exist_ok=True)
polygons = json.loads((ROOT / 'audit/2026-09-16/networks/ap71/exclusion-polygons.json').read_text())
# N-120 source nodes outside the paid network, near León and Astorga.
points = [{'lat': 42.5776288, 'lon': -5.6480244}, {'lat': 42.4576065, 'lon': -6.0531541}]
for direction, locations in [('west', points), ('east', points[::-1])]:
    for exclude in (False, True):
        name = direction + ('-excluded' if exclude else '-baseline')
        target = out / (name + '.json')
        if target.exists():
            continue
        body = {'locations': locations, 'costing': 'auto',
                'costing_options': {'auto': {'use_tolls': 1}},
                'directions_options': {'units': 'kilometers'}}
        if exclude:
            body['exclude_polygons'] = polygons
        raw = urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json=' + urllib.parse.quote(json.dumps(body)), timeout=45).read()
        result = json.loads(raw)
        assert result.get('trip'), result
        target.write_bytes(raw)
        (out / (name + '-request.json')).write_text(json.dumps({'request': body, 'sourceEndpointNodes': [2316046627, 6790546612]}, indent=2) + '\n')
        print(name, result['trip']['summary'], flush=True)
        time.sleep(.6)
