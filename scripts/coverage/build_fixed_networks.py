#!/usr/bin/env python3
"""Build Cadí/AP-46 candidates from versioned OSM roads and physical toll roofs."""
import argparse,hashlib,json,math,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPECS={
 'cadi':{'plaza':'cadi-plaza.xml','road':'c16-full.xml','relation':'3569966','bbox':'1.832,42.328,1.85,42.348','roof':'154065606','tangentWay':'154070429','booth':'146302625','ref':'C-16','southLimit':42.1,'base':1456},
 'ap46':{'plaza':'ap46-plaza.xml','road':'ap46-full.xml','relation':'1813372','bbox':'-4.47,36.892,-4.445,36.913','roof':'303994848','tangentWay':'516787827','booth':'5044370601','ref':'AP-46','base':435},
}
def build(name,downloads):
 spec=SPECS[name];roots=[E.parse(downloads/spec[k]).getroot() for k in ['road','plaza']];nodes={n.get('id'):{'lat':float(n.get('lat')),'lng':float(n.get('lon'))} for r in roots for n in r.findall('node')};ways={w.get('id'):w for r in roots for w in r.findall('way')};tags=lambda e:{t.get('k'):t.get('v') for t in e.findall('tag')};shape=lambda w:[nodes[n.get('ref')] for n in w.findall('nd')]
 coverage=[]
 for id,w in ways.items():
  t=tags(w);line=shape(w)
  selected=t.get('ref')==spec['ref'] or (t.get('toll')=='yes' and t.get('highway') in ['trunk','trunk_link','motorway','motorway_link'])
  if selected and all(p['lat']>=spec.get('southLimit',-90) for p in line):coverage.append({'id':id,'version':int(w.get('version')),'line':line})
 roof=shape(ways[spec['roof']]);w=ways[spec['tangentWay']];refs=[n.get('ref') for n in w.findall('nd')];i=refs.index(spec['booth']);a=nodes[refs[max(0,i-1)]];b=nodes[refs[min(len(refs)-1,i+1)]]
 # One transverse plane for the entire plaza: individual lanes must not be charged repeatedly.
 booth_ids=sorted({n.get('id') for r in roots[1:] for n in r.findall('node') if tags(n).get('barrier')=='toll_booth'})
 center={k:sum(nodes[id][k] for id in booth_ids)/len(booth_ids) for k in ['lat','lng']};cos=math.cos(math.radians(center['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];norm=math.hypot(dx,dy);px=-dy/norm;py=dx/norm
 projection=[(p['lng']-center['lng'])*cos*px+(p['lat']-center['lat'])*py for p in roof];line=[{'lat':center['lat']+v*py,'lng':center['lng']+v*px/cos} for v in [min(projection)-2/111195,max(projection)+2/111195]]
 bands=[]
 if name=='ap46':bands=[{'cents':0,'minutes':[0,360]},{'cents':660,'dates':['2026-05-01','2026-10-31'],'minutes':[360,1440]},{'cents':660,'weekdays':[6,7],'minutes':[360,1440]},{'cents':660,'dates':['2026-03-27','2026-04-12'],'minutes':[360,1440]}]
 toll=next(t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-'+name).copy();toll.update(lat=center['lat'],lng=center['lng'],notes='General light-vehicle candidate with actual physical charge gate. No automatic enrollment/recurrence discounts.')
 if name=='cadi':toll['source']='https://tunels.cat/wp-content/uploads/2025/12/Tunels_tarifes_2026.pdf'
 gate={'id':name+'-plaza','line':line,'direction':'both'};net={'id':toll['id'],'tollId':toll['id'],'validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','gates':[gate],'pricing':{'kind':'gates','fares':{gate['id']:{'baseCents':spec['base'],'bands':bands}}},'coverageWays':coverage,'evidence':{'checked':'2026-09-16','tariffSources':[toll['source']],'geometrySource':'https://www.openstreetmap.org/copyright'}}
 d={'generated':'2026-09-16','schema':2,'currency':'EUR','complete':False,'notes_global':'Candidate, not published country coverage. © OpenStreetMap contributors, ODbL 1.0.','tolls':[toll],'pricing':[net]};(ROOT/'pricing-candidates'/f'{name}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 out=ROOT/'audit/2026-09-16/networks'/name;out.mkdir(parents=True,exist_ok=True);e={'checked':'2026-09-16','roadSource':f'https://api.openstreetmap.org/api/0.6/relation/{spec["relation"]}/full','plazaSource':'https://api.openstreetmap.org/api/0.6/map?bbox='+spec['bbox'],'sourceHashes':{spec[k]:hashlib.sha256((downloads/spec[k]).read_bytes()).hexdigest() for k in ['road','plaza']},'booths':booth_ids,'roof':{'id':spec['roof'],'version':int(ways[spec['roof']].get('version'))},'method':'Single transverse plane centered on all mapped booth lanes; extent from the mapped roof projected perpendicular to the booth carriageway plus 2m. Every lane is one plaza charge, not one charge per nearby booth.','coverageWayCount':len(coverage),'coverageBoundary':'C-16 north of 42.1° only; excludes Manresa/Les Fonts/Vallvidrera' if name=='cadi' else 'AP-46 relation and tolled plaza approaches'};(out/'provenance.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n');print(name,len(coverage),'ways',len(booth_ids),'lanes mapped as one charge')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);args=ap.parse_args()
 for name in SPECS:build(name,args.downloads)
