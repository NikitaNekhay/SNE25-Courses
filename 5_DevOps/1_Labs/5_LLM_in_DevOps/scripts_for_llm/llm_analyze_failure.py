#!/usr/bin/env python3
"""
LLM Failure Analysis — reads CI job environment/logs and asks LLM to suggest fixes.
Runs as a 'when: on_failure' job. Writes llm-failure-report.md.
Requires: OPENROUTER_API_KEY env var.
"""

import os
import sys
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL   = "openai/gpt-4o-mini"
OUTPUT_FILE = "llm-failure-report.md"


def call_llm(api_key: str, prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gitlab.com",
        "X-Title": "CI/CD Failure Analysis",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,
        "temperature": 0.3,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    # Collect available CI context from environment
    ci_job_name      = os.environ.get("CI_JOB_NAME", "unknown")
    ci_pipeline_id   = os.environ.get("CI_PIPELINE_ID", "unknown")
    ci_commit_sha    = os.environ.get("CI_COMMIT_SHA", "unknown")
    ci_project_url   = os.environ.get("CI_PROJECT_URL", "unknown")
    ci_job_url       = os.environ.get("CI_JOB_URL", "unknown")

    # Try to read a log artifact if any previous stage saved one
    log_content = "(No log artifact found — analyze from context only)"
    for candidate in ["build.log", "test.log", "pipeline.log"]:
        if os.path.exists(candidate):
            log_content = open(candidate, encoding="utf-8", errors="replace").read()[:3000]
            break

    prompt = f"""You are a DevOps troubleshooting expert. A CI/CD pipeline job has FAILED.

## Failed Job Context
- Job name: {ci_job_name}
- Pipeline ID: {ci_pipeline_id}
- Commit SHA: {ci_commit_sha}
- Job URL: {ci_job_url}
- Project URL: {ci_project_url}

## Available Log Output
```
{log_content}
```

## Application Stack
This is a static Progressive Web App (PWA) built with plain HTML, CSS, JavaScript.
Pipeline uses: GitLab CI, Docker (nginx:alpine), Semgrep for SAST, kubectl for Kubernetes deploy.

Please provide:

## 1. Likely Root Cause
What is the most probable cause of failure for a job named "{ci_job_name}" in this stack?

## 2. Suggested Fixes (top 3)
Numbered list of concrete fix steps the developer should try.

## 3. Verification Steps
How to verify the fix worked.

## 4. Prevention
What pipeline change or code practice would prevent this failure in future?

Be specific. If the log is unavailable, reason from the job name and stack description."""

    print(f"Analyzing failure for job '{ci_job_name}' with {MODEL}…")
    try:
        analysis = call_llm(api_key, prompt)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = f"""# LLM Failure Analysis Report

**Failed Job:** {ci_job_name}
**Pipeline:** {ci_pipeline_id}
**Commit:** {ci_commit_sha}
**Model:** {MODEL}

---

{analysis}
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Failure analysis written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
