#!/usr/bin/env python3
"""AP-66 full journeys and N-630 alternatives from public street endpoints."""
import json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'pricing-candidates/ap66-avoidance';out.mkdir(exist_ok=True)
polygons=json.loads((ROOT/'audit/2026-09-16/networks/ap66/exclusion-polygons.json').read_text())
points=[{'lat':43.1164,'lon':-5.8088},{'lat':42.6000,'lon':-5.5790}]
for direction,pair in [('south',points),('north',points[::-1])]:
 for excluded in (False,True):
  name=direction+('-excluded' if excluded else '-baseline');target=out/(name+'.json')
  if target.exists():continue
  body={'locations':pair,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  if excluded:body['exclude_polygons']=polygons
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read()
  result=json.loads(raw);assert result.get('trip'),result
  target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'endpointScope':'Campomanes–León public streets'},indent=2)+'\n')
  print(name,result['trip']['summary'],flush=True);time.sleep(.6)
