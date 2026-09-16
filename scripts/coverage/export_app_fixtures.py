#!/usr/bin/env python3
"""Copy the reproducible open-plaza lane and real-route corpus into an app checkout."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('app',type=Path);args=p.parse_args()
out=args.app/'src/lib/__tests__/fixtures';assert out.is_dir()
lanes=[];routes=[]
for family in ['autema','c32','ap15']:
 catalog=json.loads((ROOT/f'pricing-candidates/{family}.json').read_text())
 lanes.append({'family':family,'networks':[{k:v for k,v in n.items() if k!='coverageWays'} for n in catalog['pricing']],'probes':json.loads((ROOT/f'audit/2026-09-16/networks/{family}/lane-probes.json').read_text())})
 rows=[]
 for net in catalog['pricing']:
  route=json.loads((ROOT/f'pricing-candidates/{family}-routes'/f"{net['id']}-traversal.json").read_text())
  rows.append({'network':net['id'],'expectedCents':next(iter(net['pricing']['fares'].values()))['baseCents'],'route':route})
 routes.append({'family':family,'catalog':catalog,'routes':rows})
for name,value in [('open-barrier-lanes',lanes),('open-barrier-routes',routes)]:
 (out/(name+'.json')).write_text(json.dumps(value,separators=(',',':'))+'\n')

# Closed-system corpus: preserve every request's independently selected tariff.
if (ROOT/'pricing-candidates/ap53.json').exists():
 import shutil
 target=out/'ap53';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/ap53.json',target/'catalog.json');cases=[]
 for path in sorted((ROOT/'pricing-candidates/ap53-routes').glob('*-request.json')):
  req=json.loads(path.read_text());response=json.loads(path.with_name(path.name.replace('-request','')).read_text())
  cases.append({'name':path.stem.removesuffix('-request'),'expectedCents':req.get('expectedCents',req.get('expectedIfPaidRouteCents')),'response':response})
 (target/'cases.json').write_text(json.dumps(cases,separators=(',',':'),ensure_ascii=False)+'\n')
