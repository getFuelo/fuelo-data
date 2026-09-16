#!/usr/bin/env python3
"""Build Artxanda candidate from OSM booth ways and the mapped toll roof."""
import argparse,hashlib,json,math,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def build(path):
 root=E.parse(path).getroot();nodes={n.get('id'):{'lat':float(n.get('lat')),'lng':float(n.get('lon'))} for n in root.findall('node')};ways={w.get('id'):w for w in root.findall('way')}
 tags=lambda w:{t.get('k'):t.get('v') for t in w.findall('tag')}
 shape=lambda w:[nodes[n.get('ref')] for n in w.findall('nd')]
 coverage=[{'id':id,'version':int(w.get('version')),'line':shape(w)} for id,w in ways.items() if tags(w).get('toll')=='yes' and tags(w).get('highway') in ['trunk','trunk_link','motorway','motorway_link']]
 roof=shape(ways['623070234']);gates=[];evidence=[]
 for gid,nid,wid in [('artxanda-inbound','32620454','11505078'),('artxanda-outbound','1458151541','28193390')]:
  w=ways[wid];refs=[n.get('ref') for n in w.findall('nd')];i=refs.index(nid);a=nodes[refs[i-1]];b=nodes[refs[i+1]];p=nodes[nid];cos=math.cos(math.radians(p['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];length=math.hypot(dx,dy);px=-dy/length;py=dx/length
  projections=[(v['lng']-p['lng'])*cos*px+(v['lat']-p['lat'])*py for v in roof]
  line=[{'lat':p['lat']+v*py,'lng':p['lng']+v*px/cos} for v in [min(projections)-2/111195,max(projections)+2/111195]]
  side=lambda q:(line[1]['lng']-line[0]['lng'])*(q['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(q['lng']-line[0]['lng'])
  gates.append({'id':gid,'line':line,'direction':'positive' if side(b)>side(a) else 'negative'})
  evidence.append({'gate':gid,'booth':nid,'way':wid,'wayVersion':int(w.get('version')),'roof':'623070234','roofVersion':int(ways['623070234'].get('version')),'method':'Perpendicular to oneway carriageway through booth; extent from projected physical toll roof plus 2m each end.'})
 toll=next(t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-artxanda').copy();toll.update(lat=nodes['32620454']['lat'],lng=nodes['32620454']['lng'],road='BI-626 / BI-627',price=1.55,price_high=None,variable=False,notes='General light-vehicle tariff. Actual north plaza, not the unrelated Bilbao city access. No automatic resident/EV discount.')
 d={'generated':'2026-09-16','schema':2,'currency':'EUR','complete':False,'notes_global':'Development candidate only. © OpenStreetMap contributors, ODbL 1.0. Spain remains incomplete.','tolls':[toll],'pricing':[{'id':'es-artxanda','tollId':'es-artxanda','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','gates':gates,'pricing':{'kind':'gates','fares':{g['id']:{'baseCents':155,'bands':[]} for g in gates}},'coverageWays':coverage,'evidence':{'checked':'2026-09-16','tariffSources':[toll['source']],'geometrySource':'https://www.openstreetmap.org/copyright'}}]}
 (ROOT/'pricing-candidates/artxanda.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 out=ROOT/'audit/2026-09-16/networks/artxanda';out.mkdir(parents=True,exist_ok=True)
 (out/'provenance.json').write_text(json.dumps({'source':'https://api.openstreetmap.org/api/0.6/map?bbox=-2.951,43.276,-2.917,43.294','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':'2026-09-16','gates':evidence,'coverageWayCount':len(coverage),'gateInventory':'Two booth nodes on opposite one-way carriageways under the same roof. Shared by the two charged tunnel branches. Existing Bilbao city booth is unrelated.'},ensure_ascii=False,indent=2)+'\n');print(len(coverage),'ways',len(gates),'directional gates')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('osm',type=Path);build(ap.parse_args().osm)
