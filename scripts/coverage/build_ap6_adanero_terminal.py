#!/usr/bin/env python3
"""Cover the AP-6 free continuation between the Adanero plaza and the A-6.

Run after build_iberpistas_ap61.py, before build_spain_candidate.py. Reads the
snapshot-pinned ways from fetch_ap6_adanero_terminal.py; needs no graph file.
Adds coverage only: no gate, entry, exit or fare changes, so journeys still
settle at the ADANERO cuts and unknown fares stay unknown.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = 'audit/2026-09-16/networks/iberpistas-ap61/adanero-terminal-ways.json'
CANDIDATE = ROOT / 'pricing-candidates/iberpistas-ap61.json'


def main():
    evidence = json.loads((ROOT / EVIDENCE).read_text())
    doc = json.loads(CANDIDATE.read_text())
    net = next(n for n in doc['pricing'] if n['id'] == 'es-ap6-ap51-ap61')
    gates = {g['id'] for g in net['gates']}
    assert {'ADANERO-entry', 'ADANERO-exit'} <= gates
    covered = {w['id'] for w in net['coverageWays']}
    for before, after in evidence['joins'].values():
        # Each chain starts or ends on a way already covered next to ADANERO.
        assert str(before) in covered or str(after) in covered, (before, after)
    added = [w for w in evidence['ways'] if w['id'] not in covered]
    net['coverageWays'] += [{'id': w['id'], 'version': w['version'], 'line': w['line']} for w in added]
    sources = net['evidence'].setdefault('coverageSources', [])
    if EVIDENCE not in sources:
        sources.append(EVIDENCE)
    CANDIDATE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    print(len(added), 'Adanero terminal ways added;', len(net['coverageWays']), 'coverage ways')


if __name__ == '__main__':
    main()
