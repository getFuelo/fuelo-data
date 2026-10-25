#!/usr/bin/env python3
"""Apply the frozen per-area evidence to the pricing candidates.

Graph-free and offline. Run before build_spain_candidate.py. Idempotent.
- audit/area-coverage/*.json: coverage only (no gate, entry, exit or fare
  changes), so journeys settle at the existing gates and unknown fares stay
  unknown.
- audit/area-gates/*.json: a main-line plaza line widened over its booth lanes
  (same centre and orientation, so crossing direction is unchanged). Applied
  only over the exact line it was measured from.
"""
import ast, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The families build_spain_candidate.py assembles, read from that script.
FAMILIES = ast.literal_eval(re.search(r'^FAMILIES=(\[.*\])$', (ROOT / 'scripts/coverage/build_spain_candidate.py').read_text(), re.M).group(1))


def network_file(network, evidence_path):
    files = [p for p in (ROOT / f'pricing-candidates/{f}.json' for f in FAMILIES)
             if any(n['id'] == network for n in json.loads(p.read_text())['pricing'])]
    assert len(files) == 1, (evidence_path.name, network, files)
    doc = json.loads(files[0].read_text())
    return files[0], doc, next(n for n in doc['pricing'] if n['id'] == network)


def main():
    total = 0
    for evidence_path in sorted((ROOT / 'audit/area-coverage').glob('*.json')):
        evidence = json.loads(evidence_path.read_text())
        rel = str(evidence_path.relative_to(ROOT))
        path, doc, net = network_file(evidence['network'], evidence_path)
        files = [path]
        covered = {w['id'] for w in net['coverageWays']}
        added = [w for w in evidence['ways'] if w['id'] not in covered]
        net['coverageWays'] += [{'id': w['id'], 'version': w['version'], 'line': w['line']} for w in added]
        sources = net['evidence'].setdefault('coverageSources', [])
        if rel not in sources: sources.append(rel)
        files[0].write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        total += len(added)
        print(f"{evidence['area']}: {len(added)} ways added to {evidence['network']} ({files[0].name})")
    print(total, 'area coverage ways added')
    for evidence_path in sorted((ROOT / 'audit/area-gates').glob('*.json')):
        evidence = json.loads(evidence_path.read_text())
        path, doc, net = network_file(evidence['network'], evidence_path)
        gate = next(g for g in net['gates'] if g['id'] == evidence['gate'])
        if gate['line'] == evidence['line']: continue
        assert gate['line'] == evidence['previousLine'], f"{evidence_path.name}: gate changed since it was measured"
        gate['line'] = evidence['line']
        rel = str(evidence_path.relative_to(ROOT))
        sources = net['evidence'].setdefault('gateSources', [])
        if rel not in sources: sources.append(rel)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        print(f"{evidence['name']}: {evidence['network']}/{evidence['gate']} widened to ±{evidence['halfLengthM']} m")


if __name__ == '__main__':
    main()
