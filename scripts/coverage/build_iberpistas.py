#!/usr/bin/env python3
"""Disabled AP-6/AP-51 settlement candidate, with separately located road markers.

The published joint OD table governs cross-road journeys. Villacastín's
internal plaza/roundabout movements do not close the financial journey.
The town cut here covers SC-SG-13 only; other public approaches remain open.
"""
import copy,gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(path):return json.loads((ROOT/path).read_text())
def write(path,value):
 p=ROOT/path;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
a,b=[read(f'pricing-candidates/{f}.json') for f in ('ap6','ap51')]
net=copy.deepcopy(a['pricing'][0]);other=b['pricing'][0]
net['id']='es-ap6-ap51';net['sharedRoads']=[{'tollId':n['tollId'],'gates':n['gates']} for n in (a['pricing'][0],other)]
net['coverageWays']=list({w['id']:w for n in (net,other) for w in n['coverageWays']}.values())
net['evidence']['tariffSources']+=other['evidence']['tariffSources']
net['gates']=[g for g in net['gates'] if not g['id'].startswith('VILLACASTIN')]+[g for g in other['gates'] if g['id'].startswith(('AVILA-','VICOLOZANO-'))]
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'));ways={w['id']:w for w in graph['ways']};nodes=graph['nodes']
def point(n):return dict(zip(('lat','lng'),nodes[str(n)]))
sourcecuts=[]
for role,wid,node in [('entry',101211843,1168433136),('exit',39041139,1168433374)]:
 w=ways[wid];i=w['nodes'].index(node);p,c,q=[point(w['nodes'][j]) for j in (i-1,i,i+1)];cos=math.cos(math.radians(c['lat']));dx=(q['lng']-p['lng'])*cos;dy=q['lat']-p['lat'];length=math.hypot(dx,dy);px,py=-dy/length,dx/length
 line=[{'lat':c['lat']+v*py/111195,'lng':c['lng']+v*px/111195/cos} for v in (-8,8)]
 cross=lambda p:(line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
 net['gates'].append({'id':'VILLACASTIN-'+role,'line':line,'direction':'positive' if cross(q)>cross(p) else 'negative'})
 sourcecuts.append({'role':role,'way':wid,'version':w['version'],'node':node,'outsideNode':1168432984})
fares=[f for f in net['pricing']['fares'] if '-sur-' not in f['from'] and '-sur-' not in f['to']]
for f in fares:f['roadIds']=['es-ap6']
fares += [{**f,'roadIds':['es-ap51']} for f in other['pricing']['fares'] if not f['from'].startswith('AP6-') and not f['to'].startswith('AP6-')]
ref=read('pricing-candidates/ap51-tariffs.json');names={'Villalba':'VILLALBA','San Rafael':'SAN RAFAEL','Adanero':'ADANERO','Vicolozano':'VICOLOZANO','Ávila':'AVILA'}
for row in ref['joint_ap6_ods']:
 for x,y in [(names[row['from']],names[row['to']]),(names[row['to']],names[row['from']])]:
  for origin in [x]+(['VILLALBA-reversible'] if x=='VILLALBA' else []):
   for dest in [y]+(['VILLALBA-reversible'] if y=='VILLALBA' else []):
    fares.append({'from':origin+'-entry','to':dest+'-exit','tariff':row['tariff'],'roadIds':['es-ap6','es-ap51']})
net['pricing']['fares']=fares;net['pricing']['entries']=[g['id'] for g in net['gates'] if g['id'].endswith('-entry')];net['pricing']['exits']=[g['id'] for g in net['gates'] if g['id'].endswith('-exit')]
assert len({(f['from'].replace('-reversible',''),f['to'].replace('-reversible','')) for f in fares})==30
catalog={**a,'schema':4,'tolls':a['tolls']+b['tolls'],'pricing':[net],'notes_global':'Disabled shared AP-6/AP-51 financial settlement. Public SC-SG-13 approach mapped; other approaches, lane and avoidance review pending. © OpenStreetMap contributors.'}
write('pricing-candidates/iberpistas.json',catalog)
locations={}
for family in ('ap6','ap51'):
 locations.update(read(f'audit/2026-09-16/networks/{family}/provenance.json')['probeLocations'])
locations['VILLACASTIN']={'entry':point(1168432984),'exit':point(1168432984)}
write('audit/2026-09-16/networks/iberpistas/provenance.json',{'probeLocations':locations,'townCuts':sourcecuts,'status':'candidate_pending_all_public_approaches','source':'../../spain-graph/provenance.json'})
print(len(net['coverageWays']),'ways',len(net['gates']),'financial gates',len(fares),'physical fares')
