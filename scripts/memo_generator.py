import json
from common import DATA,load_json,dump_json,utcnow_iso
LABEL={'growth':'growth','inflation':'inflation','rates':'rates','credit_stress':'credit stress','curve_steep':'curve steepness'}
def generate():
 f=load_json(DATA/'factor_scores.json',{}).get('factors',{});w=load_json(DATA/'weekly_signal.json',{});x=[(k,v) for k,v in f.items() if isinstance(v,(int,float))]
 pos=sorted(x,key=lambda q:q[1],reverse=True)[:2];neg=sorted(x,key=lambda q:q[1])[:2];lead=max(x,key=lambda q:abs(q[1])) if x else ('growth',0.0)
 ptxt=', '.join(f'{LABEL[k]} ({v:+.2f}z)' for k,v in pos) or 'not available';ntxt=', '.join(f'{LABEL[k]} ({v:+.2f}z)' for k,v in neg) or 'not available'
 if w.get('public_live') and len(w.get('ow',[]))==3: call=f"The frozen weekly ranking is overweight {', '.join(w['ow'])}, underweight {', '.join(w['uw'])}, with the remaining five sectors neutral."
 else: call='The public sector call remains hidden during the prescribed spin-up period; shadow rankings continue to accumulate in the immutable log.'
 lv=lead[1]; target=-0.5 if lv>0 else 0.5
 text=(f"Thesis: Macro Model v1.0 is translating the current five-factor macro configuration into relative sector scores while its live, forward-only record accumulates. "
       f"The two strongest positive factor readings are {ptxt}; the two weakest readings are {ntxt}. These readings are standardized against trailing five-year histories, so magnitude reflects how unusual the current environment is rather than an absolute economic forecast. "
       f"{call} The sector ranking is mechanical: frozen factor scores are multiplied by the frozen sector exposure matrix, then ranked top-three, middle-five, bottom-three with no discretionary override. "
       f"Data quality remains part of the signal: a stale FRED component suppresses the call rather than being filled with a model estimate. "
       f"What would change the view: {LABEL[lead[0]]}, currently {lv:+.2f}z, is the largest absolute macro impulse. A move through {target:+.1f}z would represent a material reversal of that impulse and could reorder sector scores. "
       "The weekly implementation remains frozen until the next scheduled Sunday publication; intraday market moves do not change the model's rebalance frequency.")
 words=text.split();
 if len(words)<150:
  text+=' The benchmark for evaluation is the equal-weight basket of all eleven sector ETFs, while realized relative performance is recorded only after it becomes observable.'
 words=text.split();text=' '.join(words[:250])
 o={'generated_ts_utc':utcnow_iso(),'text':text};dump_json(DATA/'memo.json',o);return o
if __name__=='__main__':print(json.dumps(generate(),indent=2))
