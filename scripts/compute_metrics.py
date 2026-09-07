import math,json,pandas as pd
from scipy.stats import spearmanr
from datetime import date,timedelta
from common import DATA,TICKERS,read_jsonl,dump_json

def gate(n,k): return f'N/A — need {max(0,k-n)} more weeks' if n<k else None

def nextweek(k):
    d=date.fromisocalendar(k[0],k[1],1)+timedelta(days=7);i=d.isocalendar();return(i.year,i.week)

def compute():
    daily=read_jsonl(DATA/'model_log.jsonl');published=read_jsonl(DATA/'weekly_signal_log.jsonl')
    try: px=pd.read_csv(DATA/'sector_prices.csv').pivot_table(index='date',columns='ticker',values='adj_close',aggfunc='last').sort_index()
    except Exception: px=pd.DataFrame()
    first={}
    for ds in px.index:
        d=pd.Timestamp(ds);first.setdefault((int(d.isocalendar().year),int(d.isocalendar().week)),ds)
    weekly=[]
    for sig in published:
        if len(sig.get('ow',[]))!=3 or len(sig.get('uw',[]))!=3: continue
        d=pd.Timestamp(sig['source_date']);source_week=(int(d.isocalendar().year),int(d.isocalendar().week));perf_week=nextweek(source_week);end_week=nextweek(perf_week);a,b=first.get(perf_week),first.get(end_week)
        if not a or not b: continue
        try: ret={t:float(px.loc[b,t]/px.loc[a,t]-1) for t in TICKERS}
        except Exception: continue
        ow=sum(ret[t] for t in sig['ow'])/3;uw=sum(ret[t] for t in sig['uw'])/3;weekly.append({'published_ts_utc':sig['published_ts_utc'],'signal_date':sig['source_date'],'start':a,'end':b,'ow_return':ow,'uw_return':uw,'benchmark_return':sum(ret.values())/11,'ls_return':ow-uw})
    n=len(weekly);hit=gate(n,8) or sum(x['ow_return']>x['uw_return'] for x in weekly)/n;cum=math.prod(1+x['ls_return'] for x in weekly)-1 if n else 'N/A — need 1 more week'
    bydate={r['date']:r for r in daily};ics=[]
    for sig in published:
        r=bydate.get(sig.get('source_date'));fr=(r.get('forward_returns') or {}).get('5d') if r else None
        if fr and sig.get('sector_scores'):
            q=spearmanr([sig['sector_scores'][t] for t in TICKERS],[fr[t] for t in TICKERS]).statistic
            if math.isfinite(q):ics.append(float(q))
    ig=gate(len(ics),12);valid=[s for s in published if len(s.get('ow',[]))==3 and len(s.get('uw',[]))==3];turns=[]
    for a,b in zip(valid,valid[1:]):turns.append(len(set(b['ow'])-set(a['ow']))/3+len(set(b['uw'])-set(a['uw']))/3)
    out={'weekly_observations':n,'hit_rate':hit,'long_short_cumulative_return':cum,'ic_12w':ig or sum(ics[-12:])/12,'ic_inception':ig or sum(ics)/len(ics),'turnover':gate(len(valid),4) or (sum(turns)/len(turns) if turns else 0.0),'weekly_history':weekly};dump_json(DATA/'metrics.json',out);return out
if __name__=='__main__': print(json.dumps(compute(),indent=2))
