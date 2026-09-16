#!/usr/bin/env python3
"""Pastoriza and exempt AC-15 movements, plus combined AG-55 whole journeys."""
import gzip,json,math,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'pricing-candidates/ag55-port-routes';out.mkdir(exist_ok=True)
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'));ways={w['id']:w for w in graph['ways']};nodes=graph['nodes']
def point(wid,index):
    w=ways[wid];lat,lon=nodes[str(w['nodes'][index])];a=nodes[str(w['nodes'][0])];b=nodes[str(w['nodes'][-1])]
    heading=round(math.degrees(math.atan2((b[1]-a[1])*math.cos(math.radians(lat)),b[0]-a[0]))%360)
    return {'lat':lat,'lon':lon,'heading':heading}
points={'Coruna':{'entry':point(26041616,0),'exit':point(795695672,-1)},
        'Arteixo':{'entry':point(795695684,0),'exit':point(795695668,-1)},
        'Porto':{'entry':point(349932303,0),'exit':point(349932304,-1)},
        'Carballo':{'entry':point(156543952,0),'exit':point(786151684,-1)}}
cases=[(a,b,0 if 'Porto' in (a,b) else 55) for a in ('Coruna','Arteixo','Porto') for b in ('Coruna','Arteixo','Porto') if a!=b]
cases.extend([('Coruna','Carballo',260),('Carballo','Coruna',260)])
for a,b,cents in cases:
    name=a+'--'+b;target=out/(name+'.json')
    if target.exists():continue
    body={'locations':[points[a]['entry'],points[b]['exit']],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
    raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();result=json.loads(raw);assert result.get('trip'),result
    target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':cents,'expectationSource':'BOE-A-2025-490 port exemption' if 'Porto' in (a,b) else 'Published independent Pastoriza and Arteixo–Carballo tariffs'},indent=2)+'\n')
    print(name,result['trip']['summary'],flush=True);time.sleep(.6)
