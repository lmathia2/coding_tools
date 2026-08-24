# Documentation Validation

Find authoritative commands in CI, Makefiles, package scripts, docs configuration, and contribution guides.

Useful validation classes:

| Class | Examples |
|---|---|
| Docs build | MkDocs, Sphinx, Docusaurus, Jekyll, mdBook |
| API generation | OpenAPI, GraphQL, TypeDoc, Javadoc, rustdoc |
| Executable examples | doctest, example tests, notebook execution |
| Links | markdown-link-check, lychee, Sphinx linkcheck |
| Drift | regenerate docs/specs and require a clean Git diff |
| Style | Vale, markdownlint, repository-specific linters |

If no automated check exists, manually verify the changed links/examples and report that automation is absent.

Do not add a new documentation framework for a one-line fix. Reuse repository-native tooling.
