#!/usr/bin/env python3
"""Retain free C-16/C-55 geometry inside Valhalla's coarse toll maneuvers.

Run after build_fixed_networks.py. This does not add gates or tariffs. The
existing Cadí/AUTEMA gates still decide payment; no route geometry is invented.
"""
import argparse, hashlib, json
from pathlib import Path
import osmium
ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'https://web.manresa.cat/web/menu/6629-comment-se-rendre-a-manresa'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pbf', type=Path)
    args = parser.parse_args()
    ways, nodes = {}, {}
    class Roads(osmium.SimpleHandler):
        def way(self, w):
            tags = dict(w.tags)
            if tags.get('ref') in ('C-16', 'C-55') and tags.get('highway') and tags.get('toll') != 'yes':
                ways[w.id] = {'id': str(w.id), 'version': w.version, 'nodes': [n.ref for n in w.nodes], 'tags': tags}
    Roads().apply_file(str(args.pbf), filters=[osmium.filter.KeyFilter('ref')])
    needed = {n for w in ways.values() for n in w['nodes']}
    class Nodes(osmium.SimpleHandler):
        def node(self, n):
            nodes[n.id] = {'lat': n.location.lat, 'lng': n.location.lon}
    Nodes().apply_file(str(args.pbf), filters=[osmium.filter.IdFilter(needed)])
    digest = hashlib.sha256()
    with args.pbf.open('rb') as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b''):
            digest.update(chunk)
    selected = []
    for w in ways.values():
        line = [nodes[n] for n in w['nodes']]
        # North of AUTEMA (C-16) and the conventional alternative (C-55).
        south, north = (41.77, 42.12) if w['tags']['ref'] == 'C-16' else (41.50, 41.80)
        if not all(south <= p['lat'] <= north and 1.70 <= p['lng'] <= 1.95 for p in line):
            continue
        selected.append({**w, 'line': line})
    target = ROOT/'pricing-candidates/cadi.json'
    doc = json.loads(target.read_text())
    network = doc['pricing'][0]
    original = {w['id']: w for w in network['coverageWays']}
    for w in selected:
        original.setdefault(w['id'], {k: w[k] for k in ('id', 'version', 'line')} | {'freeTravelSource': SOURCE})
    network['coverageWays'] = list(original.values())
    network['evidence']['tariffSources'] = list(dict.fromkeys(network['evidence']['tariffSources'] + [SOURCE]))
    doc['schema'] = 3
    target.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
    out = ROOT/'audit/2026-09-16/networks/cadi/free-corridor.json'
    out.write_text(json.dumps({'source': SOURCE, 'snapshot': args.pbf.name, 'sha256': digest.hexdigest(), 'method': 'Versioned non-tolled C-16 north of AUTEMA and C-55 conventional road. Covers free portions of mixed toll maneuvers; payment remains determined by existing plaza gates.', 'ways': [{k: w[k] for k in ('id','version','tags')} for w in selected]}, ensure_ascii=False, indent=2)+'\n')
    print(len(selected), 'free corridor source ways')
if __name__ == '__main__':
    main()
