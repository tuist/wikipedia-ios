# wikimedia/wikipedia-ios with Once

This is the default branch of tuist/wikipedia-ios. It only holds the experiment;
`main` is an unmodified mirror of
[wikimedia/wikipedia-ios](https://github.com/wikimedia/wikipedia-ios).

- `.github/workflows/sync.yml` runs every four hours: it fast-forwards `main`
  from wikimedia/wikipedia-ios and builds and tests the latest upstream commit
  with Once. The fast-forward needs a `SYNC_TOKEN` secret (Contents and
  Workflows write) because `GITHUB_TOKEN` cannot push upstream workflow file
  changes.
- `.github/workflows/once.yml` checks out a wikimedia/wikipedia-ios commit,
  writes a `once.toml` from `overlay/graph.toml` (build configuration) and
  `overlay/cache.toml` (Tuist cache), and runs `once build Wikipedia` plus the
  unit test suites upstream runs on pull requests (`WikipediaUnitTests` with the
  `Test` configuration, the WMFComponents and WMFData package tests with
  `Debug`) on the same GitHub-hosted runner and Xcode upstream uses. Once reads
  `Wikipedia.xcodeproj` directly, so the project itself is not modified.
  The shared cache and run reporting go to the
  [tuist/wikipedia-ios](https://tuist.dev/tuist/wikipedia-ios) Tuist project.
  Run it manually with a `ref` to replay any upstream commit, and with
  `remote_cache: false` for a cold baseline.

Upstream workflows are disabled in this fork so nothing from
wikimedia/wikipedia-ios's release or deploy automation runs here.
