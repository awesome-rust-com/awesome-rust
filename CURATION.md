# Curation criteria

The main list recommends stable, useful projects implemented primarily in Rust. Review the actual project behind an entry, rather than its name, popularity or association with the Rust ecosystem.

## Requirements for the main project list

| Criterion | Requirement | If it is not satisfied |
|---|---|---|
| Relevance | A useful Rust application, library, framework or development tool with a clear purpose. | Omit placeholder projects; put learning material and hosted services in their appropriate resource categories. |
| Implementation | The linked project is implemented primarily in Rust. A Rust extension, language definition or helper script is not automatically a Rust implementation. | Consider [related tools](RELATED_TOOLS.md). |
| Language share | Rust is **strictly more than 70%** of the code counted by the source host's language statistics. Exactly 70% does not qualify. | Consider related tools; this is a scope rule, not a quality rating. |
| Source availability | The public canonical source can be inspected and the entry links to the current project. | Follow redirects and official migration notices. Put unresolved source links in [review](docs/curation-review.md). |
| Maintenance | The repository is not archived, disabled or empty, and the project has not explicitly been discontinued, abandoned or deprecated as a whole. | Prefer a verified successor; preserve the old entry in [archived projects](ARCHIVED.md). |
| License | A clear project license can be found in repository metadata, license files, Cargo manifests or source/documentation declarations. | Inspect project subdirectories before concluding that the license is unresolved. Hold unresolved entries for clarification. |
| Usability | A reader can find the purpose, installation/use instructions, an example or a documentation entry point. | Request clarification or additional documentation before adding a new recommendation. |
| Identity | The canonical project is identified, including the relevant crate or subproject in a monorepo. | Consolidate duplicate recommendations or use cross-references; preserve distinct subprojects. |

Categories, organizations, documentation, presentations, registries and hosted services are not source-code projects. Keep them in clearly identified resource/category sections rather than applying a language percentage to them.

## Measuring the Rust share

For GitHub repositories, use the default branch's [language statistics](https://docs.github.com/en/rest/repos/repos#list-repository-languages):

```text
Rust share = Rust bytes / total bytes counted in language statistics
Qualifies  = Rust bytes * 10 > total bytes * 7
```

Evaluate the unrounded values. Displayed percentages may be rounded; file counts and lines of code are different measurements. GitHub uses [Linguist](https://github.com/github-linguist/linguist), whose exclusions and [attribute overrides](https://github.com/github-linguist/linguist/blob/main/docs/overrides.md) can affect the result. Investigate blanket `linguist-language=Rust` overrides or other suspicious statistics rather than treating the displayed percentage as proof.

For GitLab, use the public project language-percentage endpoint and identify that platform in the review. For other source hosts, record an equivalent, reproducible measurement and its scope. If statistics are unavailable, mark the measurement as unknown; unknown is not 0%.

A whole-repository percentage does not establish the language of a linked file or subproject. A Python helper in a Rust compiler repository remains a Python helper. When a monorepo entry needs a subproject-specific measurement, record that measurement and scope explicitly; do not silently substitute a different denominator to pass the threshold.

## Signals that require judgment

- **Activity:** more than 12 months without a default-branch commit or a release triggers review, not automatic removal. Check pull requests, maintainer responses, published packages and whether the project is intentionally stable. Repository `updated_at` alone is not evidence of code maintenance.
- **Maintenance mode:** distinguish a stable project accepting fixes from a project that declares itself discontinued. Consider consolidating recommendations into an official successor when features have moved there.
- **CI and tests:** build instructions, tests, CI and published packages support usability. No GitHub Actions workflow, a stale badge or one failing check alone is not proof that a project is unusable. Inspect the actual failure and other build services.
- **Forks:** retain independently maintained forks with a clear purpose or improvements. Do not reject a project solely because it is a fork; ordinary mirrors should point readers upstream.
- **Popularity:** stars, forks and issue counts provide context, not minimum admission thresholds. Check maintainer engagement instead of assuming that many open issues imply poor quality.
- **README wording:** a deprecated feature, old release or dependency does not mean that the whole project is deprecated. Read the surrounding context, including community-maintenance statements.

## Where entries belong

1. **Main list:** projects meeting the requirements, with appropriate categories and documentation.
2. **Related tools:** useful mixed-language projects or individual non-Rust tools outside the implementation/language-share scope.
3. **Archived projects:** archived, discontinued or explicitly deprecated projects retained for reference, with successor links where verified.
4. **Review:** unresolved source locations or license declarations. Restore entries after the issue is resolved and the criteria are met.
5. **Resources and services:** tutorials, talks, registries, hosted tools and category/organization links, evaluated for relevance and accessibility.

Existing entries with incomplete metadata are reviewed rather than declared low quality automatically. The [2026-11-10 audit](docs/curation-audit-2026-11-10.md) records the first cleanup and its limits. Language percentages and maintenance states are dated observations, not permanent certifications.

## Evidence to include in a contribution

Provide the canonical source URL, applicable crate/subproject, purpose and usage/docs link, Rust percentage with the measurement date and source, license location, and maintenance status. Explain an independent fork or a successor migration when relevant. Keep the entry description concise and order it alphabetically within its category.
