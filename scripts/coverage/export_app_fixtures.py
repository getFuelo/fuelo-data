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
