#!/usr/bin/env python3
"""Import published light-vehicle matrix cells; blanks are NOT zero fares.

Usage: python3 scripts/coverage/import_seitt.py /path/to/downloaded/2026/pdfs
Requires pdfplumber. Output is tariff-reference evidence, never a live catalog.
Coordinates and source hashes make every imported amount traceable to its cell.
"""
import argparse, hashlib, json, re
from decimal import Decimal
from pathlib import Path
import pdfplumber
ROOT = Path(__file__).resolve().parents[2]
SPECS = {
 'es-r3': ['Madrid / M-40 / M-602','M-45','M-50','M-208 Mejorada/Velilla','M-300 Arganda/Loeches','Conexión A-3'],
 'es-r5': ['M-40 / M-45','M-50 / M-506 Móstoles/Fuenlabrada','AP-41 Madrid-Toledo','M-413 Arroyomolinos/Moraleja','M-404 El Álamo/Navalcarnero','Conexión A-5'],
 'es-r4': ['M-50','Pinto-Parla','Valdemoro','Seseña','Villaseca Sagra (CM-4001)','Aranjuez','Ontígola','Ocaña / A-40'],
 'es-r2': ['Aeropuerto','Alcobendas','Ajalvir','Alcalá','Meco','Cabanillas','Guadalajara Norte','NII-Taracena'],
 'es-ap36': ['Troncal Corral Almaguer','Lateral Corral Almaguer','Quintanar Orden','Mota Cuervo','Pedernoso','Troncal San Clemente'],
 'es-ap41': ['R5','Serranillos','Carranque','Illescas','Numancia','Villaluenga','Villaseca','Toledo'],
 'es-ap7-cartagena-vera': ['Vera','Cuevas del Almanzora','Pulpí','Águilas','Cabo Cope','Ramonete','Mazarrón','Las Palas','Cartagena'],
}
def group_rows(words):
 rows=[]
 for w in sorted(words,key=lambda w:w['top']):
  if not rows or abs(w['top']-rows[-1][0]['top'])>2: rows.append([])
  rows[-1].append(w)
 return rows

def extract(path, labels, source):
 with pdfplumber.open(path) as pdf:
  words=pdf.pages[0].extract_words()
  tele=[w for w in words if w['text']=='Telepeaje']
  assert tele, 'Payment headers missing'
  header=min(w['top'] for w in tele)
  columns=sorted([w for w in words if abs(w['top']-header)<6 and (w['text']=='Telepeaje' or w['text'].startswith('Efectivo'))],key=lambda w:w['x0'])
  assert len(columns)==2*len(labels), (path,len(columns),len(labels))
  centers=[(w['x0']+w['x1'])/2 for w in columns]
  money=[w for w in words if re.fullmatch(r'\d+,\d{2}',w['text']) and w['top']>header]
  rows=group_rows(money)[:len(labels)]
  assert len(rows)==len(labels)
  entries=[]; gates=[]; cells={}; row_labels=[]
  for i,row in enumerate(rows):
   y=row[0]['top']; raw=' '.join(w['text'] for w in sorted(words,key=lambda w:w['x0']) if abs(w['top']-y)<2 and w['x1']<columns[0]['x0'])
   assert raw, (path,'missing row label',i)
   row_labels.append(raw)
   for w in row:
    x=(w['x0']+w['x1'])/2;j=min(range(len(centers)),key=lambda j:abs(centers[j]-x))
    assert abs(x-centers[j])<12, (path,'unaligned amount',w)
    key=(i,j);assert key not in cells
    cells[key]=(int(Decimal(w['text'].replace(',', '.'))*100),[round(w[k],3) for k in ['x0','top','x1','bottom']])
  for i in range(len(labels)):
   for j in range(len(labels)):
    a=cells.get((i,2*j));b=cells.get((i,2*j+1))
    assert bool(a)==bool(b),(path,'incomplete payment pair',i,j)
    if not a:continue
    entry={'from':labels[i],'to':labels[j],'tariff':{'baseCents':b[0],'bands':[{'cents':0,'minutes':[0,360]},{'cents':a[0],'minutes':[360,1440],'requires':['payment:via-t']}]},'sourceCell':{'page':1,'row':i+1,'column':j+1,'printedRow':row_labels[i],'viaTBox':a[1],'generalBox':b[1]}}
    if i==j:
     assert path.stem=='es-r2' and i<2,'Unexpected nonzero diagonal'
     entry['kind']='barrier';gates.append(entry)
    else:
     # Published matrices are symmetric. Any disagreement is an import error.
     assert cells.get((j,2*i),(None,))[0]==a[0] and cells.get((j,2*i+1),(None,))[0]==b[0],(path,'asymmetric cell',i,j)
     entries.append(entry)
  return {'kind':'tariff-reference','complete':False,'checked':'2026-09-16','currency':'EUR','vehicle_class':'light','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','source':source,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'publishedAccesses':labels,'ods':entries,'barriers':gates,'notes':['Only explicitly printed light-vehicle cells imported. Blank/dash cells remain unavailable, never zero.','Physical entry/exit mapping and route validation still required.','R-2 Aeropuerto/Alcobendas diagonal cells are independent barriers, not same-entry/exit OD fares.']}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);args=ap.parse_args()
 sources={t['id']:t['source'] for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls']}
 for id,labels in SPECS.items():
  reviewed=next(x for x in json.loads((ROOT/'audit/2026-09-16/source-fetch.json').read_text()) if id in x['ids']);assert hashlib.sha256((args.downloads/(id+'.pdf')).read_bytes()).hexdigest()==reviewed['sha256'], 'Source changed: re-review before import'
  result=extract(args.downloads/(id+'.pdf'),labels,sources[id]);target=ROOT/'pricing-candidates'/(id[3:]+'-tariffs.json');target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(id,len(result['ods']),'directed OD rows',len(result['barriers']),'barriers')
if __name__=='__main__':main()
