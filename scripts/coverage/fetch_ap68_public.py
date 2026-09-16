#!/usr/bin/env python3
"""Retained public Alagón destination, separate from the committed exit ramp."""
import json,gzip,urllib.request,urllib.parse
from pathlib import Path
R=Path(__file__).resolve().parents[2];g=json.load(gzip.open(R/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
original=json.loads((R/'pricing-candidates/ap68-routes/ZARAGOZA--ALAGÓN pk 272-request.json').read_text());body=original['request'];lat,lon=g['nodes']['46602143'];body['locations'][-1]={'lat':lat,'lon':lon}
out=R/'pricing-candidates/ap68-public-approaches';out.mkdir(exist_ok=True)
raw=(out/'ZARAGOZA--ALAGON.json').read_bytes() if (out/'ZARAGOZA--ALAGON.json').exists() else urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d
(out/'ZARAGOZA--ALAGON.json').write_bytes(raw)
(out/'ZARAGOZA--ALAGON-request.json').write_text(json.dumps({'request':body,'publicDestinationNode':46602143,'expectedPublishedJourney':['ZARAGOZA','ALAGÓN pk 275'],'expectedCents':285,'notes':'Public A-68 destination beyond the Alagón 272 one-way exit, without forcing entry into that exit ramp.'},ensure_ascii=False,indent=2)+'\n');print(d['trip']['summary'])
