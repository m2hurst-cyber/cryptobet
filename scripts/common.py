from pathlib import Path
from datetime import datetime,timezone,date
import json
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; SPEC=ROOT/'spec'; SITE=ROOT/'site'
TICKERS=['XLK','XLF','XLE','XLI','XLV','XLY','XLP','XLU','XLB','XLRE','XLC']; FACTORS=['growth','inflation','rates','credit_stress','curve_steep']; VERSION='1.0'
def utcnow_iso(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_json(p,d=None): return json.loads(p.read_text()) if p.exists() else d
def dump_json(p,o): p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def read_jsonl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def append_jsonl(p,o):
 with p.open('a') as f:f.write(json.dumps(o,sort_keys=True,separators=(',',':'))+'\n')
def holidays(): return {x.strip() for x in (SPEC/'holidays.txt').read_text().splitlines() if x.strip() and not x.startswith('#')}
def is_trading_day(d): return d.weekday()<5 and d.isoformat() not in holidays()
