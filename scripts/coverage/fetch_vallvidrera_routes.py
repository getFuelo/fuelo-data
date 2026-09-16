#!/usr/bin/env python3
"""Retain bidirectional plaza and whole-trip/avoidance evidence, sequentially."""
import json, time, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
out = ROOT/'pricing-candidates/vallvidrera-routes'
out.mkdir(exist_ok=True)
audit = ROOT/'audit/2026-09-16/networks/vallvidrera'
probes = json.loads((audit/'lane-probes.json').read_text())
polygons = json.loads((audit/'exclusion-polygons.json').read_text())
cases = []
seen = set()
for probe in probes:
    a, b = probe['geometry'][0], probe['geometry'][-1]
    key = (a['lat'], a['lng'], b['lat'], b['lng'])
    if key in seen: continue
    seen.add(key)
    cases.append(('plaza-'+str(probe['booth']), [a,b], False,
                  {'sourceProbe':{'booth':probe['booth'],'way':probe['way']}}))
# Public street endpoints in Sarrià and Sant Cugat. Unlike points inside the
# tunnel approach, these allow the free BV-1462 alternative in both directions.
points = [{'lat':41.40065,'lng':2.12206}, {'lat':41.47362,'lng':2.08249}]
for name, pair in [('north', points), ('south', points[::-1])]:
    for excluded in [False, True]:
        cases.append((name+('-excluded' if excluded else '-baseline'),pair,excluded,
                      {'endpointScope':'Sarrià–Sant Cugat public streets'}))
for name, points, excluded, evidence in cases:
    target = out/(name+'.json')
    if target.exists(): continue
    body = {'locations':[{'lat':p['lat'],'lon':p['lng']} for p in points],
            'costing':'auto','costing_options':{'auto':{'use_tolls':1}},
            'directions_options':{'units':'kilometers'}}
    if excluded: body['exclude_polygons'] = polygons
    raw = urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read()
    response = json.loads(raw)
    assert response.get('trip'),response
    target.write_bytes(raw)
    (out/(name+'-request.json')).write_text(json.dumps({'request':body,**evidence},indent=2)+'\n')
    print(name,response['trip']['summary'],flush=True)
    time.sleep(.6)
