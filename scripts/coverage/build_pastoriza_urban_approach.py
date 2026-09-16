#!/usr/bin/env python3
"""Cover the AC-552 continuation of Valhalla's mixed Pastoriza maneuver.

The fixed plaza remains the only payment trigger. These are exact public
AC-552 source ways, not the parallel V-1.4 flyover selected by a nearest-road
search against the major-road-only extract. No tolerance change is required.
"""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'audit/2026-09-16/networks/ag55/coruna-approach.osm'
x=ET.parse(source).getroot();nodes={n.attrib['id']:{'lat':float(n.attrib['lat']),'lng':float(n.attrib['lon'])} for n in x.findall('node')}
ids={166714261,622799668,622799669};records=[];provenance=[]
for w in x.findall('way'):
 if int(w.attrib['id']) not in ids:continue
 tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
 assert tags['ref']=='AC-552' and tags['highway']=='primary' and tags.get('toll')!='yes'
 records.append({'id':w.attrib['id'],'version':int(w.attrib['version']),'line':[nodes[n.attrib['ref']] for n in w.findall('nd')]})
 provenance.append({'id':w.attrib['id'],'version':w.attrib['version'],'tags':tags})
assert len(records)==3
p=ROOT/'pricing-candidates/ag55-pastoriza.json';d=json.loads(p.read_text());n=d['pricing'][0]
n['coverageWays']=[w for w in n['coverageWays'] if int(w['id']) not in ids]+records
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(ROOT/'audit/2026-09-16/networks/ag55/coruna-approach.json').write_text(json.dumps({'source':'https://api.openstreetmap.org/api/0.6/map?bbox=-8.442,43.342,-8.430,43.347','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':__doc__,'ways':provenance},ensure_ascii=False,indent=2)+'\n')
print('Pastoriza: three exact AC-552 continuation ways; fixed plaza unchanged')
