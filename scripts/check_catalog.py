#!/usr/bin/env python3
"""Check catalog Markdown and optionally review added project sources."""

import argparse
from dataclasses import dataclass
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'\]\((<[^>]+>|[^\s)]+)(?:\s+[\"\'][^\"\']*[\"\'])?\)')
BULLET = re.compile(r'^(\s*)[*+-]\s+(.+)')
PROJECT = re.compile(r'^\[([^\]]+)\]\((https?://[^\s)]+)\)')
RESOURCE_SECTIONS = {"Resources", "Registries", "Table of contents"}
NON_RUST_FILES = {".py", ".sh", ".el", ".vim", ".js", ".ts", ".c", ".cpp", ".java"}


@dataclass(frozen=True)
class Entry:
    line: int
    label: str
    url: str
    category: tuple[str, ...]


def prose_lines(text):
    """Skip fenced examples while retaining source line numbers."""
    fence = None
    fence_start = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            run, trailing = marker.groups()
            if fence is None:
                fence = run
                fence_start = number
            elif run[0] == fence[0] and len(run) >= len(fence) and not trailing.strip():
                fence = None
            continue
        if fence is None:
            yield number, line
    if fence is not None:
        raise ValueError(f'unclosed code fence starting on line {fence_start}')


def headings(text):
    used = set()
    result = []
    for number, line in prose_lines(text):
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$', line)
        if not match:
            continue
        marks, title = match.groups()
        plain = re.sub(r'<[^>]+>', '', html.unescape(title))
        plain = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', plain)
        stem = re.sub(r'[^\w\- ]', '', plain.lower()).replace(' ', '-')
        anchor = stem
        suffix = 0
        while anchor in used:
            suffix += 1
            anchor = f'{stem}-{suffix}'
        used.add(anchor)
        result.append((number, len(marks), title, anchor))
    return result


def entries(text):
    sections = {}
    parents = {}
    result = []
    for number, line in prose_lines(text):
        heading = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading:
            level = len(heading[1])
            sections = {key: value for key, value in sections.items() if key < level}
            sections[level] = heading[2]
            parents = {}
            continue
        item = BULLET.match(line)
        if not item or 2 not in sections or sections[2] in RESOURCE_SECTIONS:
            continue
        depth = len(item[1].expandtabs(4))
        parents = {key: value for key, value in parents.items() if key < depth}
        primary = PROJECT.match(item[2])
        if primary:
            category = tuple(value for key, value in sorted(sections.items()) if key >= 2)
            category += tuple(parents.values())
            result.append(Entry(number, primary[1], primary[2], category))
        parents[depth] = primary[1] if primary else item[2]
    return result


def check_markdown(root):
    root = root.resolve()
    errors = []
    documents = sorted(root.glob('*.md')) + sorted((root / 'docs').rglob('*.md'))
    for document in documents:
        text = document.read_text(encoding='utf-8')
        relative = document.relative_to(root)
        try:
            visible = list(prose_lines(text))
        except ValueError as exc:
            errors.append(f'{relative} {exc}')
            continue
        for number, line in visible:
            if re.match(r'^\s*[*+-]\s+[*+-]\s+\[', line):
                errors.append(f'{relative}:{number} duplicated list marker hides a project entry')
            for match in LINK.finditer(line):
                target = match[1].strip('<>')
                try:
                    parsed = urlsplit(target)
                except ValueError:
                    errors.append(f'{relative}:{number} malformed link {target}')
                    continue
                if parsed.scheme in {'http', 'https', 'mailto'}:
                    continue
                if parsed.scheme or re.match(r'(?i)^h?https?[l]?[/]', target):
                    errors.append(f'{relative}:{number} malformed link {target}')
                    continue
                destination = (document.parent / unquote(parsed.path)).resolve()
                if not parsed.path:
                    destination = document
                if not destination.is_relative_to(root.resolve()) or not destination.is_file():
                    errors.append(f'{relative}:{number} missing local file {target}')
                    continue
                if parsed.fragment and destination.suffix.lower() == '.md':
                    try:
                        anchors = {item[3] for item in headings(destination.read_text(encoding='utf-8'))}
                    except ValueError as exc:
                        errors.append(f'{relative}:{number} linked document {target} has an {exc}')
                        continue
                    if unquote(parsed.fragment) not in anchors:
                        errors.append(f'{relative}:{number} missing local heading {target}')

    main = (root / 'README.md').read_text(encoding='utf-8')
    try:
        outline = headings(main)
    except ValueError:
        return errors
    toc = next((item for item in outline if item[2] == 'Table of contents'), None)
    if toc:
        body = next((item for item in outline if item[0] > toc[0] and item[1] <= toc[1]), None)
        if body:
            expected = [item[3] for item in outline if item[0] >= body[0]]
            actual = []
            for number, line in prose_lines(main):
                if toc[0] < number < body[0]:
                    actual.extend(match[1] for match in re.finditer(r'\]\(#([^)]+)\)', line))
            if actual != expected:
                errors.append('README.md table of contents differs from the document headings')

    seen = {}
    for entry in entries(main):
        key = (entry.category, entry.url.rstrip('/'))
        if key in seen:
            errors.append(f'README.md:{entry.line} duplicate project in its category, first at line {seen[key]}')
        seen[key] = entry.line
    return errors


