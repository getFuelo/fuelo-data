#!/usr/bin/env python3
"""Retain small live OSM extracts for unresolved local access classification.

These are separate evidence from the dated country PBF, never silently merged
into tariff geometry. Downloading a map is not a fare or scope decision.
"""
import datetime,hashlib,json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];folder=ROOT/'audit/2026-09-16/access-context';folder.mkdir(exist_ok=True)
report=json.loads((ROOT/'audit/2026-09-16/access-inventory-reconciliation.json').read_text())
ids=[3196925975,11434681632,11508593094,8893218317,1129314542,8380303594]
for id in ids:
 p=next(p for p in report['points'] if p['node']==id);name=str(id);target=folder/(name+'.osm')
 if target.exists():continue
 lat,lng=p['lat'],p['lng'];bbox=f'{lng-.001},{lat-.001},{lng+.001},{lat+.001}'
 url='https://api.openstreetmap.org/api/0.6/map?bbox='+bbox
 raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Fuelo-toll-coverage-audit/1.0'}),timeout=45).read()
 target.write_bytes(raw);(folder/(name+'.json')).write_text(json.dumps({'node':id,'url':url,'retrieved':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n')
 print(id,len(raw),flush=True);time.sleep(1)
