#!/usr/bin/env python3
"""Compare AP-53 paid/free routes using the exact app-generated exclusion rings."""
import json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'pricing-candidates/ap53-avoidance';out.mkdir(exist_ok=True)
polygons=json.loads((ROOT/'audit/2026-09-16/networks/ap53/exclusion-polygons.json').read_text())
points=[{'lat':42.7760298,'lon':-8.4247409},{'lat':42.6817419,'lon':-8.1788633}]
for direction,locations in [('south',points),('north',points[::-1])]:
 for exclude in [False,True]:
  name=direction+('-excluded' if exclude else '-baseline');target=out/(name+'.json')
  if target.exists():continue
  body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  if exclude:body['exclude_polygons']=polygons
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceEndpointNodes':[618991350,181316497]},indent=2)+'\n');print(name,d['trip']['summary'],flush=True);time.sleep(.5)
