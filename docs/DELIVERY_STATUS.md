# Delivery and continuation checkpoint

## Completed
- Reproducible seed 20261017. 600 institutions/opportunities, 4,399 activities, 1,971 historical stage entries, 57 contracts. Twelve months, 15 states/UTs, six regions, eight representatives.
- Relational SQLite database with primary/foreign keys and checks, source CSVs, hash manifest, Pandas reporting mart and 14 annotated SQL queries.
- Seven functional Streamlit pages with shared filters, lead search, CSV downloads, score explanations, historical funnel and interactive forecast sensitivity.
- KPI and scoring definitions, source investigation, data dictionary, README, MIT license and CI workflow.
- Seven-sheet Excel workbook with formulas, filterable tables, conditional formats, charts and editable forecast multipliers.
- Two-page partnership proposal and two-page sales performance review in DOCX and PDF.
- Nine-slide leadership presentation in editable PPTX and PDF, with four native charts.
- Two resume bullets, 60–90-second project explanation and ten interview Q&As in INTERVIEW_GUIDE.md.
- New public GitHub repository. No pre-existing repository was modified.

## Verified findings from the simulation
| Measure | Result |
|---|---:|
| Open opportunities | 370 |
| Active pipeline INR | 109,230,000 |
| Signed value INR | 16,886,000 |
| Recognized revenue INR | 5,736,156.17 |
| Closed-deal win rate | 57 / 230 = 24.78% |
| Stalled open opportunities | 270 |
| Overdue next actions | 222 |
| Proposal-to-negotiation conversion | 75 / 146 = 51.37% |
| Past-due open expected close dates | 224 |
| Past-due open value INR | 70,993,000 |
| Q4 base forecast INR | 4,911,800 |
| Q4 eligible open opportunities | 108 |

These results describe generated data and do not establish real commercial benefits.

## Quality assurance
28 pytest tests passed after adding workbook verification. Coverage includes deterministic generation, PK/FK integrity, missing required fields, date ordering, won/lost contract consistency, stage history, independent SQL/Python revenue reconciliation, conversion fixtures, score bounds, no outcome-derived score inputs, forecast cutoffs and caps, overdue task logic, all 14 SQL statements, seven dashboard pages, filters, empty results, search and sensitivity.

Workbook: Artifact Tool recalculation, zero formula-error matches, key-total reconciliation, 1.2× base multiplier mutation (INR 5,894,160), restoration, exported-cache checks for all 370 lead scores and contract accrual totals. Seven sheet views rendered and inspected. Excel desktop was not opened.

Documents: every rendered page inspected. Presentation: nine slides inspected, package/layout/font checks passed; native charts retain editable data. PowerPoint desktop was not opened. Python compilation and local HTTP health are separate from public hosting; no unverified live URL is supplied.

## Public deployment verified
The user deployed the app at https://university-partnership-sales-analytics.streamlit.app/ . On 18 October 2026, all seven pages loaded in the connected browser, headline totals matched the dataset, North territory filtering changed the view, lead search handled matches and empty results, and forecast sensitivity recalculated correctly. Actual live screenshots are committed under screenshots/. See LIVE_VERIFICATION.md for evidence and remaining checks.

## Remaining validation limits
Browser download verification timed out; a completed CSV download was not observed. Narrow-screen layout has not been visually verified. Native Office validation used authoring-engine recalculation and renders, not Microsoft Excel or PowerPoint. No claim of real commercial results or calibrated predictive accuracy is made.

## Local demonstration
```bash
git clone https://github.com/harshvtomar/university-partnership-sales-analytics.git
cd university-partnership-sales-analytics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

The app uses the committed database and needs no notebook state or external credentials. See ARTIFACT_REFRESH.md for data and artifact rebuilds. Reports and their editable sources live in reports/ and scripts/.
