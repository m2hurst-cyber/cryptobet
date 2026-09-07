import csv,json
from common import SPEC,TICKERS,FACTORS
def score_and_rank(f):
 if any(f.get(k) is None for k in FACTORS): return {'sector_scores':{},'ow':[],'neutral':[],'uw':[],'no_call':True}
 with (SPEC/'exposure-matrix.csv').open() as h: rows=list(csv.DictReader(h))
 s={r['ticker']:sum(float(r[k])*float(f[k]) for k in FACTORS) for r in rows}; rank=sorted(TICKERS,key=lambda t:(-s[t],t));return {'sector_scores':s,'ow':rank[:3],'neutral':rank[3:8],'uw':rank[8:],'no_call':False}
