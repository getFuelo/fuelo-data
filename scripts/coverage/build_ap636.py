#!/usr/bin/env python3
"""AP-636: two independent gantries and Deskarga's mutually exclusive journeys.

Antzuola is a half interchange facing Deskarga, not a fourth additive toll.
Article 7 of Norma Foral 4/2020 and the collection system specification section
10.2 identify the partial TAG journey. No invented Antzuola–Bergara zero OD row.
"""
import collections, gzip, hashlib, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'audit/2026-09-16/networks/ap636'
OUT.mkdir(exist_ok=True)
graph = json.load(gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt'))
ways = {w['id']:w for w in graph['ways']}; nodes = graph['nodes']
refs = json.loads((ROOT/'pricing-candidates/ap636-tariffs.json').read_text())
old = next(t for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-ap636')
LAW = 'https://www.bidegi.eus/documents/42696171/43363894/Norma%20Foral%204_2020%20de%206%20de%20noviembre%20canon%20autov%C3%ADa%20A-636.pdf/fc8aed80-70de-9252-abf1-fa9007d146a9'
SYSTEM = 'https://www.contratacion.euskadi.eus/webkpe00-kpeperfi/es/contenidos/anuncio_contratacion/expjaso31143/es_doc/adjuntos/pliego_bases_tecnicas1.pdf'
point = lambda n: dict(zip(('lat','lng'),nodes[str(n)]))
evidence=[]
def gate(id,wid,nid):
    w=ways[wid];i=w['nodes'].index(nid)
    a,c,b=[point(n) for n in w['nodes'][i-1:i+2]]
    cos=math.cos(math.radians(c['lat']));dx=(b['lng']-a['lng'])*cos;dy=b['lat']-a['lat'];length=math.hypot(dx,dy)
    line=[{'lat':c['lat']+s*dx/length/111195,'lng':c['lng']-s*dy/length/111195/cos} for s in (-7,7)]
    cross=lambda p:(line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat'])-(line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
    evidence.append({'gate':id,'way':wid,'version':w['version'],'node':nid,'oneway':w['tags'].get('oneway')})
    return {'id':id,'line':line,'direction':'positive' if cross(b)>cross(a) else 'negative'}

at=collections.defaultdict(set)
for w in ways.values():
    for n in (w['nodes'][0],w['nodes'][-1]):at[n].add(w['id'])
selected={w['id'] for w in ways.values() if w['tags'].get('ref')=='AP-636'}
for _ in range(12):
    added={other for wid in selected for n in (ways[wid]['nodes'][0],ways[wid]['nodes'][-1]) for other in at[n]-selected
           if ways[other]['tags'].get('highway')=='motorway_link' and ways[other]['tags'].get('ref') in (None,'AP-636')}
    selected.update(added)
    if not added:break
coverage=[{'id':str(wid),'version':ways[wid]['version'],'line':[point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)]

def network(id,gates,pricing,covered):
    return {'id':id,'tollId':id,'validFrom':refs['validFrom'],'validThrough':refs['validThrough'],'timeZone':'Europe/Madrid',
            'gates':gates,'pricing':pricing,'coverageWays':covered,
            'evidence':{'checked':'2026-09-16','tariffSources':[refs['source'],LAW,SYSTEM],'geometrySource':'https://www.openstreetmap.org/copyright'}}
def toll(id,name,cents):
    return {**old,'id':id,'name':name,'price':cents/100,'price_high':None,'variable':False,'model':'fixed','source':refs['source'],
            'notes':'Development candidate; general reference excludes separately enrolled Abiatu monthly discounts.'}

networks=[];tolls=[]
for suffix,index,lanes in [('beasain',0,[(27694225,301664947),(27694624,301665205)]),('ezkio',1,[(158481317,2104862541),(421322505,2104862568)])]:
    id='es-ap636-'+suffix;gates=[gate(id+'-'+str(w),w,n) for w,n in lanes];tariff=refs['sections'][index]['tariff']
    networks.append(network(id,gates,{'kind':'gates','fares':{g['id']:tariff for g in gates}},coverage))
    tolls.append(toll(id,refs['sections'][index]['name'],tariff['baseCents']))

gates=[gate('Legazpi-entry',165813688,9427898716),gate('Legazpi-exit',165813689,9427928317),
       gate('Antzuola-entry',165816113,3417773128),gate('Antzuola-exit',429921664,4800873696),
       gate('Bergara-entry',165816869,1709676557),gate('Bergara-exit',334715038,1709676560)]
general=refs['sections'][2]['tariff'];partial={'baseCents':general['baseCents'],'bands':[{'cents':refs['conditionalJourneys'][0]['cents'],'requires':['payment:via-t']}]}
fares=[{'from':a+'-entry','to':b+'-exit','tariff':partial if 'Antzuola' in (a,b) else general}
       for a,b in [('Legazpi','Bergara'),('Bergara','Legazpi'),('Legazpi','Antzuola'),('Antzuola','Legazpi')]]
# Only the physical section between Deskarga and the western logical cut needs
# OD context. Earlier independent gantries must not require a Deskarga entry.
# Retain exact source vertices, clipping long source ways at actual cut nodes.
clips={165813688:(9427898716,None),165813689:(None,9427928317),165816869:(1709676557,None),334715038:(None,1709676560)}
odcoverage=[]
for w in coverage:
    wid=int(w['id']);ids=ways[wid]['nodes']
    if wid in clips:
        a,b=clips[wid];ids=ids[ids.index(a) if a else 0:(ids.index(b)+1) if b else len(ids)]
    elif not all(-2.360747<=point(n)['lng']<=-2.3393848 for n in ids):continue
    odcoverage.append({**w,'line':[point(n) for n in ids]})
id='es-ap636-deskarga'
net=network(id,gates,{'kind':'od','chargedAt':'exit','entries':[g['id'] for g in gates if g['id'].endswith('-entry')],
                    'exits':[g['id'] for g in gates if g['id'].endswith('-exit')],'fares':fares},odcoverage)
# Exclude the charge gantry in either direction, not the discount readers.
net['avoidanceGateIds']=['Legazpi-entry','Legazpi-exit']
networks.append(net);tolls.append(toll(id,'Deskarga: Legazpi/Urretxu–Bergara o Antzuola',general['baseCents']))
doc={'schema':2,'generated':'2026-09-16','currency':'EUR','complete':False,'tolls':tolls,'pricing':networks,
     'notes_global':'Disabled AP-636 candidate. Two independent gantries plus mutually exclusive Deskarga OD journeys. © OpenStreetMap contributors.'}
(ROOT/'pricing-candidates/ap636.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
(OUT/'provenance.json').write_text(json.dumps({'source':'../../spain-graph/provenance.json','gates':evidence,'tariffSource':refs['source'],
    'systemSource':SYSTEM,'lawSource':LAW,'systemDocumentSha256':hashlib.sha256(Path('/private/tmp/fuelo-toll-audit/ap636-system.pdf').read_bytes()).hexdigest(),
    'review':'Antzuola is a half interchange facing Deskarga. Only four direct OD movements; no assumed Antzuola–Bergara zero fare. OD coverage clips retain source vertices.',
    'ready':False},indent=2)+'\n')
print(len(coverage),'source ways;',len(odcoverage),'Deskarga context ways;',len(gates)+4,'directed gates')
