import copy
import json
from pathlib import Path
import unittest

from tools.pcs_requirements import resolve
from tools.pcs_solo import check

H='a'*64

def cr(id_,status,parent='BASELINE',target='FEAT-001'):
    x={'id':id_,'item_id':target,'status':status,'based_on':parent,
       'baseline_ref':'docs/SRS.md#3-2','baseline_sha256':H}
    if status=='APPROVED':
        x.update({'final_ref':'docs/project/changes/'+id_+'.md','final_sha256':'b'*64,
                  'decision':{'by':'owner','ref':'https://github.com/example/repo/issues/1#issuecomment-10'}})
    return x

class RequirementChangeTests(unittest.TestCase):
    def test_last_approved_wins_over_later_proposal(self):
        rows=[cr('CR-001','APPROVED'),cr('CR-002','APPROVED','CR-001'),
              cr('CR-003','PROPOSED','CR-002')]
        before=copy.deepcopy(rows)
        result=resolve(rows,item_id='FEAT-001')['items'][0]
        self.assertEqual(result['effective_change_id'],'CR-002')
        self.assertEqual(result['pending_count'],1)
        self.assertFalse(result['approval_externally_verified'])
        self.assertEqual(rows,before)
    def test_prevent_ambiguous_approved_branches(self):
        with self.assertRaisesRegex(ValueError,'AMBIGUOUS'):
            resolve([cr('CR-001','APPROVED'),cr('CR-002','APPROVED')])
    def test_stale_proposals_and_rejections_do_not_override(self):
        out=resolve([cr('CR-001','APPROVED'),cr('CR-002','REJECTED','CR-001'),
                     cr('CR-003','PROPOSED','BASELINE')])['items'][0]
        self.assertEqual(out['effective_change_id'],'CR-001')
        self.assertEqual(out['stale_proposals'],['CR-003'])
        self.assertEqual(out['rejected_count'],1)
    def test_canonical_checkpoint_validation_rejects_two_finals(self):
        sample=json.loads((Path(__file__).resolve().parents[1]/'templates'/'STATE.example.json').read_text())
        sample['state']['requirement_changes']=[cr('CR-001','APPROVED'),cr('CR-002','APPROVED')]
        with self.assertRaisesRegex(ValueError,'AMBIGUOUS_APPROVED_BRANCH'):
            check(sample)

    def test_missing_approval_fails_closed(self):
        x=cr('CR-001','APPROVED')
        del x['decision']
        with self.assertRaisesRegex(ValueError,'APPROVAL_EVIDENCE_FIELDS_REQUIRED'):
            resolve([x])
        with self.assertRaisesRegex(ValueError,'UNAPPROVED_PREDECESSOR'):
            resolve([cr('CR-002','APPROVED','CR-999')])
    def test_summary_does_not_include_unrelated_sensitive_text(self):
        x=cr('CR-001','APPROVED')
        x['private_notes']='confidential project story'
        summary=resolve([x],limit=1)
        self.assertNotIn('confidential project story',json.dumps(summary))
        self.assertEqual(resolve([],item_id='FEAT-001')['items'],[])
        with self.assertRaisesRegex(ValueError,'INVALID_LIMIT'):
            resolve([],limit=100)

if __name__=='__main__':
    unittest.main()
