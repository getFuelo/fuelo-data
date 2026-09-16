#!/usr/bin/env python3
"""Check candidate integrity offline. --release additionally enforces review gates.

Passing the default checks is NOT a certification of Spain route coverage.
"""
import argparse, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def check():
    errors=[]; count=0
    def require(ok, message):
        if not ok: errors.append(message)
    def amounts(value, path):
        if isinstance(value,dict):
            if 'maxCents' in value:
                require(type(value.get('cents')) is int and type(value['maxCents']) is int and value['maxCents']>=value['cents'],f'{path}: invalid amount interval')
            for k,v in value.items():
                if k in ('baseCents','cents','maxCents','peakCents','valleyCents'):
                    require(type(v) is int and v>=0,f'{path}.{k}: invalid cents')
                amounts(v,f'{path}.{k}')
        elif isinstance(value,list):
            for i,v in enumerate(value): amounts(v,f'{path}[{i}]')
    for path in sorted((ROOT/'pricing-candidates').glob('*.json')):
        if path.name in ('coverage-status.json','m12-geometry-evidence.json'):continue
        d=json.loads(path.read_text());count+=1
        require(d.get('complete') is False,f'{path.name}: development data cannot be complete')
        amounts(d,path.name)
        if d.get('schema') not in (2,3):
            require(d.get('kind')=='tariff-reference',f'{path.name}: unknown candidate kind')
            require(bool(d.get('source')),f'{path.name}: missing tariff source')
            continue
        if d['schema']==2:
            def no_extended_fields(value):
                if isinstance(value,dict):
                    require(not {'maxCents','freeTravelSource','excludes'} & value.keys(),path.name+': schema 3 field in schema 2')
                    for child in value.values():no_extended_fields(child)
                elif isinstance(value,list):
                    for child in value:no_extended_fields(child)
            no_extended_fields(d)
        toll_ids={t['id'] for t in d['tolls']}; nets=d['pricing']
        require({n['tollId'] for n in nets}==toll_ids,f'{path.name}: missing pricing network')
        require(len({n['id'] for n in nets})==len(nets),f'{path.name}: duplicate networks')
        for n in nets:
            prefix=path.name+':'+n['id'];gates=n['gates'];ids=[g['id'] for g in gates]
            require(bool(gates) and len(set(ids))==len(ids),prefix+': invalid gate identities')
            require(bool(n.get('coverageWays')),prefix+': missing road coverage')
            require(bool(n.get('evidence',{}).get('tariffSources')),prefix+': missing provenance')
            if 'avoidanceGateIds' in n:
                avoidance=n['avoidanceGateIds']
                require(bool(avoidance) and len(set(avoidance))==len(avoidance) and set(avoidance)<=set(ids),prefix+': invalid avoidance gates')
            for g in gates:
                require(len(g['line'])==2 and g['line'][0]!=g['line'][1],prefix+': invalid cross-section')
                for p in g['line']:
                    require(all(math.isfinite(p[k]) for k in ('lat','lng')) and abs(p['lat'])<=90 and abs(p['lng'])<=180,prefix+': invalid coordinate')
            if n['pricing']['kind']=='gates':
                require(set(n['pricing']['fares'])==set(ids),prefix+': missing or orphan gate fare')
            elif n['pricing']['kind']=='od':
                pricing=n['pricing'];entries=pricing['entries'];exits=pricing['exits']
                require(not set(entries)&set(exits) and set(entries+exits)==set(ids),prefix+': invalid OD roles')
                pairs=[(f['from'],f['to']) for f in pricing['fares']]
                require(len(set(pairs))==len(pairs),prefix+': duplicate OD fare')
                require(all(a in entries and b in exits for a,b in pairs),prefix+': orphan OD fare')
                require(pricing['chargedAt'] in ('entry','exit'),prefix+': invalid charge timing')
            else:
                require(False,prefix+': unsupported pricing model')
    manifest=json.loads((ROOT/'pricing-candidates/coverage-status.json').read_text()) if (ROOT/'pricing-candidates/coverage-status.json').exists() else None
    if manifest:
        expected={t['id'] for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls']}
        require({r['catalogId'] for r in manifest['entries']}==expected,'Status must cover every current ES catalog entry')
        for row in manifest['entries']:
            for file in row['tariffArtifacts']+row['geometryCandidates']:
                require((ROOT/file).is_file(),row['catalogId']+': missing '+file)
    return errors,count

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');args=parser.parse_args()
    errors,count=check()
    if args.release:
        status=json.loads((ROOT/'pricing-candidates/coverage-status.json').read_text())
        if status.get('complete') is not True:errors.append('Spain coverage manifest is not complete.')
        for row in status['entries']:
            if row.get('ready') is not True:errors.append(row['catalogId']+': not ready for release.')
        country=json.loads((ROOT/'tolls-es.json').read_text())
        if country.get('complete') is not True or country.get('schema') not in (2,3):
            errors.append('Served Spain catalog is not a complete supported pricing dataset.')
        errors.extend(status['nationalBlockers'])
        errors.extend(row['catalogId']+': '+b for row in status['entries'] for b in row['blockers'])
    if errors:
        print('\n'.join(errors));raise SystemExit(1)
    print(f'{count} candidate JSON files checked; development integrity only, not national coverage.')
