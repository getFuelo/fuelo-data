#!/usr/bin/env python3
"""Import explicit general light-vehicle OD rows from reviewed Ministry PDFs.

No interpolation, blank-cell filling, automatic resident or recurrence discounts.
The resulting references still require physical OD mapping before publication.
"""
import argparse,hashlib,json,re,subprocess
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPECS={'es-ap6':(1,6,'columns'),'es-ap53':(1,22,'hyphen'),'es-ap66':(1,6,'hyphen'),'es-ap68':(6,232,'columns'),'es-ap9':(2,46,'spaced'),'es-ap61':(1,18,'season'),'es-ap71':(1,6,'night')}
def cents(s):return int(Decimal(s.replace(',','.'))*100)
def tariff(values,kind):
 if kind=='night':return {'baseCents':values[3],'bands':[{'cents':values[0],'minutes':[1380,420]}]}
 if kind=='season':
  valley,normal,peak=values[:3]
  return {'baseCents':normal,'bands':[{'cents':valley,'minutes':[1380,420]},{'cents':peak,'dates':['2026-06-16','2026-09-15'],'minutes':[420,1380]},{'cents':peak,'weekdays':[5],'minutes':[900,1380]},{'cents':peak,'weekdays':[6,7],'minutes':[420,1380]},{'cents':peak,'dates':['2026-03-30','2026-04-06'],'minutes':[420,1380]}]}
 return {'baseCents':values[0],'bands':[]}
def extract(id,downloads,source):
 pages,count,kind=SPECS[id];path=downloads/(id+'.pdf');text=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True);rows=[];joint=False
 for page_no,page in enumerate(text.split('\f')[:pages],1):
  for line_no,line in enumerate(page.splitlines(),1):
   if id=='es-ap66' and line.startswith('PEAJES VEHÍCULOS LIGEROS.'):break
   if 'EXPLOTACIÓN CONJUNTA' in line:joint=True
   matches=list(re.finditer(r'(?<![\d,])\d+,\d{2}(?![\d,])',line))
   if not matches:continue
   expected=6 if kind=='night' else 5 if kind=='season' else 3
   assert len(matches)==expected or (id=='es-ap9' and line.strip().startswith('RANDE-VIGO') and len(matches)==1),(id,page_no,line)
   label=line[:matches[0].start()].strip();values=[cents(m.group()) for m in matches]
   if kind=='columns':pair=re.split(r'\s{2,}',label)
   elif kind in ['spaced','season']:pair=label.split(' - ',1) if ' - ' in label else label.split('-',1)
   else:pair=label.split('-',1)
   assert len(pair)==2,(id,label)
   rows.append({'from':pair[0].strip(),'to':pair[1].strip(),'bidirectional':True,'scope':'joint-ap6-journey' if joint else 'published-journey','tariff':tariff(values,kind),'sourceRow':{'page':page_no,'line':line_no,'printed':line.strip()}})
 assert len(rows)==count,(id,len(rows),count)
 return {'kind':'tariff-reference','complete':False,'checked':'2026-09-16','currency':'EUR','vehicle_class':'light','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','source':source,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ods':rows,'notes':['General light-vehicle rows only; physical accesses and route evidence still required.','Published names preserved, including source typos, pending explicit alias mapping.','Do not add joint AP-6 journey rows to a separately quoted AP-6 journey.','Unlisted pairs are unknown; free sections require separate evidence.']}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);args=ap.parse_args();sources={t['id']:t['source'] for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls']}
 for id in SPECS:
  reviewed=next(x for x in json.loads((ROOT/'audit/2026-09-16/source-fetch.json').read_text()) if id in x['ids']);assert hashlib.sha256((args.downloads/(id+'.pdf')).read_bytes()).hexdigest()==reviewed['sha256'], 'Source changed: re-review before import'
  d=extract(id,args.downloads,sources[id]);(ROOT/'pricing-candidates'/(id[3:]+'-tariffs.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(id,len(d['ods']),'bidirectional published rows')
if __name__=='__main__':main()
