# Renovate + Devin burn-down demo

How this repository is wired, what the audience sees, and which knob produces which effect.

## The loop

```
Renovate run (.github/workflows/renovate.yml, daily 06:17 UTC or manual dispatch)
  -> opens/updates PRs on renovate/* branches
  -> writes the Dependency Dashboard issue (#24)
        |
        |  Devin Automation "Renovate dashboard burn-down"
        |  trigger: github:issues (opened/edited) where title contains "Dependency Dashboard"
        v
Devin parent session runs !renovate_burndown
  -> reads every dashboard row + the real CI failure logs
  -> classifies each row BUNDLE / BUNDLE-WITH-FIX / DISPATCH
  -> opens ONE bundle PR with before/after evidence
  -> opens one child session per DISPATCH row
        |
        |  child sessions branch off the bundle branch
        v
Child fix PRs, each with its own before/after proof
  -> unanswered product decisions are posted as a <!-- devin-question --> comment
     on the PR that raised them; the run does not stall on them
  -> Devin Automation "Renovate burn-down: /devin-answer on a PR"
     trigger: github:issue_comment where the body starts with /devin-answer
  -> a new session applies the decision, pushes to that PR and replies in the thread
```

Nobody clicks anything between the Renovate run and the fix PRs.

## The question protocol

Devin never guesses a product decision and never blocks a background run waiting for one. It posts this on the PR the question came from and carries on with the rest:

```
<!-- devin-question -->
**Decision needed:** one sentence, the actual trade-off.

- **A)** option, and what it costs
- **B)** option, and what it costs

What I did meanwhile: <the reversible thing that kept CI green>.
Reply to this comment with `/devin-answer A` (or B, or free text) and I will apply it.
```

The HTML marker is how the follow-up session finds the question; a reply *starting with* `/devin-answer` is what fires the automation. Two live examples are open now:

- Node engines floor (`>=18` vs `>=24`): https://github.com/COG-GTM/renovate-burndown-demo/pull/33
- Keep or defer TypeScript 7: https://github.com/COG-GTM/renovate-burndown-demo/pull/31

## What actually ran here

| Stage | Artefact |
| --- | --- |
| Dashboard | https://github.com/COG-GTM/renovate-burndown-demo/issues/24 — 23 update rows + 7 detected-dependency rows |
| Parent session | https://app.devin.ai/sessions/3351e65625e54e3abfb1555cc5343dec — 6 minutes, unattended |
| Bundle PR | https://github.com/COG-GTM/renovate-burndown-demo/pull/27 — 16 of 23 rows, CI green |
| Child fix PRs | #28 jsonwebtoken 9, #29 pydantic 2, #30 node 24, #31 typescript 7, #32 cryptography 49, #33 tar 7, #34 jest 30 |

Failures worth showing, because they are why "just merge the bot's PRs" does not work:

- `requests 2.33`, `pytest 9`, `urllib3 2.7` → `No matching distribution`, because CI pinned Python 3.9 and the config had no `constraints.python`. Config bug, not a code bug.
- `pytest 7.2.0` on Python 3.14 → `AttributeError: module 'ast' has no attribute 'Str'`. Two separate Renovate PRs cancel each other out; only the bundle is mergeable.
- `PyYAML 5.4` → build failure on `cython_sources`.
- `fastapi 0.109.1` + `httpx 0.28.1` → `Client.__init__() got an unexpected keyword argument 'app'`.
- `Jinja2 2.10` on Python 3.14 → `soft_unicode` import error.
- `aws-sdk 2.1000.0` has **no** Renovate PR at all: v2 is deprecated and the successor is the `@aws-sdk/client-*` family, which is a migration, not a version bump. Renovate cannot burn this one down at any config setting.

## Where the noise comes from

`renovate.json` in this repo is deliberately the noisy profile: `prConcurrentLimit: 0` and
`prHourlyLimit: 0` mean unlimited, so the first run opened 24 PRs at once. The other sources, in the
order they usually bite:

