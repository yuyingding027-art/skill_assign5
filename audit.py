#!/usr/bin/env python3
"""
edu-email-auditor — audit.py
Audits a CSV file for valid educational email addresses.

The email column must be named exactly "email" in the CSV.

Usage:
    python3 audit.py --input <file.csv> [--whitelist <domains>] [--output <out.csv>]

Arguments:
    --input      Path to the input CSV file (required)
    --whitelist  Comma-separated extra domains to treat as educational
                 e.g. "mycollege.edu.hk,partner.ac"
    --output     Path for the annotated output CSV (default: <input>_audited.csv)
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Fixed email column name
EMAIL_COLUMN = "email"

# Standard educational domain patterns (suffix-based)
EDU_SUFFIXES = [
    # --- Hong Kong universities (explicit, non-.edu.hk domains) ---
    ".hku.hk",           # University of Hong Kong
    ".ust.hk",           # HKUST
    ".cuhk.edu.hk",      # CUHK
    ".polyu.edu.hk",     # PolyU
    ".cityu.edu.hk",     # CityU
    ".hkbu.edu.hk",      # HKBU
    ".ln.edu.hk",        # Lingnan
    ".hkmu.edu.hk",      # HKMU (Open University)
    ".eduhk.hk",         # EdUHK
    # --- General .edu.hk (covers many HK institutions) ---
    ".edu.hk",
    # --- International standard patterns ---
    ".edu",              # US and international .edu
    ".ac.uk",            # UK
    ".ac.jp",            # Japan
    ".ac.kr",            # South Korea
    ".ac.nz",            # New Zealand
    ".ac.za",            # South Africa
    ".ac.in",            # India
    ".ac.cn",            # China
    ".edu.au",           # Australia
    ".edu.cn",           # China alternate
    ".edu.sg",           # Singapore
    ".edu.tw",           # Taiwan
    ".edu.my",           # Malaysia
    ".edu.pk",           # Pakistan
    ".edu.ph",           # Philippines
    ".edu.br",           # Brazil
    ".edu.mx",           # Mexico
    ".edu.ar",           # Argentina
    ".edu.co",           # Colombia
]

# Basic email format regex (RFC-ish, practical)
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def is_valid_format(email: str) -> bool:
    """Check basic email format validity."""
    return bool(EMAIL_REGEX.match(email.strip()))


def extract_domain(email: str) -> str:
    """Return the domain part of an email, lowercased."""
    parts = email.strip().lower().split("@")
    return parts[1] if len(parts) == 2 else ""


def is_edu_domain(domain: str, extra_domains: list[str]) -> tuple[bool, str]:
    """
    Check if domain qualifies as educational.
    Returns (is_edu: bool, reason: str)
    """
    if not domain:
        return False, "no_domain"

    # Check custom whitelist first (exact match or suffix)
    for wd in extra_domains:
        wd = wd.strip().lower()
        if domain == wd or domain.endswith("." + wd):
            return True, f"custom_whitelist:{wd}"

    # Check standard edu suffixes
    for suffix in EDU_SUFFIXES:
        if domain.endswith(suffix) or domain == suffix.lstrip("."):
            return True, f"edu_suffix:{suffix}"

    return False, "non_edu_domain"


def audit_email(email: str, extra_domains: list[str]) -> dict:
    """Return a dict with all audit fields for one email."""
    raw = email.strip()

    if not raw:
        return {
            "email_valid_format": "FALSE",
            "email_is_edu": "FALSE",
            "email_audit_note": "empty_value",
            "domain": "",
        }

    valid_fmt = is_valid_format(raw)
    domain = extract_domain(raw) if valid_fmt else ""
    is_edu, reason = is_edu_domain(domain, extra_domains) if valid_fmt else (False, "invalid_format")

    edu_label = "FALSE"
    if is_edu:
        edu_label = "CUSTOM_WHITELIST" if reason.startswith("custom") else "TRUE"

    return {
        "email_valid_format": "TRUE" if valid_fmt else "FALSE",
        "email_is_edu": edu_label,
        "email_audit_note": reason if not (valid_fmt and is_edu) else "ok",
        "domain": domain,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Audit CSV file for educational email addresses.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--whitelist", default="", help="Comma-separated extra edu domains")
    parser.add_argument("--output", default=None, help="Path for annotated output CSV")
    args = parser.parse_args()

    # Resolve paths
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        base, ext = os.path.splitext(input_path)
        output_path = base + "_audited" + (ext if ext else ".csv")

    extra_domains = [d.strip() for d in args.whitelist.split(",") if d.strip()]

    # Read CSV
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = list(reader)
    except Exception as e:
        print(f"[ERROR] Could not read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("[WARNING] CSV file is empty.")
        sys.exit(0)

    # Validate fixed column name
    if EMAIL_COLUMN not in headers:
        print(f"[ERROR] Required column '{EMAIL_COLUMN}' not found.", file=sys.stderr)
        print(f"        Available columns: {headers}", file=sys.stderr)
        print(f"        Please rename your email column to '{EMAIL_COLUMN}' and retry.", file=sys.stderr)
        sys.exit(1)

    email_col = EMAIL_COLUMN

    # Audit each row
    results = []
    domain_counter = Counter()
    total = len(rows)
    valid_format_count = 0
    edu_count = 0
    invalid_format_count = 0
    non_edu_count = 0

    for row in rows:
        email = row.get(email_col, "")
        audit = audit_email(email, extra_domains)

        if audit["email_valid_format"] == "TRUE":
            valid_format_count += 1
        else:
            invalid_format_count += 1

        if audit["email_is_edu"] in ("TRUE", "CUSTOM_WHITELIST"):
            edu_count += 1
            if audit["domain"]:
                domain_counter[audit["domain"]] += 1
        elif audit["email_valid_format"] == "TRUE":
            non_edu_count += 1

        new_row = dict(row)
        new_row["email_valid_format"] = audit["email_valid_format"]
        new_row["email_is_edu"] = audit["email_is_edu"]
        new_row["email_audit_note"] = audit["email_audit_note"]
        results.append(new_row)

    # Write output CSV
    out_headers = list(headers) + ["email_valid_format", "email_is_edu", "email_audit_note"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out_headers)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"[ERROR] Could not write output: {e}", file=sys.stderr)
        sys.exit(1)

    # Print report
    print()
    print("=" * 36)
    print("   EDU EMAIL AUDIT REPORT")
    print("=" * 36)
    print(f"  Input file   : {input_path}")
    print(f"  Email column : {email_col}")
    if extra_domains:
        print(f"  Whitelist    : {', '.join(extra_domains)}")
    print("-" * 36)
    print(f"  Total rows        : {total:>6}")
    print(f"  ✅ Valid edu emails : {edu_count:>6}  ({edu_count/total*100:.1f}%)")
    print(f"  ❌ Invalid format   : {invalid_format_count:>6}  ({invalid_format_count/total*100:.1f}%)")
    print(f"  ⚠️  Non-edu domain  : {non_edu_count:>6}  ({non_edu_count/total*100:.1f}%)")
    print("-" * 36)

    if domain_counter:
        print("  Top educational domains:")
        for domain, count in domain_counter.most_common(5):
            print(f"    {domain:<28} {count:>4}")

    print("-" * 36)
    print(f"  Annotated CSV saved to:")
    print(f"  {output_path}")
    print("=" * 36)
    print()


if __name__ == "__main__":
    main()
