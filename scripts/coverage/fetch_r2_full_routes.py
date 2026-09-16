#!/usr/bin/env python3
"""Verify R-2 open barriers plus the closed journey as one real route."""
import json,time,urllib.parse,urllib.request,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
probes=json.loads((ROOT/'audit/2026-09-16/networks/r2-open/lane-probes.json').read_text())
loc=json.loads((ROOT/'audit/2026-09-16/networks/r2/provenance.json').read_text())['probeLocations']['NII-Taracena']
out=ROOT/'pricing-candidates/r2-full-routes';out.mkdir(exist_ok=True)
def heading(a,b):return round(math.degrees(math.atan2((b['lng']-a['lng'])*math.cos(math.radians(a['lat'])),b['lat']-a['lat'])))%360
for plaza,inbound,outbound in [('alcobendas',353914976,258368527),('aeropuerto',353332736,353332722)]:
 for direction,booth in [('east',inbound),('west',outbound)]:
  name=plaza+'-'+direction;target=out/(name+'.json')
  if target.exists():continue
  p=next(p for p in probes if p['booth']==booth);points=p['geometry']
  if direction=='east':
   locations=[{'lat':points[0]['lat'],'lon':points[0]['lng'],'heading':heading(points[0],points[1])},{'lat':loc['exit']['lat'],'lon':loc['exit']['lng']}]
  else:
   locations=[{'lat':loc['entry']['lat'],'lon':loc['entry']['lng']},{'lat':points[-1]['lat'],'lon':points[-1]['lng'],'heading':heading(points[-2],points[-1])}]
  body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
  raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d
  # The M-40/Aeropuerto path crosses BOTH urban plazas. Alcobendas-only starts
  # after the Aeropuerto plaza. These are independent published open-system fees.
  barrier_count=2 if plaza=='aeropuerto' else 1
  target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceProbeBooth':booth,'expectedGeneralCents':520+barrier_count*60,'expectedViaTCents':460+barrier_count*55,'expectedOpenBarriers':barrier_count},indent=2)+'\n')
  print(name,d['trip']['summary'],flush=True);time.sleep(.6)
