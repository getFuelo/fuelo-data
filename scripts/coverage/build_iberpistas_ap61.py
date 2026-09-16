#!/usr/bin/env python3
"""Add published AP-61 public/joint journeys without summing local fares.

AP6 is an internal boundary in the isolated AP-61 candidate, not a public
origin of this combined network. Unlisted cross-branch journeys stay unknown.
"""
import copy,gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def write(p,value):
 target=ROOT/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
doc=read('pricing-candidates/iberpistas.json');branch=read('pricing-candidates/ap61.json');net=doc['pricing'][0];native=branch['pricing'][0]
net['id']='es-ap6-ap51-ap61';net['sharedRoads'].append({'tollId':'es-ap61','gates':copy.deepcopy(native['gates'])})
net['coverageWays']=list({w['id']:w for n in (net,native) for w in n['coverageWays']}.values())
graph=json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
covered={w['id'] for w in net['coverageWays']};connector_ways=[]
for way in graph['ways']:
 if way['tags'].get('ref')=='AP-61' and way['tags'].get('highway')=='motorway' and str(way['id']) not in covered:
  net['coverageWays'].append({'id':str(way['id']),'version':way['version'],'line':[dict(zip(('lat','lng'),graph['nodes'][str(n)])) for n in way['nodes']]});connector_ways.append(way['id'])
net['gates'] += [g for g in native['gates'] if not g['id'].startswith('AP6-')]
net['evidence']['tariffSources']=list(dict.fromkeys(net['evidence']['tariffSources']+native['evidence']['tariffSources']))
net['pricing']['fares'] += [{**f,'roadIds':['es-ap61']} for f in native['pricing']['fares'] if not f['from'].startswith('AP6-') and not f['to'].startswith('AP6-')]
ref=read('pricing-candidates/ap61-tariffs.json');names={'OTERO DE HERREROS':'OTERO','EL HONTORIA':'HONTORIA'}
for row in ref['ods']:
 if row['from'] not in ['VILLALBA','SAN RAFAEL']:continue
 a,b=row['from'],names.get(row['to'],row['to'])
 for x,y in [(a,b),(b,a)]:
  origins=[x]+(['VILLALBA-reversible'] if x=='VILLALBA' else ['HONTORIA-sur'] if x=='HONTORIA' else [])
  destinations=[y]+(['VILLALBA-reversible'] if y=='VILLALBA' else ['HONTORIA-sur'] if y=='HONTORIA' else [])
  for origin in origins:
   for dest in destinations:net['pricing']['fares'].append({'from':origin+'-entry','to':dest+'-exit','tariff':row['tariff'],'roadIds':['es-ap6','es-ap61'] if a=='VILLALBA' else ['es-ap61']})
net['pricing']['entries']=[g['id'] for g in net['gates'] if g['id'].endswith('-entry')];net['pricing']['exits']=[g['id'] for g in net['gates'] if g['id'].endswith('-exit')]
canonical=lambda g:g.replace('-reversible','').replace('-sur','')
assert len({(canonical(f['from']),canonical(f['to'])) for f in net['pricing']['fares']})==58
assert len({(f['from'],f['to']) for f in net['pricing']['fares']})==len(net['pricing']['fares'])
doc['tolls']+=branch['tolls'];doc['notes_global']='Disabled AP-6/AP-51/AP-61 settlement candidate. Only published complete journeys; internal AP-61 connection probes do not establish a public origin. Unlisted cross-branch fares remain unknown. © OpenStreetMap contributors.'
write('pricing-candidates/iberpistas-ap61.json',doc)
base=read('audit/2026-09-16/networks/iberpistas/provenance.json');p=read('audit/2026-09-16/networks/ap61/provenance.json')
base['probeLocations'].update({k:v for k,v in p['probeLocations'].items() if k!='AP6'})
base['probeJourneys']={k:v for k,v in p['probeJourneys'].items() if 'AP6' not in k}
base['additionalAp61SourceWays']=connector_ways
base['internalBoundaryNotPublicOrigin']='AP6';base['status']='candidate_pending_real_joint_routes'
write('audit/2026-09-16/networks/iberpistas-ap61/provenance.json',base)
print(len(net['gates']),'financial gates;',len(net['pricing']['fares']),'physical fares; 58 canonical pairs')
