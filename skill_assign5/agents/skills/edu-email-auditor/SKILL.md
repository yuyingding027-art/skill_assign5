---
name: edu-email-auditor
description: Audits a CSV file containing email addresses and identifies which ones are valid educational emails (.edu, .ac.*, .edu.*, or any custom domain whitelist). Outputs a terminal summary report and an annotated CSV with per-row audit results. Use when the user wants to validate, filter, or audit a list of emails for educational institution eligibility.
---

# edu-email-auditor

## When to use this skill
- The user uploads or references a CSV file containing email addresses
- The user wants to know which emails are valid educational emails
- The user wants to filter, clean, or audit a registration/applicant list for edu-email eligibility
- The user wants statistics on how many emails pass or fail edu-email validation

## When NOT to use this skill
- The user is asking about a single email (just answer directly, no script needed)
- The file is not a CSV (e.g., plain text, Excel, JSON — tell the user to convert first)
- The user wants to send emails or do anything beyond auditing/reporting

## Expected Inputs
- A CSV file where the email column is named exactly `email`
- (Optional) A custom domain whitelist, e.g.: `--whitelist mycollege.edu,partner.ac`

> If the user's CSV uses a different column name, ask them to rename it to `email` before running.

## Step-by-step Instructions

1. Ask the user to provide the CSV file path (or accept it from context).
2. Confirm the CSV has a column named `email`. If not, ask the user to rename it.
3. If the user has a custom domain whitelist, collect it as a comma-separated list.
4. Run the audit script:

```bash
python3 .agents/skills/edu-email-auditor/scripts/audit.py \
  --input <path-to-csv> \
  [--whitelist <domain1,domain2,...>] \
  --output <output-path.csv>
```

4. Read the terminal output and summarize results to the user in plain language.
5. Confirm the annotated output CSV has been saved and tell the user where to find it.

## Output Format

### Terminal summary (printed by script):
```
=== EDU EMAIL AUDIT REPORT ===
Total rows:        120
Valid emails:       98
Invalid format:      7
Non-edu domain:     15

Top educational domains:
  hku.hk           42
  hkust.edu.hk     31
  connect.hku.hk   25

Flagged rows saved to: output_audited.csv
```

### Annotated CSV (new file):
Same as input, with two added columns:
- `email_valid_format` — TRUE / FALSE
- `email_is_edu` — TRUE / FALSE / CUSTOM_WHITELIST
- `email_audit_note` — brief reason if flagged

## Limitations
- Only checks format and domain; does not verify if the email account actually exists
- Does not handle Excel (.xlsx) files — user must export to CSV first
- Domain matching is suffix-based; subdomains (e.g., connect.hku.hk) are matched if the parent domain is in the whitelist
- Very large files (100k+ rows) may take a few seconds
