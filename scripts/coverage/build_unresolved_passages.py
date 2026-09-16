#!/usr/bin/env python3
"""Retain the historical uncertainty fixture for generic fail-closed regression tests."""
import gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
way=next(w for w in graph['ways'] if w['id']==265459454);node=12766694619;i=way['nodes'].index(node)
p,c,q=[dict(zip(('lat','lng'),graph['nodes'][str(way['nodes'][j])])) for j in (i-1,i,i+1)]
cos=math.cos(math.radians(c['lat']));dx=(q['lng']-p['lng'])*cos;dy=q['lat']-p['lat'];norm=math.hypot(dx,dy);px,py=-dy/norm,dx/norm
line=[{'lat':c['lat']+v*py/111195,'lng':c['lng']+v*px/111195/cos} for v in (-8,8)]
passage={'id':'es-c32-vallcarca-unconfirmed-bypass','tollId':'es-c32-castelldefels-vendrell','line':line,'source':'https://www.openstreetmap.org/way/265459454/history','checked':'2026-09-16'}
output={'passages':[passage],'evidence':{'source':'../../spain-graph/provenance.json','way':way['id'],'version':way['version'],'node':node,'halfWidthMeters':8,'probeGeometry':[p,c,q],'review':'valhalla-mismatch.json','status':'historical regression fixture; resolved as paid Via 1 in valhalla-mismatch.json; not emitted in the current national candidate'}}
target=ROOT/'audit/2026-09-16/networks/c32/unresolved-passages.json';target.write_text(json.dumps(output,indent=2)+'\n')
print('Historical uncertainty fixture only; country assembly checks the resolved review')
