#!/usr/bin/env python3
"""
LLM README Improvement — reads readme.md and asks LLM for 3 concrete improvements.
Writes llm-readme-suggestions.md.
Requires: OPENROUTER_API_KEY env var.
"""

import os
import sys
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL   = "openai/gpt-4o-mini"
OUTPUT_FILE = "llm-readme-suggestions.md"
README_FILES = ["readme.md", "README.md", "README.rst"]


def call_llm(api_key: str, prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gitlab.com",
        "X-Title": "CI/CD README Improve",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.4,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    readme_content = None
    for fname in README_FILES:
        if os.path.exists(fname):
            readme_content = open(fname, encoding="utf-8", errors="replace").read()[:5000]
            print(f"Found README: {fname}")
            break

    if not readme_content:
        readme_content = "(README not found — generate suggestions for a typical PWA project)"

    prompt = f"""You are a technical writer and senior developer reviewing a project README.

## Current README Content
```markdown
{readme_content}
```

## Task
Provide exactly 3 concrete improvement suggestions for this README. Each suggestion must include:

1. **What to improve** — the specific section or missing content
2. **Why it matters** — one sentence explanation
3. **Suggested content** — write the actual improved/added markdown text (ready to copy-paste)

Focus on: missing sections (setup instructions, deployment, contribution guide), clarity issues, outdated content, missing badges or visuals, accessibility of technical details to newcomers.

Format your response with clear headings for each suggestion."""

    print(f"Requesting README improvements from {MODEL}…")
    try:
        suggestions = call_llm(api_key, prompt)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    report = f"""# LLM README Improvement Suggestions

**Model:** {MODEL}
**Pipeline:** $CI_PIPELINE_URL
**Commit:** $CI_COMMIT_SHA

---

{suggestions}
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"README suggestions written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
