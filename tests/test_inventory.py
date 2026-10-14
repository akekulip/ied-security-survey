"""The catalogue inventory and the sample drawn from it."""
from collections import Counter as Counter_
import gzip
import json
from pathlib import Path
import tempfile
import unittest

import survey as s
from support import SurveyCase


class InventoryTests(SurveyCase):
    def test_inventory_places_every_catalogue_entry_and_drops_none(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            inv = self.catalogue(p, calls)
            got = {e['product_url'].rsplit('/', 1)[-1]: e for e in inv['entries']}
            self.assertEqual(sorted(got), ['cable', 'pm800', 'r100', 'r90-legacy', 'setup-software', 'x7'])
            self.assertEqual([(k, got[k]['category'], got[k]['lifecycle'], got[k]['included']) for k in ('r100', 'r90-legacy', 'pm800')],
                             [('r100','protective_relay','currently_supported',True), ('r90-legacy','protective_relay','unknown',True), ('pm800','meter','currently_supported',True)])
            self.assertEqual((got['cable']['included'], got['cable']['reason']), (False, 'accessory'))
            self.assertEqual((got['setup-software']['included'], got['setup-software']['reason'], got['setup-software']['category']), (False, 'software', 'protective_relay'))
            self.assertEqual((got['x7']['included'], got['x7']['category'], got['x7']['reason'], 'excluded_by' in got['x7']), (False, 'unclassified', 'no category rule matched', False))
            self.assertEqual((got['r100']['id'], got['r100']['model'], got['r100']['vendor'], got['r100']['domains']), ('acme_r100', 'R100', 'Acme', ['vendor.test']))
            # Being listed is the vendor's dated word that the product is on offer. The vendor's own "legacy" label decides nothing.
            listed = {'url': 'https://vendor.test/sitemap.xml', 'sha256': s.digest(self.SITEMAP), 'retrieved_at': '2026-10-13T00:00:00+00:00'}
            self.assertEqual(got['r100']['lifecycle_evidence'], [dict(listed, basis='listed in the vendor catalogue without a notice of discontinuation')])
            self.assertEqual((got['r100']['vendor_label'], got['r90-legacy']['vendor_label'], got['r90-legacy']['lifecycle_basis']), ('', 'legacy', 'catalogue listing matches legacy'))
            self.assertEqual({i['listed_in'] for i in s.load(p/'inv'/'catalogue.json')['acme']['items']}, {'https://vendor.test/sitemap.xml'})
            self.assertEqual(s.load(p/'inv'/'inventory.json')['spec']['definitions'], self.DEFINITIONS)
            self.assertEqual(calls, ['https://vendor.test/sitemap.xml'])
            self.assertEqual(len((p/'inv'/'inventory.csv').read_text(encoding='utf-8').splitlines()), 7)
            self.assertEqual(len(s.load(p/'inv'/'catalogue.json')['acme']['items']), 8)
            with self.assertRaises(FileExistsError): s.inventory(p/'vendors.json', p/'inv', p/'cache')
            # Changed rules are re-applied to the saved listing without asking the vendor again.
            changed = json.loads(json.dumps(self.VENDORS)); changed['vendors']['acme']['rules'].append({'on': 'slug', 'match': '^x7$', 'category': 'plc'})
            s.dump(p/'vendors2.json', changed)
            with self.site({}, calls): s.inventory(p/'vendors2.json', p/'inv2', p/'cache', source=p/'inv')
            self.assertEqual(len(calls), 1)
            first, again = s.load(p/'inv'/'inventory.json'), s.load(p/'inv2'/'inventory.json')
            self.assertEqual([(e['category'], e['included']) for e in again['entries'] if e['id'] == 'acme_x7'], [('plc', True)])
            # The inventory date is the day the vendor's catalogue was listed, whenever the rules are applied to it.
            self.assertEqual((again['listed_at'], again['reapplied_from']), (first['listed_at'], str(p/'inv')))
            self.assertGreater(again['created_at'], first['listed_at'])
            for broken in ({'rules': [{'match': 'x', 'category': 'switch'}]}, {'lifecycle': [{'match': 'x', 'value': 'old'}]}, {'rules': [{'match': '(', 'category': 'plc'}]},
                           {'lifecycle': [{'match': 'x', 'value': 'legacy'}]}, {'lifecycle_text': [{'match': 'x', 'value': 'discontinued'}]}):
                bad = json.loads(json.dumps(self.VENDORS)); bad['vendors']['acme'].update(broken); s.dump(p/'bad.json', bad)
                with self.subTest(broken=broken), self.assertRaises(Exception): s.inventory(p/'bad.json', p/'inv3', p/'cache', source=p/'inv')
                self.assertFalse((p/'inv3').exists())

    def test_product_list_adapter_classifies_on_the_vendor_one_line_product_type(self):
        body = json.dumps({'items': [
            {'content': {'title': 'SEL-751', 'quicklink': '/products/751/', 'teaser': '<p>Complete protection with a display panel.</p>'},
             'smartForm': {'subtitle': 'Feeder Protection Relay', 'selectDownloads': [{'id': 11}, {'id': 12}, {'id': 13}, {'id': 14}]}},
            {'content': {'title': 'SEL-4000', 'quicklink': '/products/4000/', 'teaser': 'Tests a feeder protection scheme.'}, 'smartForm': {'subtitle': 'Relay <span>Test Set</span>'}},
            {'content': {'title': 'No link'}, 'smartForm': {}}]}).encode()
        spec = json.loads(json.dumps(self.VENDORS))
        spec['vendors']['acme'].update(adapter='sel_product_selector', catalogue_api='https://vendor.test/api/list/', page_needs_javascript=True,
                                       census_documents=1, document_seeds=2, scope='^https://vendor\\.test/products/[^/]+/$')
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            s.dump(p/'vendors.json', spec)
            with self.site({'https://vendor.test/api/list/': body}, calls): s.inventory(p/'vendors.json', p/'inv', p/'cache')
            tester, relay = s.load(p/'inv'/'inventory.json')['entries']  # in URL order
            self.assertEqual((relay['model'], relay['category'], relay['included'], relay['product_url']), ('SEL-751', 'protective_relay', True, 'https://vendor.test/products/751/'))
            self.assertEqual(relay['documents'][:2], ['https://vendor.test/api/download/11/', 'https://vendor.test/api/download/12/'])
            self.assertEqual(relay['summary'], 'Feeder Protection Relay. Complete protection with a display panel.')
            self.assertEqual((tester['included'], tester['reason']), (False, 'test equipment'))
            self.assertEqual((relay['lifecycle'], [e['url'] for e in relay['lifecycle_evidence']]), ('currently_supported', ['https://vendor.test/api/list/']))
            s.sample(p/'inv'/'inventory.json', p/'census.json', census=True)
            s.sample(p/'inv'/'inventory.json', p/'deep.json', per_stratum=5, seed=1)
            self.assertEqual([x['seeds'] for x in s.load(p/'census.json')['products']], [['https://vendor.test/api/download/11/']])
            self.assertEqual([x['seeds'] for x in s.load(p/'deep.json')['products']], [['https://vendor.test/api/download/11/', 'https://vendor.test/api/download/12/']])

    def test_sample_is_seeded_stratified_and_states_its_own_frame(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td); inv = self.frame_inventory(p)
            s.sample(inv, p/'a.json', per_stratum=2, seed=7)
            s.sample(inv, p/'b.json', per_stratum=2, seed=7)
            s.sample(inv, p/'c.json', per_stratum=2, seed=8)
            self.assertEqual((p/'a.json').read_bytes(), (p/'b.json').read_bytes())
            a, c = s.load(p/'a.json'), s.load(p/'c.json')
            self.assertEqual(Counter_((x['vendor'], x['category'], x['lifecycle']) for x in a['products']),
                             {('Acme','protective_relay','currently_supported'): 2, ('Acme','protective_relay','discontinued_support_not_stated'): 2,
                              ('Acme','meter','currently_supported'): 1, ('Bolt','plc','currently_supported'): 2})
            self.assertNotEqual([x['id'] for x in a['products']], [x['id'] for x in c['products']])
            self.assertEqual({(f['vendor'], f['category'], f['lifecycle']): (f['in_catalogue'], f['selected']) for f in a['frame']},
                             {('Acme','meter','currently_supported'): (1, 1), ('Acme','protective_relay','currently_supported'): (6, 2),
                              ('Acme','protective_relay','discontinued_support_not_stated'): (2, 2), ('Bolt','plc','currently_supported'): (5, 2)})
            # The definitions and each device's lifecycle evidence travel into the config, and so under the manifest's hash.
            self.assertEqual(a['definitions'], self.DEFINITIONS)
            self.assertEqual({(x['lifecycle_basis'], x['lifecycle_evidence'][0]['url']) for x in a['products']}, {('catalogue listing', 'https://vendor.test/sitemap.xml')})
            self.assertIn('seed 7', a['sampling']); self.assertIn('14 classified catalogue entries', a['sampling'])
            self.assertIn('Inventory of 2026-10-13;', a['sampling'])
            later = dict(s.load(inv), created_at='2026-10-20T00:00:00+00:00', listed_at='2026-10-13T00:00:00+00:00')
            s.dump(p/'reapplied.json', later); s.sample(p/'reapplied.json', p/'d.json', per_stratum=2, seed=7)
            self.assertEqual((s.load(p/'d.json')['sampling'], s.load(p/'d.json')['inventory']['listed_at']), (a['sampling'], '2026-10-13T00:00:00+00:00'))
            self.assertEqual((a['seed'], a['per_stratum'], a['robots_follow_redirects'], a['inventory']['sha256']), (7, 2, ['vendor.test'], s.digest(inv.read_bytes())))
            self.assertEqual({(x['max_depth'], x['follow_pattern']) for x in a['products']}, {(1, 'manual')})
            self.assertEqual(s.validate_config(a), [])
            s.sample(inv, p/'census.json', census=True)
            census = s.load(p/'census.json')
            self.assertEqual(len(census['products']), 15)
            self.assertIn('acme_unclassified', [x['id'] for x in census['products']])
            self.assertNotIn('acme_excluded', [x['id'] for x in census['products']])
            self.assertNotIn('max_depth', census['products'][0])
            self.assertIn('Census', census['sampling'])
            for bad in ({}, {'per_stratum': 0}):
                with self.subTest(bad=bad), self.assertRaises(ValueError): s.sample(inv, p/'bad.json', **bad)
            with self.assertRaises(FileExistsError): s.sample(inv, p/'a.json', per_stratum=2, seed=7)

    def test_enrich_reads_title_lifecycle_and_category_off_the_product_page(self):
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            pages = {'https://vendor.test/products/relays/r100': b'<title>R100 Feeder Relay | Acme</title><p>Numerical relay.</p>',
                     'https://vendor.test/products/relays/r90-legacy': b'<title>R90 | Acme</title><p>Overview. Manufacturing for the R90 has been discontinued. Use the R100.</p>',
                     'https://vendor.test/products/misc/x7': b'<title>X7 | Acme</title><p>The X7 gives feeder protection for small substations. Support ended on 30 June 2019. Use the R100.</p>'}
            self.catalogue(p, calls, pages)
            s.sample(p/'inv'/'inventory.json', p/'census.json', census=True)
            with self.site(pages, calls): s.crawl(p/'census.json', p/'run', p/'cache')
            s.enrich(p/'inv'/'inventory.json', p/'run', p/'inv2')
            got = {e['id']: e for e in s.load(p/'inv2'/'inventory.json')['entries']}
            self.assertEqual((got['acme_r100']['model'], got['acme_r100']['model_basis'], got['acme_r100']['lifecycle']), ('R100 Feeder Relay', 'product page title', 'currently_supported'))
            # A notice that manufacture has ended says nothing about support, so the device is discontinued and not legacy.
            old = got['acme_r90_legacy']
            self.assertEqual((old['lifecycle'], old['lifecycle_basis'], old['vendor_label']), ('discontinued_support_not_stated', 'product page wording', 'legacy'))
            proof, = old['lifecycle_evidence']
            self.assertIn('Manufacturing for the R90 has been discontinued.', proof['quote'])
            self.assertEqual((proof['url'], proof['stated_date'], proof['retrieved_at'], len(proof['sha256'])),
                             ('https://vendor.test/products/relays/r90-legacy', '', '2026-10-13T00:00:00+00:00', 64))
            # End of support is the vendor's sentence, with the date the sentence gives.
            gone = got['acme_x7']
            self.assertEqual((gone['category'], gone['included'], gone['lifecycle']), ('protective_relay', True, 'end_of_support'))
            self.assertIn('product page text', gone['category_basis'])
            self.assertEqual((gone['lifecycle_evidence'][0]['stated_date'], 'Support ended on 30 June 2019.' in gone['lifecycle_evidence'][0]['quote']), ('30 June 2019', True))
            self.assertTrue(got['acme_pm800']['page_status'].startswith('failed: ValueError: HTTP 404'))
            self.assertNotIn('page_status', got['acme_cable'])
            self.assertIn('enriched_from', s.load(p/'inv2'/'inventory.json'))
            sheet = (p/'inv2'/'inventory.csv').read_text(encoding='utf-8').splitlines()
            self.assertIn('lifecycle_evidence_date,lifecycle_evidence_quote,lifecycle_evidence_url', sheet[0])
            self.assertEqual([line.count('30 June 2019') for line in sheet if line.startswith('acme_x7,')], [2])
            self.assertTrue(any(line.startswith('acme_r100,') and ',2026-10-13,' in line for line in sheet))
            with self.assertRaises(FileExistsError): s.enrich(p/'inv'/'inventory.json', p/'run', p/'inv2')
            # Wording rules are written after the pages are read. One limited to the page opening ignores a later notice.
            narrow = json.loads(json.dumps(self.VENDORS)); narrow['vendors']['acme']['lifecycle_text'][1]['within'] = 30
            s.dump(p/'narrow.json', narrow)
            s.enrich(p/'inv'/'inventory.json', p/'run', p/'inv3', vendors=p/'narrow.json')
            again = s.load(p/'inv3'/'inventory.json')
            self.assertEqual([(e['lifecycle'], e['lifecycle_basis']) for e in again['entries'] if e['id'] == 'acme_r90_legacy'], [('unknown', 'catalogue listing matches legacy')])
            self.assertEqual((again['vendors_sha256'], again['spec']), (s.digest((p/'narrow.json').read_bytes()), narrow))
            narrow['vendors']['acme']['lifecycle_text'][0]['value'] = 'old'; s.dump(p/'narrow.json', narrow)
            with self.assertRaisesRegex(ValueError,'lifecycle value'): s.enrich(p/'inv'/'inventory.json', p/'run', p/'inv4', vendors=p/'narrow.json')
        for text, expected in [('The EPM has been discontinued as of April 8, 2011. See the 6000.', 'April 8, 2011'), ('Obsolete December 2016. Replace it.', 'December 2016'),
                               ('Withdrawn on 2019-06-30.', '2019-06-30'), ('It has been discontinued. Updated 3 May 2024.', '')]:
            m = s.re.search('discontinued|Obsolete|Withdrawn', text)
            with self.subTest(text=text): self.assertEqual(s.stated_date(text, m.start(), m.end()), expected)

    def test_sitemap_lists_and_filters_without_touching_any_config(self):
        index = 'https://vendor.test/sitemap_index.xml'
        pages = {index: b'<sitemapindex><sitemap><loc>https://vendor.test/s1.xml</loc></sitemap><sitemap><loc> https://vendor.test/s2.xml.gz </loc></sitemap><sitemap><loc>https://vendor.test/s3.xml</loc></sitemap></sitemapindex>',
                 'https://vendor.test/s1.xml': b'<urlset><url><loc>https://vendor.test/relays/r1</loc></url><url><loc>https://vendor.test/news/a&amp;b</loc></url></urlset>',
                 'https://vendor.test/s2.xml.gz': gzip.compress(b'<urlset><url><loc><![CDATA[https://vendor.test/relays/r2]]></loc></url></urlset>')}
        with tempfile.TemporaryDirectory() as td:
            p, calls = Path(td), []
            with self.site(pages, calls):
                s.sitemap([index], None, [], 'relays', p/'inventory'/'vendor.json', p/'cache')
                result = s.load(p/'inventory'/'vendor.json')
                self.assertEqual(result['urls'], ['https://vendor.test/relays/r1','https://vendor.test/relays/r2'])
                self.assertEqual((result['total_urls'], result['matched_urls'], result['domains'], result['not_fetched']), (3, 2, ['vendor.test'], []))
                self.assertEqual([(x.get('kind'), x.get('entries')) for x in result['files']], [('index',3),('urlset',2),('urlset',1),(None,None)])
                self.assertIn('HTTP 404', result['files'][3]['error'])
                with self.assertRaises(FileExistsError): s.sitemap([index], None, [], '.', p/'inventory'/'vendor.json', p/'cache')
                s.sitemap([index], None, [], '.', p/'limited.json', p/'cache', limit=2)
                self.assertEqual(s.load(p/'limited.json')['not_fetched'], ['https://vendor.test/s2.xml.gz','https://vendor.test/s3.xml'])
            f, raw = self.scripted(td, {'https://vendor.test/robots.txt':(200,{},b'Sitemap: https://vendor.test/sitemap_index.xml\n')})
            with raw: f.robot('https://vendor.test/')
            self.assertEqual(f.robots['vendor.test']['sitemaps'], [index])


if __name__ == '__main__':
    unittest.main()
