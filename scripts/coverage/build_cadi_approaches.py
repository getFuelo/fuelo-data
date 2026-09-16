#!/usr/bin/env python3
"""Add the retained GIV-4034 entrance ramp used by Puigcerdà–Berga.

This connector is outside the C-16 relation used by the original builder. It
adds source geometry, not a gate, tariff or wider matching tolerance.
"""
import gzip
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz'
graph = json.loads(gzip.decompress(source.read_bytes()))
way = next(w for w in graph['ways'] if w['id'] == 372179846)
assert way['tags']['ref'] == 'GIV-4034' and way['tags']['highway'] == 'trunk_link'
path = ROOT / 'pricing-candidates/cadi.json'
catalog = json.loads(path.read_text())
network = catalog['pricing'][0]
known_way_ids = {x['id'] for x in network['coverageWays']}
known_nodes = {n for w in graph['ways'] if str(w['id']) in known_way_ids for n in w['nodes']}
assert any(n in known_nodes for n in [way['nodes'][0],way['nodes'][-1]]), 'Connector no longer touches the verified corridor'
line = [{'lat':graph['nodes'][str(n)][0],'lng':graph['nodes'][str(n)][1]} for n in way['nodes']]
network['coverageWays'] = [w for w in network['coverageWays'] if w['id'] != str(way['id'])]
network['coverageWays'].append({'id':str(way['id']),'version':way['version'],'line':line})
path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
evidence = {'checked':'2026-09-16','source':str(source.relative_to(ROOT)),
            'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'way':way,'finding':'Puigcerdà–Berga enters via GIV-4034; eight vertices of the provider toll maneuver were outside the original C-16 relation.',
            'regression':'pricing-candidates/general-acceptance/cadi-south-general.json',
            'change':'Include the versioned connected approach. Existing toll gate, 1456-cent general fare and 12m tolerance are unchanged.'}
(ROOT / 'audit/2026-09-16/networks/cadi/northern-approach.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print('Added Cadí GIV-4034 approach',way['id'],'version',way['version'])
