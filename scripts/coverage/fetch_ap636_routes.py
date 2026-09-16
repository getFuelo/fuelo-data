#!/usr/bin/env python3
"""Retained AP-636 routes; expected amounts are selected from source journeys."""
import gzip,json,math,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'pricing-candidates/ap636-routes';out.mkdir(exist_ok=True)
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
ways={w['id']:w for w in graph['ways']};nodes=graph['nodes']
def at(wid,index):
    ids=ways[wid]['nodes'];lat,lon=nodes[str(ids[index])]
    return {'lat':lat,'lon':lon}
def directed(wid,index):
    p=at(wid,index);a,b=at(wid,0),at(wid,-1)
    p['heading']=round(math.degrees(math.atan2((b['lon']-a['lon'])*math.cos(math.radians(p['lat'])),b['lat']-a['lat']))%360)
    return p
points={'Legazpi':{'entry':directed(165813688,0),'exit':directed(165813689,-1)},
        'Antzuola':{'entry':directed(165816113,0),'exit':directed(429921664,-1)},
        'Bergara':{'entry':directed(318438825,0),'exit':directed(165814593,-1)}}
cases=[]
for name,lanes,cents in [('Beasain',[27694225,27694624],42),('Ezkio',[158481317,421322505],82)]:
    for wid in lanes:cases.append((name+'-'+str(wid),[directed(wid,0),directed(wid,-1)],cents,cents,False))
for a,b in [('Legazpi','Bergara'),('Bergara','Legazpi'),('Legazpi','Antzuola'),('Antzuola','Legazpi')]:
    cases.append((a+'--'+b,[points[a]['entry'],points[b]['exit']],155,52 if 'Antzuola' in (a,b) else 155,False))
for name,pair in [('full-west',[directed(27694225,0),points['Bergara']['exit']]),('full-east',[points['Bergara']['entry'],directed(27694624,-1)])]:
    cases.append((name,pair,279,279,False))
    # Exclusion probes use public street endpoints, outside every excluded cut.
for name,pair in [('public-west',[{'lat':43.046422,'lon':-2.215759},{'lat':43.1149,'lon':-2.4145}]),('public-east',[{'lat':43.1149,'lon':-2.4145},{'lat':43.046422,'lon':-2.215759}])]:
    cases.append((name+'-excluded',pair,0,0,True))
polygons=json.loads((ROOT/'audit/2026-09-16/networks/ap636/exclusion-polygons.json').read_text())
for name,pair,cents,via,excluded in cases:
    target=out/(name+'.json')
    if target.exists():continue
    body={'locations':pair,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
    if excluded:body['exclude_polygons']=polygons
    raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read()
    result=json.loads(raw);assert result.get('trip'),result
    target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':cents,'expectedViaTCents':via},indent=2)+'\n')
    print(name,result['trip']['summary'],flush=True);time.sleep(.6)
