#!/usr/bin/env python3
"""Copy the reproducible open-plaza lane and real-route corpus into an app checkout."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('app',type=Path);args=p.parse_args()
out=args.app/'src/lib/__tests__/fixtures';assert out.is_dir()
lanes=[];routes=[]
for family in ['autema','c32','ap15','ap7-estepona-guadiaro','ap7-malaga-estepona','ap7-alicante-cartagena','r2-open','ag55-pastoriza']:
 catalog=json.loads((ROOT/f'pricing-candidates/{family}.json').read_text())
 lanes.append({'family':family,'networks':[{k:v for k,v in n.items() if k!='coverageWays'} for n in catalog['pricing']],'probes':json.loads((ROOT/f'audit/2026-09-16/networks/{family}/lane-probes.json').read_text())})
 rows=[]
 for net in catalog['pricing']:
  route=json.loads((ROOT/f'pricing-candidates/{family}-routes'/f"{net['id']}-traversal.json").read_text())
  rows.append({'network':net['id'],'expectedCents':next(iter(net['pricing']['fares'].values()))['baseCents'],'expectedHighCents':max([next(iter(net['pricing']['fares'].values()))['baseCents']]+[band['cents'] for band in next(iter(net['pricing']['fares'].values()))['bands']]),'route':route})
 routes.append({'family':family,'catalog':catalog,'routes':rows})
for name,value in [('open-barrier-lanes',lanes),('open-barrier-routes',routes)]:
 (out/(name+'.json')).write_text(json.dumps(value,separators=(',',':'))+'\n')

# Vallvidrera has a weekday-peak interval until the operator's holiday calendar
# is established, so its expectations are deliberately separate from fixed plazas.
if (ROOT/'pricing-candidates/vallvidrera.json').exists():
 import shutil
 target=out/'vallvidrera';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/vallvidrera.json',target/'catalog.json')
 shutil.copy(ROOT/'audit/2026-09-16/networks/vallvidrera/lane-probes.json',target/'lanes.json')
 rows=[]
 for path in sorted((ROOT/'pricing-candidates/vallvidrera-routes').glob('*-request.json')):
  rows.append({'name':path.stem.removesuffix('-request'),'request':json.loads(path.read_text())['request'],'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')

# Closed-system corpus: preserve every request's independently selected tariff.
if (ROOT/'pricing-candidates/ap636.json').exists():
 import shutil
 target=out/'ap636';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/ap636.json',target/'catalog.json')
 rows=[]
 for path in sorted((ROOT/'pricing-candidates/ap636-routes').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')

if (ROOT/'pricing-candidates/ap53.json').exists():
 import shutil
 target=out/'ap53';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/ap53.json',target/'catalog.json');cases=[]
 for path in sorted((ROOT/'pricing-candidates/ap53-routes').glob('*-request.json')):
  req=json.loads(path.read_text());response=json.loads(path.with_name(path.name.replace('-request','')).read_text())
  cases.append({'name':path.stem.removesuffix('-request'),'expectedCents':req.get('expectedCents',req.get('expectedIfPaidRouteCents')),'response':response})
 (target/'cases.json').write_text(json.dumps(cases,separators=(',',':'),ensure_ascii=False)+'\n')
 if (ROOT/'pricing-candidates/ap53-avoidance').exists():
  avoidance=[]
  for path in sorted((ROOT/'pricing-candidates/ap53-avoidance').glob('*-request.json')):
   avoidance.append({'name':path.stem.removesuffix('-request'),'request':json.loads(path.read_text())['request'],'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
  (target/'avoidance.json').write_text(json.dumps(avoidance,separators=(',',':'))+'\n')
 if (ROOT/'pricing-candidates/ap53-terminals').exists():
  terminal_cases=[]
  for path in sorted((ROOT/'pricing-candidates/ap53-terminals').glob('*-request.json')):
   request=json.loads(path.read_text());terminal_cases.append({'name':path.stem.removesuffix('-request'),'expectedCents':request['expectedCents'],'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
  (target/'terminals.json').write_text(json.dumps(terminal_cases,separators=(',',':'),ensure_ascii=False)+'\n')

for family in ['ap41','ap71','ap36','ap7-cartagena-vera','ap66','r2','ag55','ag57','r3','r5','r4','ap9-frontera','ap9-centro','ap9-sur','ap9-ferrol','ap9-norte','ap51','ap6','ap61','ap68','ap1-closed','ap8-gipuzkoa-west','ap8-bizkaia','ap8-gipuzkoa-east','supersur']:
 if not (ROOT/f'pricing-candidates/{family}.json').exists():continue
 import shutil
 target=out/family;target.mkdir(exist_ok=True);catalog=json.loads((ROOT/f'pricing-candidates/{family}.json').read_text());shutil.copy(ROOT/f'pricing-candidates/{family}.json',target/'catalog.json');rows=[]
 for path in sorted((ROOT/f'pricing-candidates/{family}-routes').glob('*-request.json')):
  a,b=path.stem.removesuffix('-request').split('--');fare=next(f for f in catalog['pricing'][0]['pricing']['fares'] if f['from']==a+'-entry' and f['to']==b+'-exit');via=next((band['cents'] for band in fare['tariff']['bands'] if band.get('requires')==['payment:via-t']),fare['tariff']['baseCents']);req=json.loads(path.read_text());rows.append({'name':a+'--'+b,'expectedCents':req.get('expectedActualCents',req['expectedGeneralCents']),**({'observedJourneys':req['observedJourneys'],'expectedGates':req['expectedGates'],'requestedDirectCents':req['expectedGeneralCents']} if req.get('observedJourneys') else {}),'expectedViaTCents':via,'expectedNightCents':next((band['cents'] for band in fare['tariff']['bands'] if band.get('minutes') in ([0,360],[1380,420])),fare['tariff']['baseCents']),'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 if (ROOT/f'pricing-candidates/{family}-avoidance').exists():
  rows=[]
  for path in sorted((ROOT/f'pricing-candidates/{family}-avoidance').glob('*-request.json')):
   rows.append({'name':path.stem.removesuffix('-request'),'request':json.loads(path.read_text())['request'],'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
  (target/'avoidance.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')

 if family=='r2' and (ROOT/'pricing-candidates/r2-full-routes').exists():
  rows=[]
  for path in sorted((ROOT/'pricing-candidates/r2-full-routes').glob('*-request.json')):
   req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),'expectedCents':req['expectedGeneralCents'],'expectedViaTCents':req['expectedViaTCents'],'expectedOpenBarriers':req['expectedOpenBarriers'],'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
  (target/'full.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 if family=='ag55' and (ROOT/'pricing-candidates/ag55-port-routes').exists():
  rows=[]
  for path in sorted((ROOT/'pricing-candidates/ag55-port-routes').glob('*-request.json')):
   req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
  (target/'port.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')

if (ROOT/'pricing-candidates/ap9.json').exists():
 import shutil
 target=out/'ap9-combined';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/ap9.json',target/'catalog.json');rows=[]
 for path in sorted((ROOT/'pricing-candidates/ap9-combined-routes').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'),ensure_ascii=False)+'\n')

if (ROOT/'audit/2026-09-16/networks/ap61/free-n603/ORTIGOSA--OTERO.json').exists():
 import shutil
 shutil.copy(ROOT/'audit/2026-09-16/networks/ap61/free-n603/ORTIGOSA--OTERO.json',out/'ap61/free-n603.json')

if (ROOT/'pricing-candidates/iberpistas.json').exists():
 import shutil
 target=out/'iberpistas';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/iberpistas.json',target/'catalog.json');rows=[]
 for path in sorted((ROOT/'pricing-candidates/iberpistas-routes').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'),ensure_ascii=False)+'\n')

if (ROOT/'pricing-candidates/ap68-public-approaches').exists():
 rows=[]
 for path in sorted((ROOT/'pricing-candidates/ap68-public-approaches').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (out/'ap68/public-approaches.json').write_text(json.dumps(rows,separators=(',',':'),ensure_ascii=False)+'\n')

# Joint AP-8/AP-1 prices include all participating roads exactly once.
if (ROOT/'pricing-candidates/ap8-ap1-shared.json').exists():
 import shutil
 target=out/'ap8-ap1-shared';target.mkdir(exist_ok=True)
 shutil.copy(ROOT/'pricing-candidates/ap8-ap1-shared.json',target/'catalog.json');rows=[]
 for path in sorted((ROOT/'pricing-candidates/ap8-ap1-shared-routes').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (target/'cases.json').write_text(json.dumps(rows,separators=(',',':'),ensure_ascii=False)+'\n')
 free=ROOT/'audit/2026-09-16/networks/ap8-ap1-shared/free-local/ERMUA--EIBAR.json'
 if free.exists():shutil.copy(free,target/'free-local.json')

local=[]
for family in ['ap8-orio','ap8-zarautz-east']:
 if not (ROOT/f'pricing-candidates/{family}.json').exists():continue
 rows=[]
 for path in sorted((ROOT/f'pricing-candidates/{family}-routes').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 local.append({'family':family,'catalog':json.loads((ROOT/f'pricing-candidates/{family}.json').read_text()),'lanes':json.loads((ROOT/f'audit/2026-09-16/networks/{family}/lane-probes.json').read_text()),'routes':rows})
if local:(out/'ap8-local-ramps.json').write_text(json.dumps(local,separators=(',',':'))+'\n')

if (ROOT/'pricing-candidates/supersur.json').exists():
 rows=[]
 for path in sorted((ROOT/'audit/2026-09-16/networks/supersur/unconstrained-alternatives').glob('*-request.json')):
  req=json.loads(path.read_text());rows.append({'name':path.stem.removesuffix('-request'),**req,'response':json.loads(path.with_name(path.name.replace('-request','')).read_text())})
 (out/'supersur/alternatives.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
