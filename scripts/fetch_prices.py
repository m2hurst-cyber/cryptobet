import argparse,io,urllib.request
from datetime import date,timedelta
import pandas as pd
from common import DATA,TICKERS
def fetch_prices(as_of=None,fixture_csv=None):
 end=date.fromisoformat(as_of) if as_of else date.today(); rows=[]; source='fixture'
 if fixture_csv:
  df=pd.read_csv(fixture_csv);df=df[df.date<=end.isoformat()];rows=df.to_dict('records')
 else:
  try:
   import yfinance as yf; source='yfinance'; px=yf.download(TICKERS,start=(end-timedelta(days=80)).isoformat(),end=(end+timedelta(days=1)).isoformat(),auto_adjust=False,progress=False,threads=True,group_by='column'); fld='Adj Close' if 'Adj Close' in px.columns.get_level_values(0) else 'Close'; fr=px[fld]
   for dt,r in fr.iterrows():
    for t in TICKERS:
     if pd.notna(r.get(t)): rows.append({'date':dt.date().isoformat(),'ticker':t,'adj_close':float(r[t]),'source':source,'carried_forward':False})
  except Exception:
   source='stooq'; series={}
   for t in TICKERS:
    u=f'https://stooq.com/q/d/l/?s={t.lower()}.us&d1={(end-timedelta(days=80)).strftime("%Y%m%d")}&d2={end.strftime("%Y%m%d")}&i=d'
    with urllib.request.urlopen(u,timeout=30) as r: series[t]=pd.read_csv(io.StringIO(r.read().decode())).set_index('Date')['Close']
   dates=sorted(set().union(*[set(s.index) for s in series.values()])); last={}
   for d in dates:
    for t,s in series.items():
     cf=False
     if d in s.index:last[t]=float(s.loc[d])
     elif t in last:cf=True
     else:continue
     rows.append({'date':str(d),'ticker':t,'adj_close':last[t],'source':source,'carried_forward':cf})
 out=pd.DataFrame(rows)
 if out.empty: raise RuntimeError('No sector prices resolved')
 out['date']=out['date'].astype(str);dates=sorted(out['date'].unique());completed=[]
 for t in TICKERS:
  s=out[out.ticker==t].sort_values('date').set_index('date')
  if s.empty: raise RuntimeError(f'No price history resolved for {t}')
  last=None
  for d in dates:
   if d in s.index:
    row=s.loc[d]
    if isinstance(row,pd.DataFrame): row=row.iloc[-1]
    last=float(row['adj_close']); src=row.get('source',source); cf=bool(row.get('carried_forward',False))
   elif last is not None: src=source;cf=True
   else: continue
   completed.append({'date':d,'ticker':t,'adj_close':last,'source':src,'carried_forward':cf})
 out=pd.DataFrame(completed);p=DATA/'sector_prices.csv'
 if p.exists():
  try:
   prior=pd.read_csv(p)
   if not prior.empty: out=pd.concat([prior,out],ignore_index=True)
  except Exception: pass
 out=out.sort_values(['date','ticker']).drop_duplicates(['date','ticker'],keep='last');out.to_csv(p,index=False);return out,source
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--as-of');a.add_argument('--fixture-csv');x=a.parse_args();print(fetch_prices(x.as_of,x.fixture_csv)[1])
