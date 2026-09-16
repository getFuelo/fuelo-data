#!/usr/bin/env python3
"""Extract a bounded major-road/toll graph from a dated Geofabrik Spain PBF.

Two streaming passes; no full-country location index. This inventory is evidence,
not an assertion that toll tags establish a payable fare.
"""
import argparse,gzip,hashlib,json,time
from pathlib import Path
import osmium
ROOT=Path(__file__).resolve().parents[2]
MAJOR={'motorway','motorway_link','trunk','trunk_link'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('pbf',type=Path);ap.add_argument('--source',required=True);args=ap.parse_args();ways={};tagged={};relations=[];started=time.monotonic()
 class Inventory(osmium.SimpleHandler):
  def node(self,n):
   tags=dict(n.tags)
   if tags.get('barrier')=='toll_booth' or tags.get('highway') in ['toll_gantry','motorway_junction']:
    tagged[n.id]={'id':n.id,'version':n.version,'lat':n.location.lat,'lng':n.location.lon,'tags':tags}
  def way(self,w):
   tags=dict(w.tags);refs=[n.ref for n in w.nodes]
   if tags.get('highway') in MAJOR or (tags.get('highway') and (tags.get('toll')=='yes' or any(id in tagged and tagged[id]['tags'].get('barrier')=='toll_booth' for id in refs))):
    ways[w.id]={'id':w.id,'version':w.version,'nodes':refs,'tags':tags}
  def relation(self,r):
   tags=dict(r.tags)
   if tags.get('route')=='road':relations.append({'id':r.id,'version':r.version,'tags':tags,'ways':[m.ref for m in r.members if m.type=='w']})
 Inventory().apply_file(str(args.pbf),filters=[osmium.filter.KeyFilter('highway','barrier','route')]);needed={n for w in ways.values() for n in w['nodes']};nodes={}
 print('inventory',len(ways),'ways',len(tagged),'tagged points',len(needed),'needed nodes',round(time.monotonic()-started,1),'s',flush=True)
 class Locations(osmium.SimpleHandler):
  def node(self,n):nodes[n.id]=[n.location.lat,n.location.lon]
 Locations().apply_file(str(args.pbf),filters=[osmium.filter.IdFilter(needed)])
 missing=needed-set(nodes);assert not missing, f'Missing {len(missing)} road nodes'
 relevant=[r for r in relations if any(id in ways for id in r['ways'])]
 out=ROOT/'audit/2026-09-16/spain-graph';out.mkdir(exist_ok=True)
 data={'nodes':nodes,'ways':list(ways.values()),'points':list(tagged.values()),'roadRelations':relevant}
 with gzip.open(out/'graph.json.gz','wt',encoding='utf8') as f:json.dump(data,f,separators=(',',':'),ensure_ascii=False)
 digest=hashlib.sha256()
 with args.pbf.open('rb') as f:
  for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
 with osmium.io.Reader(str(args.pbf)) as reader:timestamp=reader.header().get('osmosis_replication_timestamp')
 manifest={'source':args.source,'snapshot':timestamp,'sha256':digest.hexdigest(),'attribution':'© OpenStreetMap contributors, ODbL 1.0; extract by Geofabrik','ways':len(ways),'nodes':len(nodes),'taggedPoints':len(tagged),'roadRelations':len(relevant),'scope':'Major roads and mapped toll roads/booths. Excludes most local streets; a geographic inventory, not a tariff or completeness certificate.'};(out/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print('saved',out,round(time.monotonic()-started,1),'s',flush=True)
if __name__=='__main__':main()
