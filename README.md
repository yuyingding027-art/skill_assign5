# skill_assign5
# edu-email-auditor

A reusable AI skill that audits CSV files for valid educational email addresses.

## What it does

Given a CSV file containing email addresses, this skill:
- Auto-detects which column contains emails
- Validates email format (RFC-compatible regex)
- Identifies educational emails via domain suffix matching (`.edu`, `.ac.uk`, `.edu.hk`, etc.)
- Supports a custom domain whitelist (e.g. `hku.hk`, `polyu.edu.hk`)
- Outputs a terminal summary report
- Produces an annotated CSV with three added columns: `email_valid_format`, `email_is_edu`, `email_audit_note`

## Why I chose it

Email validation is a task where **code is genuinely load-bearing**. A language model cannot reliably:
- Process hundreds of CSV rows without errors or hallucinations
- Apply consistent regex validation across all rows
- Produce reproducible, structured output with statistics

The script handles all deterministic work (parsing, matching, counting, writing), while the AI orchestrates the workflow and explains results to the user.

## Skill structure

```
.agents/skills/edu-email-auditor/
├── SKILL.md                        ← Activation description + instructions
├── scripts/
│   └── audit.py                    ← Core audit script (Python, no dependencies)
└── references/
    └── domain-patterns.md          ← Reference table of recognized edu domains
```

## How to use

> The CSV file **must** have the email column named exactly `email`.  
> If your column has a different name (e.g. `Email Address`), rename it first.

### Basic usage
```bash
python3 .agents/skills/edu-email-auditor/scripts/audit.py \
  --input your_file.csv
```

### With custom domain whitelist
```bash
python3 .agents/skills/edu-email-auditor/scripts/audit.py \
  --input your_file.csv \
  --whitelist mycollege.edu,partner.ac \
  --output results_audited.csv
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--input` | ✅ | Path to input CSV file |
| `--whitelist` | Optional | Comma-separated extra edu domains |
| `--output` | Optional | Output CSV path (defaults to `<input>_audited.csv`) |

### Hong Kong universities — built-in domains

The following HK institution domains are recognized out of the box:

| Domain | Institution |
|---|---|
| `*.hku.hk` | University of Hong Kong |
| `*.ust.hk` | HKUST |
| `*.cuhk.edu.hk` | CUHK |
| `*.polyu.edu.hk` | PolyU |
| `*.cityu.edu.hk` | CityU |
| `*.hkbu.edu.hk` | HKBU |
| `*.ln.edu.hk` | Lingnan |
| `*.eduhk.hk` | EdUHK |
| `*.edu.hk` | All other HK edu institutions |

## What the script does

`audit.py` is a pure Python script with no external dependencies.

1. **Reads** the CSV using the standard `csv` module
2. **Auto-detects** the email column by checking common names (`email`, `mail`, `e-mail`, etc.)
3. **Validates format** using a practical email regex
4. **Checks domain** against 15+ standard educational suffixes and any custom whitelist
5. **Counts and categorizes** all rows (valid edu / invalid format / non-edu)
6. **Writes** annotated CSV with three new columns
7. **Prints** a formatted summary report to stdout

## Sample output

```
====================================
   EDU EMAIL AUDIT REPORT
====================================
  Input file   : sample_emails.csv
  Email column : email
  Whitelist    : hku.hk
------------------------------------
  Total rows        :     20
  ✅ Valid edu emails :     14  (70.0%)
  ❌ Invalid format   :      2  (10.0%)
  ⚠️  Non-edu domain  :      4  (20.0%)
------------------------------------
  Top educational domains:
    hku.hk                          3
    hkust.edu.hk                    2
    connect.hku.hk                  1
------------------------------------
  Annotated CSV saved to:
  sample_emails_audited.csv
====================================
```

## What worked well

- Zero external dependencies — runs anywhere with Python 3.10+
- Auto-detection of email column makes it plug-and-play for most CSV files
- Whitelist mechanism handles edge cases like `hku.hk` (not `.edu.hk`)
- Subdomain matching works automatically (`connect.hku.hk` matches `hku.hk`)
- Clean, readable output that the AI can easily summarize for the user

## Limitations

- Only validates format and domain — does **not** verify if the email account actually exists
- Does not support Excel (`.xlsx`) files — export to CSV first
- Very large files (100k+ rows) may take a few seconds
- Domain list covers major regions but may miss obscure national `.ac.*` variants

## Demo video

[Video link — to be added]
