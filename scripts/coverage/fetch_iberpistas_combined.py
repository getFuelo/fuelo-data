#!/usr/bin/env python3
"""Published AP-6/AP-51 cross-road totals; retain requests and source tariffs."""
import json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
locations={}
for family in ['ap6','ap51']:
 locations[family]=json.loads((ROOT/f'audit/2026-09-16/networks/{family}/provenance.json').read_text())['probeLocations']
ref=json.loads((ROOT/'pricing-candidates/ap51-tariffs.json').read_text())
names={'Villalba':'VILLALBA','San Rafael':'SAN RAFAEL','Adanero':'ADANERO','Vicolozano':'VICOLOZANO','Ávila':'AVILA'}
out=ROOT/'pricing-candidates/iberpistas-combined-routes';out.mkdir(exist_ok=True)
for row in ref['joint_ap6_ods']:
 for reverse in [False,True]:
  a,b=[names[row[k]] for k in (['to','from'] if reverse else ['from','to'])]
  family=lambda n:'ap6' if n in ['VILLALBA','SAN RAFAEL','ADANERO'] else 'ap51'
  points=[locations[family(a)][a]['entry'],locations[family(b)][b]['exit']]
  name=a+'--'+b;target=out/(name+'.json')
  if target.exists():continue
  body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in points],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw)
  (out/(name+'-request.json')).write_text(json.dumps({'request':body,'source':ref['source'],'sourceTariff':row['tariff']},ensure_ascii=False,indent=2)+'\n');print(name,d['trip']['summary']['length'],flush=True);time.sleep(.6)
