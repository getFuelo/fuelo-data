#!/usr/bin/env python3
"""Sequential shared-network probes, reusing byte-identical native requests."""
import argparse,json,shutil,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
p=argparse.ArgumentParser();p.add_argument('--limit',type=int);args=p.parse_args();fetched=0
cat=read(ROOT/'pricing-candidates/ap8-ap1-shared.json');provenance=read(ROOT/'audit/2026-09-16/networks/ap8-ap1-shared/provenance.json');out=ROOT/'pricing-candidates/ap8-ap1-shared-routes';out.mkdir(exist_ok=True)
fares={(f['from'],f['to']):f for f in cat['pricing'][0]['pricing']['fares']}
for name,journey in provenance['probeJourneys'].items():
 target=out/(name+'.json')
 if target.exists():continue
 if args.limit is not None and fetched>=args.limit:break
 a,b=name.split('--');fare=fares[(a+'-entry',b+'-exit')]
 body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in (journey['entry'],journey['exit'])],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 if journey.get('via'):
  body['locations'][1:1]=[{'lat':p['lat'],'lon':p['lng'],'type':'through'} for p in journey['via']]
 reused=None
 for family in ['ap8-bizkaia','ap8-gipuzkoa-west','ap1-closed']:
  req=ROOT/f'pricing-candidates/{family}-routes/{name}-request.json';response=req.with_name(name+'.json')
  if req.exists() and read(req)['request']==body and response.exists():
   reused=str(response.relative_to(ROOT));shutil.copy(response,target);break
 if not reused:
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);fetched+=1;time.sleep(.6)
 (out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedGeneralCents':fare['tariff']['baseCents'],'expectedRoadIds':fare['roadIds'],'source':cat['pricing'][0]['evidence']['tariffSources'],'reusedFrom':reused},ensure_ascii=False,indent=2)+'\n');print(name,'reused' if reused else 'fetched',flush=True)
