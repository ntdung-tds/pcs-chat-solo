#!/usr/bin/env python3
"""Read-only bounded context selector for Chat Solo. No GitHub sync or test claims."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pcs_solo import check

SENSITIVE = ('production', 'destructive', 'iam_change', 'credentials_change',
             'external_spend', 'security_sensitive', 'requires_owner_approval')

def context(doc, task_id=None, limit=6):
    check(doc)
    if type(limit) is not int or not 1 <= limit <= 12:
        raise ValueError('INVALID_LIMIT')
    s = doc['state']
    selected_id = task_id if task_id is not None else s['current'].get('active_task')
    task = next((t for t in s['tasks'] if t['id'] == selected_id), None) if selected_id else None
    if selected_id and task is None:
        raise ValueError('TASK_NOT_FOUND')
    flags = [flag for flag in SENSITIVE if task and task.get(flag) is True]
    raw_risk = str(task.get('risk', 'UNKNOWN')).upper() if task else None
    risk = raw_risk if raw_risk in ('LOW', 'NORMAL', 'HIGH', 'CRITICAL') else 'UNKNOWN' if task else None
    elevated = bool(task and (risk not in ('LOW', 'NORMAL') or flags or
                              task.get('classification') in ('CONFIDENTIAL', 'RESTRICTED')))
    active = [t for t in s['tasks'] if t['status'] not in ('ACCEPTED','CANCELLED')]
    active.sort(key=lambda t: 0 if t['id'] == selected_id else 1)
    return {
        'schema':'pcs.solo.context.v1', 'revision':doc['revision'], 'project':s['slug'],
        'active_task':s['current'].get('active_task'),
        'task':({'id':task['id'], 'status':task['status'], 'risk':risk,
                 'dependencies':task.get('dependencies', [])[:20],
                 'dependencies_remaining':max(0,len(task.get('dependencies', []))-20),
                 'sensitive_flags':flags, 'owner_review_required':elevated} if task else None),
        'backlog':{'open':len(active),
                   'shown':[{'id':t['id'],'status':t['status']} for t in active[:limit]],
                   'remaining':max(0,len(active)-limit)},
        'blockers_count':len(s['current'].get('blockers', [])),
        'next_action_present':bool(s['current'].get('next_action')),
        'handoff_contract':{'task_id':task['id'] if task else None,
                            'goal':'FETCH_FROM_APPROVED_SOURCE',
                            'scope':'FETCH_RELEVANT_PATHS',
                            'tests':'NOT_VERIFIED','owner_approval':'NOT_VERIFIED',
                            'next_action':'READ_CANONICAL_MOMENT'},
        'warning':'Metadata only. Verify source evidence, revision and Owner approval independently.'
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--file', type=Path, required=True)
    p.add_argument('--task')
    p.add_argument('--limit', type=int, default=6)
    args = p.parse_args()
    try:
        obj=json.loads(args.file.read_text(encoding='utf-8'))
        print(json.dumps(context(obj, args.task, args.limit), ensure_ascii=False, indent=2))
    except Exception as exc:
        print('PCS_SOLO_CONTEXT: ' + str(exc), file=sys.stderr)
        sys.exit(1)
