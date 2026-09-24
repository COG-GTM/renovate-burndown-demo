#!/usr/bin/env bash
# Reset the Renovate burn-down demo to its starting state.
#
#   ./docs/reset-demo.sh          # show what would change
#   ./docs/reset-demo.sh --apply  # do it
#
# Closes the Devin PRs from the previous run and clears Devin's report comment from the
# dashboard issue. The renovate/* PRs are the demo input and are left alone, as is anything
# labelled demo-infra (the workflow/docs PRs that make the demo work).
set -euo pipefail

REPO=COG-GTM/renovate-burndown-demo
DASHBOARD=24
APPLY=${1:-}

run() {
  if [ "$APPLY" = "--apply" ]; then "$@"; else echo "  would run: $*"; fi
}

echo "== Devin PRs to close =="
mapfile -t prs < <(gh pr list --repo "$REPO" --state open --limit 100 \
  --json number,headRefName,title,labels \
  --jq '.[]
        | select(.headRefName | startswith("devin/"))
        | select([.labels[].name] | index("demo-infra") | not)
        | "\(.number)\t\(.title)"')

if [ ${#prs[@]} -eq 0 ]; then
  echo "  none"
else
  for line in "${prs[@]}"; do
    num=${line%%$'\t'*}
    echo "  #$num ${line#*$'\t'}"
    # branches are kept so a close is reversible: gh pr reopen <n>
    run gh pr close "$num" --repo "$REPO" \
      --comment "Closing as part of a demo reset — superseded by the next burn-down run."
  done
fi

echo "== Devin comments on dashboard issue #$DASHBOARD =="
mapfile -t comments < <(gh api "repos/$REPO/issues/$DASHBOARD/comments" \
  --jq '.[] | select(.user.login | test("devin")) | .id')

if [ ${#comments[@]} -eq 0 ]; then
  echo "  none"
else
  for id in "${comments[@]}"; do
    echo "  comment $id"
    run gh api -X DELETE "repos/$REPO/issues/comments/$id"
  done
fi

echo "== Starting state =="
open_renovate=$(gh pr list --repo "$REPO" --state open --limit 100 --json headRefName \
  --jq '[.[] | select(.headRefName | startswith("renovate/"))] | length')
echo "  open renovate/* PRs: $open_renovate (expect 23)"
echo "  dashboard: https://github.com/$REPO/issues/$DASHBOARD"

cat <<'EOF'

To start a run:
  gh workflow run Renovate --repo COG-GTM/renovate-burndown-demo
or, if Renovate has nothing new to write, edit the dashboard issue body to fire the trigger:
  gh api repos/COG-GTM/renovate-burndown-demo/issues/24 --jq .body > /tmp/dash.md
  printf '\n<!-- demo %s -->\n' "$(date -u +%FT%TZ)" >> /tmp/dash.md
  gh api -X PATCH repos/COG-GTM/renovate-burndown-demo/issues/24 -F body=@/tmp/dash.md
EOF
