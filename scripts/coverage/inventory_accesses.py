#!/usr/bin/env python3
"""Associate mapped toll points with roads by graph connectivity, never radius alone.

This produces review candidates. It deliberately does not assign tariff rows or
infer entry/exit roles from proximity. Parking and disconnected booths remain
unassigned. Nearby points on the same connected road are grouped for review.
"""
import collections,gzip,heapq,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'audit/2026-09-16/spain-graph'
REFS={'AP-1','AP-6','AP-7','AP-8','AP-9','AP-9F','AP-9M','AP-9FS','AP-9SF','AP-15','AP-36','AP-41','AP-46','AP-51','AP-53','AP-61','AP-66','AP-68','AP-71','AP-636','A-636','AG-55','AG-57','AG-57N','C-16','C-32','M-12','R-2','R-3','R-4','R-5','BI-626','BI-627'}
def distance(a,b):return math.hypot((a[0]-b[0])*111195,(a[1]-b[1])*111195*math.cos(math.radians((a[0]+b[0])/2)))
def main():
 with gzip.open(OUT/'graph.json.gz','rt') as f:d=json.load(f)
 nodes=d['nodes'];ways={w['id']:w for w in d['ways']};at=collections.defaultdict(list);lengths={}
 for w in ways.values():
  for n in w['nodes']:at[n].append(w['id'])
 def cost(id):
  if id not in lengths:
   refs=ways[id]['nodes'];lengths[id]=sum(distance(nodes[str(a)],nodes[str(b)]) for a,b in zip(refs,refs[1:]))
  return lengths[id]
 points=[]
 for p in d['points']:
  if p['tags'].get('barrier')!='toll_booth' and p['tags'].get('highway')!='toll_gantry':continue
  queue=[(0,id) for id in at[p['id']]];heapq.heapify(queue);seen={};matches=[];best=3000
  while queue:
   dist,id=heapq.heappop(queue)
   if dist>min(3000,best+250) or id in seen:continue
   seen[id]=dist;w=ways[id];refs=set(w['tags'].get('ref','').split(';'))&REFS
   if refs:
    matches.append({'refs':sorted(refs),'way':id,'graphDistanceUpperBoundM':round(dist,1)});best=min(best,dist);continue
   for n in [w['nodes'][0],w['nodes'][-1]]:
    for other in at[n]:
     if other not in seen:heapq.heappush(queue,(dist+cost(id),other))
  point={**p,'incidentWays':at[p['id']],'roadCandidates':matches,'status':'connectivity_candidate' if matches else 'unassigned_not_certified'};points.append(point)
 # Conservative review groups; this is not a price/de-duplication algorithm.
 groups=[];assigned=set()
 for p in points:
  if p['id'] in assigned:continue
  refs={r for m in p['roadCandidates'] for r in m['refs']};group=[p];assigned.add(p['id'])
  for q in points:
   if q['id'] in assigned:continue
   other={r for m in q['roadCandidates'] for r in m['refs']}
   if refs and refs==other and distance([p['lat'],p['lng']],[q['lat'],q['lng']])<150:
    group.append(q);assigned.add(q['id'])
  groups.append({'id':'osm-review-'+str(min(x['id'] for x in group)),'refs':sorted(refs),'pointIds':[x['id'] for x in group],'names':sorted({x['tags']['name'] for x in group if x['tags'].get('name')}),'lat':sum(x['lat'] for x in group)/len(group),'lng':sum(x['lng'] for x in group)/len(group),'reviewStatus':'unreviewed','entryExitRole':'unassigned','tariffRow':'unassigned'})
 (OUT/'access-review.json').write_text(json.dumps({'source':'graph.json.gz','method':'Connectivity search up to 3km on the extracted road graph; proximity only groups connected candidates for human review. No tariffs or entry/exit roles inferred.','points':points,'groups':groups},ensure_ascii=False,indent=2)+'\n')
 counts=collections.Counter(r for g in groups for r in g['refs']);print(len(points),'mapped toll points',len(groups),'review groups',sum(not g['refs'] for g in groups),'unassigned');print(counts)
if __name__=='__main__':main()
