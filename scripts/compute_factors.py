import argparse,math,json,pandas as pd
from common import DATA,load_json,dump_json
def z(vals,w):
 s=pd.Series(vals,dtype='float64').dropna(); need=math.ceil(.9*w)
 if len(s)<need:return None,f'coverage {len(s)}/{w} < 90%'
 x=s.iloc[-w:];sd=x.std(ddof=1)
 if not math.isfinite(sd) or sd==0:return None,'invalid std'
 return float((x.iloc[-1]-x.mean())/sd),None
def vals(c,sid,asof): return [o['value'] for o in c[sid]['observations'] if o['date']<=asof]
def compute(asof):
 c=load_json(DATA/'fred_cache.json',{});comp={};flags=[]
 for sid in ['PAYEMS','INDPRO','RSAFS','CPILFESL','PCEPILFE']:
  comp[sid],e=z(vals(c,sid,asof),60); flags += [f'{sid}:{e}'] if e else []
 obs=[o for o in c['T5YIFR']['observations'] if o['date']<=asof]; s=pd.DataFrame(obs); monthly=[]
 if not s.empty:
  s['date']=pd.to_datetime(s.date); monthly=s.set_index('date').value.sort_index().resample('ME').last().ffill().tolist()
 comp['T5YIFR'],e=z(monthly,60); flags += [f'T5YIFR:{e}'] if e else []
 for sid in ['DGS10','BAMLH0A0HYM2','BAMLC0A0CM','T10Y2Y']:
  comp[sid],e=z(vals(c,sid,asof),1260); flags += [f'{sid}:{e}'] if e else []
 f={'growth':None if any(comp[k] is None for k in ['PAYEMS','INDPRO','RSAFS']) else sum(comp[k] for k in ['PAYEMS','INDPRO','RSAFS'])/3,'inflation':None if any(comp[k] is None for k in ['CPILFESL','PCEPILFE','T5YIFR']) else sum(comp[k] for k in ['CPILFESL','PCEPILFE','T5YIFR'])/3,'rates':comp['DGS10'],'credit_stress':None if comp['BAMLH0A0HYM2'] is None or comp['BAMLC0A0CM'] is None else (comp['BAMLH0A0HYM2']+comp['BAMLC0A0CM'])/2,'curve_steep':comp['T10Y2Y']}
 o={'as_of':asof,'factors':f,'components':comp,'status':'stale' if any(v is None for v in f.values()) else 'ok','data_quality_flags':flags};dump_json(DATA/'factor_scores.json',o);return o
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--as-of',required=True);x=a.parse_args();print(json.dumps(compute(x.as_of),indent=2))
