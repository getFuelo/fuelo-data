#!/usr/bin/env python3
"""Build the disabled shared AP-8/AP-1 financial network from published OD rows.

Regional boundaries do not settle a journey. Road markers are separate from
financial entry/exit gates; joint fares are never reconstructed by adding legs.
"""
import copy,gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(path):return json.loads((ROOT/path).read_text())
def write(path,value):
 p=ROOT/path;p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
families=['ap8-bizkaia','ap8-gipuzkoa-west','ap1-closed']
docs=[read(f'pricing-candidates/{f}.json') for f in families];net=copy.deepcopy(docs[0]['pricing'][0]);net['id']='es-ap8-ap1-shared'
net['gates']=[g for d in docs for g in d['pricing'][0]['gates']]
net['sharedRoads']=[{'tollId':d['pricing'][0]['tollId'],'gates':copy.deepcopy(d['pricing'][0]['gates'])} for d in docs]
coverage={w['id']:w for d in docs for w in d['pricing'][0]['coverageWays']}
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'));ways={w['id']:w for w in graph['ways']};nodes=graph['nodes']
def point(n):return dict(zip(('lat','lng'),nodes[str(n)]))
sourcecuts=[]
def cut(id,wid,node,reverse=False):
 w=ways[wid];i=w['nodes'].index(node);a,c,b=[point(w['nodes'][j]) for j in (max(0,i-1),i,min(len(w['nodes'])-1,i+1))];cos=math.cos(math.radians(c['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];length=math.hypot(dx,dy);px,py=-dy/length,dx/length
 line=[{'lat':c['lat']+v*py/111195,'lng':c['lng']+v*px/111195/cos} for v in (-8,8)]
 cross=lambda p:(line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
 sourcecuts.append({'gate':id,'way':wid,'version':w['version'],'node':node,'reverse':reverse})
 return {'id':id,'line':line,'direction':'positive' if (cross(b)>cross(a)) != reverse else 'negative'}
# North-facing Bergara plaza has a two-way public approach from GI-627.
for role in ['entry','exit']:
 gate=cut('BERGARA-NORTE-'+role,27255537,299139562,role=='exit');net['gates'].append(gate);net['sharedRoads'][2]['gates'].append(gate)
# A Bizkaia–AP-1 journey traverses Gipuzkoa without using a local plaza.
net['sharedRoads'][1]['gates'] += [cut('GIPUZKOA-mainline-east',7660201,32660349),cut('GIPUZKOA-mainline-west',7660203,281187774)]
additional=[]
for w in ways.values():
 ref=w['tags'].get('ref');inside=all(43.16<=nodes[str(n)][0]<=43.32 and -2.80<=nodes[str(n)][1]<=-2.12 for n in w['nodes'])
 if (inside and ref in ['AP-8','AP-1;AP-8','AP-8;AP-1']) or w['id'] in [27255537,1409767652]:
  if str(w['id']) not in coverage:additional.append(w['id'])
  coverage[str(w['id'])]={'id':str(w['id']),'version':w['version'],'line':[point(n) for n in w['nodes']]}
net['coverageWays']=list(coverage.values())
names={'Acceso Oeste':'OESTE','Amorebieta-Etxano':'AMOREBIETA','Iurreta':'IURRETA','Abadiño':'ABADINO','Ermua':'ERMUA','Eibar':'EIBAR','Elgoibar':'ELGOIBAR','Itziar':'ITZIAR','Zestoa – Zumaia':'ZUMAIA','Zarautz Oeste':'ZARAUTZ-OESTE','Zarautz Barrera (Donostia)':'DONOSTIA','Bergara I/N':'BERGARA-NORTE','Bergara H/S':'BERGARA-SUR','Arrasate-Mondragón':'ARRASATE','Eskoriatza':'ESKORIATZA','Luko':'LUKO','Etxabarri-Ibiña':'ETXABARRI'}
regions={}
locations={};nativeJourneys={}
for family,doc in zip(families,docs):
 p=read(f'audit/2026-09-16/networks/{family}/provenance.json');locations.update(p['probeLocations']);nativeJourneys.update(p.get('probeJourneys',{}))
 for z in p['probeLocations']:regions[z]=doc['pricing'][0]['tollId']
regions['BERGARA-NORTE']='es-ap1-gipuzkoa';locations['BERGARA-NORTE']={'entry':point(27002802),'exit':point(27002802)}
ref=read('pricing-candidates/ap8-ap1-full-tariffs.json');fares=[];journeys={}
for row in ref['ods']:
 if row['from'] not in names or row['to'] not in names or row['from']==row['to']:continue
 for a,b in [(names[row['from']],names[row['to']]),(names[row['to']],names[row['from']])]:
  roads={regions[a],regions[b]}
  if roads=={'es-ap8-bizkaia','es-ap1-gipuzkoa'}:roads.add('es-ap8-gipuzkoa')
  def aliases(z):return [z]+([z+'-oeste'] if z+'-oeste' in locations else [])
  for x in aliases(a):
   for y in aliases(b):fares.append({'from':x+'-entry','to':y+'-exit','tariff':row['tariff'],'roadIds':sorted(roads)})
  # Cross-region destinations lie east of every Bizkaia access.
  journeys[a+'--'+b]=nativeJourneys.get(a+'--'+b,{'entry':locations[a]['entry'],'exit':locations[b]['exit']})
# The unconstrained Ermua–Eibar public-road route is retained separately.
# A through point on the eastbound AP-8 verifies the published paid movement.
journeys['ERMUA--EIBAR']['via']=[point(25439405)]
net['pricing']={'kind':'od','chargedAt':'exit','entries':[g['id'] for g in net['gates'] if g['id'].endswith('-entry')],'exits':[g['id'] for g in net['gates'] if g['id'].endswith('-exit')],'fares':fares}
net['evidence']['tariffSources']=list(dict.fromkeys(s for d in docs for s in d['pricing'][0]['evidence']['tariffSources']))
write('pricing-candidates/ap8-ap1-shared.json',{**docs[0],'schema':4,'complete':False,'tolls':[t for d in docs for t in d['tolls']],'pricing':[net],'notes_global':'Disabled shared AP-8/AP-1 candidate. Published journey fares, separate road markers. All-access, discount, eastern AP-8 and avoidance review pending. © OpenStreetMap contributors.'})
write('audit/2026-09-16/networks/ap8-ap1-shared/provenance.json',{'source':'../../spain-graph/provenance.json','probeLocations':locations,'probeJourneys':journeys,'sourceCuts':sourcecuts,'additionalCoverageWays':additional,'canonicalProbeZones':list(names.values()),'status':'candidate_pending_full_validation'})
print(len(journeys),'directed canonical journeys',len(fares),'physical fare variants')
