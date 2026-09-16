#!/usr/bin/env python3
"""Nearby N-525 regression, source endpoints are actual OSM road nodes."""
import json,urllib.request,urllib.parse,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'pricing-candidates/ap53-routes'
points=[{'lat':42.7760298,'lon':-8.4247409},{'lat':42.7391276,'lon':-8.3277444}]
for direction,locations in [('south',points),('north',points[::-1])]:
 name='N525-'+direction;target=out/(name+'.json')
 if target.exists():continue
 body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':0}},'directions_options':{'units':'kilometers'}}
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=30).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':0,'sourceNodes':[618991350,244682940],'purpose':'Free N-525 alternative near AP-53, not a price inferred from empty tariff cells.'},indent=2)+'\n');print(name,d['trip']['summary'],flush=True);time.sleep(.5)
