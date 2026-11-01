import copy
import json
from pathlib import Path
import unittest

from tools.pcs_context import context

ROOT=Path(__file__).resolve().parents[1]

def sample():
    return json.loads((ROOT/'templates'/'STATE.example.json').read_text())

class ContextTests(unittest.TestCase):
    def test_bounded_and_no_untrusted_description(self):
        s=sample()
        s['state']['tasks']=[
            {'id':'T'+str(i),'status':'PLANNED','risk':'NORMAL','title':'Secret title '+str(i)}
            for i in range(230)]
        s['state']['current']['active_task']='T229'
        snapshot=copy.deepcopy(s)
        p=context(s,limit=5)
        self.assertEqual(p['task']['id'],'T229')
        self.assertEqual(p['backlog']['remaining'],225)
        self.assertNotIn('Secret title',json.dumps(p))
        self.assertEqual(s,snapshot)
    def test_risk_gate_and_invalid_params(self):
        s=sample()
        s['state']['tasks']=[{'id':'T1','status':'PLANNED','production':True}]
        p=context(s,'T1')
        self.assertTrue(p['task']['owner_review_required'])
        self.assertEqual(p['handoff_contract']['tests'],'NOT_VERIFIED')
        s['state']['tasks'][0]['risk']='Secret free-text metadata'
        packet=context(s,'T1')
        self.assertEqual(packet['task']['risk'],'UNKNOWN')
        self.assertNotIn('Secret free-text metadata',json.dumps(packet))
        with self.assertRaises(ValueError): context(s,'UNKNOWN')
        with self.assertRaises(ValueError): context(s,limit=120)
if __name__=='__main__':
    unittest.main()
