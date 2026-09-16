#!/usr/bin/env python3
"""Reconcile the full retained booth inventory with source-backed catalog inputs.

Source references and catalog road membership establish traceability, not lane detection or route
pricing. Unassigned points stay open; neither proximity nor a road number is
sufficient to assign a fare. Excluded points retain the exact evidence used.
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'audit/2026-09-16'
HGV_SOURCES = {
    'N-240': 'https://interbiak.bizkaia.eus/es/pago-por-uso-ppu',
    'N-I': 'https://www.euskadi.eus/bopv2/datos/2023/01/2300167a.shtml',
    'N-1': 'https://www.euskadi.eus/bopv2/datos/2023/01/2300167a.shtml',
    'A-15': 'https://www.euskadi.eus/bopv2/datos/2023/01/2300167a.shtml',
}


def source_nodes(value):
    """Only explicit OSM node/booth fields, never incidental numbers or ways."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ('booth', 'node') and str(child).isdigit():
                yield int(child)
            elif key == 'booths' and isinstance(child, list):
                yield from (int(x) for x in child if str(x).isdigit())
            else:
                yield from source_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_nodes(child)


def explicit_exclusion(point, ways):
    tags = point['tags']
    if tags.get('amenity') == 'parking_entrance':
        return 'parking', 'node amenity=parking_entrance'
    if ways and all(w['tags'].get('service') == 'parking_aisle' for w in ways):
        return 'parking', 'all incident source ways are parking aisles'
    if tags.get('access') in ('private', 'no') and tags.get('motorcar', tags.get('motor_vehicle')) != 'yes':
        return 'restricted_access', 'node access=' + tags['access']
    if ways and all(w['tags'].get('access') in ('private', 'no') and w['tags'].get('motorcar', w['tags'].get('motor_vehicle')) != 'yes' for w in ways):
        return 'restricted_access', 'all incident source ways prohibit public access'
    if ways and all(w['tags'].get('highway') in ('footway', 'path', 'steps') and
                    w['tags'].get('motor_vehicle') != 'yes' for w in ways):
        return 'non_motor_road', 'all incident source ways are pedestrian/path ways'
    # Legal scope is restricted to the stated road and province, not all tags
    # mentioning HGV (a road could charge cars as well).
    refs = {ref for w in ways for ref in w['tags'].get('ref', '').split(';')}
    if 43.02 < point['lat'] < 43.27 and -2.85 < point['lng'] < -2.65 and 'N-240' in refs:
        return 'heavy_goods_only', HGV_SOURCES['N-240']
    if 42.9 < point['lat'] < 43.24 and -2.3 < point['lng'] < -1.9:
        road = next((r for r in ('N-I', 'N-1', 'A-15') if r in refs), None)
        if road:
            return 'heavy_goods_only', HGV_SOURCES[road]
    return None


def intersects(a, b, c, d):
    """Strict transverse segment crossing; collinearity is not evidence."""
    def side(p, q, r):
        return (q[1]-p[1])*(r[0]-p[0]) - (q[0]-p[0])*(r[1]-p[1])
    ab_c, ab_d, cd_a, cd_b = side(a,b,c), side(a,b,d), side(c,d,a), side(c,d,b)
    return ab_c*ab_d <= 0 and cd_a*cd_b <= 0 and (ab_c != 0 or ab_d != 0) and (cd_a != 0 or cd_b != 0)


