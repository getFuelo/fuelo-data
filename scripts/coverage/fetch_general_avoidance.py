#!/usr/bin/env python3
"""Retain selective avoidance of reviewed general-fare systems, in both directions."""
import argparse,json,subprocess,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('app',type=Path);args=p.parse_args()
families=['ap36','ap41','ap7-cartagena-vera','r4','r5','supersur','ag57','ag55','ap8-gipuzkoa-east','r3'];out=ROOT/'pricing-candidates/general-avoidance';out.mkdir(exist_ok=True)
public={
 'ag55':[(43.362,-8.411),(43.213,-8.692)],
 'ap8-gipuzkoa-east':[(43.318,-1.981),(43.339,-1.789)],
 'r3':[(40.416,-3.703),(40.300,-3.437)],
 'ap36':[(39.960,-3.497),(39.208,-2.159)],
 'ap41':[(40.416,-3.703),(39.862,-4.027)],
 'ap7-cartagena-vera':[(37.605,-.986),(37.247,-1.868)],
 'r4':[(40.416,-3.703),(39.960,-3.497)],
 'r5':[(40.416,-3.703),(40.289,-4.012)],
 'supersur':[(43.206,-2.887),(43.328,-3.033)],
 'ag57':[(42.240,-8.720),(42.118,-8.850)],
}
for family in families:
 subprocess.run(['node',str(ROOT/'scripts/coverage/export_exclusion_polygons.cjs'),str(args.app),family],check=True)
 polygons=json.loads((ROOT/f'audit/2026-09-16/networks/{family}/exclusion-polygons.json').read_text())
 candidates=[]
 for request_file in (ROOT/f'pricing-candidates/{family}-routes').glob('*-request.json'):
  name=request_file.name.removesuffix('-request.json');d=json.loads(request_file.with_name(name+'.json').read_text());candidates.append((d['trip']['summary']['length'],name,request_file))
 _,name,source=max(candidates);reverse='--'.join(name.split('--')[::-1]);sources=[source,source.with_name(reverse+'-request.json')]
 for direction,source in zip(['forward','reverse'],sources):
  assert source.exists(),source
  name=family+'-public-'+direction;target=out/(name+'.json')
  request=json.loads(source.read_text());body=request['request'];pair=public[family] if direction=='forward' else public[family][::-1];body={**body,'locations':[{'lat':lat,'lon':lng} for lat,lng in pair],'exclude_polygons':polygons}
  previous=out/(name+'-request.json')
  if target.exists() and not (out/(name+'-error.json')).exists() and previous.exists() and json.loads(previous.read_text())['request']==body:continue
  target.unlink(missing_ok=True)
  (out/(name+'-request.json')).write_text(json.dumps({'request':body,'family':family,'sourcePricingProbe':str(source.relative_to(ROOT)),'endpointScope':'Public urban test points; distinct from committed one-way plaza probes','purpose':'No crossing of the selected road; other roads may remain tolled. This is not an independently certified whole-trip total.'},ensure_ascii=False,indent=2)+'\n')
  try:
   raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=60).read();d=json.loads(raw)
   if not d.get('trip'):raise ValueError(str(d))
   target.write_bytes(raw);(out/(name+'-error.json')).unlink(missing_ok=True);print(name,d['trip']['summary'],flush=True)
  except Exception as error:
   (out/(name+'-error.json')).write_text(json.dumps({'error':str(error),'body':error.read().decode('utf8',errors='replace') if isinstance(error,urllib.error.HTTPError) else None},indent=2)+'\n');print(name,'ERROR',error,flush=True)
  time.sleep(1)
