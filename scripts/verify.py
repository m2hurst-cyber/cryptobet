#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,io,json,math,os,shutil,subprocess,tempfile,urllib.request
from datetime import date,timedelta
from pathlib import Path
import pandas as pd
from common import ROOT,SPEC,DATA,SITE,TICKERS,FACTORS,read_jsonl

EXPECTED_FRED={'PAYEMS','INDPRO','RSAFS','CPILFESL','PCEPILFE','T5YIFR','DGS10','BAMLH0A0HYM2','BAMLC0A0CM','T10Y2Y'}
RESULTS=[]

def check(name,fn):
    try: RESULTS.append({'gate':name,'status':'PASS','detail':fn() or 'ok'})
    except Exception as e: RESULTS.append({'gate':name,'status':'FAIL','detail':f'{type(e).__name__}: {e}'})

def g1(live):
    if live:
        for sid in sorted(EXPECTED_FRED):
            with urllib.request.urlopen(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}',timeout=25) as r:
                txt=r.read().decode('utf-8','replace')
            rows=list(csv.reader(io.StringIO(txt)))
            if len(rows)<2: raise AssertionError(f'{sid}: no observations')
    return f'{len(EXPECTED_FRED)} distinct frozen v1.0 FRED series resolve to non-empty data' if live else f'{len(EXPECTED_FRED)} frozen IDs parsed'

def g2(live):
    if live:
        import yfinance as yf
        x=yf.download(TICKERS,period='10d',progress=False,auto_adjust=False,threads=True,group_by='column')
        if x.empty: raise AssertionError('yfinance returned no data')
        if isinstance(x.columns,pd.MultiIndex):
            lvl0=set(x.columns.get_level_values(0)); field='Adj Close' if 'Adj Close' in lvl0 else ('Close' if 'Close' in lvl0 else None)
            if not field: raise AssertionError('yfinance response has no Close/Adj Close field')
            frame=x[field]
        else: frame=x
        missing=[t for t in TICKERS if t not in frame.columns or frame[t].dropna().empty]
        if missing: raise AssertionError(f'unresolved tickers: {missing}')
    return 'all 11 sector tickers resolve on yfinance' if live else '11 frozen tickers parsed'

def g3():
    rows=list(csv.DictReader((SPEC/'exposure-matrix.csv').open()))
    if len(rows)!=11: raise AssertionError(f'expected 11 rows, got {len(rows)}')
    if [r['ticker'] for r in rows]!=TICKERS: raise AssertionError('exposure ticker order/universe mismatch')
    if list(rows[0].keys())!=['ticker','growth','inflation','rates','credit_stress','curve_steep']: raise AssertionError('exposure columns mismatch')
    for r in rows:
        for f in FACTORS:
            v=float(r[f])
            if not -1.0<=v<=1.0: raise AssertionError(f'{r["ticker"]}/{f}={v} outside [-1,1]')
    return 'exposure matrix is exactly 11 × 5; all loadings lie in [-1,1]'

def make_fixtures(td:Path):
    fred=td/'fred';fred.mkdir();end=date(2026,9,4);days=[];d=end
    while len(days)<1500:
        if d.weekday()<5: days.append(d)
        d-=timedelta(days=1)
    days=sorted(days);base={'T5YIFR':2.3,'DGS10':4.1,'BAMLH0A0HYM2':3.2,'BAMLC0A0CM':1.1,'T10Y2Y':0.4};amp={'T5YIFR':0.25,'DGS10':0.8,'BAMLH0A0HYM2':0.7,'BAMLC0A0CM':0.25,'T10Y2Y':0.9}
    for sid in base:
        obs=[{'date':dt.isoformat(),'value':base[sid]+amp[sid]*math.sin(i/53)+0.0002*i+0.03*math.cos(i/17)} for i,dt in enumerate(days)];(fred/f'{sid}.json').write_text(json.dumps({'observations':obs}))
    months=[];y,m=2019,10
    for _ in range(84):
        months.append(date(y,m,1));m+=1
        if m==13:y+=1;m=1
    for sid in ['PAYEMS','INDPRO','RSAFS','CPILFESL','PCEPILFE']:
        obs=[]
        for i,dt in enumerate(months):
            v={'PAYEMS':180+60*math.sin(i/7)+.3*i,'INDPRO':2+1.7*math.sin(i/8),'RSAFS':3.5+2*math.cos(i/9),'CPILFESL':2.8+.9*math.sin(i/11),'PCEPILFE':2.6+.7*math.sin(i/10)}[sid];obs.append({'date':dt.isoformat(),'value':v})
        (fred/f'{sid}.json').write_text(json.dumps({'observations':obs}))
    pdates=days[-35:];price=td/'sector_prices.csv'
    with price.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['date','ticker','adj_close','source','carried_forward']);w.writeheader()
        for ti,t in enumerate(TICKERS):
            b=80+ti*9
            for j,dt in enumerate(pdates): w.writerow({'date':dt.isoformat(),'ticker':t,'adj_close':b*(1+.0015*j+.006*math.sin((j+ti)/4)),'source':'fixture','carried_forward':False})
    return fred,price