def main():
    refs = collections.defaultdict(set)
    sources = []
    manifest = json.loads((AUDIT / 'spain-integration-sources.json').read_text())
    catalog_path = ROOT / 'pricing-candidates/spain-integration.json'
    catalog = json.loads(catalog_path.read_text())
    sources.append({'path': str(catalog_path.relative_to(ROOT)), 'sha256': hashlib.sha256(catalog_path.read_bytes()).hexdigest()})
    way_networks = collections.defaultdict(list)
    for network in catalog['pricing']:
        for way in network['coverageWays']:
            way_networks[str(way['id'])].append(network)
    # Shared systems retain provenance in both their component and assembled
    # networks. References are evidence links only, not certification.
    for file in sorted((AUDIT / 'networks').glob('*/provenance.json')):
        rel = str(file.relative_to(ROOT))
        sources.append({'path': rel, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        for node in source_nodes(json.loads(file.read_text())):
            refs[node].add(rel)
    decisions_file = AUDIT / 'access-scope-decisions.json'
    decisions = json.loads(decisions_file.read_text())
    sources.append({'path': str(decisions_file.relative_to(ROOT)), 'sha256': hashlib.sha256(decisions_file.read_bytes()).hexdigest()})
    overrides = {node: decision for decision in decisions['decisions'] for node in decision['nodes']}
    assert len(overrides) == sum(len(d['nodes']) for d in decisions['decisions']), 'Duplicate node scope decisions'
    rows = []
    groups = json.loads((AUDIT / 'spain-graph/access-review.json').read_text())['groups']
    for region in ('spain', 'canary-islands'):
        file = AUDIT / (region + '-graph') / 'graph.json.gz'
        sources.append({'path': str(file.relative_to(ROOT)), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        graph = json.loads(gzip.decompress(file.read_bytes()))
        incident = collections.defaultdict(list)
        for way in graph['ways']:
            for node in way['nodes']:
                incident[node].append(way)
        for point in graph['points']:
            if point['tags'].get('barrier') != 'toll_booth' and point['tags'].get('highway') != 'toll_gantry':
                continue
            ways = incident[point['id']]
            evidence = sorted(refs[point['id']]) if region == 'spain' else []
            road_evidence = sorted({network['id'] for way in ways for network in way_networks[str(way['id'])]})
            geometry_evidence = []
            for way in ways:
                for network in way_networks[str(way['id'])]:
                    coordinates = [graph['nodes'][str(n)] for n in way['nodes']]
                    for gate in network['gates']:
                        a, b = ([p['lat'], p['lng']] for p in gate['line'])
                        if any(intersects(a, b, c, d) for c, d in zip(coordinates, coordinates[1:])):
                            geometry_evidence.append({'network': network['id'], 'gate': gate['id'], 'way': way['id']})
            decision = overrides.get(point['id'])
            exclusion = (decision['category'], decision['source']) if decision else explicit_exclusion(point, ways)
            status = 'source_linked' if evidence else 'catalog_geometry_linked' if geometry_evidence else 'scope_excluded' if exclusion else 'catalog_road_linked' if road_evidence else 'needs_review'
            rows.append({
                'region': region, 'node': point['id'], 'version': point['version'],
                'lat': point['lat'], 'lng': point['lng'], 'tags': point['tags'],
                'incidentWays': [{'id': w['id'], 'version': w['version'], 'tags': w['tags']} for w in ways],
                'status': status, 'catalogSourceEvidence': evidence,
                'catalogGeometryEvidence': geometry_evidence,
                'catalogRoadEvidence': road_evidence,
                'scopeEvidence': {'category': exclusion[0], 'basis': exclusion[1], **({'decision': decision['id'], 'reason': decision['reason']} if decision else {})} if exclusion else None,
            })
    by_node = {r['node']: r for r in rows if r['region'] == 'spain'}
    group_rows = []
    for group in groups:
        counts = dict(collections.Counter(by_node[n]['status'] for n in group['pointIds']))
        group_rows.append({**group, 'pointStatusCounts': counts,
                           'reviewStatus': 'needs_review' if counts.get('needs_review') else 'inventory_reconciled',
                           'routePricingCertified': False})
    report = {'checked': '2026-09-16', 'complete': False,
              'scope': 'Light passenger car public-road tolls; exact source-linked nodes are not lane/route certificates. Tourist access fees remain open unless specifically evidenced.',
              'counts': dict(collections.Counter(r['status'] for r in rows)),
              'groupCounts': dict(collections.Counter(g['reviewStatus'] for g in group_rows)),
              'sources': sources, 'points': rows, 'groups': group_rows}
    target = AUDIT / 'access-inventory-reconciliation.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'points': len(rows), 'counts': report['counts'], 'groups': report['groupCounts']}, indent=2))


if __name__ == '__main__':
    main()
