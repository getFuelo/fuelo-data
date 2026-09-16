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
        if d.get('schema') not in (2,3,4,5):
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
        if 'unresolvedPassages' in d:
            passages=d['unresolvedPassages'];require(d['schema']==5 and bool(passages),path.name+': unresolved passages require schema 5')
            require(len({p['id'] for p in passages})==len(passages),path.name+': duplicate unresolved passages')
            for passage in passages:
                require(passage['tollId'] in toll_ids and passage['source'].startswith('https://') and passage['checked']<=d['generated'],path.name+': invalid unresolved passage provenance')
                line=passage['line'];require(len(line)==2 and 0<math.hypot(line[1]['lat']-line[0]['lat'],line[1]['lng']-line[0]['lng'])<=.003,path.name+': invalid unresolved cut')
                require(all(math.isfinite(p[k]) and abs(p[k])<=(90 if k=='lat' else 180) for p in line for k in ('lat','lng')),path.name+': invalid unresolved coordinate')
        require({id for n in nets for id in ([r['tollId'] for r in n['sharedRoads']] if n.get('sharedRoads') else [n['tollId']])}==toll_ids,f'{path.name}: missing pricing network')
        require(len({n['id'] for n in nets})==len(nets),f'{path.name}: duplicate networks')
        for n in nets:
            prefix=path.name+':'+n['id'];gates=n['gates'];ids=[g['id'] for g in gates]
            roads=n.get('sharedRoads',[]);road_ids=[r['tollId'] for r in roads]
            if roads:
                require(d['schema']>=4 and len(roads)>=2 and len(set(road_ids))==len(road_ids) and n['tollId'] in road_ids,prefix+': invalid shared roads')
                require(n['pricing']['kind']=='od',prefix+': shared roads require OD settlement')
                for road in roads:
                    marker_ids=[g['id'] for g in road['gates']]
                    require(bool(marker_ids) and len(set(marker_ids))==len(marker_ids),prefix+': invalid road markers')
                    require('avoidanceGateIds' not in road or bool(road['avoidanceGateIds']) and set(road['avoidanceGateIds'])<=set(marker_ids),prefix+': invalid road avoidance')
                    for g in road['gates']:
                        require(len(g['line'])==2 and g['line'][0]!=g['line'][1],prefix+': invalid road cross-section')
                        require(g['direction'] in ('both','positive','negative'),prefix+': invalid road direction')
                        for p in g['line']:
                            require(all(math.isfinite(p[k]) for k in ('lat','lng')) and abs(p['lat'])<=90 and abs(p['lng'])<=180,prefix+': invalid road coordinate')
            for fare in n['pricing'].get('fares',[]) if n['pricing']['kind']=='od' else []:
                assigned=fare.get('roadIds')
                require(bool(assigned) and len(set(assigned))==len(assigned) and set(assigned)<=set(road_ids) if roads else assigned is None,prefix+': invalid fare roads')
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
        if country.get('complete') is not True or country.get('schema') not in (2,3,4,5):
            errors.append('Served Spain catalog is not a complete supported pricing dataset.')
        if country.get('unresolvedPassages'):errors.append('Served Spain catalog still contains unresolved toll passages.')
        errors.extend(status['nationalBlockers'])
        errors.extend(row['catalogId']+': '+b for row in status['entries'] for b in row['blockers'])
    if errors:
        print('\n'.join(errors));raise SystemExit(1)
    print(f'{count} candidate JSON files checked; development integrity only, not national coverage.')
