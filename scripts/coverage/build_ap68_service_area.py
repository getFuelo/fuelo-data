#!/usr/bin/env python3
"""Model the published Bilbao–Arrigorriaga service-area return, without a generic self fare.

The physical return booth closes the outbound journey at its published 235c.
A separate downstream cut opens the already-paid continuation to Bilbao (0c).
Other origins/destinations have no invented service-area fare and fail closed.
"""
import gzip, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'audit/2026-09-16/networks/ap68'
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
local=json.loads((folder/'service-area-graph.json').read_text())
ways={w['id']:w for w in graph['ways']};ways.update({w['id']:w for w in local['ways']})
nodes={**graph['nodes'],**local['nodes']}
source='https://www.arabat.eus/wp-content/uploads/2026/02/26_003-Avasa-AP68-Bilbao_Zaragoza-T26.pdf'
path=ROOT/'pricing-candidates/ap68.json';doc=json.loads(path.read_text());net=doc['pricing'][0]
way=ways[231764143];assert way['tags']['oneway']=='yes' and 3241643071 in way['nodes']
# Two non-overlapping cuts on the actual one-way road, 120m apart, not two
# events at the same position whose ordering would depend on catalog order.
def cut(node,id):
 i=way['nodes'].index(node);a,c,b=[nodes[str(n)] for n in way['nodes'][i-1:i+2]]
 cos=math.cos(math.radians(c[0]));dx=(b[1]-a[1])*cos;dy=b[0]-a[0];norm=math.hypot(dx,dy)
 line=[{'lat':c[0]+s*dx/norm/111195,'lng':c[1]-s*dy/norm/111195/cos} for s in (-6,6)]
 def side(p):return (line[1]['lng']-line[0]['lng'])*(p[0]-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p[1]-line[0]['lng'])
 return {'id':id,'line':line,'direction':'positive' if side(b)>side(a) else 'negative'}
exit_id='SERVICE-RETURN-exit';entry_id='SERVICE-RETURN-entry'
net['gates']=[g for g in net['gates'] if g['id'] not in (exit_id,entry_id)]+[cut(3241643071,exit_id),cut(3241638854,entry_id)]
p=net['pricing'];p['entries']=list(dict.fromkeys(p['entries']+[entry_id]));p['exits']=list(dict.fromkeys(p['exits']+[exit_id]))
p['fares']=[f for f in p['fares'] if f['from']!=entry_id and f['to']!=exit_id]+[
 {'from':'BILBAO-entry','to':exit_id,'tariff':{'baseCents':235,'bands':[]}},
 {'from':entry_id,'to':'BILBAO-exit','tariff':{'baseCents':0,'bands':[]}}]
# The source lists the whole return price. The zero continuation is not a
# claim that arbitrary travel on the AP-68 is free.
selected=[231764143,231764150,231764142,231764151,317850941]
free=[107527587,297261481,107527586]
for id in selected+free:
 w=ways[id];record={'id':str(id),'version':w['version'],'line':[dict(zip(('lat','lng'),nodes[str(n)])) for n in w['nodes']]}
 if id in free:record['freeTravelSource']='https://interbiak.bizkaia.eus/es/pago-por-uso-ppu'
 net['coverageWays']=[r for r in net['coverageWays'] if r['id']!=str(id)]+[record]
net['evidence']['tariffSources']=list(dict.fromkeys(net['evidence']['tariffSources']+[source]))
doc['schema']=max(doc['schema'],3)
path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
(folder/'service-area-settlement.json').write_text(json.dumps({'source':source,'booth':3241643071,'way':231764143,'version':way['version'],'publishedJourney':'Bilbao – A. Serv. Arrigorriaga – Bilbao','cents':235,'continuation':'Downstream logical entry closes at Bilbao for 0 additional cents. Only complete supported journeys are priced.','freeApproachWays':free,'freeApproachSource':'https://interbiak.bizkaia.eus/es/pago-por-uso-ppu','generalCarScope':'A-8 Bilbao approach is outside passenger-car tolling; freeTravel applies only to these exact source ways.','regression':'pricing-candidates/ap68-service-area/bilbao-service-bilbao.json'},ensure_ascii=False,indent=2)+'\n')
print('AP-68 service-area return: 235 cents; no generic same-origin fare')
