#!/usr/bin/env python3
"""Retain published shared-system journeys; reuse identical probes."""
import argparse,json,shutil,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
parser=argparse.ArgumentParser();parser.add_argument('--family',choices=['iberpistas','iberpistas-ap61'],default='iberpistas');family=parser.parse_args().family
cat=read(ROOT/f'pricing-candidates/{family}.json');provenance=read(ROOT/f'audit/2026-09-16/networks/{family}/provenance.json');loc=provenance['probeLocations'];out=ROOT/f'pricing-candidates/{family}-routes';out.mkdir(exist_ok=True)
for fare in cat['pricing'][0]['pricing']['fares']:
 a,b=fare['from'].removesuffix('-entry'),fare['to'].removesuffix('-exit')
 if '-reversible' in a+b or '-sur' in a+b:continue
 name=a+'--'+b;target=out/(name+'.json')
 if target.exists():continue
 journey=provenance.get('probeJourneys',{}).get(name)
 entry=a+'-sur' if a=='HONTORIA' and b in ['VILLALBA','SAN RAFAEL'] else a
 exit=b+'-sur' if b=='HONTORIA' and a in ['VILLALBA','SAN RAFAEL'] else b
 points=[journey['entry'],journey['exit']] if journey else [loc[entry]['entry'],loc[exit]['exit']]
 body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in points],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 if journey and journey.get('via'):body['locations'][1:1]=[{'lat':p['lat'],'lon':p['lng'],'type':'through'} for p in journey['via']]
 expected_gates=journey.get('expectedGates',[entry+'-entry',exit+'-exit']) if journey else [entry+'-entry',exit+'-exit']
 reused=None
 for source_family in ('ap6','ap51','ap61','iberpistas-combined','iberpistas'):
  req=ROOT/f'pricing-candidates/{source_family}-routes/{name}-request.json';response=req.with_name(name+'.json')
  if req.exists() and read(req)['request']==body and response.exists():
   reused=str(response.relative_to(ROOT));shutil.copy(response,target);break
 if not reused:
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);time.sleep(.6)
 (out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceTariff':fare['tariff'],'expectedRoadIds':fare['roadIds'],'expectedGates':expected_gates,'source':cat['pricing'][0]['evidence']['tariffSources'],'reusedFrom':reused},ensure_ascii=False,indent=2)+'\n');print(name,'reused' if reused else 'fetched',flush=True)
