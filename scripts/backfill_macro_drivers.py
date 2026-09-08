#!/usr/bin/env python3
from __future__ import annotations
import io, json, math, os
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'macro_driver_history.json'
RAW=ROOT/'data'/'macro_history_cache'
RAW.mkdir(parents=True,exist_ok=True)

# Historical-location layer only. Momentum (-5..+5) remains the separate Daily Macro Pulse score.
# Each component is standardized over a trailing 60-month window; parent level is the
# equal-weight average of available oriented component z-scores, converted to a trailing
# 60-month percentile. This is intentionally separate from Macro Model v1.0 sector factors.
DRIVERS={
 'Growth / activity':[
  ('INDPRO','yoy',1),('PAYEMS','yoy',1),('RSAFS','yoy',1),('GDPC1','yoy',1)],
 'Consumer':[
  ('DSPIC96','yoy',1),('PCEC96','yoy',1),('RRSFS','yoy',1),('UMCSENT','level',1)],
 'Housing':[
  ('MORTGAGE30US','level',-1),('HOUST','yoy',1),('PERMIT','yoy',1),('HSN1F','yoy',1),('MSACSR','level',-1),('CSUSHPINSA','yoy',1)],
 'Labor market':[
  ('PAYEMS','yoy',1),('UNRATE','level',-1),('LNS12300060','level',1),('ICSA','level',-1),('CCSA','level',-1),('JTSHIR','level',1),('CES0500000003','yoy',1)],
 'Prices / inflation':[
  ('CPILFESL','yoy',1),('CPIAUCSL','yoy',1),('PCEPILFE','yoy',1),('PCEPI','yoy',1),('PPIACO','yoy',1),('CUSR0000SAH1','yoy',1),('T5YIFR','level',1)],
 'Fiscal impulse':[
  ('FGEXPND','yoy',1),('FGRECPT','yoy',-1),('GFDEBTN','yoy',1)],
 'Financial conditions':[
  ('NFCI','level',-1),('DGS2','level',-1),('DGS10','level',-1),('DFII10','level',-1),('DTWEXBGS','level',-1),('VIXCLS','level',-1)],
 'Credit / liquidity':[
  ('BAMLH0A0HYM2','level',-1),('BAMLC0A0CM','level',-1),('DRTSCILM','level',-1),('TOTCI','yoy',1),('DRALACBS','level',-1)],
 'Market expectations':[
  ('T10Y2Y','level',1),('T5YIE','level',1),('SP500','yoy',1),('VIXCLS','level',-1)],
 'Trade / global':[
  ('EXPGS','yoy',1),('IMPGS','yoy',-1),('DTWEXBGS','level',-1),('GSCPI','level',-1)],
 'Corporate earnings':[
  ('CP','yoy',1),('CPATAX','yoy',1),('A053RC1Q027SBEA','yoy',1)]
}

START='2019-01-01'
END=datetime.now(timezone.utc).date().isoformat()


def fred_csv(sid:str)->pd.Series:
    url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}'
    r=requests.get(url,timeout=30,headers={'User-Agent':'RGIP-Macro-Pulse/1.0'})
    r.raise_for_status()
    df=pd.read_csv(io.StringIO(r.text))
    if df.shape[1]<2: raise ValueError(f'{sid}: malformed CSV')
    d=pd.to_datetime(df.iloc[:,0],errors='coerce')
    v=pd.to_numeric(df.iloc[:,1],errors='coerce')
    s=pd.Series(v.values,index=d,name=sid).dropna()
    if s.empty: raise ValueError(f'{sid}: no observations')
    # Persist source download once. Subsequent release-aware updater can append/revise this cache.
    df.to_csv(RAW/f'{sid}.csv',index=False)
    return s


def monthly(s:pd.Series)->pd.Series:
    # Use last observation available within each calendar month, then carry released values forward.
    return s.resample('ME').last().ffill()


def transform(s:pd.Series,kind:str)->pd.Series:
    s=monthly(s)
    if kind=='yoy': return s.pct_change(12)*100.0
    return s


def rolling_z(s:pd.Series,window=60,minp=24)->pd.Series:
    mu=s.rolling(window,min_periods=minp).mean()
    sd=s.rolling(window,min_periods=minp).std(ddof=0).replace(0,np.nan)
    return (s-mu)/sd


def rolling_percentile(s:pd.Series,window=60,minp=24)->pd.Series:
    def pct(x):
        a=np.asarray(x,dtype=float)
        a=a[np.isfinite(a)]
        if len(a)==0:return np.nan
        return 100.0*(np.sum(a<a[-1])+0.5*np.sum(a==a[-1]))/len(a)
    return s.rolling(window,min_periods=minp).apply(pct,raw=True)

series_cache={}
errors={}
all_ids=sorted({sid for comps in DRIVERS.values() for sid,_,_ in comps})
for sid in all_ids:
    try: series_cache[sid]=fred_csv(sid)
    except Exception as e: errors[sid]=str(e)

payload={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'history_start':START,
         'method':'Trailing 60-month oriented component z-scores -> equal-weight parent composite -> trailing 60-month percentile',
         'drivers':{},'series_errors':errors,'series_cache_status':{}}
for sid,s in series_cache.items():
    payload['series_cache_status'][sid]={
      'source':f'https://fred.stlouisfed.org/series/{sid}',
      'last_observation_date':s.index.max().date().isoformat(),
      'cached_at_utc':payload['generated_at_utc']
    }

for name,comps in DRIVERS.items():
    zs=[]; used=[]; unavailable=[]
    component_latest={}
    for sid,kind,sign in comps:
        if sid not in series_cache:
            unavailable.append(sid); continue
        t=transform(series_cache[sid],kind)
        z=rolling_z(t)*sign
        zs.append(z.rename(sid)); used.append(sid)
        vv=t.dropna()
        component_latest[sid]={
          'latest_date': vv.index.max().date().isoformat() if len(vv) else None,
          'latest_value': round(float(vv.iloc[-1]),6) if len(vv) else None,
          'transformation':kind,'orientation':sign
        }
    if len(zs)<2:
        payload['drivers'][name]={'status':'insufficient','used_components':used,'unavailable_components':unavailable}
        continue
    frame=pd.concat(zs,axis=1).sort_index()
    # Require at least half of defined components when possible; otherwise available verified set.
    parent=frame.mean(axis=1,skipna=True)
    pct=rolling_percentile(parent)
    last12=pct.dropna().tail(12)
    if last12.empty:
        payload['drivers'][name]={'status':'insufficient_history','used_components':used,'unavailable_components':unavailable}
        continue
    current=float(last12.iloc[-1])
    q='Q1' if current<=25 else 'Q2' if current<=50 else 'Q3' if current<=75 else 'Q4'
    payload['drivers'][name]={
      'status':'verified_partial' if unavailable else 'verified',
      'used_components':used,'unavailable_components':unavailable,
      'component_latest':component_latest,
      'current_percentile':round(current,1),'quartile':q,
      'latest_date':last12.index[-1].date().isoformat(),
      'history_1y':[{'date':idx.date().isoformat(),'percentile':round(float(val),1)} for idx,val in last12.items()]
    }

OUT.write_text(json.dumps(payload,indent=2),encoding='utf-8')
print(json.dumps({'out':str(OUT),'drivers':{k:v.get('status') for k,v in payload['drivers'].items()},'errors':errors},indent=2))
