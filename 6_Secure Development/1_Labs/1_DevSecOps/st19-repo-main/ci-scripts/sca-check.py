#!/usr/bin/env python3
"""Parse Trivy JSON report and enforce SCA quality gate.
Policy: fail on CRITICAL or HIGH vulnerabilities.
"""
import json, sys

with open(sys.argv[1]) as f:
    data = json.load(f)

critical = 0
high = 0
medium = 0
low = 0
all_vulns = []

for result in data.get("Results", []):
    target = result.get("Target", "unknown")
    for vuln in result.get("Vulnerabilities", []):
        sev = vuln.get("Severity", "UNKNOWN")
        vid = vuln.get("VulnerabilityID", "?")
        pkg = vuln.get("PkgName", "?")
        installed = vuln.get("InstalledVersion", "?")
        fixed = vuln.get("FixedVersion", "n/a")
        title = vuln.get("Title", "")[:80]
        all_vulns.append((sev, vid, pkg, installed, fixed, title))
        if sev == "CRITICAL":
            critical += 1
        elif sev == "HIGH":
            high += 1
        elif sev == "MEDIUM":
            medium += 1
        else:
            low += 1

for sev, vid, pkg, installed, fixed, title in sorted(all_vulns):
    print(f"  [{sev}] {vid} {pkg}@{installed} (fix: {fixed}) - {title}")

print(f"\nSCA Summary: {critical} CRITICAL, {high} HIGH, {medium} MEDIUM, {low} LOW")
print(f"Total vulnerabilities: {len(all_vulns)}")

if critical > 0 or high > 0:
    print("SCA GATE FAILED: Critical/High vulnerabilities found!")
    sys.exit(1)
else:
    print("SCA gate passed.")
    sys.exit(0)
