# Contributing

Contributions are welcome. Our goal is to recommend projects that are stable and useful to people building with Rust.

## Before adding a project

Read the [curation criteria](CURATION.md). For the main project list, confirm that:

- The actual linked project is implemented primarily in Rust, with a Rust language share **strictly greater than 70%**.
- The canonical source is publicly accessible and has not been archived, disabled or explicitly discontinued/deprecated as a whole.
- A clear license and a purpose, usage example, installation instructions or documentation entry point can be found.
- The entry is not a duplicate. A fork has a clear independent purpose; a monorepo entry identifies its crate/subproject.

Popularity, fork status, an old commit or one failing CI check is not an automatic rejection. Missing language statistics are unknown, not zero. See the criteria for how to measure the language share and handle these review signals.

Useful projects outside the language threshold belong in [related tools](RELATED_TOOLS.md). Retired projects belong in [archived projects](ARCHIVED.md); unresolved source/license entries belong in [review](docs/curation-review.md). Tutorials, registries and services remain in their relevant resource categories.

## Editing the list

Edit [README.md](README.md), choose the appropriate category, keep entries alphabetically ordered, and open a pull request. Use a concise description:

```markdown
* [owner/project](https://github.com/owner/project) [[crate-name](https://crates.io/crates/crate-name)] — What the project does.
```

The crate link is optional. If you include a CI badge, use a current workflow or build-service URL rather than a historical template.

## Pull request evidence

Include the following information when adding or restoring a project:

- Canonical source URL and the relevant crate/subproject, if applicable.
- Rust share, measurement source/scope and date, evaluated before rounding.
- License file, Cargo declaration or other explicit license location.
- Maintenance status and a documentation/use-example link.
- Reason for an independent fork, successor replacement or duplicate cross-reference, when applicable.

For removals or moves, state the reason and preserve useful historical or migration context. A project can be useful and high quality while falling outside this list's language-share scope.

Thank you for helping keep the list useful and current.
