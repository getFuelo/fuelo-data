#!/usr/bin/env python3
"""Fetch all 20 directed AP-53 zone pairs, without assuming the router uses tolls."""
import gzip,json,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
with gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt') as f:d=json.load(f)
ways={w['id']:w for w in d['ways']};nodes=d['nodes']
def p(n):a=nodes[str(n)];return {'lat':a[0],'lon':a[1]}
net=json.loads((ROOT/'pricing-candidates/ap53.json').read_text())['pricing'][0]
evidence=json.loads((ROOT/'audit/2026-09-16/networks/ap53/provenance.json').read_text())
southentry=next(g for g in evidence['gates'] if g['gate']=='Lalín-entry');southway=ways[southentry['way']]
locations={
'Santiago':{'entry':p(ways[119472403]['nodes'][0]),'exit':p(ways[98039345]['nodes'][-1])},
'Ribadulla':{'entry':p(ways[679120821]['nodes'][0]),'exit':p(ways[98020218]['nodes'][-1])},
'Bandeira':{'entry':p(ways[93387468]['nodes'][0]),'exit':p(ways[98039414]['nodes'][-1])},
'Silleda':{'entry':p(ways[98171705]['nodes'][0]),'exit':p(ways[98171698]['nodes'][-1])},
'Lalín':{'entry':p(southway['nodes'][0]),'exit':p(ways[98176729]['nodes'][-1])}}
out=ROOT/'pricing-candidates/ap53-routes';out.mkdir(exist_ok=True)
for row in net['pricing']['fares']:
 if 'south-entry' in row['from']:continue
 a=row['from'].removesuffix('-entry');b=row['to'].removesuffix('-exit');name=a+'--'+b;target=out/(name+'.json')
 if target.exists():continue
 body={'locations':[locations[a]['entry'],locations[b]['exit']],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=30).read();response=json.loads(raw);assert response.get('trip'),response;target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedIfPaidRouteCents':row['tariff']['baseCents']},ensure_ascii=False,indent=2)+'\n');print(name,response['trip']['summary']['length'],response['trip']['summary']['has_toll'],flush=True);time.sleep(.5)