def g4():
    touched=[DATA/'fred_cache.json',DATA/'sector_prices.csv',DATA/'factor_scores.json',DATA/'model_log.jsonl',DATA/'weekly_signal_log.jsonl',DATA/'metrics.json',DATA/'memo.json',DATA/'weekly_signal.json',SITE/'index.html',SITE/'model.html'];snap={p:(p.read_bytes() if p.exists() else None) for p in touched}
    try:
        (DATA/'fred_cache.json').write_text('{}\n');(DATA/'sector_prices.csv').write_text('date,ticker,adj_close,source,carried_forward\n');(DATA/'model_log.jsonl').write_text('');(DATA/'weekly_signal_log.jsonl').write_text('');(DATA/'weekly_signal.json').write_text('{"public_live":false,"ow":[],"uw":[],"neutral":[]}\n')
        with tempfile.TemporaryDirectory() as td:
            fred,price=make_fixtures(Path(td));from daily_runner import run;result=run('2026-09-04',str(fred),str(price))
        rows=read_jsonl(DATA/'model_log.jsonl')
        if result.get('status')!='ok' or len(rows)!=1: raise AssertionError('daily_runner did not append exactly one row')
        r=rows[0];required={'date','run_ts_utc','model_version','public_live','factor_scores','sector_scores','ow','uw','neutral','prices_close','data_quality_flags','forward_returns'}
        if set(r)!=required: raise AssertionError(f'log schema mismatch: {set(r)^required}')
        if r['model_version']!='1.0' or r['public_live'] is not False: raise AssertionError('version/live gate mismatch')
        if len(r['factor_scores'])!=5 or len(r['sector_scores'])!=11 or len(r['ow'])!=3 or len(r['uw'])!=3 or len(r['neutral'])!=5: raise AssertionError('invalid factors/ranking dimensions')
        return 'one full daily_runner end-to-end run produced a valid immutable v1.0 log row'
    finally:
        for p,b in snap.items():
            if b is None:
                if p.exists(): p.unlink()
            else: p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)

def g5():
    from compute_metrics import compute
    lp=DATA/'model_log.jsonl';wp=DATA/'weekly_signal_log.jsonl';mp=DATA/'metrics.json';old=(lp.read_bytes(),wp.read_bytes(),mp.read_bytes())
    try:
        lp.write_text('');wp.write_text('');m=compute();expected={'hit_rate':'N/A — need 8 more weeks','long_short_cumulative_return':'N/A — need 1 more week','ic_12w':'N/A — need 12 more weeks','ic_inception':'N/A — need 12 more weeks','turnover':'N/A — need 4 more weeks'}
        for k,v in expected.items():
            if m.get(k)!=v: raise AssertionError(f'{k}: expected {v!r}, got {m.get(k)!r}')
        return 'empty-log metrics return exact sample-size N/A gates'
    finally: lp.write_bytes(old[0]);wp.write_bytes(old[1]);mp.write_bytes(old[2])

def g6():
    from site_builder import build
    build()
    try: from playwright.sync_api import sync_playwright
    except ImportError as e: raise RuntimeError('Playwright is required for headless site verification') from e
    errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto((SITE/'index.html').as_uri());page.wait_for_load_state('load')
        if 'Model spinning up' not in page.locator('body').inner_text(): raise AssertionError('OFF-state spin-up panel missing')
        page.get_by_role('button',name='RGIP Dashboard').click();page.get_by_role('button',name='Inflation').click();page.goto((SITE/'model.html').as_uri());page.wait_for_load_state('load')
        if 'Full historical model log' not in page.locator('body').inner_text(): raise AssertionError('model log table missing')
        browser.close()
    if errors: raise AssertionError('JavaScript page errors: '+'; '.join(errors))
    return 'index.html and model.html render in headless Chromium; interactive tabs execute without JS errors'

def g7():
    out=SITE/'assets/methodology.pdf';p=subprocess.run(['pandoc',str(SPEC/'methodology.md'),'-s','--pdf-engine=weasyprint','-o',str(out)],capture_output=True,text=True,timeout=90)
    if p.returncode!=0 or not out.exists() or out.stat().st_size<1000: raise AssertionError(p.stderr[-1000:])
    return f'methodology PDF builds successfully ({out.stat().st_size} bytes)'

def g8():
    if (SPEC/'public_live.txt').read_text().strip().lower()!='false': raise AssertionError('spec/public_live.txt must be false')
    rows=read_jsonl(DATA/'model_log.jsonl')
    if rows and rows[-1].get('public_live') is not False: raise AssertionError('latest production log row public_live is not false')
    return 'public_live=false in frozen configuration'+(' and latest log row' if rows else '; no production row exists yet')

def g9():
    actionlint=shutil.which('actionlint')
    if not actionlint: raise RuntimeError('actionlint unavailable')
    p=subprocess.run([actionlint],cwd=ROOT,capture_output=True,text=True,timeout=30)
    if p.returncode: raise AssertionError((p.stdout+p.stderr)[-3000:])
    return 'all GitHub Actions workflows pass actionlint'

def g10():
    txt=(ROOT/'README.md').read_text().lower()
    for phrase in ['how to add a factor','how to flip public_live','how to troubleshoot cron failures']:
        if phrase not in txt: raise AssertionError(f'missing README section: {phrase}')
    return 'README documents factor versioning, live-flag flip, and cron troubleshooting'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--live-resolution',action='store_true');args=ap.parse_args()
    check('1_fred_series',lambda:g1(args.live_resolution));check('2_sector_tickers',lambda:g2(args.live_resolution));check('3_exposure_matrix',g3);check('4_end_to_end',g4);check('5_metric_gates',g5);check('6_site_render',g6);check('7_methodology_pdf',g7);check('8_public_live_off',g8);check('9_actionlint',g9);check('10_readme',g10)
    (ROOT/'verification-report.json').write_text(json.dumps(RESULTS,indent=2)+'\n');print(json.dumps(RESULTS,indent=2));fails=[r for r in RESULTS if r['status']=='FAIL']
    if fails:
        with (SPEC/'decisions.md').open('a') as f:
            f.write('\n## Verification failure log — '+date.today().isoformat()+'\n')
            for r in fails:f.write(f"- {r['gate']}: {r['detail']}\n")
    return 1 if fails else 0
if __name__=='__main__': raise SystemExit(main())
