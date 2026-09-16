#!/usr/bin/env python3
"""Build the AP-71 OD candidate using versioned physical plazas and entry cuts."""
import collections
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
with gzip.open(ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz', 'rt') as f:
    graph = json.load(f)
ways = {w['id']: w for w in graph['ways']}
nodes = graph['nodes']
at = collections.defaultdict(set)
for way in ways.values():
    for node in way['nodes']:
        at[node].add(way['id'])
selected = {w['id'] for w in ways.values() if w['tags'].get('ref') == 'AP-71'}
# The provider's tolled maneuver starts on the public N-6 roundabout.
# Preserve those approach geometries separately from the paid OD context.
selected.add(62298372)
for _ in range(16):
    added = set()
    for wid in selected:
        for node in ways[wid]['nodes']:
            for other in at[node] - selected:
                tags = ways[other]['tags']
                if tags.get('ref') in (None, 'AP-71') and (tags.get('toll') == 'yes' or tags.get('highway') == 'motorway_link') and tags.get('highway') in ('motorway', 'motorway_link'):
                    added.add(other)
    selected.update(added)
    if not added:
        break

# These three connected links lead exclusively north into AP-66. Expanding
# reference-less links from the common Leon interchange must not claim them
# as AP-71 OD travel. Retain the public/free approaches separately below.
ap66_links = {4869445, 34038866, 306889014}
selected.difference_update(ap66_links)

def point(node):
    lat, lng = nodes[str(node)]
    return {'lat': lat, 'lng': lng}

gates, evidence, locations = [], [], {}

def add(zone, role, wid, node, half=8, reverse=False):
    way = ways[wid]
    i = way['nodes'].index(node)
    a, b = point(way['nodes'][i - 1]), point(way['nodes'][i + 1])
    center = point(node)
    cos = math.cos(math.radians(center['lat']))
    dx, dy = (b['lng'] - a['lng']) * cos, b['lat'] - a['lat']
    norm = math.hypot(dx, dy)
    px, py = -dy / norm, dx / norm
    line = [{'lat': center['lat'] + v * py / 111195,
             'lng': center['lng'] + v * px / 111195 / cos} for v in (-half, half)]
    cross = lambda p: (line[1]['lng'] - line[0]['lng']) * (p['lat'] - line[0]['lat']) - (line[1]['lat'] - line[0]['lat']) * (p['lng'] - line[0]['lng'])
    positive = cross(b) > cross(a)
    if reverse:
        positive = not positive
    gid = zone + '-' + role
    gates.append({'id': gid, 'line': line, 'direction': 'positive' if positive else 'negative'})
    evidence.append({'gate': gid, 'way': wid, 'version': way['version'], 'node': node,
                     'halfWidthMeters': half, 'reverseSourceWay': reverse})

# Terminal entry cuts precede the first exit divergence on the opposite
# carriageway. A cut beside the booth would miss the adjacent-access trip.
# Likewise, terminal exits follow the final ramp merge: adjacent trips pay
# at their ramp plaza and do not cross the mainline collection booth.
add('León', 'exit', 202458085, 487277293)
add('León', 'entry', 768796262, 2316217167)
add('Astorga', 'exit', 202458086, 48221517)
add('Astorga', 'entry', 768796574, 487256789)
locations['León'] = {'entry': point(ways[768796262]['nodes'][0]), 'exit': point(2316217193)}
locations['Astorga'] = {'entry': point(ways[768796574]['nodes'][0]), 'exit': point(487256843)}
for zone, wid, booth, outside in [
    ('Villadangos', 545291458, 48221137, 48221149),
    ('Hospital de Orbigo', 545554589, 48221647, 736801069),
]:
    # These two-way source ways run from the tolled network towards the public road.
    add(zone, 'entry', wid, booth, reverse=True)
    add(zone, 'exit', wid, booth)
    locations[zone] = {'entry': point(outside), 'exit': point(outside)}

refs = json.loads((ROOT / 'pricing-candidates/ap71-tariffs.json').read_text())
fares = []
for row in refs['ods']:
    base = row['tariff']['baseCents']
    night = row['tariff']['bands'][0]['cents']
    # Monthly trip rank is unknown. The operator applies a 0..50% rebate
    # to the paid day/night tariff. Floor only the lower interval bound;
    # this is not a claim about the operator's half-cent rounding rule.
    tariff = {'baseCents': base, 'bands': [
        {'cents': night, 'minutes': [1380, 420], 'excludes': ['payment:via-t']},
        {'cents': base // 2, 'maxCents': base, 'minutes': [420, 1380], 'requires': ['payment:via-t']},
        {'cents': night // 2, 'maxCents': night, 'minutes': [1380, 420], 'requires': ['payment:via-t']},
    ]}
    for a, b in [(row['from'], row['to']), (row['to'], row['from'])]:
        fares.append({'from': a + '-entry', 'to': b + '-exit', 'tariff': tariff})
assert len(fares) == 12
net = {'id': 'es-ap71', 'tollId': 'es-ap71', 'validFrom': refs['validFrom'],
       'validThrough': refs['validThrough'], 'timeZone': 'Europe/Madrid', 'gates': gates,
       'pricing': {'kind': 'od', 'chargedAt': 'exit', 'entries': [g['id'] for g in gates if g['id'].endswith('-entry')],
                   'exits': [g['id'] for g in gates if g['id'].endswith('-exit')], 'fares': fares},
       'coverageWays': [{'id': str(wid), 'version': ways[wid]['version'], 'line': [point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)],
       'evidence': {'checked': '2026-09-16', 'tariffSources': [refs['source'], 'https://www.autopistas.com/descuento/cliente-frecuente-4/'], 'geometrySource': 'https://www.openstreetmap.org/copyright'}}
for way in net['coverageWays']:
    source = ways[int(way['id'])]
    if source['tags'].get('toll') != 'yes' and source['tags'].get('highway') != 'motorway':
        way['freeTravelSource'] = 'https://www.openstreetmap.org/way/' + way['id'] + '/history'
net['avoidanceGateIds'] = net['pricing']['entries']
toll = next(t for t in json.loads((ROOT / 'tolls-es.json').read_text())['tolls'] if t['id'] == 'es-ap71')
doc = {'schema': 3, 'generated': '2026-09-16', 'currency': 'EUR', 'complete': False,
       'tolls': [toll], 'pricing': [net], 'notes_global': 'Disabled AP-71 OD candidate. General day/night reference fares exclude rebates; Via-T with unknown monthly trip rank preserves a 50..100 percent interval. Physical-card rebates require a separate explicit profile. © OpenStreetMap contributors.'}
(ROOT / 'pricing-candidates/ap71.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
out = ROOT / 'audit/2026-09-16/networks/ap71'
out.mkdir(exist_ok=True)
(out / 'provenance.json').write_text(json.dumps({'source': '../../spain-graph/provenance.json', 'gates': evidence, 'probeLocations': locations, 'coverageAssignedToAp66': sorted(ap66_links), 'status': 'candidate_pending_real_routes'}, ensure_ascii=False, indent=2) + '\n')
print(len(gates), 'gates', len(fares), 'directed OD fares', len(selected), 'ways')
