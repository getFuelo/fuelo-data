#!/usr/bin/env python3
"""Retain the operator's special Bilbao–service area–Bilbao journey."""
import json, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'pricing-candidates/ap68-service-area';out.mkdir(exist_ok=True)
# Public city origin/destination, via the one-way return road at the actual
# service-area booth. Through points keep the complete journey in one leg.
locations=[{'lat':43.2568,'lon':-2.9239},
 {'lat':43.19021,'lon':-2.89693,'type':'through'},
 {'lat':43.1903084,'lon':-2.8964218,'type':'through'},
 {'lat':43.2568,'lon':-2.9239}]
body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
name='bilbao-service-bilbao';p=out/(name+'.json')
if not p.exists():
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=60).read()
 d=json.loads(raw);assert d.get('trip'),d
 p.write_bytes(raw)
(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':235,'source':'https://www.arabat.eus/wp-content/uploads/2026/02/26_003-Avasa-AP68-Bilbao_Zaragoza-T26.pdf','publishedJourney':'Bilbao – A. Servicio Arrigorriaga – Bilbao'},ensure_ascii=False,indent=2)+'\n')
print(json.loads(p.read_text())['trip']['summary'])
