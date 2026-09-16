#!/usr/bin/env python3
"""Build a disabled AP-41 closed-system candidate from all eight published accesses."""
import collections,gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
with gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt') as f:data=json.load(f)
ways={w['id']:w for w in data['ways']};nodes=data['nodes'];at=collections.defaultdict(set)
for w in ways.values():
 for n in w['nodes']:at[n].add(w['id'])
selected={w['id'] for w in ways.values() if w['tags'].get('ref')=='AP-41'}
for _ in range(16):
 added=set()
 for wid in selected:
  for n in ways[wid]['nodes']:
   for other in at[n]-selected:
    t=ways[other]['tags']
    if t.get('toll')=='yes' and t.get('ref') in [None,'AP-41'] and t.get('highway') in ['motorway','motorway_link','service']:added.add(other)
 selected.update(added)
 if not added:break

def point(n):a=nodes[str(n)];return {'lat':a[0],'lng':a[1]}
def section(center,a,b,half):
 cos=math.cos(math.radians(center['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];norm=math.hypot(dx,dy);px=-dy/norm;py=dx/norm
 return [{'lat':center['lat']+v*py/111195,'lng':center['lng']+v*px/111195/cos} for v in [-half,half]]
def sense(line,a,b):
 cross=lambda p:(line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
 return 'positive' if cross(b)>cross(a) else 'negative'
gates=[];evidence=[];locations={}
def add_terminal(zone,exitway,booth,enter_north):
 w=ways[exitway];i=w['nodes'].index(booth);a=point(w['nodes'][i-1]);b=point(w['nodes'][i+1]);center=point(booth);line=section(center,a,b,14)
 gates.append({'id':zone+'-exit','line':line,'direction':sense(line,a,b)});evidence.append({'gate':zone+'-exit','way':exitway,'version':w['version'],'node':booth,'kind':'collection-plaza'})
 options=[]
 for wid in selected:
  other=ways[wid]
  if other['tags'].get('highway')!='motorway' or other['tags'].get('ref')!='AP-41':continue
  if (point(other['nodes'][-1])['lat']>point(other['nodes'][0])['lat'])!=enter_north:continue
  for j,n in enumerate(other['nodes'][1:-1],1):
   p=point(n);options.append((math.hypot(p['lat']-center['lat'],(p['lng']-center['lng'])*.77),wid,j,n))
 dist,wid,j,n=min(options);assert dist<.001,(zone,dist);other=ways[wid];a=point(other['nodes'][j-1]);b=point(other['nodes'][j+1]);line=section(point(n),a,b,8);gates.append({'id':zone+'-entry','line':line,'direction':sense(line,a,b)});evidence.append({'gate':zone+'-entry','way':wid,'version':other['version'],'node':n,'kind':'logical-entry-carriageway'})
 # Retain provider probe coordinates outside the logical cut, on the proper
 # source carriageway; they intentionally isolate AP-41 from R-5 charges.
 locations[zone]={'entry':point(other['nodes'][0]),'exit':point(w['nodes'][-1])}
add_terminal('R5',95979739,1062072034,False)
add_terminal('Toledo',884091617,418650668,True)
# Each definition lists an entry direction and the paired collection booths.
# Bidirectional shared approaches use opposite events across the same cut.
specs=[
 ('Serranillos',278709678,1106445678,[1106445678,358358459],True,45549677),
 ('Carranque',903010659,726203567,[726203567],True,946522412),
 ('Illescas',84633592,1132332140,[1132332140,3371150295],True,97824261),
 ('Numancia',98324420,1137596386,[1137596386,3371149547],True,330160149),
 ('Villaluenga',85475869,991023544,[991023544],True,946431304),
 ('Villaseca',946404541,999320160,[999320160,8760698990],True,946404542),
]
for zone,wid,booth,booths,forward,exitway in specs:
 w=ways[wid];i=w['nodes'].index(booth);a=point(w['nodes'][max(0,i-1)]);b=point(w['nodes'][min(len(w['nodes'])-1,i+1)])
 center={k:sum(point(n)[k] for n in booths)/len(booths) for k in ['lat','lng']};spread=max(math.hypot((point(n)['lat']-center['lat']),(point(n)['lng']-center['lng'])*.77)*111195 for n in booths);line=section(center,a,b,spread+6);di=sense(line,a,b)
 for role in ['entry','exit']:
  gid=zone+'-'+role;gates.append({'id':gid,'line':line,'direction':di if role=='entry' else ('negative' if di=='positive' else 'positive')});evidence.append({'gate':gid,'way':wid,'version':w['version'],'booths':booths,'kind':'ramp-plaza'})
 # On two-way approaches the outside endpoint is the free-road side (start
 # of the selected entry way), not the main-carriageway end of its continuation.
 locations[zone]={'entry':point(w['nodes'][0]),'exit':point(w['nodes'][0]) if w['tags'].get('oneway')=='no' else point(ways[exitway]['nodes'][-1])}
refs=json.loads((ROOT/'pricing-candidates/ap41-tariffs.json').read_text());assert len(refs['ods'])==56
fares=[{'from':r['from']+'-entry','to':r['to']+'-exit','tariff':r['tariff']} for r in refs['ods']]
net={'id':'es-ap41','tollId':'es-ap41','validFrom':refs['validFrom'],'validThrough':refs['validThrough'],'timeZone':'Europe/Madrid','gates':gates,'pricing':{'kind':'od','chargedAt':'exit','entries':[g['id'] for g in gates if g['id'].endswith('-entry')],'exits':[g['id'] for g in gates if g['id'].endswith('-exit')],'fares':fares},'coverageWays':[{'id':str(wid),'version':ways[wid]['version'],'line':[point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)],'evidence':{'checked':'2026-09-16','tariffSources':[refs['source']],'geometrySource':'https://www.openstreetmap.org/copyright'}}
toll=next(t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-ap41');doc={'schema':2,'generated':'2026-09-16','currency':'EUR','complete':False,'tolls':[toll],'pricing':[net],'notes_global':'Disabled AP-41 OD candidate; source-backed cash/Via-T/day/night matrix. Geometry and all approaches require route validation. © OpenStreetMap contributors.'}
(ROOT/'pricing-candidates/ap41.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');out=ROOT/'audit/2026-09-16/networks/ap41';out.mkdir(exist_ok=True);(out/'provenance.json').write_text(json.dumps({'source':'../../spain-graph/provenance.json','gates':evidence,'probeLocations':locations,'status':'candidate_pending_real_routes'},ensure_ascii=False,indent=2)+'\n');print(len(gates),'gates',len(fares),'OD pairs',len(selected),'source ways')
