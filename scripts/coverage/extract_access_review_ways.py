#!/usr/bin/env python3
"""Retain every incident way for unresolved access nodes, including local roads.

The major-road extract is intentionally incomplete for parking/service roads.
A node absent from that extract's ways must not be called disconnected until
this full-PBF check has run. Never infer a fare from these tags.
"""
import argparse, json
from pathlib import Path
import osmium
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('spain',type=Path);p.add_argument('canaries',type=Path);a=p.parse_args()
report=json.loads((ROOT/'audit/2026-09-16/access-inventory-reconciliation.json').read_text())
target=ROOT/'audit/2026-09-16/access-review-ways.json'
previous=json.loads(target.read_text()) if target.exists() else []
result=[]
for region,source in [('spain',a.spain),('canary-islands',a.canaries)]:
 ids={x['node'] for x in report['points'] if x['status']=='needs_review' and x['region']==region};ids.update(n for r in previous if r['region']==region for n in r['reviewedNodes']);ways=[];nodes={};node_tags={}
 class Ways(osmium.SimpleHandler):
  def way(self,w):
   refs=[n.ref for n in w.nodes]
   matched=ids.intersection(refs)
   if matched:ways.append({'id':w.id,'version':w.version,'tags':dict(w.tags),'nodes':refs,'accessNodes':sorted(matched)})
 Ways().apply_file(str(source));needed={n for w in ways for n in w['nodes']}
 class Nodes(osmium.SimpleHandler):
  def node(self,n):
   nodes[str(n.id)]=[n.location.lat,n.location.lon]
   if n.tags:node_tags[str(n.id)]=dict(n.tags)
 Nodes().apply_file(str(source),filters=[osmium.filter.IdFilter(needed)])
 result.append({'region':region,'sourceManifest':region+'-graph/provenance.json','reviewedNodes':sorted(ids),'ways':ways,'nodes':nodes,'nodeTags':node_tags})
 print(region,len(ids),'reviewed nodes',len(ways),'incident ways',flush=True)
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
