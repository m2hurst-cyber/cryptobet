import os,json,argparse,urllib.parse,urllib.request
from datetime import date,timedelta
from pathlib import Path
from common import DATA,dump_json,load_json,utcnow_iso
SERIES={'PAYEMS':'chg','INDPRO':'pc1','RSAFS':'pc1','CPILFESL':'pc1','PCEPILFE':'pc1','T5YIFR':'lin','DGS10':'lin','BAMLH0A0HYM2':'lin','BAMLC0A0CM':'lin','T10Y2Y':'lin'}
def fetch_all(as_of=None,fixture_dir=None):
 end=date.fromisoformat(as_of) if as_of else date.today(); start=(end-timedelta(days=365*7)).isoformat(); key=os.getenv('FRED_API_KEY'); out={}; flags=[]
 for sid,units in SERIES.items():
  if fixture_dir: obs=json.loads((Path(fixture_dir)/f'{sid}.json').read_text())['observations']
  else:
   if not key: raise RuntimeError('FRED_API_KEY is required; refusing to fabricate data')
   q=urllib.parse.urlencode({'series_id':sid,'api_key':key,'file_type':'json','observation_start':start,'observation_end':end.isoformat(),'units':units,'sort_order':'asc'})
   with urllib.request.urlopen('https://api.stlouisfed.org/fred/series/observations?'+q,timeout=30) as r: raw=json.load(r)
   obs=[{'date':o['date'],'value':float(o['value'])} for o in raw.get('observations',[]) if o['value'] not in ('','.')] 
  out[sid]={'retrieved_ts_utc':utcnow_iso(),'units':units,'observations':obs}
  if not obs: flags.append(f'{sid}:EMPTY')
 dump_json(DATA/'fred_cache.json',out); return out,flags
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--as-of');a.add_argument('--fixture-dir');x=a.parse_args();print(json.dumps(fetch_all(x.as_of,x.fixture_dir)[1]))
