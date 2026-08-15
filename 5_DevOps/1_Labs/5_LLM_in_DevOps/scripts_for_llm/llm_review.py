#!/usr/bin/env python3
"""
LLM Code Review — sends PWA source code to OpenRouter API and writes a markdown report.
Requires: OPENROUTER_API_KEY env var.
"""

import os
import sys
import glob
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-8b-instruct"
MAX_CHARS = 6000
OUTPUT_FILE = "llm-review-report.md"

SOURCE_FILES = [
    "index.html",
    "script.js",
    "style.css",
    "sw.js",
    "manifest.json",
]


def read_sources(files, max_chars):
    parts = []
    total = 0
    for fname in files:
        if not os.path.exists(fname):
            continue
        content = open(fname, encoding="utf-8", errors="replace").read()
        if total + len(content) > max_chars:
            content = content[: max_chars - total] + "\n... [truncated]"
        parts.append(f"### {fname}\n```\n{content}\n```\n")
        total += len(content)
        if total >= max_chars:
            break
    # fallback: scan for any code files if hardcoded list found nothing
    if not parts:
        for ext in ("*.html", "*.js", "*.css", "*.py"):
            for f in glob.glob(f"**/{ext}", recursive=True):
                if ".git" in f or "node_modules" in f:
                    continue
                content = open(f, encoding="utf-8", errors="replace").read()
                if total + len(content) > max_chars:
                    content = content[: max_chars - total] + "\n... [truncated]"
                parts.append(f"### {f}\n```\n{content}\n```\n")
                total += len(content)
                if total >= max_chars:
                    break
    return "\n".join(parts)


def call_llm(api_key, prompt):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gitlab.com",
        "X-Title": "CI/CD LLM Review",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.3,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)

    if resp.status_code != 200:
        print(f"DEBUG: HTTP {resp.status_code}", file=sys.stderr)
        print(f"DEBUG: Response: {resp.text[:500]}", file=sys.stderr)

    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    print(f"API key loaded: {api_key[:4]}...{api_key[-4:]}")
    print(f"Model: {MODEL}")

    sources = read_sources(SOURCE_FILES, MAX_CHARS)
    if not sources:
        print("ERROR: No source files found in current directory", file=sys.stderr)
        print(f"DEBUG: CWD = {os.getcwd()}", file=sys.stderr)
        print(f"DEBUG: Files here = {os.listdir('.')}", file=sys.stderr)
        sys.exit(1)

    prompt = f"""You are a senior software engineer performing an automated code review inside a CI/CD pipeline.

Below is the full source code of a Progressive Web App (PWA) built with plain HTML, CSS, and JavaScript.

{sources}

Please provide a structured review with the following sections:

## 1. Application Description
Describe what this application does in 2-3 sentences.

## 2. Code Quality Observations
List up to 5 concrete observations about code quality, structure, or best practices (positive or negative).

## 3. Potential Bugs or Issues
List up to 5 potential bugs, edge cases, or reliability issues you spot in the code.

## 4. Security Concerns
List any security concerns visible in the client-side code (XSS risks, unsafe API calls, etc.).

## 5. Summary
One paragraph summary of overall quality and the most important improvement to make.

Be concise and specific. Reference file names and line patterns where possible."""

    print(f"Sending {len(sources)} chars of source to {MODEL} via OpenRouter...")
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

    report = f"""# LLM Code Review Report

**Model:** {MODEL}
**Pipeline:** {ci_pipeline_url}
**Commit:** {ci_commit_sha}

---

{review}
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
