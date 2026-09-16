#!/usr/bin/env python3
"""Explicit, sequential public-server probes for a candidate's full OD table."""
import argparse,json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser();parser.add_argument('family',choices=['ap41','ap71','ap36','ap7-cartagena-vera','ap66','r2','ag55','ag57']);args=parser.parse_args();family=args.family
catalog=json.loads((ROOT/f'pricing-candidates/{family}.json').read_text());net=catalog['pricing'][0];locations=json.loads((ROOT/f'audit/2026-09-16/networks/{family}/provenance.json').read_text())['probeLocations'];out=ROOT/f'pricing-candidates/{family}-routes';out.mkdir(exist_ok=True)
for fare in net['pricing']['fares']:
 if family=='ag57' and ('-sur-' in fare['from'] or '-sur-' in fare['to']):continue
 a=fare['from'].removesuffix('-entry');b=fare['to'].removesuffix('-exit');name=a+'--'+b;target=out/(name+'.json')
 if target.exists():continue
 points=[locations[a]['entry'],locations[b]['exit']];body={'locations':[{'lat':p['lat'],'lon':p['lng']} for p in points],'costing':'auto','costing_options':{'auto':{'use_tolls':1}},'directions_options':{'units':'kilometers'}}
 raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read();d=json.loads(raw);assert d.get('trip'),d;target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedGeneralCents':fare['tariff']['baseCents']},indent=2)+'\n');print(name,d['trip']['summary']['length'],d['trip']['summary']['has_toll'],flush=True);time.sleep(.6)
