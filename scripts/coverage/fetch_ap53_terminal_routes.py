#!/usr/bin/env python3
"""Validate individual terminal accesses and the legally free Lalín movements."""
import gzip,json,math,time,urllib.request,urllib.parse,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'pricing-candidates/ap53-terminals';out.mkdir(exist_ok=True)
with gzip.open(ROOT/'audit/2026-09-16/spain-graph/graph.json.gz','rt') as f:d=json.load(f)
nodes=d['nodes'];ways=d['ways']
def closest(ref,lat,lng,direction=None):
 ids={n for w in ways if w['tags'].get('ref')==ref and (direction is None or (nodes[str(w['nodes'][-1])][0]>nodes[str(w['nodes'][0])][0])==direction) for n in w['nodes']}
 n=min(ids,key=lambda n:math.hypot(nodes[str(n)][0]-lat,(nodes[str(n)][1]-lng)*.735));a=nodes[str(n)];return n,{'lat':a[0],'lon':a[1]}
ends={name:closest('N-525',lat,lng) for name,lat,lng in [('Lalín Oeste',42.68,-8.18),('Lalín Centro',42.64,-8.13),('Lalín Este',42.62,-8.10),('Alto de Santo Domingo',42.578,-8.064)]}
# Northern origin/destination remain on the AP-53 outside its observed gates,
# keeping unrelated AP-9 charges outside these isolated-network fixtures.
w={w['id']:w for w in ways};p=lambda n:{'lat':nodes[str(n)][0],'lon':nodes[str(n)][1]}
origins={'south':p(w[119472403]['nodes'][0]),'north':p(w[98039345]['nodes'][-1])}
cases=[]
for name,(n,loc) in ends.items():
 for direction in ['south','north']:
  locations=[origins[direction],loc] if direction=='south' else [loc,origins[direction]]
  cases.append((name+'-'+direction,locations,725,[n],'paid terminal access'))
for a,b in itertools.permutations(ends,2):
 na,pa=ends[a];nb,pb=ends[b];midid,mid=closest('AP-53',(pa['lat']+pb['lat'])/2,(pa['lon']+pb['lon'])/2,pb['lat']>pa['lat']);mid['type']='through'
 cases.append((a+'--'+b,[pa,mid,pb],0,[na,midid,nb],'free internal terminal movement, forced onto the actual AP-53'))
for name,locations,cents,ids,purpose in cases:
 target=out/(name+'.json')
 if target.exists():continue
 body={'locations':locations,'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();r=json.loads(raw);assert r.get('trip'),r;target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':cents,'sourceEndpointNodes':ids,'purpose':purpose},ensure_ascii=False,indent=2)+'\n');print(name,r['trip']['summary']['length'],r['trip']['summary']['has_toll'],flush=True);time.sleep(.5)
