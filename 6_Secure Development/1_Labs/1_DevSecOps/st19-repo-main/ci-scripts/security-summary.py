#!/usr/bin/env python3
"""Generate security summary report with metrics from all scan artifacts."""
import json, os, sys
from datetime import datetime

report = {
    "pipeline_id": os.environ.get("CI_PIPELINE_ID", "unknown"),
    "commit_sha": os.environ.get("CI_COMMIT_SHORT_SHA", "unknown"),
    "branch": os.environ.get("CI_COMMIT_REF_NAME", "unknown"),
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "scans": {},
    "metrics": {}
}

print("=" * 60)
print("  SECURITY PIPELINE SUMMARY REPORT")
print("=" * 60)
print(f"  Pipeline: #{report['pipeline_id']}")
print(f"  Commit:   {report['commit_sha']}")
print(f"  Branch:   {report['branch']}")
print(f"  Date:     {report['timestamp']}")
print("=" * 60)

# --- Gitleaks ---
gitleaks_file = "gitleaks-report.json"
if os.path.exists(gitleaks_file):
    with open(gitleaks_file) as f:
        try:
            data = json.load(f)
            leaks = len(data) if isinstance(data, list) else 0
        except:
            leaks = 0
    report["scans"]["secrets"] = {"tool": "Gitleaks", "leaks_found": leaks}
    status = "PASS" if leaks == 0 else "FAIL"
    print(f"\n  [Secrets Scan - Gitleaks]     {status}  (leaks: {leaks})")
else:
    print("\n  [Secrets Scan - Gitleaks]     SKIPPED (no report)")

# --- Semgrep SAST ---
semgrep_file = "semgrep-report.json"
if os.path.exists(semgrep_file):
    with open(semgrep_file) as f:
        data = json.load(f)
    results = data.get("results", [])
    by_sev = {}
    for r in results:
        sev = r.get("extra", {}).get("severity", "UNKNOWN")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    report["scans"]["sast"] = {"tool": "Semgrep", "total": len(results), "by_severity": by_sev}
    errors = by_sev.get("ERROR", 0)
    status = "PASS" if errors == 0 else "FAIL"
    print(f"  [SAST - Semgrep]              {status}  (total: {len(results)}, errors: {errors})")
else:
    print("  [SAST - Semgrep]              SKIPPED (no report)")

# --- Trivy SCA ---
sca_file = "trivy-sca-report.json"
if os.path.exists(sca_file):
    with open(sca_file) as f:
        data = json.load(f)
    vulns = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0
    for result in data.get("Results", []):
        for v in result.get("Vulnerabilities", []):
            sev = v.get("Severity", "UNKNOWN")
            vulns[sev] = vulns.get(sev, 0) + 1
            total += 1
    report["scans"]["sca"] = {"tool": "Trivy", "total": total, "by_severity": vulns}
    blocking = vulns["CRITICAL"] + vulns["HIGH"]
    status = "PASS" if blocking == 0 else "FAIL"
    print(f"  [SCA - Trivy]                 {status}  (C:{vulns['CRITICAL']} H:{vulns['HIGH']} M:{vulns['MEDIUM']} L:{vulns['LOW']})")
else:
    print("  [SCA - Trivy]                 SKIPPED (no report)")

# --- Trivy Image ---
image_file = "trivy-image-report.json"
if os.path.exists(image_file):
    with open(image_file) as f:
        data = json.load(f)
    vulns = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total = 0
    for result in data.get("Results", []):
        for v in result.get("Vulnerabilities", []):
            sev = v.get("Severity", "UNKNOWN")
            vulns[sev] = vulns.get(sev, 0) + 1
            total += 1
    report["scans"]["image"] = {"tool": "Trivy", "total": total, "by_severity": vulns}
    status = "PASS" if vulns["CRITICAL"] == 0 else "FAIL"
    print(f"  [Image Scan - Trivy]          {status}  (C:{vulns['CRITICAL']} H:{vulns['HIGH']} M:{vulns['MEDIUM']} L:{vulns['LOW']})")
else:
    print("  [Image Scan - Trivy]          SKIPPED (no report)")

# --- Metrics ---
print("\n" + "=" * 60)
print("  SECURITY METRICS")
print("=" * 60)

total_scans = len(report["scans"])
passed_scans = sum(1 for s in report["scans"].values()
                   if s.get("leaks_found", 0) == 0 and
                   s.get("by_severity", {}).get("CRITICAL", 0) == 0)

# Metric 1: Security scan pass rate
pass_rate = (passed_scans / total_scans * 100) if total_scans > 0 else 0
print(f"\n  Metric 1 - Security Scan Pass Rate:    {pass_rate:.0f}% ({passed_scans}/{total_scans} scans passed)")

# Metric 2: Total vulnerability count by severity
all_crit = sum(s.get("by_severity", {}).get("CRITICAL", 0) for s in report["scans"].values())
all_high = sum(s.get("by_severity", {}).get("HIGH", 0) for s in report["scans"].values())
all_med = sum(s.get("by_severity", {}).get("MEDIUM", 0) for s in report["scans"].values())
all_low = sum(s.get("by_severity", {}).get("LOW", 0) for s in report["scans"].values())
print(f"  Metric 2 - Vulnerability Severity:     CRITICAL={all_crit} HIGH={all_high} MEDIUM={all_med} LOW={all_low}")

# Metric 3: Security gate enforcement (did any gate block?)
total_findings = sum(s.get("total", 0) + s.get("leaks_found", 0) for s in report["scans"].values())
print(f"  Metric 3 - Total Security Findings:    {total_findings}")

print("\n" + "=" * 60)

# Write JSON report
report["metrics"] = {
    "scan_pass_rate_pct": pass_rate,
    "total_critical": all_crit,
    "total_high": all_high,
    "total_medium": all_med,
    "total_low": all_low,
    "total_findings": total_findings
}

with open("security-summary.json", "w") as f:
    json.dump(report, f, indent=2)

print("  Report saved to security-summary.json")
print("=" * 60)
