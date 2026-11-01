#!/usr/bin/env python3
"""Optional offline state helper. Never claims to synchronize to GitHub."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone

STATUSES = {'PLANNED', 'IN_PROGRESS', 'BLOCKED', 'TECH_DONE',
            'INTEGRATION_PENDING', 'ACCEPTED', 'CANCELLED'}
TYPES = ['tasks', 'features', 'flows', 'releases']
ID = re.compile(r'^[A-Za-z][A-Za-z0-9._-]{0,79}$')
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]{1,62}$')
FORBIDDEN = {'collaboration', 'agent_registry', 'lead', 'contributors', 'assignments', 'agent_proposals'}


def clock():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def stable(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(obj):
    return hashlib.sha256(stable(obj).encode('utf-8')).hexdigest()


def check(obj):
    if not __debug__:
        raise RuntimeError('PCS Solo refuses Python -O: state validation must remain active')
    assert isinstance(obj, dict) and obj.get('schema') == 'pcs.solo.v1', 'Invalid wrapper schema'
    assert type(obj.get('revision')) is int and obj['revision'] > 0, 'Invalid revision'
    s = obj.get('state')
    assert isinstance(s, dict) and s.get('schema') == 'pcs.solo.project.v1', 'Invalid project schema'
    assert isinstance(s.get('slug'), str) and SLUG.fullmatch(s['slug']) and not s['slug'].endswith('-'), 'Invalid slug'
    assert isinstance(s.get('name'), str) and s['name'].strip(), 'Missing project name'
    assert not (FORBIDDEN & set(s)), 'Multi-agent fields forbidden in Solo state'
    for key in TYPES + ['source_refs', 'decisions', 'risks', 'artifacts']:
        assert isinstance(s.get(key), list), f'Invalid {key} list'
    assert isinstance(s.get('product_map'), dict) and isinstance(s.get('architecture_map'), dict), 'Missing maps'
    assert isinstance(s.get('policy'), dict), 'Missing policy'
    visibility = s['policy'].get('repository_visibility', 'USER_CHOICE')
    assert visibility in ('PUBLIC', 'PRIVATE', 'USER_CHOICE'), 'Invalid repository visibility'
    if visibility == 'PUBLIC':
        assert s['policy'].get('content_classification') == 'PUBLIC' and s['policy'].get('public_content_reviewed') is True, 'PUBLIC_POLICY_REQUIRED: explicit review'
        for group in TYPES + ['source_refs', 'decisions', 'risks', 'artifacts']:
            assert all(isinstance(x, dict) and x.get('classification') == 'PUBLIC' for x in s[group]), 'PUBLIC_DATA_BLOCKED: ' + group
    raw = stable(s)
    assert not re.search(r'(?<![A-Za-z0-9_])(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{25,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)', raw), 'SECURITY_BLOCKED: suspected credentials'

    current = s.get('current')
    assert isinstance(current, dict) and isinstance(current.get('next_action'), str) and current['next_action'].strip(), 'Missing next_action'
    seen, tasks = set(), {}
    for collection in TYPES:
        for t in s[collection]:
            assert isinstance(t, dict) and isinstance(t.get('id'), str) and ID.fullmatch(t['id']), 'Invalid item id'
            assert t['id'] not in seen, 'Duplicate item id'
            seen.add(t['id'])
            assert t.get('status') in STATUSES, 'Invalid status'
            if collection == 'tasks':
                tasks[t['id']] = t
            if t['status'] == 'ACCEPTED':
                assert t.get('evidence') and any(e.get('verified') is True and e.get('ref') for e in t['evidence']), 'ACCEPTED needs verified evidence'
                assert t.get('acceptance', {}).get('decision') == 'APPROVED', 'ACCEPTED needs approval'
                if collection == 'tasks' and t.get('qa', {}).get('required', True):
                    assert t.get('qa', {}).get('status') == 'PASS', 'Task QA not passed'
                if collection == 'features':
                    assert t.get('integration', {}).get('status') == 'PASS', 'Feature integration not passed'
                if collection == 'flows':
                    assert t.get('e2e', {}).get('status') == 'PASS', 'Flow E2E not passed'
                if collection == 'releases':
                    assert t.get('security', {}).get('status') == 'PASS' and t.get('rollback', {}).get('status') == 'PASS', 'Release security/rollback not passed'
    for t in tasks.values():
        deps = t.get('dependencies', [])
        assert isinstance(deps, list) and len(deps) == len(set(deps)), 'Invalid dependencies'
        assert all(d in tasks and d != t['id'] for d in deps), 'Missing/self dependency'
    visited, visiting = set(), set()
    def walk(id_):
        assert id_ not in visiting, 'Dependency cycle'
        if id_ in visited:
            return
        visiting.add(id_)
        for dep in tasks[id_].get('dependencies', []):
            walk(dep)
        visiting.remove(id_)
        visited.add(id_)
    for id_ in tasks:
        walk(id_)
    assert len(stable(obj).encode('utf-8')) < 750000, 'State too large'
    return True


def moment(obj):
    check(obj)
    s = obj['state']
    rows = [f'# PCS Chat Solo Moment — {s["name"]}', '',
        f'- Revision: {obj["revision"]}', f'- Updated: {obj["updated_at"]}',
        '- Source: `pcs/STATE.json`', f'- Phase: {s.get("phase", "DISCOVERY")}',
        f'- Next action: {s["current"]["next_action"]}',
        f'- Blockers: {"; ".join(s["current"].get("blockers", [])) or "None"}', '',
        '## Tasks']
    tasks = s['tasks']
    # Keep the human/AI handoff short; the full backlog lives in canonical STATE.
    open_tasks = [t for t in tasks if t['status'] not in ('ACCEPTED', 'CANCELLED')]
    finished = [t for t in tasks if t['status'] == 'ACCEPTED']
    active_id = s['current'].get('active_task')
    active = [t for t in open_tasks if t['id'] == active_id]
    queued = [t for t in open_tasks if t['id'] != active_id]
    selected_open = active + queued[:max(0, 12 - len(active))]
    selected_done = finished[-3:]
    rows += [f'- Open: {len(open_tasks)} | Accepted: {len(finished)} | Cancelled: '
             f'{len(tasks) - len(open_tasks) - len(finished)}']
    rows += [f'- {t["id"]}: {t.get("title", t["id"])} ({t["status"]})'
             for t in selected_open + selected_done] or ['- None']
    if len(open_tasks) > len(selected_open):
        rows.append(f'- ... {len(open_tasks) - len(selected_open)} more open tasks in pcs/STATE.json')
    if len(finished) > len(selected_done):
        rows.append(f'- ... {len(finished) - len(selected_done)} earlier accepted tasks in pcs/STATE.json')
    rows += ['', '## Acceptance', '- Evidence and Owner approval must be verified outside the state file.',
             '- This document is derived, not a second source of truth.', '']
    return '\n'.join(rows)


def atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, prefix='.pcs-solo-', delete=False) as out:
        out.write(payload)
        tmp = Path(out.name)
    os.replace(tmp, path)


def init(root, slug, name):
    template = Path(__file__).resolve().parent.parent / 'templates' / 'STATE.example.json'
    obj = json.loads(template.read_text(encoding='utf-8'))
    obj['state']['slug'], obj['state']['name'] = slug, name
    obj['updated_at'] = clock()
    check(obj)
    folder = root / 'pcs'
    assert not (folder / 'STATE.json').exists(), 'State already exists; refusing overwrite'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'STATE.json'
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    atomic(folder / 'MOMENT.md', moment(obj))
    return obj


def checkpoint(root, new_obj, expected):
    folder = root / 'pcs'
    before = json.loads((folder / 'STATE.json').read_text(encoding='utf-8'))
    check(before)
    assert before['revision'] == expected, 'CONFLICT: reload current revision'
    check(new_obj)
    assert new_obj['revision'] == expected + 1, 'Revision must advance exactly one'
    assert new_obj['state']['slug'] == before['state']['slug'], 'Cannot change project identity'
    event = {'schema': 'pcs.solo.moment.v1', 'revision': new_obj['revision'],
             'previous_sha256': digest(before), 'state_sha256': digest(new_obj), 'at': clock()}
    event_name = f'MOM-{new_obj["revision"]:06d}-{digest(new_obj)[:12]}.json'
    events_dir = folder / 'moments'
    events_dir.mkdir(parents=True, exist_ok=True)
    event_path = events_dir / event_name
    with event_path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(event, indent=2) + '\n')
    # Local only. A remote GitHub commit must contain STATE + Moment together.
    atomic(folder / 'STATE.json', json.dumps(new_obj, ensure_ascii=False, indent=2) + '\n')
    atomic(folder / 'MOMENT.md', moment(new_obj))
    return event_name



def inspect(obj, group='tasks', limit=12):
    check(obj)
    assert group in TYPES + ['source_refs', 'decisions', 'risks', 'artifacts'], 'INVALID_GROUP'
    assert type(limit) is int and 1 <= limit <= 50, 'INVALID_LIMIT'
    items = obj['state'][group]
    active = obj['state']['current'].get('active_task')
    open_items = [x for x in items if x.get('status') not in ('ACCEPTED','CANCELLED')] if group in TYPES else items
    prioritized = sorted(open_items, key=lambda x: (0 if x.get('id') == active else 1 if x.get('status') in ('BLOCKED','IN_PROGRESS','TECH_DONE','INTEGRATION_PENDING') else 2))
    chosen = prioritized[:limit]
    return {'schema':'pcs.solo.inspect.v1','revision':obj['revision'],'group':group,'total':len(items),
      'shown':[{'id':x.get('id', '#'+str(items.index(x)+1)), 'status':x.get('status')} for x in chosen],
      'remaining':len(open_items)-len(chosen), 'warning':'Not an external evidence or approval verification'}

def diff(before, after, limit=12):
    check(before)
    check(after)
    assert before['state']['slug'] == after['state']['slug'], 'PROJECT_MISMATCH'
    assert after['revision'] > before['revision'], 'NON_INCREMENTAL_REVISION'
    assert type(limit) is int and 1 <= limit <= 50, 'INVALID_LIMIT'
    out = {}
    for group in TYPES + ['source_refs', 'decisions', 'risks', 'artifacts']:
        def entries(doc):
            return {str(x.get('id', '#'+str(i+1))):x for i,x in enumerate(doc['state'][group])}
        a,b = entries(before),entries(after)
        changes = []
        for key in sorted(set(a)|set(b)):
            if key not in a: changes.append({'id':key,'kind':'ADDED'})
            elif key not in b: changes.append({'id':key,'kind':'REMOVED'})
            elif stable(a[key]) != stable(b[key]):
                fields = sorted(k for k in set(a[key])|set(b[key]) if a[key].get(k)!=b[key].get(k))
                changes.append({'id':key,'kind':'CHANGED','fields_changed':fields[:20],
                    'status_before':a[key].get('status'),'status_after':b[key].get('status')})
        out[group] = {'total':len(changes),'shown':changes[:limit],'remaining':max(0,len(changes)-limit)}
    return {'schema':'pcs.solo.diff.v1','from':before['revision'],'to':after['revision'],'groups':out,
            'warning':'Structural diff only; free text omitted'}

def cli():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    init_cmd = sub.add_parser('init')
    init_cmd.add_argument('--root', type=Path, required=True)
    init_cmd.add_argument('--slug', required=True)
    init_cmd.add_argument('--name', required=True)
    verify_cmd = sub.add_parser('verify')
    verify_cmd.add_argument('--root', type=Path, required=True)
    checkpoint_cmd = sub.add_parser('checkpoint')
    checkpoint_cmd.add_argument('--root', type=Path, required=True)
    checkpoint_cmd.add_argument('--input', type=Path, required=True)
    checkpoint_cmd.add_argument('--expect', type=int, required=True)
    inspect_cmd = sub.add_parser('inspect')
    inspect_cmd.add_argument('--root', type=Path, required=True)
    inspect_cmd.add_argument('--group', default='tasks')
    inspect_cmd.add_argument('--limit', type=int, default=12)
    diff_cmd = sub.add_parser('diff')
    diff_cmd.add_argument('--before', type=Path, required=True)
    diff_cmd.add_argument('--after', type=Path, required=True)
    diff_cmd.add_argument('--limit', type=int, default=12)
    args = p.parse_args()
    if args.command == 'init':
        obj = init(args.root, args.slug, args.name)
        print('initialized revision', obj['revision'])
    elif args.command == 'inspect':
        obj = json.loads((args.root / 'pcs' / 'STATE.json').read_text(encoding='utf-8'))
        print(json.dumps(inspect(obj, args.group, args.limit), ensure_ascii=False, indent=2))
    elif args.command == 'diff':
        a = json.loads(args.before.read_text(encoding='utf-8'))
        b = json.loads(args.after.read_text(encoding='utf-8'))
        print(json.dumps(diff(a, b, args.limit), ensure_ascii=False, indent=2))
    elif args.command == 'verify':
        obj = json.loads((args.root / 'pcs' / 'STATE.json').read_text(encoding='utf-8'))
        check(obj)
        print('verified revision', obj['revision'])
    else:
        obj = json.loads(args.input.read_text(encoding='utf-8'))
        print('checkpoint', checkpoint(args.root, obj, args.expect))


if __name__ == '__main__':
    try:
        cli()
    except Exception as exc:
        print('PCS_CHAT_SOLO_ERROR:', exc, file=sys.stderr)
        sys.exit(1)
