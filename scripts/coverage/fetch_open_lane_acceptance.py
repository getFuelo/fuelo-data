#!/usr/bin/env python3
"""Exercise every retained source-lane probe against the live router, once.

Expected amounts reuse the independently reviewed tariff references of the
existing plaza acceptance corpus; they are not computed by the app engine.
These are directed lane traversals, not exhaustive public-origin journeys.
"""
import argparse,gzip,json,math,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('app',type=Path);args=p.parse_args()
reference=json.loads((args.app/'src/lib/__tests__/fixtures/open-barrier-routes.json').read_text())
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'));points={p['id']:p for p in graph['points']}
out=ROOT/'pricing-candidates/open-lane-acceptance';out.mkdir(exist_ok=True)
def heading(a,b):return round(math.degrees(math.atan2((b['lng']-a['lng'])*math.cos(math.radians(a['lat'])),b['lat']-a['lat']))%360)
for group in reference:
 family=group['family'];expected={r['network']:r['expectedHighCents'] for r in group['routes']}
 probes=json.loads((ROOT/f'audit/2026-09-16/networks/{family}/lane-probes.json').read_text())
 for i,probe in enumerate(probes):
  name=f'{family}-{i:03d}';target=out/(name+'.json')
  if target.exists():continue
  pts=probe['geometry'];position=graph['nodes'].get(str(probe['booth']))
  assert position is not None, ('Missing source booth coordinates',probe['booth'])
  booth={'lat':position[0],'lng':position[1]}
  index=min(range(len(pts)),key=lambda i:(pts[i]['lat']-booth['lat'])**2+(pts[i]['lng']-booth['lng'])**2)
  assert 0<index<len(pts)-1,(name,index)
  locations=[{'lat':pts[0]['lat'],'lon':pts[0]['lng'],'heading':heading(pts[0],pts[1])},
    {'lat':pts[index]['lat'],'lon':pts[index]['lng'],'heading':heading(pts[index-1],pts[index+1]),'type':'through'},
    {'lat':pts[-1]['lat'],'lon':pts[-1]['lng'],'heading':heading(pts[-2],pts[-1])}]
  body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d
  target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'family':family,'network':probe['network'],'expectedCents':expected[probe['network']],'sourceProbe':{k:v for k,v in probe.items() if k!='geometry'},'tariffReference':'app:src/lib/__tests__/fixtures/open-barrier-routes.json','at':'2026-09-16T10:00:00Z'},ensure_ascii=False,indent=2)+'\n')
  print(name,d['trip']['summary']['length'],flush=True);time.sleep(.8)
