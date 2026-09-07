import argparse,json
from datetime import date
from common import DATA,SPEC,TICKERS,VERSION,utcnow_iso,is_trading_day,append_jsonl,read_jsonl
from backfill_returns import backfill
from fetch_fred import fetch_all
from fetch_prices import fetch_prices
from compute_factors import compute
from score_and_rank import score_and_rank
from compute_metrics import compute as metrics
from memo_generator import generate
from site_builder import build
def run(as_of=None,fixture_dir=None,fixture_prices=None):
 d=date.fromisoformat(as_of) if as_of else date.today()
 if not is_trading_day(d):return {'status':'skipped','date':d.isoformat()}
 backfill();fetch_all(d.isoformat(),fixture_dir);px,_=fetch_prices(d.isoformat(),fixture_prices);f=compute(d.isoformat());r=score_and_rank(f['factors']);latest_date=px.date.max();latest=px[px.date==latest_date];day=latest.set_index('ticker').adj_close.to_dict();flags=list(f.get('data_quality_flags',[]));flags += [f'{x.ticker}:PRICE_CARRIED_FORWARD' for x in latest.itertuples() if bool(x.carried_forward)];missing=[t for t in TICKERS if t not in day];flags += [f'{t}:MISSING_PRICE' for t in missing];rows=read_jsonl(DATA/'model_log.jsonl')
 if any(x['date']==d.isoformat() for x in rows):raise RuntimeError('append-only violation: date exists')
 live=(SPEC/'public_live.txt').read_text().strip().lower()=='true';row={'date':d.isoformat(),'run_ts_utc':utcnow_iso(),'model_version':VERSION,'public_live':live,'factor_scores':f['factors'],'sector_scores':r['sector_scores'],'ow':r['ow'],'uw':r['uw'],'neutral':r['neutral'],'prices_close':{t:float(day[t]) for t in TICKERS if t in day},'data_quality_flags':flags,'forward_returns':{'1d':None,'5d':None,'20d':None}}
 if r['no_call'] or missing:row['ow']=row['uw']=row['neutral']=[];row['data_quality_flags'].append('NO_CALL_DATA_QUALITY')
 append_jsonl(DATA/'model_log.jsonl',row);metrics();generate();build();return {'status':'ok','row':row}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--as-of');a.add_argument('--fixture-dir');a.add_argument('--fixture-prices');x=a.parse_args();print(json.dumps(run(x.as_of,x.fixture_dir,x.fixture_prices),indent=2))
