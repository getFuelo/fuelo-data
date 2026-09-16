#!/usr/bin/env python3
"""Public Santiago/Silleda journeys, including selective exclusion in both directions."""
import json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'pricing-candidates/ap53-public';out.mkdir(exist_ok=True)
polygons=json.loads((ROOT/'audit/2026-09-16/networks/ap53/exclusion-polygons.json').read_text())
points=[{'lat':42.8805,'lon':-8.5457},{'lat':42.6978,'lon':-8.2454}]
for north in (False,True):
 for avoid in (False,True):
  name=('north' if north else 'south')+('-excluded' if avoid else '-general');path=out/(name+'.json')
  body={'locations':points[::-1] if north else points,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  if avoid:body['exclude_polygons']=polygons
  if not path.exists():
   raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;path.write_bytes(raw);time.sleep(.7)
  (out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':0 if avoid else 435,'source':'https://acega.es/tarifas/','publishedJourney':'Santiago–Silleda','scope':'Public city endpoints; app-generated exclusions.'},ensure_ascii=False,indent=2)+'\n')
  print(name,json.loads(path.read_text())['trip']['summary'],flush=True)
