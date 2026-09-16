#!/usr/bin/env python3
"""Assemble all Spanish systems for integration audit, never for publication.

Native regional fixtures remain useful in isolation, but release also requires
this combined catalog to pass: overlapping coverage and shared settlements can
otherwise hide failures. Readiness is deliberately not inferred from assembly.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FAMILIES=['iberpistas','ap61','ap9','ap68','ap8-ap1-shared','ap8-gipuzkoa-east','ap8-orio','ap8-zarautz-east','supersur','ap636','ap15','ap36','ap41','ap46','ap53','ap66','ap71','ap7-alicante-cartagena','ap7-cartagena-vera','ap7-estepona-guadiaro','ap7-malaga-estepona','ag55','ag55-pastoriza','ag57','artxanda','autema','c32','cadi','m12','r2','r2-open','r3','r4','r5','vallvidrera']
PARENTS={'ap15':'es-ap15','ap636':'es-ap636','ag55-pastoriza':'es-ag55','c32':'es-c32-castelldefels-vendrell','m12':'es-m12','r2-open':'es-r2','ap8-orio':'es-ap8-gipuzkoa','ap8-zarautz-east':'es-ap8-gipuzkoa'}
for f in ['ap7-alicante-cartagena','ap7-estepona-guadiaro','ap7-malaga-estepona']:PARENTS[f]='es-'+f
legacy=json.loads((ROOT/'tolls-es.json').read_text());tolls={t['id']:t for t in legacy['tolls']};pricing=[];sources=[]
for family in FAMILIES:
 p=ROOT/f'pricing-candidates/{family}.json';d=json.loads(p.read_text());sources.append(str(p.relative_to(ROOT)))
 for n in d['pricing']:
  if family in PARENTS:n['tollId']=PARENTS[family]
  assert n['tollId'] in tolls,(family,n['tollId'])
  pricing.append(n)
assert len({n['id'] for n in pricing})==len(pricing)
doc={'schema':4,'generated':'2026-09-16','currency':'EUR','complete':False,'tolls':list(tolls.values()),'pricing':pricing,'notes_global':'Disabled Spanish integration candidate. Assembly does not certify source inventory, tariffs, access coverage or avoidance. © OpenStreetMap contributors.'}
(ROOT/'pricing-candidates/spain-integration.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
(ROOT/'audit/2026-09-16/spain-integration-sources.json').write_text(json.dumps({'complete':False,'sources':sources,'networks':len(pricing),'roads':len(tolls),'roadNormalization':PARENTS},indent=2)+'\n')
print(len(pricing),'settlement networks;',len(tolls),'catalog roads; release disabled')
