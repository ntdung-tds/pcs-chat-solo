#!/usr/bin/env python3
"""Single-file PCS SRS delta ledger, read on demand; never sync original SRS."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
from uuid import uuid4

HEADER='# PCS SRS Changes\n<!-- pcs-srs-changes:v1 -->\n'
ID=re.compile(r'^[A-Za-z][A-Za-z0-9._-]{0,79}$')
BLOCK=re.compile(r'^```pcs-change\n([^\n]+)\n```$',re.MULTILINE)
def guard(ok,code):
    if not ok: raise ValueError('PCS_SRS_CHANGE: '+code)
def identifier(x):return isinstance(x,str) and bool(ID.fullmatch(x))
def good(x,max_len=2000):return isinstance(x,str) and bool(x.strip()) and len(x)<=max_len
def date(x):
    if not good(x,64) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})',x):
        return False
    try:
        parsed=datetime.fromisoformat(x.replace('Z','+00:00'))
        return parsed.tzinfo is not None and abs(parsed.utcoffset().total_seconds())<=14*3600
    except (ValueError,TypeError,OverflowError):return False

def parse_ledger(markdown=HEADER):
    guard(isinstance(markdown,str) and markdown.startswith(HEADER),'INVALID_HEADER')
    events,proposals,decided,tips=[],{},set(),{}
    for match in BLOCK.finditer(markdown):
        try:e=json.loads(match.group(1))
        except json.JSONDecodeError as exc:raise ValueError('PCS_SRS_CHANGE: INVALID_EVENT_JSON') from exc
        guard(isinstance(e,dict) and identifier(e.get('id')),'INVALID_CHANGE_ID')
        if e.get('kind')=='PROPOSE':
            guard(e['id'] not in proposals,'DUPLICATE_CHANGE_ID')
            guard(identifier(e.get('item_key')) and identifier(e.get('task_id')),'INVALID_WORK_CONTEXT')
            guard(e.get('feature_id') is None or identifier(e.get('feature_id')),'INVALID_FEATURE')
            guard(e.get('srs_ref')=='UNMAPPED' or good(e.get('srs_ref'),512),'INVALID_SRS_REF')
            guard(good(e.get('before')) and good(e.get('after')) and e['before']!=e['after'],'INVALID_DELTA')
            guard(good(e.get('reason'),512) and date(e.get('at')),'INVALID_PROVENANCE')
            guard(e.get('based_on')==tips.get(e['item_key'],'BASELINE'),'STALE_PROPOSAL_BASE:'+e['id'])
            proposals[e['id']]=e
        elif e.get('kind')=='DECIDE':
            p=proposals.get(e['id'])
            guard(p is not None and e['id'] not in decided,'MISSING_OR_DUPLICATE_PROPOSAL')
            guard(e.get('decision') in ('APPROVED','REJECTED'),'INVALID_DECISION')
            guard(good(e.get('actor'),256) and good(e.get('ref'),1024) and date(e.get('at')),'DECISION_PROVENANCE_REQUIRED')
            if e['decision']=='APPROVED':
                guard(p['based_on']==tips.get(p['item_key'],'BASELINE'),'STALE_APPROVAL_BASE:'+e['id'])
                tips[p['item_key']]=e['id']
            decided.add(e['id'])
        else:raise ValueError('PCS_SRS_CHANGE: INVALID_EVENT_KIND')
        events.append(e)
    guard(len(re.findall(r'^```pcs-change$',markdown,re.MULTILINE))==len(events),'UNPARSED_EVENT')
    return {'events':events,'proposals':proposals,'decided':decided,'tips':tips}

def active_context(doc,tasks=None,features=None):
    s=doc.get('state',doc)
    tasks=tasks if tasks is not None else s.get('tasks')
    features=features if features is not None else s.get('features',[])
    tid=s.get('current',{}).get('active_task') or s.get('project',{}).get('active_task_id')
    guard(identifier(tid) and isinstance(tasks,list),'ACTIVE_TASK_REQUIRED')
    task=next((t for t in tasks if t.get('id')==tid),None)
    guard(task is not None,'ACTIVE_TASK_NOT_FOUND')
    related=[f for f in features if tid in f.get('required_tasks',[]) or f.get('id') in task.get('feature_ids',[])]
    feature=related[0] if len(related)==1 else None
    ref=task.get('srs_ref') or task.get('requirement_ref') or (feature or {}).get('srs_ref') or 'UNMAPPED'
    return {'task_id':tid,'feature_id':feature['id'] if feature else None,
        'item_key':feature['id'] if feature else tid,'srs_ref':ref if good(ref,512) else 'UNMAPPED',
        'mapping':'ACTIVE_CONTEXT','ambiguous_features':len(related)>1}

def append_event(markdown,event):
    before=parse_ledger(markdown)
    heading='### '+event.get('id','INVALID')+' — '+event.get('kind','INVALID')
    if event.get('kind')=='DECIDE':heading+=' '+event.get('decision','')
    updated=markdown.rstrip()+'\n\n'+heading+'\n\n```pcs-change\n'+json.dumps(event,ensure_ascii=False,separators=(',',':'))+'\n```\n'
    guard(len(parse_ledger(updated)['events'])==len(before['events'])+1,'EVENT_NOT_APPENDED')
    return updated

def propose_from_active(markdown,doc,change,tasks=None,features=None):
    context=active_context(doc,tasks,features)
    guard(identifier(change.get('id')),'INVALID_CHANGE_ID')
    # The agent derives a stable criterion slug; the Owner never supplies a section number.
    # Feature/Task identifies context, but is not a unique requirement.
    requirement_key=change.get('requirement_key')
    guard(isinstance(requirement_key,str) and bool(re.fullmatch(r'[a-z][a-z0-9-]{1,39}',requirement_key)),
          'REQUIREMENT_KEY_REQUIRED')
    item_key=context['item_key']+'.'+requirement_key
    guard(identifier(item_key),'REQUIREMENT_SCOPE_TOO_LONG')
    ledger=parse_ledger(markdown)
    # A legacy unscoped Feature/Task chain must be reconciled, not silently forked.
    guard(not any(p['item_key']==context['item_key'] and 'requirement_key' not in p
        for p in ledger['proposals'].values()),'LEGACY_SCOPE_REVIEW_REQUIRED')
    prior=ledger['proposals'].get(ledger['tips'].get(item_key))
    if prior:guard(change.get('before')==prior['after'],'DELTA_BASELINE_MISMATCH')
    event={'kind':'PROPOSE','id':change['id'],**context,'item_key':item_key,
        'requirement_key':requirement_key,'based_on':ledger['tips'].get(item_key,'BASELINE'),
        'before':change.get('before'),'after':change.get('after'),'reason':change.get('reason'),
        'at':change.get('at') or datetime.now(timezone.utc).isoformat()}
    if 'source_ref' in change:event['source_ref']=change['source_ref']
    return event,append_event(markdown,event)

def summary(markdown,item_key=None,limit=6,task_id=None,feature_id=None,max_items=8):
    guard(type(limit) is int and 1<=limit<=20,'INVALID_LIMIT')
    guard(type(max_items) is int and 1<=max_items<=50,'INVALID_MAX_ITEMS')
    for x in (item_key,task_id,feature_id):
        if x is not None:guard(identifier(x),'INVALID_FILTER')
    ledger=parse_ledger(markdown);proposals=ledger['proposals'];decided=ledger['decided'];tips=ledger['tips']
    keys=[item_key] if item_key else list(dict.fromkeys(p['item_key'] for p in proposals.values()
        if (not task_id or p['task_id']==task_id) and (not feature_id or p.get('feature_id')==feature_id)))
    items=[]
    for key in keys[:max_items]:
        all_=[p for p in proposals.values() if p['item_key']==key]
        tip=tips.get(key);final=proposals.get(tip)
        items.append({'item_key':key,'task_id':all_[-1]['task_id'] if all_ else None,
            'feature_id':all_[-1].get('feature_id') if all_ else None,
            'requirement_key':all_[-1].get('requirement_key') if all_ else None,
            'srs_ref':all_[-1]['srs_ref'] if all_ else 'UNMAPPED',
            'effective_change_id':tip,'effective_delta':{'before':final['before'],'after':final['after']} if final else None,
            'pending_count':sum(p['id'] not in decided for p in all_), 'history_count':len(all_),
            'recent_change_ids':[p['id'] for p in all_[-limit:]],'verified_external_decision':False})
    return {'schema':'pcs.srs-changes.v1','items':items,'total_items':len(keys),
        'remaining_items':max(0,len(keys)-max_items),
        'warning':'Recorded decision needs independent GitHub verification; never auto-update original SRS.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'))
    p.add_argument('--item');p.add_argument('--task');p.add_argument('--feature');p.add_argument('--limit',type=int,default=6)
    p.add_argument('--max-items',type=int,default=8)
    p.add_argument('--record',type=Path);p.add_argument('--expect');a=p.parse_args()
    file=a.root/'pcs'/'SRS_CHANGES.md'
    if a.record:
        lock=file.with_suffix('.md.lock')
        with lock.open('x',encoding='utf-8'):
            try:
                current=file.read_text(encoding='utf-8') if file.exists() else HEADER
                if a.expect:guard(hashlib.sha256(current.encode()).hexdigest()==a.expect,'STALE_FILE_HASH')
                event=json.loads(a.record.read_text(encoding='utf-8'))
                if event.get('kind')=='PROPOSE':
                    doc=json.loads((a.root/'pcs'/'STATE.json').read_text(encoding='utf-8'))
                    event,updated=propose_from_active(current,doc,event)
                else:updated=append_event(current,event)
                temp=file.with_name(file.name+'.'+uuid4().hex+'.tmp')
                temp.write_text(updated,encoding='utf-8');temp.replace(file)
                print(json.dumps({'recorded':event['id'],'kind':event['kind'],
                    'sha256':hashlib.sha256(updated.encode()).hexdigest()}))
            finally:lock.unlink(missing_ok=True)
    else:
        current=file.read_text(encoding='utf-8') if file.exists() else HEADER
        print(json.dumps(summary(current,a.item,a.limit,task_id=a.task,feature_id=a.feature,max_items=a.max_items),ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:raise SystemExit(str(exc)) from exc
