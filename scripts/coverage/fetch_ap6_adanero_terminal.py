#!/usr/bin/env python3
"""Freeze the AP-6 carriageways between the Adanero plaza and the A-6 merge.

OSM tags these ways toll=yes, so the router reports the tolled span running
~7 km past the ADANERO cuts to the A-6. They carry no booth: the journey has
already settled at the ADANERO gates. The 2026-09-16 graph bbox stopped at
40.897, leaving them outside coverage and every journey through Adanero
unavailable. Ways and nodes are pinned to the graph snapshot so coverage stays
reproducible without the (unretained) graph file.
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = json.loads((ROOT / 'audit/2026-09-16/spain-graph/provenance.json').read_text())['snapshot']
OUT = ROOT / 'audit/2026-09-16/networks/iberpistas-ap61/adanero-terminal-ways.json'
API = 'https://api.openstreetmap.org/api/0.6'
# Northbound after ADANERO-exit (way 1221530432), southbound before
# ADANERO-entry (way 768603931), each in carriageway order.
NORTHBOUND = [768604121, 306797170, 1221529424, 1221529423, 148621809, 148621804]
SOUTHBOUND = [202159363, 148621806, 148621811]
JOINS = {'northbound': (1221530432, 4711088), 'southbound': (1221529422, 768603931)}


def get(path):
    request = urllib.request.Request(API + path, headers={'User-Agent': 'Fuelo-toll-coverage-audit/1.0'})
    return json.loads(urllib.request.urlopen(request, timeout=45).read())['elements']


def at_snapshot(kind, element_id):
    versions = [e for e in get(f'/{kind}/{element_id}/history.json') if e['timestamp'] <= SNAPSHOT]
    assert versions and versions[-1].get('visible', True), (kind, element_id)
    return versions[-1]


def main():
    ways = {}
    for wid in NORTHBOUND + SOUTHBOUND + [w for pair in JOINS.values() for w in pair]:
        ways[wid] = at_snapshot('way', wid)
    for direction, order in (('northbound', NORTHBOUND), ('southbound', SOUTHBOUND)):
        before, after = JOINS[direction]
        chain = [before] + order + [after]
        for a, b in zip(chain, chain[1:]):
            assert ways[a]['nodes'][-1] == ways[b]['nodes'][0], (direction, a, b)
    out = []
    for wid in NORTHBOUND + SOUTHBOUND:
        way = ways[wid]
        tags = way['tags']
        assert tags.get('ref') == 'AP-6' and tags.get('highway') == 'motorway' and tags.get('oneway') == 'yes', wid
        line = []
        for node_id in way['nodes']:
            node = at_snapshot('node', node_id)
            # A booth here would be a charging point, not a free continuation.
            assert node.get('tags', {}).get('barrier') != 'toll_booth', (wid, node_id)
            line.append({'lat': node['lat'], 'lng': node['lon']})
        out.append({'id': str(wid), 'version': way['version'], 'line': line,
                    'direction': 'northbound' if wid in NORTHBOUND else 'southbound'})
    OUT.write_text(json.dumps({
        'snapshot': SNAPSHOT,
        'source': API + ' (way and node history at the graph snapshot)',
        'attribution': '© OpenStreetMap contributors, ODbL 1.0',
        'reason': 'AP-6 carriageways tagged toll=yes between the ADANERO cuts and the A-6 merge; no booth, the OD journey settles at the ADANERO gates.',
        'joins': {k: list(v) for k, v in JOINS.items()},
        'ways': out,
    }, ensure_ascii=False, indent=2) + '\n')
    print(len(out), 'ways,', sum(len(w['line']) for w in out), 'nodes ->', OUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
