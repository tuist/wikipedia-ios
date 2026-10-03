# wikimedia/wikipedia-ios with Once

This is the default branch of tuist/wikipedia-ios. It only holds the experiment;
`main` is an unmodified mirror of
[wikimedia/wikipedia-ios](https://github.com/wikimedia/wikipedia-ios).

- `.github/workflows/sync.yml` runs every four hours: it fast-forwards `main`
  from wikimedia/wikipedia-ios and builds and tests the latest upstream commit
  with Once. The fast-forward needs a `SYNC_TOKEN` secret (Contents and
  Workflows write) because `GITHUB_TOKEN` cannot push upstream workflow file
  changes.
- `.github/workflows/once.yml` checks out a wikimedia/wikipedia-ios commit, adds
  `overlay/once.toml`, and runs `once build Wikipedia` and `once test` on the
  same GitHub-hosted runner and Xcode wikimedia/wikipedia-ios uses for its unit
  tests. Once reads `Wikipedia.xcodeproj` directly, so no manifest is needed.
  The shared cache and run reporting go to the
  [tuist/wikipedia-ios](https://tuist.dev/tuist/wikipedia-ios) Tuist project.
  Run it manually with a `ref` to replay any upstream commit, and with
  `remote_cache: false` for a cold baseline.

Upstream workflows are disabled in this fork so nothing from
wikimedia/wikipedia-ios's release or deploy automation runs here.
