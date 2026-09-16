#!/usr/bin/env python3
"""Map published open-system plazas from the national OSM graph.

One finite crossing plane per plaza, not one charge per mapped lane. Candidates
remain disabled until their route corpus and country coverage are reviewed.
"""
import collections,gzip,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'audit/2026-09-16/spain-graph'
FAMILIES={
 'r2-open':{'ref':'R-2','coverageRefs':['R-2','M-50'],'lat':[40.48,40.57],'lng':[-3.68,-3.488],'parent':'es-r2','tariffFamily':'r2','groups':[
  ('osm-review-258368527','es-r2-alcobendas','Alcobendas',60),
  ('osm-review-353332722','es-r2-aeropuerto','Aeropuerto',60)]},
 'vallvidrera':{'ref':'C-16','lat':[41.385,41.50],'groups':[
  ('osm-review-255620252','es-vallvidrera','Túnels de Vallvidrera',470)]},
 'ap7-alicante-cartagena':{'ref':'AP-7','lat':[37.65,38.15],'lng':[-.96,-.65],'parent':'es-ap7-alicante-cartagena','groups':[
  ('osm-review-721015144','es-ap7-montesinos-troncal','TRONCAL DE LOS MONTESINOS',285),
  ('osm-review-295557912','es-ap7-zenia-troncal','TRONCAL DE LA ZENIA',285),
  ('osm-review-297701500','es-ap7-zenia-acceso','ACCESO DE LA ZENIA',285)]},
 'ap7-estepona-guadiaro':{'ref':'AP-7','lat':[36.25,36.46],'lng':[-5.40,-5.12],'parent':'es-ap7-estepona-guadiaro','groups':[
  ('osm-review-31477964','es-ap7-manilva-troncal','TRONCAL DE MANILVA',245),
  ('osm-review-302819538','es-ap7-manilva-acceso','ACCESO DE MANILVA',120)]},
 'ap7-malaga-estepona':{'ref':'AP-7','lat':[36.42,36.65],'lng':[-5.17,-4.60],'parent':'es-ap7-malaga-estepona','groups':[
  ('osm-review-297560234','es-ap7-calahonda-troncal','TRONCAL DE CALAHONDA',570),
  ('osm-review-14144724369','es-ap7-calahonda-acceso','ACCESO DE CALAHONDA',355),
  ('osm-review-13842373','es-ap7-san-pedro-troncal','TRONCAL DE SAN PEDRO DE ALCANTARA',385),
  ('osm-review-280770329','es-ap7-san-pedro-acceso','ACCESO DE SAN PEDRO DE ALCANTARA',220)]},
 'autema':{'ref':'C-16','lat':[41.46,41.80],'groups':[
  ('osm-review-141831078','es-c16-sant-vicenc-c55','Ramal Sant Vicenç–C55',490),
  ('osm-review-150686870','es-c16-terrassa-manresa','Manresa troncal',976),
  ('osm-review-255558497','es-c16-sant-cugat-terrassa','Les Fonts',319)]},
 'c32':{'ref':'C-32','lat':[41.15,41.40],'groups':[
  ('osm-review-279743006','es-c32-vallcarca','Vallcarca troncal',842),
  ('osm-review-332289114','es-c32-cubelles-acceso','Cubelles acceso',269),
  ('osm-review-981187977','es-c32-calafell-acceso','Calafell acceso',79),
  ('osm-review-1489211488','es-c32-cubelles-troncal','Cubelles troncal',503)]},
 'ap15':{'ref':'AP-15','lat':[42.12,43.0],'groups':[
  ('osm-review-938123','es-ap15-marcilla-tronco','Marcilla tronco',685),
  ('osm-review-938352','es-ap15-sarasa','Sarasa',265),
  ('osm-review-93036740','es-ap15-oriz-tiebas','Oriz–Tiebas / Imárcoain',455),
  ('osm-review-195885934','es-ap15-marcilla-enlace','Marcilla enlace',345)]},
}
def main():
 with gzip.open(SOURCE/'graph.json.gz','rt') as f:data=json.load(f)
 review=json.loads((SOURCE/'access-review.json').read_text());groups={g['id']:g for g in review['groups']};points={p['id']:p for p in review['points']};ways={w['id']:w for w in data['ways']};nodes=data['nodes'];at=collections.defaultdict(set)
 for w in ways.values():
  for n in w['nodes']:at[n].add(w['id'])
 legacy={t['id']:t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls']}
 for family,spec in FAMILIES.items():
  inside=lambda w:all(spec['lat'][0]<=nodes[str(n)][0]<=spec['lat'][1] and spec.get('lng',[-180,180])[0]<=nodes[str(n)][1]<=spec.get('lng',[-180,180])[1] for n in w['nodes'])
  tariff_reference=json.loads((ROOT/f"pricing-candidates/{spec.get('tariffFamily',family)}-tariffs.json").read_text()) if spec.get('parent') else None
  selected={w['id'] for w in ways.values() if w['tags'].get('ref') in spec.get('coverageRefs',[spec['ref']]) and inside(w)}
  for groupid, *_ in spec['groups']:
   for nid in groups[groupid]['pointIds']:
    selected.update(wid for wid in points[nid]['incidentWays'] if inside(ways[wid]))
  frontier=set(selected)
  for _ in range(12):
   added=set()
   for id in frontier:
    for n in [ways[id]['nodes'][0],ways[id]['nodes'][-1]]:
     for other in at[n]-selected:
      w=ways[other];t=w['tags']
      if (t.get('toll')=='yes' or (family=='vallvidrera' and t.get('highway')=='motorway_link')) and t.get('highway') in ['motorway_link','trunk_link','motorway','trunk','service'] and t.get('ref') in [None,spec['ref']] and inside(w):added.add(other)
   selected.update(added);frontier=added
   if not added:break
  coverage=[{'id':str(id),'version':ways[id]['version'],'line':[{'lat':nodes[str(n)][0],'lng':nodes[str(n)][1]} for n in ways[id]['nodes']]} for id in sorted(selected)]
  tolls=[];networks=[];evidence=[];probes=[]
  for groupid,id,name,price in spec['groups']:
   group=groups[groupid];booths=[points[n] for n in group['pointIds']];center={'lat':group['lat'],'lng':group['lng']};cos=math.cos(math.radians(center['lat']));angles=[];lane_ways=set()
   for p in booths:
    for wid in p['incidentWays']:
     if wid not in selected:continue
     w=ways[wid];refs=w['nodes'];i=refs.index(p['id']);a=nodes[str(refs[max(0,i-1)])];b=nodes[str(refs[min(len(refs)-1,i+1)])];theta=math.atan2(b[0]-a[0],(b[1]-a[1])*cos);angles.append(theta);lane_ways.add(wid)
   assert angles,(family,name,'no connected mapped lane')
   theta=math.atan2(sum(math.sin(2*a) for a in angles),sum(math.cos(2*a) for a in angles))/2;px=-math.sin(theta);py=math.cos(theta)
   values=[(p['lng']-center['lng'])*cos*px+(p['lat']-center['lat'])*py for p in booths]
   line=[{'lat':center['lat']+v*py,'lng':center['lng']+v*px/cos} for v in [min(values)-8/111195,max(values)+8/111195]]
   old=legacy[id] if id in legacy else legacy[spec.get('parent','es-c32-castelldefels-vendrell' if family=='c32' else 'es-ap15')]
   tariff=next(row['tariff'] for row in tariff_reference['barriers'] if row.get('name',row.get('from'))==name) if tariff_reference else {'baseCents':price,'bands':[]}
   if family=='vallvidrera':
    reference=json.loads((ROOT/'pricing-candidates/vallvidrera-tariffs.json').read_text())['generalReference']
    # The operator does not identify its applicable holiday calendar. Preserve
    # both possible fares during weekday peak hours; weekends/off-peak are exact.
    tariff={'baseCents':reference['valleyCents'],'bands':[{'cents':reference['valleyCents'],'maxCents':reference['peakCents'],'weekdays':reference['peakWeekdays'],'minutes':interval} for interval in reference['peakMinutes']]}
   assert tariff['baseCents']==price
   high=max([price]+[band.get('maxCents',band['cents']) for band in tariff['bands']])
   toll=old.copy();toll.update(id=id,name=name,lat=center['lat'],lng=center['lng'],price=price/100,price_high=high/100 if high>price else None,variable=high>price,model='fixed',notes='General tariff at this physical plaza only. Conditional discounts require separately confirmed eligibility.')
   if tariff_reference:toll['source']=tariff_reference['source']
   tolls.append(toll)
   gate={'id':id+'-plaza','line':line,'direction':'both'};networks.append({'id':id,'tollId':id,'validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','gates':[gate],'pricing':{'kind':'gates','fares':{gate['id']:tariff}},'coverageWays':coverage,'evidence':{'checked':'2026-09-16','tariffSources':[toll['source']],'geometrySource':'https://www.openstreetmap.org/copyright'}})
   evidence.append({'network':id,'reviewGroup':groupid,'booths':group['pointIds'],'laneWays':sorted(lane_ways),'method':'Single plane through booth group center, normal to the mean unoriented lane tangent; spans all booth centers plus 8m at each end. Must validate real routes and individual lane crossings.'})
   for booth in booths:
    incoming=[];outgoing=[]
    for wid in booth['incidentWays']:
     w=ways[wid];sequences=[w['nodes']]
     if w['tags'].get('oneway')=='-1':sequences=[list(reversed(w['nodes']))]
     elif w['tags'].get('oneway')!='yes':sequences.append(list(reversed(w['nodes'])))
     for refs in sequences:
      i=refs.index(booth['id'])
      if i>0:incoming.append((wid,refs[:i+1]))
      if i<len(refs)-1:outgoing.append((wid,refs[i:]))
    for a,left in incoming:
     for b,right in outgoing:
      if left[-2]==right[1]:continue
      refs=left+right[1:]
      # A source way may end at a lane merge inside the plaza. Follow the
      # unique legal continuation to the next split, so this is a traversal
      # of the plaza rather than an arbitrary OSM way fragment.
      used={a,b}
      for _ in range(8):
       choices=[]
       for wid in at[refs[-1]]-used:
        w=ways[wid]
        if wid not in selected:continue
        seq=w['nodes'];oneway=w['tags'].get('oneway')
        if oneway=='-1':seq=list(reversed(seq))
        i=seq.index(refs[-1])
        if i<len(seq)-1 and seq[i+1]!=refs[-2]:choices.append((wid,seq[i:]))
        if i>0 and oneway not in ['yes','-1'] and seq[i-1]!=refs[-2]:choices.append((wid,list(reversed(seq[:i+1]))))
       if len(choices)!=1:break
       wid,seq=choices[0];used.add(wid);refs+=seq[1:]
      probes.append({'network':id,'booth':booth['id'],'way':str(a)+'/'+str(b),'versions':[ways[a]['version'],ways[b]['version']],'traversedWays':[{'id':wid,'version':ways[wid]['version']} for wid in sorted(used)],'geometry':[{'lat':nodes[str(n)][0],'lng':nodes[str(n)][1]} for n in refs]})
  doc={'generated':'2026-09-16','schema':3 if family=='vallvidrera' else 2,'currency':'EUR','complete':False,'notes_global':'Development candidate only; © OpenStreetMap contributors, ODbL 1.0. No claim of national coverage.','tolls':tolls,'pricing':networks};(ROOT/'pricing-candidates'/f'{family}.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');out=ROOT/'audit/2026-09-16/networks'/family;out.mkdir(parents=True,exist_ok=True);(out/'provenance.json').write_text(json.dumps({'source':'../../spain-graph/provenance.json','gates':evidence,'coverageWayCount':len(coverage),'reviewStatus':'candidate_pending_routes'},ensure_ascii=False,indent=2)+'\n');(out/'lane-probes.json').write_text(json.dumps(probes,separators=(',',':'))+'\n');print(family,len(networks),'plazas',len(coverage),'ways',len(probes),'lane probes')
if __name__=='__main__':main()
