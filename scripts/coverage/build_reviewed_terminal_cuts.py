#!/usr/bin/env python3
"""Repair terminal cuts using reviewed source topology, preserving paid probes.

Santurtzi: all western ramps must enter after their merge.
Oiartzun: settle the AP-8 exit before it merges with public local traffic.
GI-20: retain its distinct AP-8 entry for avoidance and fail-closed pricing;
its general OD tariff is not inferred from the second-ring Donostia entry.
Run after build_closed_plazas.py, before build_general_avoidance.py.
"""
import gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
for family,zone,role,way_id,node_id in [('supersur','SANTURTZI','entry',307656593,984775225),('ap8-gipuzkoa-east','DONOSTIA-ESTE','entry',31237370,783791631),('ap8-gipuzkoa-east','OIARTZUN','exit',997126261,2814306535),('ap8-gipuzkoa-east','GI20','entry',31233054,13793505493)]:
 way=next(w for w in graph['ways'] if w['id']==way_id)
 node=node_id;i=way['nodes'].index(node)
 a,c,b=[graph['nodes'][str(n)] for n in [way['nodes'][j] for j in (max(0,i-1),i,min(len(way['nodes'])-1,i+1))]]
 cos=math.cos(math.radians(c[0]));dx=(b[1]-a[1])*cos;dy=b[0]-a[0];length=math.hypot(dx,dy)
 line=[{'lat':c[0]+v*dx/length/111195,'lng':c[1]-v*dy/length/111195/cos} for v in (-8,8)]
 def side(p):return (line[1]['lng']-line[0]['lng'])*(p[0]-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p[1]-line[0]['lng'])
 p=ROOT/f'pricing-candidates/{family}.json';d=json.loads(p.read_text())
 net=d['pricing'][0]
 if not any(g['id']==zone+'-'+role for g in net['gates']):
  net['gates'].append({'id':zone+'-'+role});net['pricing']['entries'].append(zone+'-'+role)
 g=next(g for g in net['gates'] if g['id']==zone+'-'+role);g.update(line=line,direction='positive' if side(b)>side(a) else 'negative')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 p=ROOT/f'audit/2026-09-16/networks/{family}/provenance.json';d=json.loads(p.read_text())
 if not any(g['zone']==zone and g['role']==role for g in d['gates']):d['gates'].append({'zone':zone,'role':role,'kind':'logical-terminal-cut','outsideNode':563708,'tariffStatus':'Unmapped general GI-20 entry fare; fail closed until sourced. Avoidance may use the physical entry.'})
 g=next(g for g in d['gates'] if g['zone']==zone and g['role']==role);g.update(way=way['id'],version=way['version'],node=node)
 if zone=='GI20':g['outsideNode']=563708
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(family,zone,role,'source cut updated')
