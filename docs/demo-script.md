# Demo script — Renovate + Devin dependency burn-down

Run time: 12–15 minutes talking, ~8 minutes of Devin working in the background while you talk.
Companion to `renovate-demo.md`, which holds the config detail you dip into when asked.

The shape of the story: **a bot that only creates work → an agent that closes it out → the one
thing it refuses to decide for you.**

---

## Before the call (5 minutes)

Run `docs/reset-demo.sh` (or the manual steps at the bottom). It closes the previous run's Devin
PRs and leaves the repo in the starting state:

| Should be true at the start | Check |
| --- | --- |
| 24 open `renovate/*` PRs, 7 of them red | `gh pr list --author yubinjee-cog` |
| Dashboard issue #24 open, no Devin comment on it | https://github.com/COG-GTM/renovate-burndown-demo/issues/24 |
| No open `devin/*` PRs | `gh pr list --search "head:devin/"` |
| Both automations enabled | https://app.devin.ai/automations |

Open these tabs in order: dashboard issue, PR list filtered to red CI, Devin automations page,
this repo's Actions tab.

---

## 1. The problem, in their language (2 min)

Open the **PR list**. 24 open PRs from a bot, 7 red.

> "This is a week of Renovate on one small service. Every one of these is somebody's afternoon.
> Nobody merges them, so the backlog grows, and the security ones sit in it."

Open **issue #24**, the Dependency Dashboard.

> "Renovate is honest about it — it writes this issue as the inventory of everything it wants to
> do. Open, rate-limited, pending approval, and at the bottom the config warnings it hit. This is
> the input to everything that follows."

Point at one red PR (#13, pytest 9) and one that looks fine (#17, grouped non-major).

> "The trap: #13 is red because CI pins Python 3.9. #17 moves Python forward, which fixes #13 —
> but #17 is red too, because it kept pytest at a version that can't run on 3.14. Each PR is
> judged alone; the answer only exists in the combination. That's the part a human has to do, 24 times."

## 2. Fire it (1 min)

Actions → **Renovate** → Run workflow. When it finishes, the dashboard issue rewrites itself.

> "That edit is the trigger. Nobody is going to touch anything from here on."

Show the automation: `github:issues`, title contains "Dependency Dashboard" →
starts a Devin session with the burn-down playbook, `bypass_approval` so it can spawn children.

*(If Renovate has nothing new to write, use the fallback in the reset script to edit the issue
body directly — the trigger is the issue edit, not Renovate itself.)*

## 3. Talk while it works (4–5 min)

The session appears within seconds. Leave it open on one side and go back to the PR list.

> "It reads every row on that dashboard, pulls the *actual CI failure logs* — not the check name —
> and puts each row in one of three buckets: safe to bundle, bundle once I fix it, or too risky,
> hand it to its own agent."

Now the noise conversation, which is the one most people actually want:

> "Why 24 PRs at all? That's configuration, not fate." Walk `renovate.json` vs
> `renovate.tuned.json` — grouping collapses 24 → ~4, `prConcurrentLimit`/`prHourlyLimit` drain
> the backlog gradually, `minimumReleaseAge` stops day-zero releases, `major.dependencyDashboardApproval`
> turns the dashboard into the approval queue, and `constraints.python` alone would have prevented
> 3 of the 7 red PRs.

> "Tuning gets you from 24 PRs to 4. It does not get you to zero — someone still has to decide
> whether pydantic 2 breaks the product. That's the half Renovate cannot do, and it's the half
> Devin is doing right now."

Worth landing: `aws-sdk` v2 is on the dashboard with **no PR**, because the successor is the
`@aws-sdk/client-*` family. No Renovate setting will ever fix that one.

## 4. The bundle (3 min)

The session posts its report as a comment on issue #24 and opens the bundle PR.

Open the **bundle PR**:

- **Rationale by section** — "runtime bump and everything it unblocks", "security patches", "CI
  actions", "config fixes". Not a dump of 16 bumps; a reason for each group.
- **Deviations** — where it went *past* what Renovate proposed because the proposed version
  couldn't build on the new runtime.
- **Excluded, with reasons in plain English** — every row it did not bundle and where that work went.
- **Before/after evidence pack** — same tests, same endpoints, same CLI, run on the base branch
  first and replayed on the bundle.

> "This is the bit to be sceptical about, so it doesn't ask you to take its word. Baseline captured
> *before* anything moved, identical commands replayed after, every difference listed and
> justified — the pytest version header and one new deprecation warning. Editing a test to make a
> difference go away is explicitly forbidden."

Then the **child PRs** — one per risky update, each branched off the bundle so they don't fight it,
each with its own proof. Show #30 (Node 24): the only behavioural difference is V8's
malformed-JSON error wording, shown side by side rather than hand-waved.

## 5. The question (2 min) — the closer

Open the question comment on the tar 7 PR.

> "tar 7 drops Node 16, so `engines.node` has to move. Is the floor 18, which is what tar actually
> needs, or 24, which is what CI runs and what TypeScript 7 needs? That's a product decision —
> who your consumers are. It is not Devin's call, and it didn't guess."

Point out the shape: the trade-off in one sentence, two options with what each costs, and **what
it did meanwhile** so the branch is green either way. It did not stall waiting for you.

Reply `/demo-devin-answer A`.

> "That comment is itself a trigger."

A new session starts, implements the choice on that branch, re-runs the proof, pushes, and answers
in the thread. Wait for it if you have time; it's the most convincing 90 seconds of the demo.

## 6. Close (1 min)

> "Renovate found the work. Devin did the work, showed its evidence, and asked the one question
> that was genuinely yours to answer — on the PR, where your team already is. Nothing here is
> bespoke: it's a scheduled job, an issue, a playbook, and two triggers."

---

## If they ask

**"Would it merge without asking?"** Not here — the playbook forbids merging, and every change is
a reviewable PR. Automerge is available per-tier in Renovate (the tuned profile automerges only
GitHub Actions bumps).

**"What if it gets it wrong?"** It's a PR against your CI with a before/after pack. The failure
mode is a rejected PR, not a bad deploy. And it demotes rather than forces: anything it can't get
green locally gets dispatched to its own agent instead of being pushed into the bundle.

**"Does this scale to N repos?"** The playbook is org-wide and the trigger is per-repo config.
Cost control is on the automation: ACU cap, invocations per hour, concurrency.

**"Why not just turn on automerge?"** That's fine for the boring tier and it's in the tuned
profile. It answers nothing for majors, and majors are where the backlog actually lives.

**"Can it work from Dependabot?"** Same shape — the dashboard is the only Renovate-specific part.
A Dependabot variant reads the open PR list instead.

## Reset, manually

1. Close every open `devin/*` PR (bundle + children) and delete nothing else.
2. Leave the 24 `renovate/*` PRs open — they are the demo input.
3. Delete the Devin comment from issue #24 so it reads as untouched.
4. Leave both automations enabled.

Do not reset mid-call: a second run correctly reports "already burned down, nothing to do", which
is the right behaviour but a dull demo.
