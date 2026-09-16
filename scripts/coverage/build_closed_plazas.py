#!/usr/bin/env python3
"""Closed-system candidates with explicit source associations for every access."""
import collections
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# zone, booth group, source entry way, entry booth, reversed source direction,
# outside entry node, outside exit node. Published zone names are preserved.
SPECS = {'ap36': {'ref': 'AP-36', 'accesses': [
    ('Troncal Corral Almaguer', 'osm-review-30297630', 183749260, 30299730, False, None, (173086102, -1)),
    ('Troncal San Clemente', 'osm-review-30295021', 435004158, 30295021, False, None, (435004151, -1)),
    ('Lateral Corral Almaguer', 'osm-review-983425201', 24220447, 983425215, False, None, (183927767, -1)),
    ('Quintanar Orden', 'osm-review-983425415', 24336301, 983425538, False, None, (183927756, -1)),
    ('Pedernoso', 'osm-review-983425493', 84657479, 983425894, False, None, (183927749, -1)),
    ('Mota Cuervo', 'osm-review-983425503', 82101660, 983425503, False, (82101660, 0), (82101660, 0)),
]}, 'ap7-cartagena-vera': {'ref': 'AP-7', 'bbox': [37.19, -1.95, 37.70, -.99], 'accesses': [
    ('Cartagena', 'osm-review-186853438', 384760606, 295558078, False, None, (1317470846, -1)),
    ('Las Palas', 'osm-review-186852042', 131391524, 186852042, False, None, (769373449, -1)),
    ('Mazarrón', 'osm-review-264688958', 769371991, 12195595280, False, None, (98864421, -1)),
    ('Ramonete', 'osm-review-1535236954', 140645747, 1535236954, False, None, (140645746, -1)),
    ('Cabo Cope', 'osm-review-1454017078', 140645745, 1454017080, False, None, (132120099, -1)),
    ('Águilas', 'osm-review-2431640698', 1318528135, 2431640698, False, None, (169927310, -1)),
    ('Pulpí', 'osm-review-1537685703', 1319109532, 1537685713, False, None, (1319109533, -1)),
    ('Cuevas del Almanzora', 'osm-review-3100395406', 179755312, 3100395406, False, None, (179755324, -1)),
    ('Vera', 'osm-review-264694281', 1319348645, 299818774, False, None, (180019164, -1)),
]}}

with gzip.open(ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz', 'rt') as f:
    graph = json.load(f)
review = json.loads((ROOT / 'audit/2026-09-16/spain-graph/access-review.json').read_text())
groups = {g['id']: g for g in review['groups']}
ways = {w['id']: w for w in graph['ways']}
nodes = graph['nodes']
at = collections.defaultdict(set)
for way in ways.values():
    for node in way['nodes']:
        at[node].add(way['id'])

def point(node):
    lat, lng = nodes[str(node)]
    return {'lat': lat, 'lng': lng}

for family, spec in SPECS.items():
    bounds = spec.get('bbox', [-90, -180, 90, 180])
    inside = lambda w: all(bounds[0] <= nodes[str(n)][0] <= bounds[2] and bounds[1] <= nodes[str(n)][1] <= bounds[3] for n in w['nodes'])
    selected = {w['id'] for w in ways.values() if w['tags'].get('ref') == spec['ref'] and inside(w)}
    for _ in range(20):
        added = set()
        for wid in selected:
            for node in ways[wid]['nodes']:
                for other in at[node] - selected:
                    tags = ways[other]['tags']
                    if tags.get('ref') in (None, spec['ref']) and tags.get('highway') == 'motorway_link' and inside(ways[other]):
                        added.add(other)
        selected.update(added)
        if not added:
            break
    gates, locations, evidence = [], {}, []
    for zone, groupid, wid, booth, reverse, outside_entry, outside_exit in spec['accesses']:
        way, group = ways[wid], groups[groupid]
        i = way['nodes'].index(booth)
        a = point(way['nodes'][max(0, i-1)])
        b = point(way['nodes'][min(len(way['nodes'])-1, i+1)])
        if reverse:
            a, b = b, a
        center = {k: sum(point(n)[k] for n in group['pointIds']) / len(group['pointIds']) for k in ('lat', 'lng')}
        cos = math.cos(math.radians(center['lat']))
        dx, dy = (b['lng']-a['lng'])*cos, b['lat']-a['lat']
        length = math.hypot(dx, dy)
        assert length > 0
        px, py = -dy/length, dx/length
        projection = [(point(n)['lng']-center['lng'])*cos*px + (point(n)['lat']-center['lat'])*py for n in group['pointIds']]
        line = [{'lat': center['lat']+v*py, 'lng': center['lng']+v*px/cos} for v in (min(projection)-6/111195, max(projection)+6/111195)]
        cross = lambda p: (line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat']) - (line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
        positive = cross(b) > cross(a)
        for role in ('entry', 'exit'):
            gates.append({'id': zone+'-'+role, 'line': line, 'direction': 'positive' if (positive if role=='entry' else not positive) else 'negative'})
        entry_way, entry_index = outside_entry or (wid, 0)
        exit_way, exit_index = outside_exit
        locations[zone] = {'entry': point(ways[entry_way]['nodes'][entry_index]), 'exit': point(ways[exit_way]['nodes'][exit_index])}
        evidence.append({'zone': zone, 'reviewGroup': groupid, 'booths': group['pointIds'],
                         'entryWay': wid, 'version': way['version'], 'entryBooth': booth,
                         'reverseEntryWay': reverse, 'line': line})
    refs = json.loads((ROOT / f'pricing-candidates/{family}-tariffs.json').read_text())
    fares = [{'from': r['from']+'-entry', 'to': r['to']+'-exit', 'tariff': r['tariff']} for r in refs['ods']]
    assert len(fares) == len(locations)*(len(locations)-1)
    net = {'id': 'es-'+family, 'tollId': 'es-'+family, 'validFrom': refs['validFrom'], 'validThrough': refs['validThrough'],
           'timeZone': 'Europe/Madrid', 'gates': gates,
           'pricing': {'kind': 'od', 'chargedAt': 'exit', 'entries': [g['id'] for g in gates if g['id'].endswith('-entry')],
                       'exits': [g['id'] for g in gates if g['id'].endswith('-exit')], 'fares': fares},
           'coverageWays': [{'id': str(wid), 'version': ways[wid]['version'], 'line': [point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)],
           'evidence': {'checked': '2026-09-16', 'tariffSources': [refs['source']], 'geometrySource': 'https://www.openstreetmap.org/copyright'}}
    toll = next(t for t in json.loads((ROOT / 'tolls-es.json').read_text())['tolls'] if t['id'] == 'es-'+family)
    doc = {'schema': 2, 'generated': '2026-09-16', 'currency': 'EUR', 'complete': False, 'tolls': [toll], 'pricing': [net],
           'notes_global': 'Disabled closed-system candidate. Explicit source-way access associations and published OD rows; route checks are required separately. © OpenStreetMap contributors.'}
    (ROOT / f'pricing-candidates/{family}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
    out = ROOT / f'audit/2026-09-16/networks/{family}'
    out.mkdir(exist_ok=True)
    (out / 'provenance.json').write_text(json.dumps({'source': '../../spain-graph/provenance.json', 'gates': evidence, 'probeLocations': locations, 'status': 'candidate_pending_real_routes'}, ensure_ascii=False, indent=2)+'\n')
    print(family, len(gates), 'gates', len(fares), 'OD fares', len(selected), 'ways')
