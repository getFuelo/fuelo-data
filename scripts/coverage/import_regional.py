#!/usr/bin/env python3
"""Import explicit regional operator tariff rows without assuming blank=free."""
import argparse,hashlib,json,re,subprocess
from decimal import Decimal
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
def cents(s):return int(Decimal(s.replace('€','').replace(',','.').strip())*100)
def base(source,path):
 assert hashlib.sha256(path.read_bytes()).hexdigest()==json.loads((ROOT/'scripts/coverage/source-lock.json').read_text())[path.name], 'Source changed: re-review before import'
 return {'kind':'tariff-reference','complete':False,'checked':'2026-09-16','currency':'EUR','vehicle_class':'light','validFrom':'2026-01-01','validThrough':'2026-12-31','timeZone':'Europe/Madrid','source':source,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'notes':['Published general light-vehicle rows only. Geographic mapping and route verification are separate.','Blank/dash cells are not zero; no unverified enrollment/recurrence discounts.']}
def write(name,d):(ROOT/'pricing-candidates'/(name+'-tariffs.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('downloads',type=Path);args=ap.parse_args();D=args.downloads
 path=D/'es-ag55.html';tables=BeautifulSoup(path.read_text(),'html.parser').find_all('table');assert len(tables)==2
 for name,table,expected in zip(['ag55','ag57'],tables,[9,12]):
  d=base('https://www.autoestradas.com/la-autopista/tarifas/',path);rows=[];missing=[]
  for i,row in enumerate(table.find_all('tr')[1:],2):
   cols=[c.get_text(' ',strip=True) for c in row.find_all(['td','th'])];assert len(cols)==4
   a,b=re.split(r'\s+[–-]\s+',cols[0],maxsplit=1)
   if not re.fullmatch(r'\d+,\d{2}',cols[1]):missing.append({'from':a,'to':b,'printed':cols[1]});continue
   rows.append({'from':a,'to':b,'tariff':{'baseCents':cents(cols[1]),'bands':[]},'sourceRow':i})
  assert len(rows)==expected;d.update(ods=rows,unpricedPublishedRows=missing);write(name,d);print(name,len(rows),'rows')
 path=D/'arabat.html';table=BeautifulSoup(path.read_text(),'html.parser').find('table');raw=table.find_all('tr');dest=[c.get_text(' ',strip=True) for c in raw[0].find_all('th')][1:];rows=[];origin=None
 for i,row in enumerate(raw[1:],2):
  cols=row.find_all(['th','td'],recursive=False)
  if cols[0].get('rowspan'):origin=cols.pop(0).get_text(' ',strip=True)
  vals=[c.get_text(' ',strip=True) for c in cols]
  if vals[0]!='Ligeros':continue
  assert len(vals)==len(dest)+1
  for j,(to,value) in enumerate(zip(dest,vals[1:]),3):
   if not value:continue
   assert re.fullmatch(r'\d+(?:\.\d{1,2})?',value)
   rows.append({'from':origin,'to':to,'tariff':{'baseCents':cents(value),'bands':[]},'sourceCell':{'row':i,'column':j,'printed':value}})
 d=base('https://www.arabat.eus/es/ap-1/tarifas-ap-1/',path);d.update(ods=rows,scope='Published combined AP-8/AP-1 access matrix; not independent regional sums');write('ap8-ap1-joint',d);print('ap8-ap1-joint',len(rows),'rows')
 path=D/'es-c16-sant-cugat-terrassa.html';table=BeautifulSoup(path.read_text(),'html.parser').find('table');row=next(r for r in table.find_all('tr') if r.find('td') and r.find('td').get_text(strip=True)=='II');cols=[c.get_text(' ',strip=True) for c in row.find_all('td')];assert len(cols)==8
 d=base('https://www.autema.com/es/tarifas-y-descuentos/tarifas/',path);d['barriers']=[{'name':name,'tariff':{'baseCents':cents(cols[i]),'bands':[]},'sourceColumn':i+1} for name,i in [('Manresa',2),('Sant Vicenç',4),('Les Fonts',6)]];write('autema',d);print('autema',len(d['barriers']),'barriers')
 for name,labels in [('ap15',['SARASA','ORIZ-TIEBAS','MARCILLA TRONCO','MARCILLA ENLACE'])]:
  path=D/('es-'+name+'.pdf');text=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True);d=base('https://www.audenasa.es/wp-content/uploads/Tarifas-2026-Recorrido.pdf',path);d['barriers']=[]
  for label in labels:
   line=next(l for l in text.splitlines() if l.startswith(label));money=re.findall(r'\d+,\d{2}',line);assert len(money)==3;d['barriers'].append({'name':label,'tariff':{'baseCents':cents(money[0]),'bands':[]},'sourceRow':line.strip()})
  d['ods']=[]
  for line in text.splitlines():
   if ' - ' not in line:continue
   money=re.findall(r'\d+,\d{2}',line)
   if len(money)!=3:continue
   label=line[:line.index(money[0])].strip();a,b=label.split(' - ',1);d['ods'].append({'from':a,'to':b,'tariff':{'baseCents':cents(money[0]),'bands':[]},'sourceRow':line.strip()})
  assert len(d['ods'])==10;write(name,d);print(name,len(d['barriers']),'barriers',len(d['ods']),'OD references (do not double charge)')
if __name__=='__main__':main()