1. **One PR per dependency.** The default. 24 dependencies, 24 PRs. Fixed with `groupName` in `packageRules`.
2. **`separateMajorMinor` (default true).** A dependency that has both a minor and a major available produces two PRs for the same package.
3. **No rate limits.** Defaults are `prHourlyLimit: 2` / `prConcurrentLimit: 10`; this repo removed both, so the whole backlog lands in one burst.
4. **Rebase churn.** Default `rebaseWhen: auto` re-pushes open PR branches when the base branch moves, so every merge re-runs CI on every open Renovate PR. `rebaseWhen: "conflicted"` stops it.
5. **Brand-new releases.** No `minimumReleaseAge`, so a release published an hour ago gets a PR and sometimes gets yanked.
6. **Security alerts bypass your rules.** `osvVulnerabilityAlerts` + `vulnerabilityAlerts` PRs ignore schedules and grouping by design — that is correct behaviour, but it is unbatchable volume.
7. **Lockfile-only and digest updates.** Transitive-only bumps and Action SHA pins produce PRs with no manifest change.
8. **Missing `constraints`.** Renovate proposes versions your runtime cannot install, so the PR is red before anyone looks at it. This produced 3 of the 7 red PRs here.

## The knobs, and what each one demonstrates

`renovate.tuned.json` is the same repo under control. Swap it over `renovate.json` to show the before/after:

| Setting in `renovate.tuned.json` | Effect on the dashboard |
| --- | --- |
| `groupName` per manager and update type | 24 PRs collapse to ~4 |
| `schedule: ["* 0-6 * * 1"]` + `timezone` | PRs only appear in the Monday-morning window |
| `prConcurrentLimit: 5`, `prHourlyLimit: 2` | backlog drains gradually; the rest sits in the dashboard's "Rate-Limited" section |
| `minimumReleaseAge: "7 days"` | fresh releases wait; they appear in the "Pending" section with a countdown |
| `major.dependencyDashboardApproval: true` | majors open no PR until someone ticks the dashboard checkbox — the dashboard becomes the queue Devin works from |
| `vulnerabilityAlerts` with `schedule: []` and `minimumReleaseAge: null` | security fixes still jump every restriction |
| `github-actions` group with `automerge: true` | the boring tier merges itself; nobody reviews an Action bump |
| `constraints.python` | no more `No matching distribution` PRs |
| `rebaseWhen: "conflicted"` | CI stops re-running on every open PR after each merge |

Two settings that matter for the demo but are not in the file: `"extends": ["config:best-practices"]`
pulls in abandonment detection (dashboard warns about deprecated packages with a replacement PR
available), and `ignoreDeps` is the honest answer for anything nobody intends to upgrade.

## Running the demo

1. Show the dashboard issue #24. Point at the sections: Open, Rate-Limited, Pending Approval, Detected Dependencies, and "Found renovate config warnings".
2. Trigger a Renovate run: Actions → Renovate → Run workflow. The dashboard rewrites itself.
3. The dashboard edit fires the Devin Automation; the parent session starts with no human input.
4. While it runs, walk the noise list above against the actual PR list.
5. Open the bundle PR: the grouping rationale, the before/after evidence pack, green CI.
6. Open a child fix PR, e.g. #30 (Node 24): the only behavioural difference is V8's malformed-JSON 400 wording, shown side by side rather than asserted.
7. Open the PR comment where a child asked a question instead of guessing — the Node engines floor (`>=18` from tar 7 vs `>=24`) on #33, and whether TypeScript 7 stays on #31. Reply `/devin-answer A`; a session starts on that comment, implements the choice, pushes to the PR and answers in the thread.

## Setup requirements

- `RENOVATE_TOKEN` repository secret: a PAT (or App token) with `repo` + `workflow` scope. Without it the workflow fails at the Renovate step.
- The Devin Automations live in Devin settings, not in this repo, and need `bypass_approval` so the parent can spawn children unattended. Two are wired for this repo: the dashboard trigger (`github:issues`, title contains "Dependency Dashboard", runs `!renovate_burndown`, posts its report back as an issue comment) and the answer trigger (`github:issue_comment`, body starts with `/devin-answer`).
- The Renovate GitHub App is an alternative to `.github/workflows/renovate.yml`; do not run both against this repo or you get duplicate PRs.
