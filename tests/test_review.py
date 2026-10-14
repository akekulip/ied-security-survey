"""Review rows: what a reviewer may claim, what each claim has to show, and carrying a review to a refetch."""
from pathlib import Path
import tempfile
import unittest

import survey as s
from support import SurveyCase


class ReviewTests(SurveyCase):
    def test_review_hash_binding(self):
        source,row=self.fixture()
        s.validate_reviews([row],[source],{'p'})
        row['source_hashes']['s']='changed'
        with self.assertRaisesRegex(ValueError,'hash mismatch'): s.validate_reviews([row],[source],{'p'})

    def test_wrong_product_or_failed_source_rejected(self):
        for change in [{'product_id':'q'},{'status':'failed'}]:
            source,row=self.fixture(); source.update(change)
            with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_unreviewed_claim_and_empty_evidence_rejected(self):
        source,row=self.fixture()
        row['reviewer']=''
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})
        row['reviewer']='test'; row['source_ids']=[]
        with self.assertRaises(ValueError): s.validate_reviews([row],[source],{'p'})

    def test_duplicate_cells_rejected(self):
        source,row=self.fixture()
        with self.assertRaises(ValueError): s.validate_reviews([row,row],[source],{'p'})

    def test_evidence_quote_must_be_in_the_cited_segment(self):
        segments = lambda sid: [{'location':'pdf-page:2','text':'Note:  TLS is supported\nfor DNP3 sessions on port 20000.'},
                                {'location':'pdf-page:3','text':'Unrelated page about HTTPS administration.'}]
        def check(evidence, **kw):
            source,row=self.fixture(); row['evidence']=evidence
            s.validate_reviews([row],[source],{'p'},segments,**kw)
        good = {'source_id':'s','location':'pdf-page:2','quote':'TLS is supported for DNP3 sessions'}
        check([good], require_evidence=True)
        check([])
        for bad in [dict(good,location='pdf-page:3'), dict(good,location='page 2'), dict(good,quote='TLS is always supported for DNP3 sessions'),
                    dict(good,quote='TLS is supported'), dict(good,source_id='other')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check([bad])
        with self.assertRaisesRegex(ValueError,'verbatim evidence quote'): check([], require_evidence=True)
        broken = lambda sid: [{'location':'pdf-page:9','text':'By default, all RTACs have a self-\nsigned X.509 certificate enabled.'}]
        for spelling in ['self-signed', 'self- signed', 'selfsigned']:
            source,row=self.fixture(); row['evidence']=[{'source_id':'s','location':'pdf-page:9','quote':f'all RTACs have a {spelling} X.509 certificate'}]
            with self.subTest(spelling=spelling): s.validate_reviews([row],[source],{'p'},broken)
        source,row=self.fixture(); row.update(status='unknown', source_ids=[], source_hashes={})
        s.validate_reviews([row],[source],{'p'},segments,require_evidence=True)

    def test_a_capability_is_recorded_once_per_interface(self):
        def check(*changes):
            source, row = self.fixture()
            rows = [dict(row, **c) for c in changes]
            s.validate_reviews(rows, [source], {'p'})
        dnp = {'interface':'DNP3 server', 'interface_class':'control_protocol'}
        web = {'interface':'Web interface', 'interface_class':'management'}
        check(dnp, web)
        board = dict(dnp, status='conditional', conditions='needs option board', review_status='confirmed')
        with self.assertRaisesRegex(ValueError,'confirmed row may not leave a field not_assessed'): check(board)
        check(dict(board, model_scope='X1-D', hardware_revision='not established', support_basis=['optional_module'],
                   default_state='undocumented', activation_needs=['none_stated']))
        check({'status':'unknown','interface':'','interface_class':'','source_ids':[],'source_hashes':{}}, dnp)
        for bad in [(dnp, dict(dnp, interface=' dnp3  SERVER ')), ({'interface_class':''},), ({'interface_class':'scada'},),
                    (dnp, dict(dnp, feature='ssh', interface_class='management')), (dict(dnp, status='conditional'),),
                    (dict(dnp, review_status='verified'),)]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check(*bad)

    def test_evidence_may_cite_a_short_range_of_segments(self):
        blocks = [{'location':f'html-block:{i+1}','text':t} for i, t in enumerate(['CIP Security', 'lets devices', 'authenticate each other.', 'Other'])]
        def check(location, quote='CIP Security lets devices authenticate each other.'):
            source, row = self.fixture(); row['evidence'] = [{'source_id':'s','location':location,'quote':quote}]
            s.validate_reviews([row],[source],{'p'},lambda sid: blocks)
        check('html-block:1-3')
        check('html-block:2-3', 'lets devices authenticate each other.')
        for bad in ['html-block:1-2', 'html-block:3-1', 'html-block:1-12', 'html-block:3-9', 'block 1 to 3']:
            with self.subTest(bad=bad), self.assertRaises(ValueError): check(bad)

    def test_four_results_and_a_lifecycle_that_needs_evidence(self):
        self.assertEqual(s.STATUSES, ('supported', 'conditional', 'explicitly_unsupported', 'unknown'))
        source, row = self.fixture()
        silent = dict(row, status='unknown', unknown_reason='complete_document_silent', location='', protocol='', implementation='', interface='DNP3', interface_class='control_protocol')
        s.validate_reviews([silent], [source], {'p'}, require_evidence=True)
        s.validate_reviews([dict(silent, status='not_documented', unknown_reason='')], [source], {'p'}, require_evidence=True)
        for change in [{'interface_class':''}, {'firmware':''}, {'interface':''}, {'source_ids':[]}, {'unknown_reason':'no manual found'}]:
            with self.subTest(change=change), self.assertRaises(ValueError): s.validate_reviews([dict(silent, **change)], [source], {'p'})
        # Sources that disagree leave the cell unknown; the row still has to say which sources and where.
        split = dict(row, status='conflicting')
        s.validate_reviews([split], [source], {'p'})
        self.assertEqual((split['status'], split['unknown_reason'], s.token(split), s.named(split)), ('unknown', 'sources_conflict', 'conflict', 'unknown: sources conflict'))
        with self.assertRaisesRegex(ValueError,'claim requires source evidence'): s.validate_reviews([dict(split, source_ids=[], source_hashes={})], [source], {'p'})
        # Not enough evidence is the plain unknown: no source, no interface, and the reason need not be written out.
        for reason in ('', 'not_enough_evidence'):
            s.validate_reviews([dict(row, status='unknown', unknown_reason=reason, source_ids=[], source_hashes={}, interface='', interface_class='')], [source], {'p'})
        base = {'sampling':'x','products':[{'id':'p','vendor':'v','model':'m','category':'c','lifecycle':'end_of_support','domains':['vendor.test'],'seeds':[]}]}
        self.assertEqual(s.validate_config(base), ['p: lifecycle "end_of_support" has no lifecycle_evidence; the report will refuse it', 'p: no seeds, so every cell stays unknown'])
        base['products'][0]['lifecycle_evidence'] = [{'url':'https://vendor.test/eol','retrieved_at':'2026-10-01','quote':'Support for model m has ended.'}]
        self.assertEqual(s.validate_config(base), ['p: no seeds, so every cell stays unknown'])
        # A label from before 1.6.0 is read, said to be one, and reported as unknown. Anything else is refused.
        base['products'][0]['lifecycle'] = 'legacy'
        self.assertEqual(s.validate_config(base), ['p: lifecycle "legacy" is a label from before 1.6.0 and is reported as unknown', 'p: no seeds, so every cell stays unknown'])
        base['products'][0]['lifecycle'] = 'old'
        with self.assertRaisesRegex(ValueError,'lifecycle must be one of'): s.validate_config(base)
        self.assertEqual((s.life_words('discontinued_support_not_stated'), s.life_words('end_of_support'), s.life_words(None)),
                         ('discontinued, support not stated', 'end of support', 'not recorded'))

    def test_a_result_states_how_it_is_obtained_how_it_ships_and_what_activates_it(self):
        source, row = self.fixture()
        ok = dict(row, model_scope='X1-D', hardware_revision='rev B', support_basis=['built_in'], default_state='disabled',
                  activation_needs=['configuration', 'certificates_or_keys'], activation_requirements='Enable TLS and load an X.509 certificate.',
                  review_status='confirmed')
        s.validate_reviews([ok], [source], {'p'})
        # A row from an earlier review has none of these facts: each reads as not assessed, which is not "undocumented".
        s.validate_reviews([row], [source], {'p'})
        self.assertEqual(s.facts(row), {'basis': ['not_assessed'], 'default': 'not_assessed', 'needs': ['not_assessed'], 'deployment': 'unknown'})
        for change, message in [
                ({'support_basis': []}, 'support_basis is empty'), ({'support_basis': ['licence']}, 'supported means built in'),
                ({'support_basis': ['built_in', 'not_stated']}, 'support_basis mixes a value'), ({'support_basis': ['cloud']}, 'support_basis is a list from'),
                ({'default_state': 'off'}, 'default_state is one of'), ({'default_state': ''}, 'default_state is one of'),
                ({'activation_needs': []}, 'activation_needs is empty'), ({'activation_requirements': ''}, 'activation_requirements does not describe them'),
                ({'model_scope': ''}, 'model_scope is empty'), ({'hardware_revision': ''}, 'hardware_revision is empty'),
                ({'default_state': 'not_assessed'}, 'confirmed row may not leave a field not_assessed'),
                ({'unknown_reason': 'sources_conflict'}, 'unknown_reason belongs to an unknown row'), ({'deployment_status': 'on'}, 'deployment_status must be one of')]:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message + r".*\('p', 'tls'\)"):
                s.validate_reviews([dict(ok, **change)], [source], {'p'})
        licensed = dict(ok, status='conditional', conditions='needs the TLS licence', support_basis=['licence'])
        s.validate_reviews([licensed], [source], {'p'})
        # Explicit non-support has no basis, default or activation to state.
        absent = dict(row, status='explicitly_unsupported')
        s.validate_reviews([absent], [source], {'p'})
        for change, message in [({'support_basis': ['built_in']}, 'belongs to a supported or conditional result only'), ({'default_state': 'disabled'}, 'default_state is one of'),
                                ({'activation_needs': ['configuration']}, 'belongs to a supported or conditional result only')]:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message): s.validate_reviews([dict(absent, **change)], [source], {'p'})
        # Each stated fact needs its own words from the document when quotes are required.
        segments = lambda sid: [{'location':'pdf-page:2','text':'TLS is supported for DNP3 sessions. TLS is disabled by default. Enable TLS and load an X.509 certificate. TLS needs the security licence.'}]
        quote = lambda words, about=None: dict({'source_id':'s','location':'pdf-page:2','quote':words}, **({'about':about} if about else {}))
        capability, default = quote('TLS is supported for DNP3 sessions.'), quote('TLS is disabled by default.', 'default')
        activation, condition = quote('Enable TLS and load an X.509 certificate.', 'activation'), quote('TLS needs the security licence.', 'conditions')
        check = lambda r, evidence: s.validate_reviews([dict(r, evidence=evidence)], [source], {'p'}, segments, require_evidence=True)
        check(ok, [capability, default, activation])
        check(licensed, [capability, default, activation, condition])
        for r, evidence, message in [(ok, [capability, activation], 'about: default'), (ok, [capability, default], 'about: activation'), (ok, [default, activation], 'verbatim evidence quote'),
                                     (ok, [capability, default, dict(activation, about='setup')], 'evidence "about" must be one of'),
                                     (licensed, [capability, default, activation], 'about: conditions'),
                                     (ok, [capability, activation, dict(default, quote='TLS is enabled by default.')], 'evidence quote not found')]:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message): check(r, evidence)
        # "Undocumented" and "none stated" are statements about the documents and need no quote.
        check(dict(ok, default_state='undocumented', activation_needs=['none_stated'], activation_requirements=''), [capability])

    def test_deployment_is_unknown_unless_evidence_from_an_installation_is_cited(self):
        source, row = self.fixture(); source.update(url='https://vendor.test/manual.pdf', final_url='https://vendor.test/manual.pdf')
        field = {'kind':'utility configuration audit', 'reference':'Audit report 2025-07, feeder relays', 'date':'2025-07-14', 'scope':'12 relays at one substation'}
        s.validate_reviews([dict(row, deployment_status='disabled', deployment_evidence=[field])], [source], {'p'})
        s.validate_reviews([dict(row, deployment_status='unknown')], [source], {'p'})
        for change, message in [({'deployment_status':'enabled'}, 'needs deployment_evidence'),
                                ({'deployment_status':'enabled', 'deployment_evidence':[dict(field, date='')]}, 'needs deployment_evidence'),
                                # What the manual says can be enabled is not evidence that anyone enabled it.
                                ({'deployment_status':'enabled', 'deployment_evidence':[dict(field, reference='https://vendor.test/manual.pdf')]}, 'not deployment evidence'),
                                ({'deployment_status':'enabled', 'deployment_evidence':[dict(field, reference='s')]}, 'not deployment evidence')]:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, message): s.validate_reviews([dict(row, **change)], [source], {'p'})
        self.assertFalse(s.untouched({'status':'unknown', 'deployment_status':'enabled'}))
        self.assertTrue(s.untouched({'status':'unknown', 'deployment_status':'unknown', 'support_basis':[], 'default_state':'', 'model_scope':'not established'}))

    def test_rebind_carries_a_review_to_a_refetch_only_when_the_text_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            url = 'https://vendor.test/a'
            cfg = self.config(p, [{'id':'a','seeds':[url]}])
            for name, body in [('old', b'<script>var nonce="1"</script><p>TLS is supported for DNP3 sessions.</p>'),
                               ('new', b'<script>var nonce="2"</script><p>TLS is supported for DNP3 sessions.</p>'),
                               ('changed', b'<p>TLS is supported for DNP3 sessions from firmware 9.</p>')]:
                with self.site({url: body}, []): s.crawl(cfg, p/name, p/'cache')
            old, new = s.load(p/'old'/'sources.json')[0], s.load(p/'new'/'sources.json')[0]
            self.assertEqual((old['id'], old['text_sha256']), (new['id'], new['text_sha256']))
            self.assertNotEqual(old['sha256'], new['sha256'])
            where = s.load(p/'old'/'candidates.json')[0]['location']
            row = {'product_id':'a','feature':'tls','status':'supported','source_ids':[old['id']],'source_hashes':{old['id']:old['sha256']},
                   'location':where,'protocol':'DNP3 over TLS','interface':'DNP3 server','interface_class':'control_protocol','firmware':'not established',
                   'implementation':'native','evidence':[{'source_id':old['id'],'location':where,'quote':'TLS is supported for DNP3 sessions.'}],
                   'rationale':'explicit','reviewer':'A. Reviewer','reviewed_at':'2026-10-13','review_status':'draft'}
            s.dump(p/'reviews.json', [row])
            with self.assertRaisesRegex(ValueError,'hash mismatch'): s.report(p/'new', p/'reviews.json', p/'refused')
            s.rebind(p/'reviews.json', p/'old', p/'new', p/'rebound.json')
            moved = s.load(p/'rebound.json')[0]
            self.assertEqual(moved['source_hashes'], {old['id']: new['sha256']})
            self.assertEqual([(x['source_id'], x['from_sha256'], x['to_sha256'], x['text_sha256'], x['basis']) for x in moved['rebound']],
                             [(old['id'], old['sha256'], new['sha256'], new['text_sha256'], 'extracted text unchanged')])
            self.assertEqual(s.load(p/'reviews.json'), [row])
            s.report(p/'new', p/'rebound.json', p/'report', require_evidence=True)
            self.assertIn('Re-bound rows: 1 rows were written against an earlier fetch of the same documents', (p/'report'/'REPORT.md').read_text(encoding='utf-8'))
            # Changed wording is a new document as far as the review goes.
            with self.assertRaisesRegex(ValueError, r'need a new review: .*a/tls'): s.rebind(p/'reviews.json', p/'old', p/'changed', p/'no.json')
            self.assertFalse((p/'no.json').exists())
            with self.assertRaises(FileExistsError): s.rebind(p/'reviews.json', p/'old', p/'new', p/'rebound.json')
            # Rows already bound to the run are left as they are.
            s.rebind(p/'rebound.json', p/'old', p/'new', p/'again.json')
            self.assertEqual(s.load(p/'again.json'), [moved])


if __name__ == '__main__':
    unittest.main()
