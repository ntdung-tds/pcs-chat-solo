import unittest
from tools.pcs_srs_changes import HEADER,append_event,active_context,parse_ledger,propose_from_active,summary
state={'state':{'current':{'active_task':'TASK-5'},'tasks':[{'id':'TASK-5','srs_ref':'docs/SRS.md#security'}],
    'features':[{'id':'FEAT-2','required_tasks':['TASK-5']}]}}
def prop(id_,before,after,base):
    return {'kind':'PROPOSE','id':id_,'task_id':'TASK-5','feature_id':'FEAT-2','item_key':'FEAT-2',
        'srs_ref':'docs/SRS.md#security','before':before,'after':after,'reason':'Owner requested',
        'based_on':base,'at':'2026-11-01T10:00:00Z'}
def decide(id_,decision='APPROVED'):
    return {'kind':'DECIDE','id':id_,'decision':decision,'actor':'owner',
        'ref':'https://github.com/example/repo/issues/10#issuecomment-3','at':'2026-11-01T10:01:00Z'}
class SRSChangeTests(unittest.TestCase):
    def test_active_context_needs_no_section_from_owner(self):
        self.assertEqual(active_context(state)['item_key'],'FEAT-2')
        e,m=propose_from_active(HEADER,state,{'id':'CR-1','before':'12','after':'8','reason':'Owner change'})
        self.assertEqual(e['srs_ref'],'docs/SRS.md#security')
        self.assertEqual(len(parse_ledger(m)['events']),1)
    def test_ambiguous_context_falls_back_to_task(self):
        s={'state':dict(state['state'],features:[{'id':'F1','required_tasks':['TASK-5']},
                     {'id':'F2','required_tasks':['TASK-5']}])}
        self.assertEqual(active_context(s)['item_key'],'TASK-5')
        self.assertTrue(active_context(s)['ambiguous_features'])
    def test_latest_approved_and_pending_proposal(self):
        m=HEADER
        for e in [prop('CR-1','12','10','BASELINE'),decide('CR-1'),
                  prop('CR-2','10','8','CR-1'),decide('CR-2'),prop('CR-3','8','9','CR-2')]:m=append_event(m,e)
        result=summary(m,item_key='FEAT-2')['items'][0]
        self.assertEqual(result['effective_change_id'],'CR-2')
        self.assertEqual(result['effective_delta']['after'],'8')
        self.assertEqual(result['pending_count'],1)
    def test_reject_conflicting_approvals_and_duplicates(self):
        m=append_event(HEADER,prop('CR-1','12','10','BASELINE'))
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):append_event(m,prop('CR-1','12','9','BASELINE'))
        m=append_event(m,prop('CR-2','12','8','BASELINE'))
        m=append_event(m,decide('CR-1'))
        with self.assertRaisesRegex(ValueError,'STALE_APPROVAL'):append_event(m,decide('CR-2'))
    def test_reject_unverified_missing_decision_fields(self):
        m=append_event(HEADER,prop('CR-1','12','8','BASELINE'))
        with self.assertRaisesRegex(ValueError,'DECISION_PROVENANCE'):
            append_event(m,{'kind':'DECIDE','id':'CR-1','decision':'APPROVED','actor':'owner','ref':'','at':'2026-11-01T10:00:00Z'})
        self.assertFalse(summary(append_event(m,decide('CR-1')))['items'][0]['verified_external_decision'])
if __name__=='__main__':unittest.main()
