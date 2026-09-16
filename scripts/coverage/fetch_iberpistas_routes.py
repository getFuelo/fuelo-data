#!/usr/bin/env python3
"""Retain all thirty published shared-system journeys; reuse identical probes."""
import json,shutil,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
cat=read(ROOT/'pricing-candidates/iberpistas.json');loc=read(ROOT/'audit/2026-09-16/networks/iberpistas/provenance.json')['probeLocations'];out=ROOT/'pricing-candidates/iberpistas-routes';out.mkdir(exist_ok=True)
for fare in cat['pricing'][0]['pricing']['fares']:
 a,b=fare['from'].removesuffix('-entry'),fare['to'].removesuffix('-exit')
 if '-reversible' in a+b:continue
 name=a+'--'+b;target=out/(name+'.json')
 if target.exists():continue
 body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in (loc[a]['entry'],loc[b]['exit'])],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 reused=None
 for family in ('ap6','ap51','iberpistas-combined'):
  req=ROOT/f'pricing-candidates/{family}-routes/{name}-request.json';response=req.with_name(name+'.json')
  if req.exists() and read(req)['request']==body and response.exists():
   reused=str(response.relative_to(ROOT));shutil.copy(response,target);break
 if not reused:
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);time.sleep(.6)
 (out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceTariff':fare['tariff'],'expectedRoadIds':fare['roadIds'],'source':cat['pricing'][0]['evidence']['tariffSources'],'reusedFrom':reused},ensure_ascii=False,indent=2)+'\n');print(name,'reused' if reused else 'fetched',flush=True)
