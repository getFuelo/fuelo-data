#!/usr/bin/env python3
"""Published Ferrol-branch to Coruña totals, crossing two pricing systems."""
import json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert (ROOT/'pricing-candidates/ap9.json').is_file(), 'Run build_closed_plazas.py first'
a=json.loads((ROOT/'audit/2026-09-16/networks/ap9-ferrol/provenance.json').read_text())['probeLocations']
b=json.loads((ROOT/'audit/2026-09-16/networks/ap9-norte/provenance.json').read_text())['probeLocations']
refs=json.loads((ROOT/'pricing-candidates/ap9-tariffs.json').read_text())
out=ROOT/'pricing-candidates/ap9-combined-routes';out.mkdir(exist_ok=True)
for row in refs['ods']:
 if row['from'] not in ['FENE','CABANAS','MIÑO'] or row['to']!='A CORUÑA':continue
 for reverse in [False,True]:
  origin,destination=('CORUNA',row['from']) if reverse else (row['from'],'CORUNA')
  points=[b['CORUNA']['entry'],a[row['from']]['exit']] if reverse else [a[row['from']]['entry'],b['CORUNA']['exit']]
  name=origin+'--'+destination;target=out/(name+'.json')
  if target.exists():continue
  body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in points],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw)
  (out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedGeneralCents':row['tariff']['baseCents'],'sourceRow':row['sourceRow']},ensure_ascii=False,indent=2)+'\n');print(name,d['trip']['summary']['length'],flush=True);time.sleep(.6)
