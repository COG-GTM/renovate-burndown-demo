# Deprecated dependencies

Tracked deprecations that Renovate reports but cannot fix automatically, because no
drop-in replacement version exists.

## npm `aws-sdk` (AWS SDK for JavaScript v2) — pinned at `2.1000.0`

Status: deprecated / end-of-support. npm publishes the deprecation notice
"The AWS SDK for JavaScript (v2) has reached end-of-support, and no longer receives
updates. Please migrate your code to use AWS SDK for JavaScript (v3)."
v3 is a different package family (`@aws-sdk/client-*`), so there is no version bump
that resolves this.

Usage in this repo, as of this commit:

- No source file imports it. `git grep -i aws-sdk -- . ':!package-lock.json' ':!package.json'`
  returns nothing; the only JS sources are `src/server.js` (express, lodash, zod,
  jsonwebtoken) and `test/smoke.test.js` (assert, http, jsonwebtoken, lodash, minimist).
- Nothing depends on it transitively: `npm ls aws-sdk` lists it only under the project
  root, so it is a direct dependency with no dependents.

Consequence: the package is installed by `npm install` and shipped in the Docker image,
but no code path can reach it. It is an install-size and audit-noise cost only, not a
runtime risk.

Open decision (migrate to `@aws-sdk/client-*` v3 vs. remove the dependency) is tracked on
the pull request that added this file; `package.json` is deliberately left unchanged until
it is answered.
