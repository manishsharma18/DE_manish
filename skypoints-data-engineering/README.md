
# SkyPoints – End-to-End Data Engineering Assessment

A Python + Snowflake SQL + GitHub implementation of the Incubyte Data Engineer assessment.

## Business flow

Source Excel/CSV member feeds and partner redemption JSON -> Python ingestion/standardization/validation -> Snowflake RAW -> STAGING -> latest-member country targets + flattened redemption facts.

## Repository structure

```text
skypoints-data-engineering/
├── data/
│   ├── input/                 # supplied IND.xlsx, USA.xlsx, AUS.xlsx
│   └── redemption/            # sample redemption JSON
├── python/
│   ├── src/skypoints/
│   │   ├── config.py
│   │   ├── ingest.py
│   │   ├── normalize.py
│   │   ├── validate.py
│   │   └── run_pipeline.py
│   └── tests/
├── snowflake/
│   ├── 01_database_and_tables.sql
│   ├── 02_load_raw.sql
│   ├── 03_transform_members.sql
│   ├── 04_redemptions.sql
│   └── 05_data_quality.sql
├── .github/workflows/python-tests.yml
├── requirements.txt
└── .gitignore
```

## Important observations from the supplied assessment files

- The PDF asks for raw, staging and country target DDL; derived `AGE` and `STALE_MEMBER`; latest-record-wins country movement; flattened JSON; and data-quality checks.
- The supplied India workbook has columns `ID, Name, DOB, TierCode, EnrollmentDate, Individual or Corporate, Flight Date`.
- The USA workbook has `ID, Name, TierCode, EnrollmentDate, FlightDate`. It does not contain DOB or the individual/corporate field.
- The Australia workbook has `Unique ID, Member Name, Tier Type, Date of Birth, Date of Enrollment, Date of Flight`. One enrollment date is malformed (`2021-13-13`).
- IDs repeat across the country workbooks (for example ID `1` appears in India, USA and Australia). Therefore this implementation uses `(SOURCE_COUNTRY, MEMBER_ID)` as the safe source identity for these supplied samples. Before production, confirm whether the source system guarantees a globally unique member ID. If it does, use `MEMBER_ID` alone as the business key.
- The PDF sample has a mismatch between its header/layout and examples: the layout includes Post Code, but the sample row does not; the header uses `DOB` while the design table calls it Date of Birth. This project standardizes to `DATE_OF_BIRTH`.
- Do not silently repair malformed or ambiguous source dates. Invalid values are sent to the reject output for review.

## 1. Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Place the supplied workbooks in `data/input/` and run:

```bash
python -m python.src.skypoints.run_pipeline
```

The local demonstration writes:
- `output/member_normalized.csv`
- `output/member_rejects.csv`
- `output/redemptions_flat.csv`

The Python demonstration does not require Snowflake credentials. It prepares validated, standardized files for Snowflake loading.

## 2. Snowflake execution

Run SQL scripts in numeric order in a Snowflake worksheet:
1. `snowflake/01_database_and_tables.sql`
2. `snowflake/02_load_raw.sql` (adjust stage/file paths for your Snowflake stage)
3. `snowflake/03_transform_members.sql`
4. `snowflake/04_redemptions.sql`
5. `snowflake/05_data_quality.sql`

For a real deployment, upload normalized CSV/JSON files to an internal or external Snowflake stage and use `COPY INTO`. The SQL includes a stage-based loading example. Replace the stage name and file names with your environment's values.

## 3. Scale design for billions of daily records

- Land immutable files in cloud object storage; retain file name, file row number, ingestion timestamp and batch ID.
- Use Snowpipe or Snowpipe Streaming for continuous ingestion, or scheduled `COPY INTO` for batch files.
- Use warehouse sizing/multi-cluster warehouses based on measured workload, not a fixed oversized warehouse.
- Process incrementally by batch/date; avoid repeatedly scanning all historical data.
- Use `COPY INTO` with file metadata and load history for safe re-runs.
- Deduplicate with `ROW_NUMBER()` and a deterministic ordering (`SOURCE_UPDATED_AT`, then `INGESTED_AT`, then source sequence).
- Use `MERGE` for idempotent upserts. Country movement must remove a member from the old country target and insert/update the new country target in one controlled transaction or publish targets from a canonical current-member table.
- Keep rejects and DQ metrics; alert on unexpected reject-rate increases.
- Cluster only when query patterns and measured micro-partition pruning justify it. Do not automatically cluster every table.
- Flatten JSON using `LATERAL FLATTEN`; retain the raw VARIANT payload for replay/audit.
- Use least-privilege roles, encryption, secret management and PII masking policies for DOB and member data.

## 4. GitHub workflow

```bash
git init
git add .
git commit -m "chore: initialize SkyPoints data engineering project"
git add python/
git commit -m "feat: add Python ingestion and validation"
git add snowflake/
git commit -m "feat: add Snowflake raw staging and target models"
git add .github README.md
git commit -m "ci: add tests and project documentation"
git branch -M main
git remote add origin https://github.com/<your-user>/skypoints-data-engineering.git
git push -u origin main
```

Make incremental commits as requested by the assessment. Do not commit credentials, private keys or production data.

## 5. Known design decisions / assumptions

1. Country is inferred from the source workbook name for the provided country-separated files. For the assessment's pipe-delimited feed, country comes from the `Country` field.
2. Missing optional fields remain NULL. For example, USA DOB is not fabricated.
3. Invalid date strings are rejected, not coerced into guessed dates.
4. `STALE_MEMBER` is true when the last flight is more than 90 days before the processing date. A missing last-flight date is treated as unknown (`NULL`), not stale.
5. Age is calculated as of the processing date and is NULL when DOB is missing/invalid.
6. A production source should provide a source update timestamp or sequence. If absent, ingestion timestamp is a fallback but cannot reliably establish business recency across delayed files.
7. `MEMBER_ID` is stored as VARCHAR to preserve leading zeros and avoid numeric conversion.

## 6. Tests

```bash
pytest -q
```
