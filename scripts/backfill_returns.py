import json,pandas as pd
from common import DATA,TICKERS,read_jsonl
def backfill():
 p=DATA/'model_log.jsonl';rows=read_jsonl(p)
 if not rows:return 0
 px=pd.read_csv(DATA/'sector_prices.csv').pivot_table(index='date',columns='ticker',values='adj_close',aggfunc='last').sort_index();ds=list(px.index);pos={d:i for i,d in enumerate(ds)};before=[{k:v for k,v in r.items() if k!='forward_returns'} for r in rows];n=0
 for r in rows:
  fr=r.setdefault('forward_returns',{'1d':None,'5d':None,'20d':None});i=pos.get(r['date'])
  if i is None:continue
  for name,h in [('1d',1),('5d',5),('20d',20)]:
   if fr.get(name) is None and i+h<len(ds): fr[name]={t:float(px.loc[ds[i+h],t]/px.loc[ds[i],t]-1) for t in TICKERS};n+=1
 after=[{k:v for k,v in r.items() if k!='forward_returns'} for r in rows]
 if before!=after:raise RuntimeError('immutability violation')
 if n:
  with p.open('w') as f:
   for r in rows:f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
 return n
if __name__=='__main__':print(backfill())
