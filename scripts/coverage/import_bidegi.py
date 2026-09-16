#!/usr/bin/env python3
"""Complete the reviewed joint matrix and separate conditional eastern fares.

The PDF's row/column layout is hash-locked. Blank cells remain unknown. Every
amount shared with the separately imported Arabat matrix must agree exactly.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('downloads',type=Path);args=p.parse_args()
pdf=args.downloads/'es-ap8-gipuzkoa.pdf';digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
assert digest==json.loads((ROOT/'scripts/coverage/source-lock.json').read_text())[pdf.name]
text=subprocess.check_output(['pdftotext','-layout',str(pdf),'-'],text=True)
source=next(t['source'] for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls'] if t['id']=='es-ap8-gipuzkoa')
names=['Acceso Oeste','Amorebieta-Etxano','Iurreta','Abadiño','Ermua','Eibar','Bergara I/N','Bergara H/S','Arrasate-Mondragón','Eskoriatza','Luko','Etxabarri-Ibiña','Elgoibar','Itziar','Zestoa – Zumaia','Zarautz Oeste','Zarautz Barrera (Donostia)']
columns=[64,83,96,110,126,141,152,166,180,196,215,234,252,271,289,308,337]
base=json.loads((ROOT/'pricing-candidates/ap8-ap1-joint-tariffs.json').read_text());pairs={tuple(sorted((r['from'],r['to']))):dict(r,bidirectional=True) for r in base['ods']}
lines=[(i,l) for i,l in enumerate(text.splitlines(),1) if 'Arinak / Ligeros' in l][:17]
assert len(lines)==17
checked=0;added=0
for row,(line_number,line) in enumerate(lines):
 for match in re.finditer(r'\d+,\d{2}',line):
  center=(match.start()+match.end())/2;column=min(range(17),key=lambda c:abs(columns[c]-center))
  assert abs(columns[column]-center)<3
  a,b=names[row],names[column];cents=int(match.group().replace(',',''));key=tuple(sorted((a,b)))
  evidence={'source':source,'sha256':digest,'page':1,'line':line_number,'row':row,'column':column,'printed':match.group()}
  if key in pairs:
   assert pairs[key]['tariff']['baseCents']==cents,(a,b,cents,pairs[key])
   checked+=1;pairs[key].setdefault('corroboratingCells',[]).append(evidence)
  else:
   pairs[key]={'from':a,'to':b,'bidirectional':True,'tariff':{'baseCents':cents,'bands':[]},'sourceCell':evidence};added+=1
assert added==15 and len(pairs)==181
full={**base,'ods':list(pairs.values()),'additionalSources':[{'url':source,'sha256':digest}],'notes':base['notes']+['Bidegi 2026 matrix adds 15 Amorebieta-Etxano pairs missing from the Arabat HTML extraction. Every common amount agrees.','Same-zone Itziar row is retained, not assigned to a guessed turnaround.'], 'sourceCrossCheck':{'addedPairs':added,'matchingDirectedCells':checked}}
(ROOT/'pricing-candidates/ap8-ap1-full-tariffs.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n')
# Visually reviewed small tables below the matrix. Oñaurre is explicitly TAG-only.
rows=[('Donostia - SS. E / Hernani / Astigarraga / Lasarte','Oiartzun',161),('Donostia - SS. E / Hernani / Astigarraga / Lasarte','Irun M/O',224),('Donostia - SS. E / Hernani / Astigarraga / Lasarte','Oñaurre',247),('Donostia - SS. E / Hernani / Astigarraga / Lasarte','Behobia',315),('Oiartzun','Irun M/O',224),('Oiartzun','Oñaurre',247),('Oiartzun','Behobia',315),('Irun Ventas','Oñaurre',50),('Irun Ventas','Behobia',117),('Zarautz E','Donostia - SS M/O / Astigarraga / Hernani',280),('Orio','Donostia - SS M/O / Astigarraga / Hernani',219)]
general=[];conditional=[]
for a,b,cents in rows:
 if b=='Oñaurre':conditional.append({'from':a,'to':b,'cents':cents,'requires':['payment:via-t'],'sourceNote':'Tarifa aplicable en caso de pago con telepeaje'})
 else:general.append({'from':a,'to':b,'tariff':{'baseCents':cents,'bands':[]}})
east={k:base[k] for k in ['kind','complete','checked','currency','vehicle_class','validFrom','validThrough','timeZone']}
east.update(source=source,sha256=digest,ods=general,conditionalJourneys=conditional,scope='Eastern and Zarautz/Orio small tables, page 1',notes=['Printed access labels preserved. Directional physical mapping is required before pricing.','Oñaurre amounts are conditional references only; no cash/general price is fabricated.','Blank cells are unknown, not free travel.'])
(ROOT/'pricing-candidates/ap8-east-tariffs.json').write_text(json.dumps(east,ensure_ascii=False,indent=2)+'\n')
print(len(pairs),'joint pairs,',len(general),'eastern general rows,',len(conditional),'conditional TAG rows')
