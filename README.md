# Automated Report Distribution

An automated weekly sales report pipeline: synthetic transaction data -> aggregation
-> matplotlib charts -> HTML + PDF report -> (documented, stubbed) email distribution.
This mirrors a recurring "dashboard emailed to a distribution list" workflow, built
end-to-end and safe to run — no real email is ever sent by this repo.

**Design doc first:** see [`docs/design.md`](docs/design.md) for the problem
statement, ER diagram, data dictionary, and schema design decisions — read that
before the source code.

## What this demonstrates

- Star-schema data modeling (fact_sales + dim_store + dim_product), documented in `docs/design.md`
- Aggregation and reporting logic in pandas
- Chart generation with matplotlib and rendering into both HTML and PDF outputs
- A safe, clearly-documented pattern for an email-distribution step (SMTP), with
  the actual send stubbed out and logged instead of executed
- CI/CD: a GitHub Actions workflow that regenerates the report on a weekly schedule

## Repo structure

```
automated-report-distribution/
├── docs/
│   └── design.md              # problem statement, ER/flow diagrams, data dictionary, schema
├── src/
│   ├── generate_data.py       # synthetic sales data generator (seeded, reproducible)
│   ├── build_report.py        # aggregates data, builds charts, renders HTML + PDF
│   ├── email_distribution.py  # documented SMTP stub -- logs, never sends
│   └── config.py              # SMTP + distribution-list configuration (no real values)
├── data/
│   ├── fact_sales.csv
│   ├── dim_store.csv
│   └── dim_product.csv
├── reports/
│   ├── sample_report_YYYY-MM-DD.html   # committed sample output
│   └── sample_report_YYYY-MM-DD.pdf    # committed sample output
├── tests/
│   └── test_build_report.py
├── .github/workflows/generate_report.yml   # scheduled report regeneration
├── requirements.txt
└── .gitignore
```

## How to run

```bash
pip install -r requirements.txt

# regenerate the synthetic dataset (optional -- data/ is already committed)
python src/generate_data.py

# build the HTML + PDF report into reports/
python src/build_report.py

# see what the (stubbed) distribution step would do -- does NOT send email
python src/email_distribution.py

# run the test suite
pytest tests/ -v
```

## Sample output

A pre-built sample report is committed under `reports/` so you can see the
output without running anything -- open the `.html` file in a browser or the
`.pdf` directly.

## On the email-distribution step

`src/email_distribution.py` is fully documented with the real `smtplib` wiring
that production use would require (SMTP host/port/TLS, credentials read from
environment variables / GitHub Actions secrets, multipart message with the PDF
attached). The actual `send_report()` function is a stub: it logs exactly what
it would send and to whom, then returns without opening a network connection.
This is deliberate -- a cloned copy of this repo should never be able to
accidentally email real recipients.

## Scheduling

`.github/workflows/generate_report.yml` runs the full pipeline (tests -> generate
data -> build report -> run the distribution stub) every Monday at 06:00 UTC via
GitHub Actions `schedule`, and can also be triggered manually via
`workflow_dispatch`. The generated report is uploaded as a workflow artifact.

## Caveats

- All data is synthetic (`src/generate_data.py`, seeded for reproducibility).
- No real email is sent; see "On the email-distribution step" above.
