#!/usr/bin/env python3
"""Read-only final-effective requirement change resolver; never verifies remote approvals."""
import argparse
import json
from pathlib import Path
import re
import sys

ID = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{0,79}$')
SHA = re.compile(r'^[a-fA-F0-9]{64}$')
STATUSES = {'PROPOSED', 'REJECTED', 'APPROVED'}

def valid(value, pattern):
    return isinstance(value, str) and bool(pattern.fullmatch(value))

def nonblank(value):
    return isinstance(value, str) and 0 < len(value) <= 1024 and bool(value.strip())

def resolve(changes, item_id=None, limit=8):
    if not isinstance(changes, list):
        raise ValueError('INVALID_LEDGER')
    if type(limit) is not int or limit < 1 or limit > 50:
        raise ValueError('INVALID_LIMIT')
    if item_id is not None and not valid(item_id, ID):
        raise ValueError('INVALID_ITEM_ID')
    ids, groups = {}, {}
    for record in changes:
        if not isinstance(record, dict) or not valid(record.get('id'), ID) or \
           not valid(record.get('item_id'), ID) or record.get('status') not in STATUSES or \
           not nonblank(record.get('baseline_ref')) or \
           (record.get('based_on') != 'BASELINE' and not valid(record.get('based_on'), ID)):
            raise ValueError('INVALID_CHANGE_RECORD')
        if record['id'] in ids:
            raise ValueError('DUPLICATE_CHANGE_ID')
        base_digest = record.get('baseline_sha256')
        if base_digest is not None and not valid(base_digest, SHA):
            raise ValueError('INVALID_BASELINE_DIGEST')
        if record['status'] == 'APPROVED' and (not valid(base_digest, SHA) or
            not valid(record.get('final_sha256'), SHA) or
            not nonblank(record.get('final_ref')) or
            not nonblank(record.get('decision', {}).get('by')) or
            not nonblank(record.get('decision', {}).get('ref'))):
            raise ValueError('APPROVAL_EVIDENCE_FIELDS_REQUIRED')
        ids[record['id']] = record
        groups.setdefault(record['item_id'], []).append(record)
    summary = []
    for item, records in groups.items():
        baseline = records[0]['baseline_ref']
        pinned = next((c.get('baseline_sha256') for c in records if c.get('baseline_sha256')), None)
        for c in records:
            if c['baseline_ref'] != baseline or (pinned and c.get('baseline_sha256') and c['baseline_sha256'] != pinned):
                raise ValueError('BASELINE_MISMATCH:' + item)
        approved = [c for c in records if c['status'] == 'APPROVED']
        children = {}
        for c in approved:
            parent = c['based_on']
            if parent != 'BASELINE' and (parent not in ids or
                ids[parent]['item_id'] != item or ids[parent]['status'] != 'APPROVED'):
                raise ValueError('UNAPPROVED_PREDECESSOR:' + c['id'])
            if parent in children:
                raise ValueError('AMBIGUOUS_APPROVED_BRANCH:' + item)
            children[parent] = c
        current, selected, walked = 'BASELINE', None, 0
        while current in children:
            selected = children[current]
            current = selected['id']
            walked += 1
            if walked > len(approved):
                raise ValueError('CHANGE_CYCLE:' + item)
        if walked != len(approved):
            raise ValueError('DISCONNECTED_APPROVAL_CHAIN:' + item)
        if item_id is not None and item != item_id:
            continue
        proposed = [c for c in records if c['status'] == 'PROPOSED']
        summary.append({
            'item_id':item, 'baseline_ref':baseline,
            'effective_change_id':selected['id'] if selected else None,
            'effective_ref':selected['final_ref'] if selected else baseline,
            'pending_count':len(proposed), 'approved_count':len(approved),
            'rejected_count':sum(c['status']=='REJECTED' for c in records),
            'stale_proposals':[c['id'] for c in proposed if c['based_on'] != current][:limit],
            'recent_change_ids':[{'id':c['id'],'status':c['status']} for c in records[-limit:]],
            'approval_externally_verified':False,
            'warning':'Recorded approval claim: verify Owner identity, original/final source hashes and GitHub decision independently.'
        })
    return {'schema':'pcs.requirement-changes.v1','items':summary,
        'warning':'Read-only. An approved requirement is not proof of implemented/tested/accepted work.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--file',type=Path,required=True)
    p.add_argument('--item')
    p.add_argument('--limit',type=int,default=8)
    a=p.parse_args()
    doc=json.loads(a.file.read_text(encoding='utf-8'))
    from tools.pcs_solo import check
    check(doc)
    print(json.dumps(resolve(doc['state'].get('requirement_changes', []),a.item,a.limit),
        ensure_ascii=False,indent=2))

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('PCS_REQUIREMENTS_ERROR:',exc,file=sys.stderr)
        sys.exit(1)
