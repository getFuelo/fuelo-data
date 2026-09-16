#!/usr/bin/env python3
"""Retain public Cadí journeys and the app's exact exclusion behavior.

One request at a time, resumable; source-backed expectations are independent of
responses. No tariff is inferred from a provider toll flag.
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
out = ROOT / 'pricing-candidates/general-acceptance'
out.mkdir(exist_ok=True)
polygons = json.loads((ROOT / 'audit/2026-09-16/networks/cadi/exclusion-polygons.json').read_text())
# Public urban endpoints in Puigcerdà and Berga. Unlike a point at a booth,
# each allows a genuine alternative via the Collada de Toses.
points = [{'lat':42.4312,'lon':1.9284}, {'lat':42.1044,'lon':1.8461}]
for direction, pair in [('cadi-south',points), ('cadi-north',points[::-1])]:
    for avoided in [False, True]:
        name = direction + ('-avoided' if avoided else '-general')
        path = out / (name + '.json')
        if path.exists(): continue
        body = {'locations':pair,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
        if avoided: body['exclude_polygons'] = polygons
        request = {'request':body,'expectedCents':0 if avoided else 1456,
                   'source':'https://tunels.cat/es/tunel-del-cadi/',
                   'scope':'General light car, public endpoints Puigcerdà–Berga; explicit Cadí exclusion in avoided cases.'}
        data = urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read()
        response = json.loads(data)
        assert response.get('trip'), response
        path.write_bytes(data)
        (out / (name + '-request.json')).write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n')
        print(name,response['trip']['summary'],flush=True)
        time.sleep(.7)
