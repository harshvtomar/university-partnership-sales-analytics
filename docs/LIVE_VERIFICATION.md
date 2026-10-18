# Live deployment verification — 18 October 2026

Live app: https://university-partnership-sales-analytics.streamlit.app/

Deployed by the project owner. Verified through the actual Streamlit UI, not a static replica. Source checkpoint tested: b1994a36aee2feea27667cde1c2e3b38737cb7c7. This verification changes only documentation and screenshots.

| Check | Observed result |
|---|---|
| Navigation | All seven pages loaded without an application exception |
| Executive metrics | 600 institutions; 370 active opportunities; INR 10.92 crore pipeline; 57 wins; INR 57.36 lakh recognized revenue; 24.8% displayed win rate |
| Pipeline | 270 stalled, 222 overdue, 418 ever qualified; historical funnel and tables rendered |
| Lead search | Ahmedabad returned matching fictional institutions, led by University 426 at 80.16; unmatched text produced an empty table without an exception |
| Territory filter | North selected: 160 opportunities, 92 active, INR 2.92 crore pipeline, 18 wins; restored to all territories afterward |
| Territory and representatives | Charts and comparison tables loaded; simulation and sample-size caveats visible |
| Forecast sensitivity | Default base INR 49.12 lakh; 1.05 sensitivity produced INR 51.57 lakh; restored to 1.00 |
| Recommendations | Data-backed overdue, stalled, bottleneck, territory, account and stale-date recommendations loaded |
| Desktop visual review | Overview and lead-intelligence screenshots inspected; readable cards, charts, search and tables |

## Evidence
- ../screenshots/Executive_Overview.png — actual live overview.
- ../screenshots/Lead_Intelligence.png — live Ahmedabad search results.

## Scope limits
The connected browser was signed in to Streamlit; an independent signed-out access test was not performed. CSV download control was present and clicked, but the automation download event timed out, so completed-file delivery is unverified. Mobile/narrow-screen visual QA remains pending. Previous 28 automated tests and successful CI are recorded separately; they were not rerun for this documentation-only update.
