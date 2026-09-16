#!/usr/bin/env python3
"""Probe the versioned northbound cash lane missing from the reference filter."""
import json,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];folder=ROOT/'pricing-candidates/ag55-extra-lanes';folder.mkdir(exist_ok=True)
source=json.loads((ROOT/'pricing-candidates/ag55-routes/Paiosaco--Arteixo-request.json').read_text());body=source['request'];body['locations'].insert(1,{'lat':43.2761996,'lon':-8.5273796,'type':'through','radius':2})
name='Paiosaco--Arteixo-cash';response=folder/(name+'.json')
if not response.exists():
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;response.write_bytes(raw)
(folder/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':source['expectedGeneralCents'],'sourceWay':257088583,'sourceWayVersion':5,'booth':14073595984,'expectedGates':['Paiosaco-entry','Arteixo-exit']},indent=2)+'\n')
print(name,json.loads(response.read_text())['trip']['summary'])
