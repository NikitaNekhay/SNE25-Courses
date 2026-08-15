#!/usr/bin/env bash
# create_mr_from_llm.sh — Creates a branch with LLM README suggestions and opens a GitLab MR.
# Requires: GITLAB_TOKEN, CI_PROJECT_ID, CI_SERVER_URL (all available in GitLab CI).
# Artifact: llm-readme-suggestions.md (from llm-readme-improve job).
set -euo pipefail

SUGGESTIONS_FILE="llm-readme-suggestions.md"
BRANCH_NAME="llm-readme-improvement-${CI_COMMIT_SHORT_SHA:-$(date +%s)}"
MR_TITLE="[LLM] Automated README improvement suggestions"

# Validate required vars
: "${GITLAB_TOKEN:?GITLAB_TOKEN is not set — add it as a masked CI/CD variable}"
: "${CI_PROJECT_ID:?CI_PROJECT_ID must be set (auto-set in GitLab CI)}"
: "${CI_SERVER_URL:?CI_SERVER_URL must be set (auto-set in GitLab CI)}"

GITLAB_API="${CI_SERVER_URL}/api/v4"

# Check suggestions file exists
if [ ! -f "$SUGGESTIONS_FILE" ]; then
  echo "ERROR: $SUGGESTIONS_FILE not found — llm-readme-improve must run first"
  exit 1
fi

# Configure git
git config --global user.email "llm-bot@ci.pipeline"
git config --global user.name  "LLM CI Bot"
git config --global safe.directory '*'

# Clone the repo fresh (current directory is already cloned by GitLab)
git checkout -b "$BRANCH_NAME"

# Append LLM suggestions to README
echo "" >> readme.md
echo "---" >> readme.md
echo "" >> readme.md
echo "<!-- LLM-generated improvement suggestions (pipeline $CI_PIPELINE_ID) -->" >> readme.md
cat "$SUGGESTIONS_FILE" >> readme.md

git add readme.md
git commit -m "docs: add LLM-generated README improvement suggestions [skip ci]"

# Push branch via HTTPS with token auth
REMOTE_URL="${CI_SERVER_URL}/${CI_PROJECT_PATH}.git"
AUTHED_URL="${CI_SERVER_URL/http:\/\//http://gitlab-ci-token:${GITLAB_TOKEN}@}"
AUTHED_URL="${AUTHED_URL/https:\/\//https://gitlab-ci-token:${GITLAB_TOKEN}@}"

git remote set-url origin "${AUTHED_URL}/${CI_PROJECT_PATH}.git" 2>/dev/null || true
git push origin "$BRANCH_NAME" --force

echo "Branch pushed: $BRANCH_NAME"

# Create MR via GitLab API
MR_BODY=$(cat <<EOF
## Automated README Improvement (LLM-generated)

This MR was automatically created by the CI/CD pipeline after the \`llm-readme-improve\` stage.

**Source:** LLM analysis of \`readme.md\` using model \`openai/gpt-4o-mini\` via OpenRouter.

**Pipeline:** ${CI_PIPELINE_URL:-N/A}
**Commit:** ${CI_COMMIT_SHA:-N/A}

### Suggestions included:
$(head -30 "$SUGGESTIONS_FILE")

---
> ⚠️ Review all LLM suggestions critically before merging. LLM output may contain inaccuracies.
EOF
)

RESPONSE=$(curl -s -w "\n%{http_code}" \
  --request POST "${GITLAB_API}/projects/${CI_PROJECT_ID}/merge_requests" \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --header "Content-Type: application/json" \
  --data "{
    \"source_branch\": \"${BRANCH_NAME}\",
    \"target_branch\": \"main\",
    \"title\": \"${MR_TITLE}\",
    \"description\": $(echo "$MR_BODY" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'),
    \"remove_source_branch\": true,
    \"labels\": \"llm-generated,documentation\"
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "201" ]; then
  MR_URL=$(echo "$BODY" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("web_url",""))' 2>/dev/null || echo "N/A")
  echo "✓ MR created successfully: $MR_URL"
else
  echo "ERROR: MR creation failed (HTTP $HTTP_CODE)"
  echo "$BODY"
  exit 1
fi
