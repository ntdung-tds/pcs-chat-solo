import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pcs_solo', ROOT / 'tools' / 'pcs_solo.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample():
    return json.loads((ROOT / 'templates' / 'STATE.example.json').read_text())


class SoloTests(unittest.TestCase):
    def test_example_valid(self):
        self.assertTrue(mod.check(sample()))
    def test_no_multi_agent_registry(self):
        for key in mod.FORBIDDEN:
            s = sample()
            s['state'][key] = []
            with self.assertRaises(AssertionError):
                mod.check(s)
    def test_accepted_requires_independent_evidence(self):
        s = sample()
        s['state']['tasks'].append({'id': 'T1', 'status': 'ACCEPTED'})
        with self.assertRaises(AssertionError):
            mod.check(s)
    def test_dependency_cycle_rejected(self):
        s = sample()
        s['state']['tasks'] = [{'id': 'T1','status':'PLANNED','dependencies':['T2']},
                                {'id': 'T2','status':'PLANNED','dependencies':['T1']}]
        with self.assertRaises(AssertionError):
            mod.check(s)
    def test_init_verify_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original = mod.init(root, 'sample-project', 'Sample Project')
            mod.check(original)
            with self.assertRaises(AssertionError):
                mod.init(root, 'sample-project', 'Sample Project')
            new = copy.deepcopy(original)
            new['revision'] = 2
            new['state']['current']['next_action'] = 'Write architecture'
            event_name = mod.checkpoint(root, new, expected=1)
            self.assertTrue((root / 'pcs' / 'moments' / event_name).exists())
            self.assertIn('Write architecture', (root / 'pcs' / 'MOMENT.md').read_text())
            with self.assertRaises(AssertionError):
                mod.checkpoint(root, new, expected=1)
    def test_moment_is_bounded_and_shows_current_task(self):
        s = sample()
        s['state']['tasks'] = [
            {'id': f'T{i}', 'status': 'PLANNED', 'title': f'Task {i}'}
            for i in range(1, 151)
        ]
        s['state']['current']['active_task'] = 'T150'
        for i in range(151, 161):
            s['state']['tasks'].append({
                'id': f'T{i}', 'status': 'ACCEPTED',
                'evidence': [{'verified': True, 'ref': 'https://example.com/verified-sample'}],
                'acceptance': {'decision': 'APPROVED'}, 'qa': {'status': 'PASS'}
            })
        m = mod.moment(s)
        self.assertIn('Open: 150 | Accepted: 10 | Cancelled: 0', m)
        self.assertIn('- T150: Task 150 (PLANNED)', m)
        self.assertIn('138 more open tasks', m)
        self.assertIn('7 earlier accepted tasks', m)
        self.assertNotIn('- T149:', m)
        self.assertLess(len(m), 2300)

    def test_optimized_python_cannot_disable_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mod.init(root, 'sample-project', 'Name')
            result = subprocess.run(
                [sys.executable, '-O', str(ROOT / 'tools' / 'pcs_solo.py'),
                 'verify', '--root', str(root)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('validation must remain active', result.stderr)

    def test_no_silent_project_identity_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = mod.init(root, 'sample-project', 'Name')
            s['revision'] = 2
            s['state']['slug'] = 'different-project'
            with self.assertRaises(AssertionError):
                mod.checkpoint(root, s, expected=1)


if __name__ == '__main__':
    unittest.main()
