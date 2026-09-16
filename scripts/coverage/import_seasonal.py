#!/usr/bin/env python3
"""Import per-barrier Mediterranean AP-7 tariffs and their published calendar."""
import argparse,hashlib,json,re,subprocess
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPECS={'ap7-alicante-cartagena':3,'ap7-estepona-guadiaro':2,'ap7-malaga-estepona':4}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);args=ap.parse_args();sources={t['id']:t['source'] for t in json.loads((ROOT/'tolls-es.json').read_text())['tolls']}
 for name,count in SPECS.items():
  path=args.downloads/('es-'+name+'.pdf');text=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True);by_name={}
  reviewed=next(x for x in json.loads((ROOT/'audit/2026-09-16/source-fetch.json').read_text()) if 'es-'+name in x['ids']);assert hashlib.sha256(path.read_bytes()).hexdigest()==reviewed['sha256'], 'Source changed: re-review before import'
  for line in text.splitlines():
   if not re.match(r'\s*(TRONCAL|ACCESO)',line):continue
   amount=re.search(r'\d+,\d{2}',line)
   if not amount:continue
   label=line[:amount.start()].strip();by_name.setdefault(label,[]).append((int(Decimal(amount.group().replace(',','.'))*100),line.strip()))
  assert len(by_name)==count and all(len(v)==2 for v in by_name.values())
  barriers=[]
  for label,((low,low_row),(high,high_row)) in by_name.items():
   barriers.append({'name':label,'tariff':{'baseCents':low,'bands':[{'cents':high,'dates':['2026-06-01','2026-09-30']},{'cents':high,'dates':['2026-03-27','2026-04-12']}]},'sourceRows':{'normal':low_row,'special':high_row}})
  d={'kind':'tariff-reference','complete':False,'checked':'2026-09-16','currency':'EUR','vehicle_class':'light','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','source':sources['es-'+name],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'barriers':barriers,'notes':['General light-vehicle rate; frequent-user status is not assumed from Via-T ownership.','High season June–September and the 17 days from Friday of Passion Week through Sunday after Easter (2026-03-27 through 2026-04-12).','Map each actual barrier/access before pricing routes; never charge the sum of all catalog barriers to every journey.']}
  (ROOT/'pricing-candidates'/(name+'-tariffs.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(name,len(barriers),'barriers')
if __name__=='__main__':main()
