#!/usr/bin/env python3
"""Enable reviewed physical exclusions for general-fare closed systems.

Ordinary systems use directed entry cuts. R-3 preserves its free corridor;
AP-8/AP-1 use dedicated road-boundary markers rather than all shared entries.
The subsequent provider acceptance must pass before readiness is changed.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FAMILIES=['ap36','ap41','ap7-cartagena-vera','r4','r5','supersur','ag57','ag55','ap8-gipuzkoa-east','r3']
for family in FAMILIES:
 path=ROOT/f'pricing-candidates/{family}.json';doc=json.loads(path.read_text())
 for n in doc['pricing']:
  p=n['pricing'];assert p['kind']=='od' and not n.get('sharedRoads')
  assert family=='r3' or all(f['tariff']['baseCents']>0 for f in p['fares']), 'Review free general journeys separately'
  # Published time-dependent free travel still has the same physical system.
  # Selecting this road for exclusion is an explicit user preference.
  n['avoidanceGateIds']=p['entries'][:]
  if family=='r3':
   # Preserve both directions of the general M-50–M-208 free corridor.
   free_gates={f[k] for f in p['fares'] if f['tariff']['baseCents']==0 for k in ('from','to')}
   n['avoidanceGateIds']=[g for g in p['entries']+p['exits'] if g not in free_gates]
   assert all(f['from'] in n['avoidanceGateIds'] or f['to'] in n['avoidanceGateIds'] for f in p['fares'] if f['tariff']['baseCents']>0)
 path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
 print(family,len(n['avoidanceGateIds']),'entry cuts')

# AP-8 Gipuzkoa / AP-1 have dedicated physical road-boundary markers inside
# their shared settlement. Do not exclude every financial entry: doing so
# would also cut Bizkaia when only Gipuzkoa or AP-1 was selected.
path=ROOT/'pricing-candidates/ap8-ap1-shared.json';doc=json.loads(path.read_text())
for n in doc['pricing']:
 for road in n.get('sharedRoads',[]):
  if road['tollId'] in ('es-ap8-gipuzkoa','es-ap1-gipuzkoa'):
   road['avoidanceGateIds']=[g['id'] for g in road['gates'] if g['id'].endswith('-entry') or '-mainline-' in g['id']]
   assert road['avoidanceGateIds']
path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
