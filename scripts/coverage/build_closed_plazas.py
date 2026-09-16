#!/usr/bin/env python3
"""Closed-system candidates with explicit source associations for every access."""
import collections
import gzip
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# zone, booth group, source entry way, entry booth, reversed source direction,
# outside entry node, outside exit node. Published zone names are preserved.
SPECS = {'ap9-norte': {'ref':'AP-9','additionalRefs':['AP-9F','AP-9FS','AP-9SF','AP-9M','AP-9 M'],'tariffFamily':'ap9','tollId':'es-ap9','bbox':[42.95,-8.48,43.34,-8.19],
    'filterFareZones':['A CORUÑA O A BARCALA','GUISAMO O STA MARTA','GUISAMO/STA MARTA','MACENDA','ORDES','SIGUEIRO','SIGÜEIRO','SANTIAGO'],
    'tariffZoneAliases':{'A CORUÑA O A BARCALA':'CORUNA','GUISAMO O STA MARTA':'GUISAMO','GUISAMO/STA MARTA':'GUISAMO','SIGÜEIRO':'SIGUEIRO'},
    'excludeSelfPairs':True,'expectedDirectedFares':30,'viaTUnknownHistory':True,
    'zoneAliases':{'SIGUEIRO-norte':'SIGUEIRO'},'reverseSideSuffix':'-norte',
    'orderedZones':['CORUNA','GUISAMO','MACENDA','ORDES','SIGUEIRO','SANTIAGO'],
    'additionalSources':['https://www.audasa.es/la-autopista/descuentos-vehiculos-ligeros/','https://www.boe.es/buscar/doc.php?id=BOE-A-2021-12683'],
    'accesses':[],'logicalAccesses':[
      ('CORUNA',(29005426,99409315,99409314),(16269917,99407891,99407895)),
      ('GUISAMO',(16269923,91192201,91192199),(213896080,91190560,91190561)),
      ('MACENDA',(327163132,3338864531,2437664581),(327163130,280713390,2161602701)),
      ('ORDES',(104380819,1204265500,1204265289,True),(104380819,1204265500,1204265289)),
      ('SIGUEIRO',(800780746,7489986831,5015243648),(541031753,7489978570,5058979556)),
      ('SIGUEIRO-norte',(518664033,5363242806,5232642799),(800780745,145964805,3848910790)),
      ('SANTIAGO',(29007630,162290969,162290960),(29007625,162292691,162292678)),
    ]}, 'ap9-ferrol': {'ref':'AP-9F','tariffFamily':'ap9','tollId':'es-ap9','bbox':[43.30,-8.26,43.454,-8.13],
    'filterFareZones':['FENE','CABANAS','MIÑO','GUISAMO'],
    'expectedDirectedFares':12,'viaTUnknownHistory':True,
    'additionalSources':['https://www.audasa.es/la-autopista/descuentos-vehiculos-ligeros/','https://www.boe.es/buscar/doc.php?id=BOE-A-2021-12683'],
    'accesses':[],'logicalAccesses':[
      ('FENE',(70068615,85896100,85896085),(210247221,91191193,91191209)),
      ('CABANAS',(589618367,5630313125,2232445389),(589618365,280711541,186952299)),
      ('MIÑO',(25744037,1808337567,106147362),(25744037,1808337567,106147362,True)),
      ('GUISAMO',(213896080,91190560,1830693710),(16269923,91192201,1830693689)),
    ]}, 'ap9-sur': {'ref':'AP-9','tariffFamily':'ap9','tollId':'es-ap9','bbox':[42.257,-8.68,42.414,-8.62],
    'filterFareZones':['PONTEVEDRA','VILABOA','MORRAZO','RANDE','VIGO / PUXEIROS'],
    'expectedDirectedFares':8,'viaTUnknownHistory':True,'tariffZoneAliases':{'VIGO / PUXEIROS':'VIGO-PUXEIROS'},
    'freePairs':[('MORRAZO','VIGO-PUXEIROS','https://www.audasa.es/wp-content/uploads/pdf/tarifas/2026/Tarifas-20260101.pdf')],
    'additionalSources':['https://www.audasa.es/la-autopista/descuentos-vehiculos-ligeros/','https://www.boe.es/buscar/doc.php?id=BOE-A-2021-12683'],
    'accesses':[],'logicalAccesses':[
      ('PONTEVEDRA',(697601807,29968117,29969292),(29015006,29957622,29959502)),
      ('VILABOA',(233911039,8639722480,2422259426),(23968275,259836284,259836285)),
      ('MORRAZO',(24621813,3607096712,3739153838),(683328151,5075691312,3739153838)),
      ('RANDE',(136733859,1428333959,1428333977),(136276193,1495150357,1428333973)),
      ('VIGO-PUXEIROS',(29016054,29958917,29962724),(29016043,29969136,29965495)),
    ]}, 'ap9-centro': {'ref':'AP-9','tariffFamily':'ap9','tollId':'es-ap9','bbox':[42.435,-8.71,42.827,-8.53],
    'filterFareZones':['SANTIAGO','PADRON','CARRACEDO','CALDAS DE REIS','CURRO','PONTEVEDRA'],
    'excludeSelfPairs':True,'expectedDirectedFares':26,'viaTUnknownHistory':True,
    'extraCoverageWays':[154415948,230997178],
    'additionalSources':['https://www.audasa.es/la-autopista/descuentos-vehiculos-ligeros/','https://www.boe.es/buscar/doc.php?id=BOE-A-2021-12683'],
    'accesses':[],'logicalAccesses':[
      ('SANTIAGO',(29012981,56442327,56441486),(29012989,56441266,56443060)),
      ('PADRON',(7742864,56443726,940926782),(375673552,56442215,940926782)),
      ('CARRACEDO',(7656093,29969841,55481169),(7656087,29961779,55481160)),
      ('CALDAS DE REIS',(1254326178,1665300957,417759231,True),(1254326178,1665300957,417759231)),
      ('CURRO',(154415948,2371176644,1586329833),(230997178,1586329830,1586329842)),
      ('PONTEVEDRA',(697599414,29962630,29957044),(697601809,29968733,29960841)),
    ]}, 'ap9-frontera' : {'ref':'AP-9','tariffFamily':'ap9','tollId':'es-ap9','bbox':[42.069,-8.66,42.175,-8.62],
    'filterFareZones':['PUXEIROS','PORRIÑO','TUI'],'viaTUnknownHistory':True,
    'additionalSources':['https://www.audasa.es/la-autopista/descuentos-vehiculos-ligeros/','https://www.boe.es/buscar/doc.php?id=BOE-A-2021-12683'],
    'accesses':[],'logicalAccesses':[
      ('PUXEIROS',(91617365,1039336765,1039336859),(91617393,442075588,442075589)),
      ('PORRIÑO',(1160820724,1482106893,10796547344),(1160820721,1482124533,10796547345)),
      ('TUI',(342973178,4878457700,3499091176),(134876275,1482120324,1482120022)),
    ]}, 'r4' : {'ref':'R-4','bbox':[39.935,-3.77,40.28,-3.53], 'expectedDirectedFares':34,
    'tariffZoneAliases':{'M-50':'M50','Pinto-Parla':'Pinto','Valdemoro':'Valdemoro','Seseña':'Sesena','Villaseca Sagra (CM-4001)':'Villaseca','Aranjuez':'Aranjuez','Ontígola':'Ontigola','Ocaña / A-40':'Ocana'},
    'zoneAliases':{'Valdemoro-madrid':'Valdemoro'},'reverseSideSuffix':'-madrid',
    'orderedZones':['M50','Pinto','Valdemoro','Sesena','Villaseca','Aranjuez','Ontigola','Ocana'],'accesses':[],
    'logicalAccesses':[
      ('M50',(60650660,248050952,248050933),(60583180,52735534,2139030765)),
      ('Pinto',(1469456051,1429085343,568607936),(129545735,358897474,568607955)),
      ('Valdemoro',(30146972,1302707072,4566582019),(28491481,1302707006,332212871)),
      ('Valdemoro-madrid',(30146954,313012137,313012135),(264632448,335621746,332212810)),
      ('Sesena',(123603113,312808585,1212248291),(123603097,1212248281,1212248341)),
      ('Villaseca',(1392211207,1017729830,2139030596),(1392211207,1017729830,2139030596,True)),
      ('Aranjuez',(230997897,2394196254,1104563380),(230997901,2394196230,4561534258)),
      ('Ontigola',(95218761,1017729680,1104563747),(95218761,1017729680,1104563747,True)),
      ('Ocana',(95990409,52736430,1112125088),(95218782,8856675185,8856675174)),
    ]}, 'r5' : {'ref':'R-5','bbox':[40.25,-4.05,40.365,-3.73], 'expectedDirectedFares':26,
    'extraCoverageWays':[31958590,28068194,56760006],
    'tariffZoneAliases':{'M-40 / M-45':'M40-M45','M-50 / M-506 Móstoles/Fuenlabrada':'M50-M506','AP-41 Madrid-Toledo':'AP41','M-413 Arroyomolinos/Moraleja':'M413','M-404 El Álamo/Navalcarnero':'M404','Conexión A-5':'A5'},
    'zoneAliases':{'M50-M506-madrid':'M50-M506','AP41-madrid':'AP41'},'reverseSideSuffix':'-madrid',
    'orderedZones':['M40-M45','M50-M506','AP41','M413','M404','A5'],'accesses':[],
    'logicalAccesses':[
      ('M40-M45',(28667979,5639764807,309904844),(28667978,359398385,315055133)),
      ('M50-M506',(251386749,357901802,2576106216),(31955005,2576106197,357900887)),
      ('M50-M506-madrid',(251386747,2576106232,2576106228),(251386748,412246539,5700590514)),
      ('AP41',(56760304,710552978,413519748),(31958539,413519744,357977728)),
      ('AP41-madrid',(31958590,707148363,357979463),(28068194,357979278,308205283)),
      ('M413',(31978403,710550207,1898701321),(31978399,710550239,568802571)),
      ('M404',(32061815,359942994,359942889),(32061802,1310956582,359942850)),
      ('A5',(25413968,276977630,257315465),(1222741339,360300187,409820704)),
    ]}, 'r3' : {'freePairs':[('M50','M208','https://ayto-velilla.es/la-direccion-general-de-carreteras-incluira-la-m-208-en-su-tramo-proximo-a-la-calle-frascuelo-en-los-planes-de-accion-contra-el-ruido/')], 'ref':'R-3','additionalRefs':['Salida M 300'],'bbox':[40.25,-3.65,40.43,-3.37], 'expectedDirectedFares':26,
    'tariffZoneAliases':{'Madrid / M-40 / M-602':'M40','M-45':'M45','M-50':'M50','M-208 Mejorada/Velilla':'M208','M-300 Arganda/Loeches':'M300','Conexión A-3':'A3'},
    'zoneAliases':{'M45-oeste':'M45','M50-oeste':'M50','M208-oeste':'M208'},
    'orderedZones':['M40','M45','M50','M208','M300','A3'],'accesses':[],
    'logicalAccesses':[
      ('M40',(31165865,261208545,346866638),(23725720,256922957,256923202)),
      ('M45',(368920339,346858786,346861003),(1223180452,346868255,3714255231)),
      ('M45-oeste',(520247005,256922949,256922947),(35471377,346864447,5071076888)),
      ('M50',(312603283,1080662618,352685028),(1223186515,307862077,352684824)),
      ('M50-oeste',(312603278,1080662438,1080662368),(31512165,5313450724,415935675)),
      ('M208',(36072206,304009292,421419554),(36072236,1119321167,421419575)),
      ('M208-oeste',(36072258,1119321139,421419795),(36072228,421419533,304009286)),
      ('M300',(550110519,261612896,306085166),(365558631,304176122,3519117173)),
      ('A3',(35804478,307863152,418628022),(368926230,5313504556,304010236)),
    ]}, 'ag57' : {'ref':'AG-57','additionalRefs':['AG-57N'], 'bbox':[42.105,-8.805,42.165,-8.70],
    'bidirectionalRows':True,'expectedDirectedFares':24,
    'zoneAliases':{'A Ramallosa-sur':'A Ramallosa'},'accesses':[],
    'logicalAccesses':[
        ('Vigo',(30639427,4724254267,338860633),(252789015,68834794,338860640)),
        ('Vincios',(52669356,338860923,338860945),(769030907,338860959,338860806)),
        ('Gondomar',(206870568,2169170655,2169170644),(38330023,12896459204,452591581)),
        ('Nigrán',(71903229,68831665,68832322),(9218874,68830118,10083886434)),
        ('A Ramallosa',(1422200349,1784646933,1783752107),(1422183083,13069862060,1783752105)),
        ('A Ramallosa-sur',(167095504,1784976698,1783752072),(1101960214,13069962967,1783752070)),
        ('Baiona',(167096006,107983618,1784981675),(1101960216,13069962968,1784981676)),
    ]}, 'ag55' : {'ref':'AG-55','bbox':[43.20,-8.68,43.322,-8.47],
    'excludeCoverageWays':[795695668,795695678],
    'filterFareZones':['Arteixo','Paiosaco','Laracha','Carballo'],'bidirectionalRows':True,'accesses':[],
    'logicalAccesses':[
        ('Arteixo',(769028620,285118382,285118318),(1465177144,285172019,285172032)),
        ('Paiosaco',(188413423,1037453360,1990432049),(188413423,1037453360,1990432050,True)),
        ('Laracha',(39473216,1871156571,4553788387),(461221636,1687779465,1871156594)),
        ('Carballo',(156543952,691690003,699045240),(176397986,970590197,285118558)),
    ]}, 'r2': {'ref':'R-2','bbox':[40.49,-3.50,40.80,-3.10],
    'freeApproachWays':[329573260,329573259,329573253,57700096], 'accesses':[
    ('Ajalvir','osm-review-161872278',329280725,161872278,False,None,(28699460,-1)),
    ('Alcalá','osm-review-409505056',37520682,439206819,False,(329573260,1),(329573259,1)),
    ('Meco','osm-review-276999231',1012505416,276999231,False,None,(1012505413,-1)),
    ('Cabanillas','osm-review-280428937',33487089,280428937,False,None,(329277831,-1)),
    ('Guadalajara Norte','osm-review-439218762',1510856672,439218765,False,None,(1510856667,-1)),
], 'logicalAccesses':[
    # Beyond the Guadalajara ramps: the main collection booth alone cannot
    # close the published, fully rebated Guadalajara Norte–NII-Taracena trip.
    ('NII-Taracena',(26417902,13810674060,289445377),(26418045,13810674061,289445374)),
]}, 'ap36': {'ref': 'AP-36', 'accesses': [
    ('Troncal Corral Almaguer', 'osm-review-30297630', 183749260, 30299730, False, None, (173086102, -1)),
    ('Troncal San Clemente', 'osm-review-30295021', 435004158, 30295021, False, None, (435004151, -1)),
    ('Lateral Corral Almaguer', 'osm-review-983425201', 24220447, 983425215, False, None, (183927767, -1)),
    ('Quintanar Orden', 'osm-review-983425415', 24336301, 983425538, False, None, (183927756, -1)),
    ('Pedernoso', 'osm-review-983425493', 84657479, 983425894, False, None, (183927749, -1)),
    ('Mota Cuervo', 'osm-review-983425503', 82101660, 983425503, False, (82101660, 0), (82101660, 0)),
]}, 'ap7-cartagena-vera': {'ref': 'AP-7', 'bbox': [37.19, -1.95, 37.70, -.99], 'accesses': [
    ('Cartagena', 'osm-review-186853438', 384760606, 295558078, False, None, (1317470846, -1)),
    ('Las Palas', 'osm-review-186852042', 131391524, 186852042, False, None, (769373449, -1)),
    ('Mazarrón', 'osm-review-264688958', 769371991, 12195595280, False, None, (98864421, -1)),
    ('Ramonete', 'osm-review-1535236954', 140645747, 1535236954, False, None, (140645746, -1)),
    ('Cabo Cope', 'osm-review-1454017078', 140645745, 1454017080, False, None, (132120099, -1)),
    ('Águilas', 'osm-review-2431640698', 1318528135, 2431640698, False, None, (169927310, -1)),
    ('Pulpí', 'osm-review-1537685703', 1319109532, 1537685713, False, None, (1319109533, -1)),
    ('Cuevas del Almanzora', 'osm-review-3100395406', 179755312, 3100395406, False, None, (179755324, -1)),
    ('Vera', 'osm-review-264694281', 1319348645, 299818774, False, None, (180019164, -1)),
]}, 'ap66': {'ref': 'AP-66', 'accesses': [
    ('LA MAGDALENA', 'osm-review-31431077', 44385458, 31431077, False, None, (159051078, -1)),
    ('OBLANCA', 'osm-review-1423285874', 545291462, 1423285875, False, None, (545291464, -1)),
], 'logicalAccesses': [
    ('LEON', (44366324, 945906800, 945906452), (56680757, 563837513, 563837638)),
    # Stay south of the bridge: the free N-630 below it crosses the old cut in
    # 2D and would create a spurious second entry after a completed northbound trip.
    ('CAMPOMANES', (4803589, 30826577, 30826569), (94658795, 814868480, 30826562)),
]}}

