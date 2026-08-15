#!/usr/bin/env python3
"""
LLM Security Review — sends CI/CD pipeline config + source code to OpenRouter
with a security/reliability/trust-focused prompt. Writes llm-security-report.md.
Requires: OPENROUTER_API_KEY env var.
"""

import os
import sys
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-8b-instruct"
MAX_CHARS_SRC = 4000
MAX_CHARS_CI = 3000
OUTPUT_FILE = "llm-security-report.md"

SOURCE_FILES = ["index.html", "script.js", "sw.js"]
CI_FILES = [".gitlab-ci.yml"]


def read_file(path, max_chars):
    if not os.path.exists(path):
        return ""
    content = open(path, encoding="utf-8", errors="replace").read()
    if len(content) > max_chars:
        content = content[:max_chars] + "\n... [truncated]"
    return content


def call_llm(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gitlab.com",
        "X-Title": "CI/CD Security Review",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000,
        "temperature": 0.2,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)

    if resp.status_code != 200:
        print(f"DEBUG: HTTP {resp.status_code}", file=sys.stderr)
        print(f"DEBUG: Response: {resp.text[:500]}", file=sys.stderr)

    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    print(f"API key loaded: {api_key[:4]}...{api_key[-4:]}")
    print(f"Model: {MODEL}")

    ci_section = ""
    for f in CI_FILES:
        content = read_file(f, MAX_CHARS_CI)
        if content:
            ci_section += f"### {f}\n```yaml\n{content}\n```\n\n"

    src_remaining = MAX_CHARS_SRC
    src_section = ""
    for f in SOURCE_FILES:
        content = read_file(f, src_remaining)
        if content:
            src_section += f"### {f}\n```\n{content}\n```\n\n"
            src_remaining -= len(content)
        if src_remaining <= 0:
            break

    if not ci_section and not src_section:
        print("ERROR: No files found to review", file=sys.stderr)
        print(f"DEBUG: CWD = {os.getcwd()}", file=sys.stderr)
        print(f"DEBUG: Files here = {os.listdir('.')}", file=sys.stderr)
        sys.exit(1)

    prompt = f"""You are a DevSecOps expert performing a security, reliability, and trust audit of a CI/CD pipeline and its application source code.

Analyze from THREE perspectives: SECURITY, RELIABILITY, and TRUST.

## CI/CD Pipeline Configuration
{ci_section if ci_section else "(not found)"}

## Application Source Code (subset)
{src_section if src_section else "(not found)"}

---

For each perspective provide a numbered list of findings. Each finding must include:
- A clear description of the risk
- The affected file/section
- Severity: LOW / MEDIUM / HIGH / CRITICAL
- Justification from the code

### SECURITY
Identify vulnerabilities, secrets exposure, injection risks, insecure API calls, hardcoded credentials, supply chain risks, and data leakage vectors.

### RELIABILITY
Identify single points of failure, missing retry logic, no health checks, pipeline steps without error handling, timeout risks, and missing rollback strategies.

### TRUST
Assess trustworthiness of LLM-generated output in this pipeline. Can LLM output be blindly trusted? What are risks of acting on LLM advice in automated workflows?

### SUMMARY TABLE
| Finding # | Perspective | Severity | One-line description |

Be specific, reference exact file names. Flag speculative findings with "(speculative)"."""

    print(f"Sending security review prompt to {MODEL} via OpenRouter...")
    try:
        review = call_llm(api_key, prompt)
    except requests.HTTPError as e:
        print(f"HTTP error from OpenRouter: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error calling OpenRouter: {e}", file=sys.stderr)
        sys.exit(1)

    ci_pipeline_url = os.environ.get("CI_PIPELINE_URL", "N/A")
    ci_commit_sha = os.environ.get("CI_COMMIT_SHA", "N/A")

    report = f"""# LLM Security Review Report

**Model:** {MODEL}
**Focus:** Security / Reliability / Trust
**Pipeline:** {ci_pipeline_url}
**Commit:** {ci_commit_sha}

---

{review}

---

## Critical Assessment (fill in after reviewing)

| Finding # | Valid / Questionable / Incorrect | Reason |
|-----------|----------------------------------|--------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Security report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