def added_entries(current, previous):
    known = {entry.url.rstrip('/') for entry in entries(previous)}
    return [entry for entry in entries(current) if entry.url.rstrip('/') not in known]


def github_repo(url):
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    parts = parsed.path.strip('/').split('/')
    if parsed.hostname != 'github.com' or len(parts) < 2:
        return None
    owner, name = parts[:2]
    name = name.removesuffix('.git')
    if any(part in {'.', '..'} or not re.fullmatch(r'[\w.-]+', part, re.ASCII) for part in (owner, name)):
        return None
    return f'{owner}/{name}'


def get_json(url):
    headers = {'User-Agent': 'awesome-rust-catalog-check', 'Accept': 'application/json'}
    token = os.environ.get('GITHUB_TOKEN')
    if urlsplit(url).hostname == 'api.github.com' and token:
        headers['Authorization'] = f'Bearer {token}'
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def review_project(entry):
    errors = []
    reviews = []
    location = f'README.md:{entry.line} {entry.label}'
    url = entry.url
    parsed = urlsplit(url)
    if parsed.hostname == 'crates.io' and parsed.path.startswith('/crates/'):
        name = parsed.path.split('/')[2]
        try:
            crate = get_json('https://crates.io/api/v1/crates/' + quote(name, safe=''))['crate']
            url = crate.get('repository') or crate.get('homepage') or url
        except (URLError, TimeoutError, ValueError, KeyError) as exc:
            return errors, [f'{location} package source needs review ({type(exc).__name__})']
    repo = github_repo(url)
    if not repo:
        return errors, [f'{location} source host or project scope needs manual review']
    if '/blob/' in urlsplit(url).path and Path(urlsplit(url).path).suffix.lower() in NON_RUST_FILES:
        errors.append(f'{location} links to a non-Rust source file')
    api = f'https://api.github.com/repos/{repo}'
    try:
        metadata = get_json(api)
        if not isinstance(metadata, dict) or not isinstance(metadata.get('full_name'), str):
            return errors, [f'{location} repository metadata needs manual review']
        if metadata.get('archived') or metadata.get('disabled'):
            errors.append(f'{location} source repository is archived or disabled')
        languages = get_json(api + '/languages')
    except HTTPError as exc:
        if exc.code == 404:
            errors.append(f'{location} public source lookup returned HTTP 404')
        else:
            reviews.append(f'{location} source lookup needs review (HTTP {exc.code})')
        return errors, reviews
    except (URLError, TimeoutError, ValueError) as exc:
        return errors, reviews + [f'{location} source lookup needs review ({type(exc).__name__})']
    if not isinstance(languages, dict) or any(type(size) is not int or size < 0 for size in languages.values()):
        reviews.append(f'{location} language statistics are unavailable')
        return errors, reviews
    total = sum(languages.values())
    rust = languages.get('Rust', 0)
    if total == 0:
        reviews.append(f'{location} language statistics are empty')
    elif rust * 10 <= total * 7:
        errors.append(f'{location} Rust share is {rust / total:.2%}, requiring strictly more than 70%')
    else:
        print(f'PASS {location} Rust share {rust / total:.2%}')
    if not metadata.get('license'):
        reviews.append(f'{location} inspect license files, Cargo manifests and source declarations')
    if '/tree/' in url or '/blob/' in url:
        reviews.append(f'{location} verify the linked file/subproject scope against repository statistics')
    return errors, reviews


def previous_readme(root, ref):
    commit = subprocess.check_output(
        ['git', 'rev-parse', '--verify', '--end-of-options', f'{ref}^{{commit}}'],
        cwd=root, text=True, stderr=subprocess.PIPE,
    ).strip()
    return subprocess.check_output(['git', 'show', f'{commit}:README.md'], cwd=root, text=True, stderr=subprocess.PIPE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref', help='Compare project URLs with this Git commit or ref')
    parser.add_argument('--github', action='store_true', help='Review source metadata for new project URLs')
    args = parser.parse_args()
    errors = check_markdown(ROOT)
    reviews = []
    if args.github and not errors:
        try:
            previous = previous_readme(ROOT, args.base_ref) if args.base_ref else ''
        except subprocess.CalledProcessError:
            parser.error(f'Cannot read README.md at base ref {args.base_ref!r}')
        current = (ROOT / 'README.md').read_text(encoding='utf-8')
        candidates = added_entries(current, previous)
        checked = set()
        for entry in candidates:
            if entry.url in checked:
                continue
            checked.add(entry.url)
            project_errors, project_reviews = review_project(entry)
            errors.extend(project_errors)
            reviews.extend(project_reviews)
        print(f'Reviewed {len(checked)} new project URLs')
    for message in reviews:
        print(f'REVIEW {message}')
    for message in errors:
        print(f'ERROR {message}', file=sys.stderr)
    if errors:
        return 1
    print('Catalog checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
