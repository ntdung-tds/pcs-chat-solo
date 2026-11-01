#!/usr/bin/env python3
"""Verify repository seed manifest (excluding generated caches and the manifest itself)."""
from pathlib import Path
import hashlib
import sys

ROOT = Path(__file__).resolve().parent
EXCLUDED = {'.git', '__pycache__', 'distribution'}

def main():
    entries = {}
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(x in EXCLUDED for x in path.relative_to(ROOT).parts) or path.name.endswith('.pyc') or path.name == 'MANIFEST.sha256':
            continue
        entries[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    lines = (ROOT / 'MANIFEST.sha256').read_text().splitlines()
    expected = dict(line.split('  ', 1)[::-1] for line in lines if line.strip())
    errors = [(key, expected.get(key), actual) for key, actual in entries.items() if expected.get(key) != actual]
    missing = sorted(set(expected) - set(entries))
    if errors or missing:
        print('SEED_INTEGRITY_FAILED', errors[:10], missing[:10], file=sys.stderr)
        sys.exit(1)
    print(f'SEED_INTEGRITY_PASS: {len(entries)} files')

if __name__ == '__main__': main()
