#!/usr/bin/env python3
"""Fetch one real Valhalla lane traversal per mapped open-system plaza.

Run explicitly; sequential public-server requests, with request/response evidence.
This never enables country completeness and never calls a paid routing API.
"""
import json,math,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def distance(a,b):return math.hypot((a['lat']-b['lat'])*111195,(a['lng']-b['lng'])*81000)
def heading(a,b):
 lat=math.radians((a['lat']+b['lat'])/2);return round(math.degrees(math.atan2((b['lng']-a['lng'])*math.cos(lat),b['lat']-a['lat']))%360)
def main():
 for family in ['autema','c32','ap15']:
  catalog=json.loads((ROOT/'pricing-candidates'/f'{family}.json').read_text());probes=json.loads((ROOT/'audit/2026-09-16/networks'/family/'lane-probes.json').read_text());out=ROOT/'pricing-candidates'/(family+'-routes');out.mkdir(exist_ok=True)
  for net in catalog['pricing']:
   options=[p for p in probes if p['network']==net['id']];p=min(options,key=lambda p:sum(distance(a,b) for a,b in zip(p['geometry'],p['geometry'][1:])));pts=p['geometry'];name=net['id']+'-traversal';target=out/(name+'.json')
   if target.exists():continue
   body={'locations':[{'lat':pts[0]['lat'],'lon':pts[0]['lng'],'heading':heading(pts[0],pts[1])},{'lat':pts[-1]['lat'],'lon':pts[-1]['lng'],'heading':heading(pts[-2],pts[-1])}],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
   raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=30).read();d=json.loads(raw);target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'sourceProbe':{'booth':p['booth'],'way':p['way'],'versions':p['versions']}},indent=2)+'\n');print(family,name,d.get('trip',{}).get('summary'),flush=True);time.sleep(.5)
if __name__=='__main__':main()
