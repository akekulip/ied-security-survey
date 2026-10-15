"""Avoid repeating PDF parsing while preserving independent per-product provenance and replay checks."""
from pathlib import Path
import tempfile
from unittest.mock import patch

from pypdf import PdfReader

from iedsurvey.crawl import crawl
from iedsurvey.extract import PDFReuse
from iedsurvey.runs import rebuild, replay
from iedsurvey.store import digest, dump, load
from support import SurveyCase, tiny_pdf


class SharedPDFTests(SurveyCase):
    def test_reuse_checks_the_supplied_raw_bytes_even_when_the_pdf_is_cached(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            body = tiny_pdf(['DNP3 supports TLS.'])
            source = {'id': 'a', 'sha256': digest(body), 'headers': {'Content-Type': 'application/pdf'}}
            reuse = PDFReuse(p)
            segments, _, facts = reuse.parse(source, body)
            dump(p / 'a.segments.json', segments)
            reuse.remember(source, facts)
            with self.assertRaisesRegex(ValueError, 'source bytes hash mismatch'):
                reuse.parse(dict(source, id='b'), b'changed bytes')

    def test_reuse_refuses_changed_page_locations_in_its_fresh_intermediate(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            body = tiny_pdf(['DNP3 supports TLS.'])
            source = {'id': 'a', 'sha256': digest(body), 'headers': {'Content-Type': 'application/pdf'}}
            reuse = PDFReuse(p)
            segments, _, facts = reuse.parse(source, body)
            dump(p / 'a.segments.json', segments)
            reuse.remember(source, facts)
            segments[0]['location'] = 'pdf-page:99'
            dump(p / 'a.segments.json', segments)
            with self.assertRaisesRegex(ValueError, 'shared PDF segments changed'):
                reuse.parse(dict(source, id='b'), body)

    def shared_run(self, p):
        a, b = 'https://vendor.test/a.pdf', 'https://vendor.test/b.pdf'
        cfg = self.config(p, [{'id': 'a', 'seeds': [a], 'aliases': ['RelayX']},
                              {'id': 'b', 'seeds': [b], 'aliases': ['RelayY']}])
        body = tiny_pdf(['RelayX supports TLS for DNP3.', 'Security requires configuration.'])
        return cfg, {a: body, b: body}

    def test_shared_pdf_is_parsed_once_and_each_product_keeps_its_own_scope(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            cfg, pages = self.shared_run(p)
            with self.site(pages, []), patch('pypdf.PdfReader', wraps=PdfReader) as reader:
                crawl(cfg, p / 'run', p / 'cache')
            self.assertEqual(reader.call_count, 1)
            sources = load(p / 'run/sources.json')
            self.assertEqual([s['model_mentions'] for s in sources], [1, 0])
            self.assertNotEqual(sources[0]['id'], sources[1]['id'])
            self.assertEqual(sources[0]['sha256'], sources[1]['sha256'])
            for source in sources:
                self.assertTrue((p / 'run' / (source['id'] + '.segments.json')).exists())
            tls = [h for h in load(p / 'run/candidates.json') if h['feature'] == 'tls']
            self.assertEqual([(h['product_id'], h['model_mentioned']) for h in tls], [('a', True), ('b', False)])

    def test_rebuild_and_replay_parse_each_shared_pdf_once(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            cfg, pages = self.shared_run(p)
            with self.site(pages, []):
                crawl(cfg, p / 'run', p / 'cache')
            with patch('pypdf.PdfReader', wraps=PdfReader) as reader:
                rebuild(p / 'run', p / 'cache', p / 'rebuilt')
            self.assertEqual(reader.call_count, 1)
            for old, new in zip(load(p / 'run/sources.json'), load(p / 'rebuilt/sources.json')):
                self.assertEqual((old['sha256'], old['text_sha256']), (new['sha256'], new['text_sha256']))
            with patch('pypdf.PdfReader', wraps=PdfReader) as reader:
                replay(p / 'rebuilt', p / 'cache', p / 'replay')
            self.assertEqual(reader.call_count, 1)
