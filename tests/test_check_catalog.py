import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_catalog as catalog


PREAMBLE = '''# Collection
## Table of contents
* [Libraries](#libraries)
## Libraries
'''


class MarkdownChecks(unittest.TestCase):
    def check(self, content, extra_files=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text(content, encoding='utf-8')
            for name, text in (extra_files or {}).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')
            return catalog.check_markdown(root)

    def test_duplicate_marker_is_reported(self):
        errors = self.check(PREAMBLE + '* * [robot](https://github.com/owner/robot)\n')
        self.assertTrue(any('duplicated list marker' in error for error in errors))

    def test_fenced_examples_are_ignored(self):
        content = PREAMBLE + '````markdown\n* * [sample](missing.md)\n```\n````\n'
        self.assertEqual(self.check(content), [])

    def test_unclosed_fence_fails(self):
        errors = self.check(PREAMBLE + '```markdown\n[hidden](missing.md)\n')
        self.assertTrue(any('unclosed code fence' in error for error in errors))

    def test_relative_links_and_duplicate_heading_suffixes(self):
        content = PREAMBLE + '[Instructions](docs/guide.md#install-1)\n'
        extra = {'docs/guide.md': '# Install\n# Install\n[Home](../README.md#libraries)\n'}
        self.assertEqual(self.check(content, extra), [])

    def test_missing_local_file_and_fragment_fail(self):
        content = PREAMBLE + '[Missing](absent.md)\n[Heading](#absent)\n'
        self.assertEqual(len(self.check(content)), 2)

    def test_table_of_contents_detects_stale_heading(self):
        content = PREAMBLE + '### Added category\n'
        errors = self.check(content)
        self.assertTrue(any('table of contents differs' in error for error in errors))

    def test_duplicate_in_one_category_fails(self):
        content = PREAMBLE + '* [a](https://github.com/owner/a)\n' * 2
        self.assertTrue(any('duplicate project' in error for error in self.check(content)))

    def test_same_source_in_distinct_groups_is_allowed(self):
        content = PREAMBLE + '* SQL\n  * [a](https://github.com/owner/a)\n'
        content += '* NoSQL\n  * [a](https://github.com/owner/a)\n'
        self.assertEqual(self.check(content), [])

    def test_heading_suffix_avoids_an_existing_slug(self):
        anchors = [item[3] for item in catalog.headings('# Tool\n# Tool-1\n# Tool\n')]
        self.assertEqual(anchors, ['tool', 'tool-1', 'tool-2'])

    def test_malformed_url_is_reported(self):
        errors = self.check(PREAMBLE + '[bad](httpsL//github.com/owner/project)\n')
        self.assertTrue(any('malformed link' in error for error in errors))


class ChangedEntries(unittest.TestCase):
    def test_only_new_primary_project_urls_are_reviewed(self):
        old = PREAMBLE + '* [a](https://github.com/owner/a) — Old description.\n'
        current = PREAMBLE + '* [a](https://github.com/owner/a) — New description.\n'
        current += '* [b](https://github.com/owner/b) [CI](https://github.com/owner/b/actions)\n'
        urls = [entry.url for entry in catalog.added_entries(current, old)]
        self.assertEqual(urls, ['https://github.com/owner/b'])

    def test_tutorial_becoming_a_project_is_reviewed(self):
        old = '## Resources\n* [a](https://github.com/owner/a)\n'
        current = PREAMBLE + '* [a](https://github.com/owner/a)\n'
        self.assertEqual(len(catalog.added_entries(current, old)), 1)

    def test_git_base_read_uses_the_requested_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            (root / 'README.md').write_text(PREAMBLE, encoding='utf-8')
            subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
            subprocess.run(
                ['git', '-c', 'user.name=Catalog Test', '-c', 'user.email=test@example.com',
                 'commit', '-qm', 'Initial catalog'], cwd=root, check=True,
            )
            (root / 'README.md').write_text('Changed working tree\n', encoding='utf-8')
            self.assertEqual(catalog.previous_readme(root, 'HEAD'), PREAMBLE)


class SourceReview(unittest.TestCase):
    def setUp(self):
        self.entry = catalog.Entry(10, 'Project', 'https://github.com/owner/project', ('Libraries',))
        self.metadata = {
            'full_name': 'owner/project', 'archived': False, 'disabled': False,
            'license': {'spdx_id': 'MIT'},
        }

    def review(self, languages, metadata=None, entry=None):
        metadata = self.metadata if metadata is None else metadata

        def lookup(url):
            return languages if url.endswith('/languages') else metadata

        with patch.object(catalog, 'get_json', side_effect=lookup):
            with patch('sys.stdout', new_callable=io.StringIO):
                return catalog.review_project(entry or self.entry)

    def test_exactly_seventy_percent_fails(self):
        errors, reviews = self.review({'Rust': 70, 'C': 30})
        self.assertTrue(any('strictly more than 70%' in error for error in errors))
        self.assertEqual(reviews, [])

    def test_above_seventy_uses_unrounded_values(self):
        errors, reviews = self.review({'Rust': 700001, 'C': 299999})
        self.assertEqual((errors, reviews), ([], []))

    def test_known_non_rust_repository_fails(self):
        errors, reviews = self.review({'Python': 100})
        self.assertTrue(any('0.00%' in error for error in errors))

    def test_empty_statistics_need_review(self):
        errors, reviews = self.review({})
        self.assertEqual(errors, [])
        self.assertTrue(any('statistics are empty' in review for review in reviews))

    def test_malformed_statistics_need_review(self):
        errors, reviews = self.review({'Rust': 'unknown'})
        self.assertEqual(errors, [])
        self.assertTrue(any('statistics are unavailable' in review for review in reviews))

    def test_missing_repository_metadata_needs_review(self):
        errors, reviews = self.review({'Rust': 100}, metadata={})
        self.assertEqual(errors, [])
        self.assertTrue(any('repository metadata' in review for review in reviews))

    def test_archive_status_fails_even_with_rust_code(self):
        metadata = dict(self.metadata, archived=True)
        errors, reviews = self.review({'Rust': 100}, metadata=metadata)
        self.assertTrue(any('archived or disabled' in error for error in errors))

    def test_missing_license_needs_manifest_review(self):
        metadata = dict(self.metadata, license=None)
        errors, reviews = self.review({'Rust': 100}, metadata=metadata)
        self.assertEqual(errors, [])
        self.assertTrue(any('Cargo manifests' in review for review in reviews))

    def test_python_helper_cannot_use_whole_rust_repository_share(self):
        entry = catalog.Entry(10, 'helper', 'https://github.com/owner/compiler/blob/main/helper.py', ('Libraries',))
        errors, reviews = self.review({'Rust': 95, 'Python': 5}, entry=entry)
        self.assertTrue(any('non-Rust source file' in error for error in errors))

    def test_rate_limit_is_reported_for_review(self):
        error = HTTPError(self.entry.url, 403, 'Rate limited', {}, None)
        with patch.object(catalog, 'get_json', side_effect=error):
            errors, reviews = catalog.review_project(self.entry)
        self.assertEqual(errors, [])
        self.assertTrue(any('HTTP 403' in review for review in reviews))

    def test_source_not_found_fails(self):
        error = HTTPError(self.entry.url, 404, 'Missing', {}, None)
        with patch.object(catalog, 'get_json', side_effect=error):
            errors, reviews = catalog.review_project(self.entry)
        self.assertTrue(any('HTTP 404' in error for error in errors))

    def test_crate_repository_is_resolved_before_review(self):
        entry = catalog.Entry(10, 'crate', 'https://crates.io/crates/test-crate', ('Libraries',))

        def lookup(url):
            if url.startswith('https://crates.io/'):
                return {'crate': {'repository': self.entry.url}}
            return {'Rust': 100} if url.endswith('/languages') else self.metadata

        with patch.object(catalog, 'get_json', side_effect=lookup):
            with patch('sys.stdout', new_callable=io.StringIO):
                errors, reviews = catalog.review_project(entry)
        self.assertEqual((errors, reviews), ([], []))

    def test_other_source_host_needs_manual_review(self):
        entry = catalog.Entry(10, 'project', 'https://gitlab.com/owner/project', ('Libraries',))
        with patch.object(catalog, 'get_json') as lookup:
            errors, reviews = catalog.review_project(entry)
        lookup.assert_not_called()
        self.assertEqual(errors, [])
        self.assertTrue(reviews)

    def test_repository_urls_require_the_exact_github_host(self):
        self.assertIsNone(catalog.github_repo('https://github.com.example.com/owner/project'))
        self.assertEqual(catalog.github_repo('https://github.com/owner/project.git'), 'owner/project')

    def test_api_token_is_sent_only_to_github_api(self):
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test-token'}):
            for host, expected in [('api.github.com', 'Bearer test-token'), ('crates.io', None)]:
                with self.subTest(host=host):
                    with patch.object(catalog, 'urlopen', return_value=io.BytesIO(b'{}')) as request:
                        catalog.get_json(f'https://{host}/example')
                    self.assertEqual(request.call_args.args[0].get_header('Authorization'), expected)


if __name__ == '__main__':
    unittest.main()