with gzip.open(ROOT / 'audit/2026-09-16/spain-graph/graph.json.gz', 'rt') as f:
    graph = json.load(f)
review = json.loads((ROOT / 'audit/2026-09-16/spain-graph/access-review.json').read_text())
groups = {g['id']: g for g in review['groups']}
ways = {w['id']: w for w in graph['ways']}
nodes = graph['nodes']
at = collections.defaultdict(set)
for way in ways.values():
    for node in way['nodes']:
        at[node].add(way['id'])

def point(node):
    lat, lng = nodes[str(node)]
    return {'lat': lat, 'lng': lng}

for family, spec in SPECS.items():
    bounds = spec.get('bbox', [-90, -180, 90, 180])
    inside = lambda w: all(bounds[0] <= nodes[str(n)][0] <= bounds[2] and bounds[1] <= nodes[str(n)][1] <= bounds[3] for n in w['nodes'])
    selected = {w['id'] for w in ways.values() if (w['tags'].get('ref') in [spec['ref']]+spec.get('additionalRefs',[]) or (family == 'ap66' and w['tags'].get('nat_ref') == 'AP-66')) and inside(w)}
    for _ in range(20):
        added = set()
        for wid in selected:
            for node in ways[wid]['nodes']:
                for other in at[node] - selected:
                    tags = ways[other]['tags']
                    if tags.get('ref') in [None, spec['ref']]+spec.get('additionalRefs',[]) and tags.get('highway') == 'motorway_link' and inside(ways[other]):
                        added.add(other)
        selected.update(added)
        if not added:
            break
    selected.update(spec.get('freeApproachWays',[]))
    selected.update(spec.get('extraCoverageWays',[]))
    # Arteixo public slip roads belong to the independent Pastoriza section.
    # Duplicating them in the closed system invents missing OD context on
    # exempt port movements and makes the result depend on catalog order.
    selected.difference_update(spec.get('excludeCoverageWays',[]))
    gates, locations, evidence = [], {}, []
    for zone, groupid, wid, booth, reverse, outside_entry, outside_exit in spec['accesses']:
        way, group = ways[wid], groups[groupid]
        i = way['nodes'].index(booth)
        a = point(way['nodes'][max(0, i-1)])
        b = point(way['nodes'][min(len(way['nodes'])-1, i+1)])
        if reverse:
            a, b = b, a
        center = {k: sum(point(n)[k] for n in group['pointIds']) / len(group['pointIds']) for k in ('lat', 'lng')}
        cos = math.cos(math.radians(center['lat']))
        dx, dy = (b['lng']-a['lng'])*cos, b['lat']-a['lat']
        length = math.hypot(dx, dy)
        assert length > 0
        px, py = -dy/length, dx/length
        projection = [(point(n)['lng']-center['lng'])*cos*px + (point(n)['lat']-center['lat'])*py for n in group['pointIds']]
        line = [{'lat': center['lat']+v*py, 'lng': center['lng']+v*px/cos} for v in (min(projection)-6/111195, max(projection)+6/111195)]
        cross = lambda p: (line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat']) - (line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
        positive = cross(b) > cross(a)
        for role in ('entry', 'exit'):
            gates.append({'id': zone+'-'+role, 'line': line, 'direction': 'positive' if (positive if role=='entry' else not positive) else 'negative'})
        entry_way, entry_index = outside_entry or (wid, 0)
        exit_way, exit_index = outside_exit
        locations[zone] = {'entry': point(ways[entry_way]['nodes'][entry_index]), 'exit': point(ways[exit_way]['nodes'][exit_index])}
        evidence.append({'zone': zone, 'reviewGroup': groupid, 'booths': group['pointIds'],
                         'entryWay': wid, 'version': way['version'], 'entryBooth': booth,
                         'reverseEntryWay': reverse, 'line': line})
    # Logical terminal cuts must lie outside ramp splits/merges, not blindly
    # on collection booths that adjacent-access trips may also cross.
    for zone, entry, exit in spec.get('logicalAccesses', []):
        locations[zone] = {}
        for role, cut in [('entry', entry), ('exit', exit)]:
            wid, node, outside = cut[:3]
            reverse = len(cut)>3 and cut[3]
            way = ways[wid]
            i = way['nodes'].index(node)
            # At an endpoint use the adjoining source segment's tangent.
            # This allows a cut before a fork without crossing a nearby trunk.
            a, center, b = [point(way['nodes'][j]) for j in (max(0,i-1),i,min(len(way['nodes'])-1,i+1))]
            cos = math.cos(math.radians(center['lat']))
            dx, dy = (b['lng']-a['lng'])*cos, b['lat']-a['lat']
            length = math.hypot(dx, dy)
            px, py = -dy/length, dx/length
            line = [{'lat': center['lat']+v*py/111195, 'lng': center['lng']+v*px/111195/cos} for v in (-8, 8)]
            cross = lambda p: (line[1]['lng']-line[0]['lng'])*(p['lat']-line[0]['lat']) - (line[1]['lat']-line[0]['lat'])*(p['lng']-line[0]['lng'])
            positive = cross(b)>cross(a)
            gates.append({'id': zone+'-'+role, 'line': line, 'direction': 'positive' if positive != reverse else 'negative'})
            locations[zone][role] = point(outside)
            evidence.append({'zone': zone, 'role': role, 'kind': 'logical-terminal-cut', 'way': wid,
                             'version': way['version'], 'node': node, 'outsideNode': outside, **({'reverseSourceDirection':True} if reverse else {})})
    tariff_family = spec.get('tariffFamily',family)
    refs = json.loads((ROOT / f'pricing-candidates/{tariff_family}-tariffs.json').read_text())
    fares = []
    for row in refs['ods']:
        if spec.get('excludeSelfPairs') and row['from']==row['to']:continue
        if spec.get('filterFareZones') and not all(row[k] in spec['filterFareZones'] for k in ('from','to')):
            continue
        normalize = lambda zone: spec.get('tariffZoneAliases',{}).get(zone,zone)
        pairs = [(normalize(row['from']), normalize(row['to']))]
        if row.get('bidirectional') or spec.get('bidirectionalRows'):
            pairs.append((normalize(row['to']), normalize(row['from'])))
        fares.extend({'from': a+'-entry', 'to': b+'-exit', 'tariff': ({'baseCents':row['tariff']['baseCents'],'bands':[{'cents':0,'maxCents':row['tariff']['baseCents'],'requires':['payment:via-t']}]} if spec.get('viaTUnknownHistory') else row['tariff'])} for a,b in pairs)
    assert len(fares) == spec.get('expectedDirectedFares',len(locations)*(len(locations)-1))
    for a,b,source in spec.get('freePairs',[]):
        fares.extend({'from':origin+'-entry','to':destination+'-exit','tariff':{'baseCents':0,'bands':[]}} for origin,destination in [(a,b),(b,a)])
    canonical_fares = list(fares)
    aliases = spec.get('zoneAliases',{})
    for fare in canonical_fares:
        origins = [fare['from']] + [alias+'-entry' for alias,zone in aliases.items() if fare['from']==zone+'-entry']
        destinations = [fare['to']] + [alias+'-exit' for alias,zone in aliases.items() if fare['to']==zone+'-exit']
        fares.extend({**fare,'from':a,'to':b} for a in origins for b in destinations if (a,b)!=(fare['from'],fare['to']))
    net = {'id': 'es-'+family, 'tollId': spec.get('tollId','es-'+family), 'validFrom': refs['validFrom'], 'validThrough': refs['validThrough'],
           'timeZone': 'Europe/Madrid', 'gates': gates,
           'pricing': {'kind': 'od', 'chargedAt': 'exit', 'entries': [g['id'] for g in gates if g['id'].endswith('-entry')],
                       'exits': [g['id'] for g in gates if g['id'].endswith('-exit')], 'fares': fares},
           'coverageWays': [{'id': str(wid), 'version': ways[wid]['version'], 'line': [point(n) for n in ways[wid]['nodes']]} for wid in sorted(selected)],
           'evidence': {'checked': '2026-09-16', 'tariffSources': [refs['source']]+([refs['discountSource']['url']] if refs.get('discountSource') else [])+[p[2] for p in spec.get('freePairs',[])]+spec.get('additionalSources',[]), 'geometrySource': 'https://www.openstreetmap.org/copyright'}}
    if family == 'ap66':
        net['avoidanceGateIds'] = [g['id'] for g in gates if g['id'].endswith('-entry')]
    if family == 'r2':
        # The shared plaza cross-sections block entry AND exit carriageways.
        # Every paid OD pair touches at least one of these four plazas; the
        # only pair touching neither is the rebated Guadalajara–Taracena pair.
        # Never exclude the two terminal gates of that free movement.
        net['avoidanceGateIds'] = [zone+'-entry' for zone in ('Ajalvir','Alcalá','Meco','Cabanillas')]
    for way in net['coverageWays']:
        if int(way['id']) in spec.get('freeApproachWays',[]):
            assert ways[int(way['id'])]['tags'].get('toll') != 'yes'
            way['freeTravelSource'] = 'https://www.openstreetmap.org/way/'+way['id']+'/history'
    toll = next(t for t in json.loads((ROOT / 'tolls-es.json').read_text())['tolls'] if t['id'] == spec.get('tollId','es-'+family))
    schema = 3 if spec.get('freeApproachWays') or any('maxCents' in band for fare in fares for band in fare['tariff']['bands']) else 2
    doc = {'schema': schema, 'generated': '2026-09-16', 'currency': 'EUR', 'complete': False, 'tolls': [toll], 'pricing': [net],
           'notes_global': 'Disabled closed-system candidate. Explicit source-way access associations and published OD rows; route checks are required separately. © OpenStreetMap contributors.'}
    (ROOT / f'pricing-candidates/{family}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
    out = ROOT / f'audit/2026-09-16/networks/{family}'
    out.mkdir(exist_ok=True)
    journeys = {}
    if spec.get('orderedZones'):
        order = spec['orderedZones']
        suffix = spec.get('reverseSideSuffix','-oeste')
        for fare in canonical_fares:
            a,b = fare['from'].removesuffix('-entry'),fare['to'].removesuffix('-exit')
            entry = a+suffix if order.index(b)<order.index(a) and a+suffix in locations else a
            exit = b+suffix if order.index(a)<order.index(b) and b+suffix in locations else b
            journeys[a+'--'+b] = {'entry':locations[entry]['entry'],'exit':locations[exit]['exit'], 'expectedGates':[entry+'-entry',exit+'-exit']}
    (out / 'provenance.json').write_text(json.dumps({'source': '../../spain-graph/provenance.json', 'gates': evidence, 'probeLocations': locations, 'canonicalProbeZones':sorted({f['from'].removesuffix('-entry') for f in canonical_fares}), **({'probeJourneys':journeys} if journeys else {}), 'status': 'candidate_pending_real_routes'}, ensure_ascii=False, indent=2)+'\n')
    print(family, len(gates), 'gates', len(fares), 'OD fares', len(selected), 'ways')

# Regenerate the combined candidate offline with the five audited subsystems.
families = ['ap9-ferrol','ap9-norte','ap9-centro','ap9-sur','ap9-frontera']
docs = [json.loads((ROOT/f'pricing-candidates/{f}.json').read_text()) for f in families]
combined = {**docs[0], 'pricing':[n for d in docs for n in d['pricing']]}
combined['notes_global'] = 'Disabled combined AP-9 candidate. Whole-network probes use published journey totals; local access and release review remain open. © OpenStreetMap contributors.'
(ROOT/'pricing-candidates/ap9.json').write_text(json.dumps(combined,ensure_ascii=False,indent=2)+'\n')
