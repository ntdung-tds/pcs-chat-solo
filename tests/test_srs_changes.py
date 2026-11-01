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
        e,m=propose_from_active(HEADER,state,{'id':'CR-1','before':'12','after':'8','reason':'Owner change','requirement_key':'password-length'})
        self.assertEqual(e['srs_ref'],'docs/SRS.md#security')
        self.assertEqual(len(parse_ledger(m)['events']),1)
    def test_ambiguous_context_falls_back_to_task(self):
        s={'state':dict(state['state'],features=[{'id':'F1','required_tasks':['TASK-5']},
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
    def test_independent_requirements_same_feature_do_not_overwrite(self):
        m=HEADER
        e,m=propose_from_active(m,state,{'id':'CR-P1','requirement_key':'password-length',
            'before':'min 12','after':'min 8','reason':'Owner'})
        m=append_event(m,decide('CR-P1'))
        independent,m=propose_from_active(m,state,{'id':'CR-U1','requirement_key':'username-length',
            'before':'max 24','after':'max 40','reason':'Owner'})
        self.assertEqual(independent['based_on'],'BASELINE')
        self.assertNotEqual(independent['item_key'],e['item_key'])
        nxt,next_m=propose_from_active(m,state,{'id':'CR-P2','requirement_key':'password-length',
            'before':'min 8','after':'min 10','reason':'Owner'})
        self.assertEqual(nxt['based_on'],'CR-P1')
        self.assertEqual(summary(next_m,task_id='TASK-5')['total_items'],2)
        self.assertEqual(summary(next_m,feature_id='FEAT-2')['total_items'],2)
        with self.assertRaisesRegex(ValueError,'DELTA_BASELINE_MISMATCH'):
            propose_from_active(m,state,{'id':'CR-P3','requirement_key':'password-length',
                'before':'unrelated','after':'other','reason':'Owner'})
        with self.assertRaisesRegex(ValueError,'REQUIREMENT_KEY_REQUIRED'):
            propose_from_active(m,state,{'id':'CR-BAD','before':'x','after':'y','reason':'Owner'})
    def test_bounded_multi_requirement_summary(self):
        m=HEADER
        for i in range(14):
            e=prop('CR-Q'+str(i),'before','after','BASELINE')
            e['item_key']='FEAT-2.aspect'+str(i)
            e['requirement_key']='aspect'+str(i)
            m=append_event(m,e)
        out=summary(m,task_id='TASK-5')
        self.assertEqual(out['total_items'],14)
        self.assertEqual(out['remaining_items'],6)
        self.assertEqual(len(out['items']),8)
        self.assertEqual(len(summary(m,max_items=20)['items']),14)
        with self.assertRaisesRegex(ValueError,'INVALID_MAX_ITEMS'):
            summary(m,max_items=100)
    def test_legacy_unscoped_history_must_be_reconciled(self):
        m=append_event(HEADER,prop('CR-LEGACY','12','10','BASELINE'))
        self.assertEqual(summary(m,item_key='FEAT-2')['total_items'],1)
        with self.assertRaisesRegex(ValueError,'LEGACY_SCOPE_REVIEW_REQUIRED'):
            propose_from_active(m,state,{'id':'CR-NEW','requirement_key':'password-length',
                'before':'10','after':'8','reason':'Owner'})
if __name__=='__main__':unittest.main()
