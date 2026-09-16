#!/usr/bin/env python3
"""AP-53 candidate: physical intermediate plazas and directed terminal cuts.

Lalín access aliases share exactly the published terminal fares. This does not
infer a price for unlisted pairs or certify travel entirely inside that zone.
"""
import collections,gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
with gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt') as f:d=json.load(f)
ways={w['id']:w for w in d['ways']};nodes=d['nodes'];pts={p['id']:p for p in d['points']};at=collections.defaultdict(set)
for w in ways.values():
 for n in w['nodes']:at[n].add(w['id'])
selected={w['id'] for w in ways.values() if w['tags'].get('ref')=='AP-53'}
# Dozón terminal boundary: the road reference changes to AG-53 just before
# exit 56. Provider maneuvers span that free connector and the N-525 approach.
selected.update([237087438,147588076,66835415])
for _ in range(12):
 added=set()
 for wid in selected:
  for n in ways[wid]['nodes']:
   for other in at[n]-selected:
    t=ways[other]['tags']
    free_terminal_ramp=t.get('highway') in ['motorway_link','trunk_link'] and all(nodes[str(n)][0]<42.704 and nodes[str(n)][1]>-8.23 for n in ways[other]['nodes'])
    if t.get('highway') in ['motorway_link','trunk_link','motorway','service'] and (t.get('toll')=='yes' or free_terminal_ramp) and t.get('ref') in [None,'AP-53']:added.add(other)
 selected.update(added)
 if not added:break

def point(n):
 a=nodes[str(n)];return {'lat':a[0],'lng':a[1]}
