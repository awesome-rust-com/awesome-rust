# Curation audit: 2026-11-10

This cleanup applies the [curation criteria](../CURATION.md) to the main list. Source snapshot: [`df0b5d1f333f0573b07cb9cdfc479d5a4f306004`](https://github.com/awesome-rust-com/awesome-rust/tree/df0b5d1f333f0573b07cb9cdfc479d5a4f306004). Observations were collected on 2026-11-10 (Asia/Shanghai).

## Scope and disposition

The source README contained 938 primary list links, excluding its table of contents, badges and links inside descriptions. This included 867 project entries and 71 category/resource/service links. Repeated projects in different categories were counted separately.

| Disposition | Original entries | Destination |
|---|---:|---|
| Archived or explicitly discontinued/deprecated | 111 | [Historical projects](../ARCHIVED.md) |
| Rust share at or below 70% | 77 | [Related tools](../RELATED_TOOLS.md) |
| Individual Shell/Python helper scripts | 2 | Related tools |
| Source could not be recovered | 15 | [Source review](curation-review.md#source-links-to-repair-15-entries) |
| License declaration not confirmed | 7 | [License review](curation-review.md#license-clarification-7-entries) |
| Total project entries moved out of the main list | **212** | 190 classification moves and 22 review holds |

The 111 historical entries comprise 101 archived repositories and 10 unarchived projects with explicit project-level discontinuation/deprecation statements. The 190 classification moves represent 188 distinct source targets; the two helper scripts are entries within the Rust compiler repository, not a judgment against that repository.

The split preserves useful mixed-language tools such as Deno and Servo outside the strict implementation-language scope. A missing license signal is a request for clarification, not a legal conclusion. The review document retains the original targets of broken links so they can be repaired.

Ten now-empty linked category entries were removed along with empty grouping bullets and six empty sections. Seven verified successor project entries were added, giving **723 primary list links** after the cleanup (`938 - 212 - 10 + 7`). The main list's table of contents was regenerated from the remaining headings.

## Successor recommendations

The following source repositories were accessible, unarchived, non-empty, above the language threshold and had an identifiable project license at review time. They preserve functionality formerly represented by retired entries. This metadata/documentation check does not substitute for building each project.

| Previous entry | Current source | Rust snapshot |
|---|---|---:|
| simias/rustation | [simias/rustation-ng](https://github.com/simias/rustation-ng) | 99.85% |
| ogham/exa | [eza-community/eza](https://github.com/eza-community/eza) | 91.01% |
| xi-editor | [lapce/lapce](https://github.com/lapce/lapce) | 98.69% |
| xsv | [dathere/qsv](https://github.com/dathere/qsv) | 71.78% |
| Rust Language Server | [rust-lang/rust-analyzer](https://github.com/rust-lang/rust-analyzer) | 96.87% |
| fdehau/tui-rs | [ratatui/ratatui](https://github.com/ratatui/ratatui) | 99.77% |
| djc/askama | [askama-rs/askama](https://github.com/askama-rs/askama) | 96.58% |

The existing clap and tempfile entries remain the main-list destinations for functionality previously provided by docopt.rs and tempdir; they were not duplicated.

## Source-link repairs

| Previous entry | Source now linked | Basis |
|---|---|---|
| trust-dns | [Source](https://github.com/hickory-dns/hickory-dns) | Original README points to the successor source |
| ParityDB | [Source](https://github.com/paritytech/parity-db) | crates.io repository metadata identifies the source |
| flosse/rust-sun | [Source](https://codeberg.org/flosse/sun) | Original README points to the successor source |
| elastic-rs/elastic-reqwest | [Source](https://github.com/elastic-rs/elastic) | Original README points to the successor source |
| Kiss3D | [Source](https://github.com/dimforge/kiss3d) | crates.io repository metadata identifies the source |
| Kiss3d | [Source](https://github.com/dimforge/kiss3d) | crates.io repository metadata identifies the source |
| Susurrus/serialport-rs | [Source](https://github.com/serialport/serialport-rs) | crates.io repository metadata identifies the source |
| pyros2097/rust-embed | [Source](https://pyrossh.dev/repos/rust-embed) | crates.io repository metadata identifies the source |

The Codeberg sun project and author-hosted rust-embed source still need host/language-statistics verification, as recorded in the review document. Their previous GitHub placeholders or unavailable URLs were not used to infer a 0% Rust share.

The cleanup also removes the malformed legacy Specs badge link and corrects the Oryxis release badge's URL scheme. These are badge-format repairs, separate from the eight source migrations.

## Checks and interpretation

GitHub metadata was collected for 828 original source targets; unavailable targets remain distinguishable from repositories with empty language statistics. Additional successor sources were checked separately. For accessible GitHub sources the review considered:

- Canonical name, source availability, archive/disable/empty status and fork relationship.
- Default-branch commit date, latest GitHub Release and status-check summary.
- Language-byte totals, root `.gitattributes`, source scope and individual-file implementations.
- Repository license metadata, license-file names, Cargo manifests, README declarations and targeted subdirectory/source-header checks.
- README content, documentation/usage entry points and CI configuration or badge references.

GitLab sources were checked using their public project and language endpoints. When a platform omitted a maintenance field, the value was left unknown instead of assuming a positive status.

Project-level README notices were read in context. Deprecated old versions, an unmaintained integration, a discontinued chat channel, or an original author handing maintenance to the community were not treated as project abandonment. In particular, the glium community-maintenance statement and generic-array's old-version deprecation did not trigger removals.

More than one year without a default-branch commit or GitHub Release, missing CI, a failing check, low stars and fork status alone did not trigger removal. Those signals still need maintainer/PR/build review for affected existing entries. License checks also inspected subprojects: configure_me and vulkust were retained after their Cargo declarations were found.

The historical, related-tool and review tables retain the category, measured percentage where applicable, reason and a pinned link to each original entry. Percentages and maintenance statuses can change; restore or reclassify projects when updated evidence satisfies the criteria.

No complete build matrix, dependency-vulnerability audit or code-security review was performed across the referenced projects. This is a dated curation review, not a claim that every retained project has passed a full technical audit.
