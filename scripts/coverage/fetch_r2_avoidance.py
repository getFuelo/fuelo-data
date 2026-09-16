#!/usr/bin/env python3
"""Use exact app exclusions on every R-2 OD probe, retaining the free pair."""
import json,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'pricing-candidates/r2-avoidance';out.mkdir(exist_ok=True)
polygons=json.loads((ROOT/'audit/2026-09-16/networks/r2/exclusion-polygons.json').read_text())
for path in sorted((ROOT/'pricing-candidates/r2-routes').glob('*-request.json')):
    name=path.stem.removesuffix('-request');target=out/(name+'.json')
    if target.exists():continue
    original=json.loads(path.read_text());body=original['request'].copy();body['exclude_polygons']=polygons
    a,b=name.split('--')
    # Original Ajalvir probes are already on the committed motorway approach,
    # after the last free exit. Use the M-113 junction outside the toll road.
    # OSM way 23628638 terminal node 255960167 in the retained national graph.
    if a=='Ajalvir':body['locations'][0]={'lat':40.5170631,'lon':-3.5050036}
    if b=='Ajalvir':body['locations'][1]={'lat':40.5170631,'lon':-3.5050036}
    # Destination probes on a one-way exit ramp can only be reached through
    # the plaza. Use the public junction for both endpoints when avoiding it.
    public={'Meco':{'lat':40.5390527,'lon':-3.3081827}, # node 276998168, M-116 junction
            'Cabanillas':{'lat':40.6211008,'lon':-3.2421573}} # node 280428859, N-320
    for i,zone in enumerate((a,b)):
        if zone in public:body['locations'][i]=public[zone]
    try:raw=urllib.request.urlopen('https://valhalla1.openstreetmap.de/route?json='+urllib.parse.quote(json.dumps(body)),timeout=45).read()
    except urllib.error.HTTPError as error:
        errors=ROOT/'audit/2026-09-16/networks/r2/avoidance-probe-review';errors.mkdir(exist_ok=True)
        (errors/(name+'-error.json')).write_bytes(error.read())
        (errors/(name+'-error-request.json')).write_text(json.dumps(body,indent=2)+'\n')
        raise
    result=json.loads(raw);assert result.get('trip'),result
    target.write_bytes(raw);(out/(name+'-request.json')).write_text(json.dumps({'request':body,'expectedCents':0,'baselineRequest':'../r2-routes/'+path.name,'baselineGeneralCents':original['expectedGeneralCents']},indent=2)+'\n')
    print(name,result['trip']['summary'],flush=True);time.sleep(.6)
