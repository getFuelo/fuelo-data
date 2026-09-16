#!/usr/bin/env python3
"""Retain local Oiartzun connectors omitted from the major-road-only graph."""
import argparse,json,osmium
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('pbf',type=Path);args=p.parse_args()
seeds={9464504594,278535218};selected={}
for depth in range(3):
 class Ways(osmium.SimpleHandler):
  def way(self,w):
   if 'highway' not in w.tags:return
   ns=[n.ref for n in w.nodes]
   if seeds.intersection(ns):selected[w.id]={'id':w.id,'version':w.version,'nodes':ns,'tags':dict(w.tags)}
 Ways().apply_file(str(args.pbf),filters=[osmium.filter.EntityFilter(osmium.osm.WAY),osmium.filter.KeyFilter('highway')])
 seeds.update(n for w in selected.values() for n in w['nodes'])
 print('depth',depth+1,'ways',len(selected),flush=True)
nodes={}
class Nodes(osmium.SimpleHandler):
 def node(self,n):nodes[str(n.id)]=[n.location.lat,n.location.lon]
Nodes().apply_file(str(args.pbf),filters=[osmium.filter.EntityFilter(osmium.osm.NODE),osmium.filter.IdFilter(seeds)])
assert len(nodes)==len(seeds)
source=json.loads((ROOT/'audit/2026-09-16/spain-graph/provenance.json').read_text())
out=ROOT/'audit/2026-09-16/networks/ap8-gipuzkoa-east/local-access-graph.json'
out.write_text(json.dumps({'source':'../../spain-graph/provenance.json','snapshot':source['snapshot'],'sourceSha256':source['sha256'],'seedNodes':[9464504594,278535218],'hops':3,'ways':list(selected.values()),'nodes':nodes},ensure_ascii=False,indent=2)+'\n')