def plane(center,a,b,half):
 cos=math.cos(math.radians(center['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];length=math.hypot(dx,dy);px=-dy/length;py=dx/length
 return [{'lat':center['lat']+v*py/111195,'lng':center['lng']+v*px/111195/cos} for v in [-half,half]]
def direction(line,a,b):
 def cross(p):return (line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
 return 'positive' if cross(b)>cross(a) else 'negative'
gates=[];roles={};evidence=[]
def add(zone,role,wid,nid,half=12):
 w=ways[wid];i=w['nodes'].index(nid);a=point(w['nodes'][max(0,i-1)]);b=point(w['nodes'][min(len(w['nodes'])-1,i+1)]);line=plane(point(nid),a,b,half);gid=zone+'-'+role
 gates.append({'id':gid,'line':line,'direction':direction(line,a,b)});roles[gid]=(zone,role)
 evidence.append({'gate':gid,'way':wid,'wayVersion':w['version'],'node':nid,'halfWidthMeters':half,'kind':'physical-plaza' if nid in pts and pts[nid]['tags'].get('barrier')=='toll_booth' else 'logical-entry-boundary'})
# Northern paid terminal: southbound traffic bypasses the collection booths.
# Place its logical entry on the actual southbound AP-53, beside Vedra.
w=ways[119472403];nid=min(w['nodes'],key=lambda n:abs(nodes[str(n)][0]-42.77992));add('Santiago','entry',w['id'],nid,8)
# Northbound main lane and Via-T are covered by one exit section.
add('Santiago','exit',98039388,764911133,14)
# Southern terminal: the collection barrier is southbound, with a separate
# northbound entry carriageway. Locate the latter from its directed source way.
options=[]
for wid in selected:
 w=ways[wid]
 if w['tags'].get('ref')!='AP-53' or w['tags'].get('highway')!='motorway':continue
 a=point(w['nodes'][0]);b=point(w['nodes'][-1])
 if b['lat']<=a['lat']:continue
 for nid in w['nodes']:
  p=point(nid);dist=math.hypot((p['lat']-42.7080631),(p['lng']+8.2298935)*.735)
  options.append((dist,wid,nid))
_,wid,nid=min(options);assert _<.001;add('Lalín','entry',wid,nid,8);add('Lalín','exit',98176727,1132439387,10)
# A shared finite cut spans each ramp plaza. Entry and exit are opposite
# directed events, even at Bandeira where each role has two source lanes.
for zone,entry,exit in [('Ribadulla',[(679120821,6359222638)],[(98020218,1134259768)]),('Bandeira',[(93387468,1132443183),(93387467,1132443184)],[(98039414,1132443182),(98039397,1132443185)]),('Silleda',[(679126251,1135796958)],[(98171698,1135796872)])]:
 allids=[nid for _,nid in entry+exit];center={k:sum(point(n)[k] for n in allids)/len(allids) for k in ['lat','lng']};w=ways[entry[0][0]];i=w['nodes'].index(entry[0][1]);a=point(w['nodes'][i-1]);b=point(w['nodes'][i+1]);half=math.hypot(max(point(n)['lat'] for n in allids)-min(point(n)['lat'] for n in allids),(max(point(n)['lng'] for n in allids)-min(point(n)['lng'] for n in allids))*.735)*111195/2+5;line=plane(center,a,b,half);di=direction(line,a,b)
 for role,lanes in [('entry',entry),('exit',exit)]:
  gid=zone+'-'+role;gates.append({'id':gid,'line':line,'direction':di if role=='entry' else ('negative' if di=='positive' else 'positive')});roles[gid]=(zone,role);evidence.append({'gate':gid,'sourceLanes':[{'way':w,'version':ways[w]['version'],'booth':n} for w,n in lanes],'halfWidthMeters':half,'kind':'physical-plaza'})
# Silleda has a separate southbound ramp that bypasses the ticket plaza.
# It still enters the charged journey to the southern collection terminal.
w=ways[98171705];add('Silleda-south','entry',w['id'],w['nodes'][1],6)
roles['Silleda-south-entry']=('Silleda','entry')
refs=json.loads((ROOT/'pricing-candidates/ap53-tariffs.json').read_text());pairs={}
def alias(name):return 'Lalín' if name.startswith('Lalín') or name=='Alto de Santo Domingo' else 'Ribadulla' if name=='Ribadull' else name
for row in refs['ods']:
 a,b=alias(row['from']),alias(row['to']);key=(a,b)
 if key in pairs:assert pairs[key]==row['tariff']
 pairs[key]=row['tariff'];pairs[(b,a)]=row['tariff']
assert len(pairs)==20
# ACEGA/BOE: Via-T may qualify for a free reverse journey within 24h and
# retrospective monthly recurrence discounts. Without trip history, preserve
# the full supported 0..general interval; cash/card retains the general fare.
for pair,tariff in list(pairs.items()):
 pairs[pair]={'baseCents':tariff['baseCents'],'bands':[{'cents':0,'maxCents':tariff['baseCents'],'requires':['payment:via-t']}]}

network={'id':'es-ap53','tollId':'es-ap53','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','gates':gates,'pricing':{'kind':'od','chargedAt':'exit','entries':[k for k,v in roles.items() if v[1]=='entry'],'exits':[k for k,v in roles.items() if v[1]=='exit'],'fares':[{'from':entry,'to':exit,'tariff':pairs[(a,b)]} for entry,(a,role) in roles.items() if role=='entry' for exit,(b,other_role) in roles.items() if other_role=='exit' and (a,b) in pairs]},'coverageWays':[{'id':str(wid),'version':ways[wid]['version'],'line':[point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)],'evidence':{'checked':'2026-09-16','tariffSources':[refs['source'],'https://acega.es/tarifas/'],'geometrySource':'https://www.openstreetmap.org/copyright'}}
network['avoidanceGateIds']=network['pricing']['entries']
# Source-backed free terminal region, entirely beyond the southern collection
# boundary. Keep the plaza approach outside this exception (conservative gap).
free_source='https://www.lamoncloa.gob.es/consejodeministros/referencias/paginas/1999/c2910990.aspx'
for way in network['coverageWays']:
 if all(p['lat']<42.704 and p['lng']>-8.23 for p in way['line']):
  ref=ways[int(way['id'])]['tags'].get('ref')
  if ref=='AG-53':
   way['freeTravelSource']='https://www.xunta.gal/es/notas-de-prensa/-/nova/85353/xunta-acuerda-solicitarle-gobierno-espana-liberacion-del-peaje-53-para-unificar'
  elif ref=='N-525':
   way['freeTravelSource']='https://www.openstreetmap.org/way/'+way['id']+'/history'
  else:
   way['freeTravelSource']=free_source
 elif ways[int(way['id'])]['tags'].get('toll')=='no' and all(p['lat']>42.832 for p in way['line']):
  way['freeTravelSource']='https://www.boe.es/diario_boe/txt.php?id=BOE-A-2008-16770'
network['evidence']['tariffSources'].append(free_source)

toll=next(t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-ap53');doc={'generated':'2026-09-16','schema':3,'currency':'EUR','complete':False,'tolls':[toll],'pricing':[network],'notes_global':'Development candidate; © OpenStreetMap contributors. General light-vehicle fares; Via-T uses an explicit 0..general range when return/monthly history is unknown. Closed trips and unlisted zone-internal trips remain unavailable.'}
(ROOT/'pricing-candidates/ap53.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');out=ROOT/'audit/2026-09-16/networks/ap53';out.mkdir(exist_ok=True);(out/'provenance.json').write_text(json.dumps({'gates':evidence,'source':'../../spain-graph/provenance.json','aliases':{'Lalín Oeste/Centro/Este and Alto de Santo Domingo':'Lalín','Ribadull (PDF typo)':'Ribadulla'},'aliasEvidence':'All collapsed tariff rows have equal published fares; BOE-A-2025-7166 also defines Lalín as Alto de Santo Domingo for journey purposes.','status':'candidate_pending_real_routes'},ensure_ascii=False,indent=2)+'\n');print(len(gates),'gates',len(pairs),'directed OD pairs',len(selected),'coverage ways')
