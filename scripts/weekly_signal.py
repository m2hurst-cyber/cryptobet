import json
from common import DATA,VERSION,read_jsonl,dump_json,utcnow_iso,append_jsonl

def publish():
    rows=read_jsonl(DATA/'model_log.jsonl')
    if not rows: raise RuntimeError('No completed trading-day row')
    r=rows[-1]
    o={'published_ts_utc':utcnow_iso(),'model_version':VERSION,'source_date':r['date'],'public_live':r.get('public_live',False),'factor_scores':r.get('factor_scores',{}),'sector_scores':r.get('sector_scores',{}),'ow':r.get('ow',[]),'uw':r.get('uw',[]),'neutral':r.get('neutral',[]),'prices_close':r.get('prices_close',{}),'data_quality_flags':r.get('data_quality_flags',[])}
    if o['data_quality_flags'] or len(o['ow'])!=3:
        o['ow']=[];o['uw']=[];o['neutral']=[]
    ledger=DATA/'weekly_signal_log.jsonl';past=read_jsonl(ledger)
    same=[x for x in past if x.get('source_date')==o['source_date'] and x.get('model_version')==VERSION]
    if same:
        x=same[-1]
        for k in ['factor_scores','sector_scores','ow','uw','neutral','prices_close','data_quality_flags']:
            if x.get(k)!=o.get(k): raise RuntimeError('weekly publication immutability violation for existing source_date')
        o=x
    else:
        append_jsonl(ledger,o)
    dump_json(DATA/'weekly_signal.json',o);return o
if __name__=='__main__': print(json.dumps(publish(),indent=2))
