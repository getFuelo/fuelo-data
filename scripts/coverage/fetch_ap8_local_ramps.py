#!/usr/bin/env python3
"""Retain both directional ramp traversals and every mapped source-lane probe."""
import json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for family in ['ap8-orio','ap8-zarautz-east']:
 catalog=json.loads((ROOT/f'pricing-candidates/{family}.json').read_text());net=catalog['pricing'][0];out=ROOT/f'pricing-candidates/{family}-routes';out.mkdir(exist_ok=True)
 for probe in json.loads((ROOT/f'audit/2026-09-16/networks/{family}/lane-probes.json').read_text()):
  name=str(probe['booth']);target=out/(name+'.json')
  if target.exists():continue
  body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in [probe['geometry'][0],probe['geometry'][-1]]],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw)
  (out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceBooth':probe['booth'],'expectedGeneralCents':next(iter(net['pricing']['fares'].values()))['baseCents']},indent=2)+'\n');print(family,name,d['trip']['summary']['length'],flush=True);time.sleep(.6)
