# Resume and interview guide

## Resume entry
**University Partnership & Sales Pipeline Analytics | Python, SQL, Streamlit, Plotly, Excel**
https://github.com/harshvtomar/university-partnership-sales-analytics

- Built a B2B EdTech sales analytics system covering 600 simulated institutional prospects and 4,399 activities, using Python and SQLite to track stage conversions, territory performance and overdue follow-ups.
- Developed a seven-page interactive dashboard, explainable lead scoring and scenario-based partnership forecasts, with a formula-driven Excel workbook and management recommendations grounded in reconciled KPIs.

## 60–90-second explanation
I built this project around a business development problem: a higher-education sales team needs to know which institutions to approach, where opportunities are getting stuck and what might close next quarter. I created a reproducible simulation with 600 institutions and over 4,000 sales activities across 12 months. I used Python for preparation, SQLite for relational reporting, and Streamlit and Plotly for a seven-page dashboard.

I kept stage-transition history so funnel conversion comes from actual stage entries rather than the current-stage distribution. I also separated signed contract value from recognized revenue and documented every denominator. For outreach, I used an explainable 100-point score rather than claiming a predictive model from synthetic data.

The simulation identified 222 overdue follow-ups and 224 open deals with stale expected close dates. My recommendation was to clean those records before expanding prospecting. The base next-quarter forecast is about INR 49.12 lakh across 108 eligible deals, based on explicit assumptions. I reconciled financial totals across Python, SQL and Excel and tested dashboard pages and edge cases. The results demonstrate an analytical workflow, not real commercial gains.

## Ten interview questions and answers

1. **How does this help a Management Trainee?** It supports prospect prioritisation, account review, follow-up discipline, territory planning and commercially useful reporting.
2. **Why use synthetic data?** I investigated AISHE and OGD but did not acquire a suitable reusable institution extract. Public directories also do not provide a real company's private CRM history. All names and commercial records are explicitly fictional.
3. **What is the schema?** Institutions link to opportunities, which link to activities, stage-history events and optional won contracts. A one-row-per-opportunity mart prevents revenue duplication from joins.
4. **How is win rate defined?** Won divided by Won plus Lost: 57/230 or 24.78%. Open deals are excluded and a zero denominator returns N/A.
5. **Why record stage history?** Current stages describe inventory. Historical entries identify which opportunities advanced, enabling distinct-opportunity conversion denominators.
6. **What is your most useful finding?** Pipeline hygiene: 222 overdue next actions and 224 stale expected close dates. I propose owner reviews before interpreting gross pipeline as near-term bookings.
7. **How does the score work?** Eight bounded factors sum to 100: size, market assumption, engagement, segment, response, potential value, stage and recency. High priority starts at 70. It is a heuristic, not ML.
8. **How did you avoid leakage?** Scores use open-opportunity information through the snapshot; closure reason, actual close date and recognized revenue are not scoring inputs. I did not validate predictions on simulator-generated labels.
9. **How is the forecast calculated?** Open deals expected in Oct–Dec 2026 are weighted by stage probability. Scenario multipliers are 0.7/1.0/1.3, capped at 100%. Past-due expected dates are excluded and disclosed.
10. **What would you change for real deployment?** Use authorised CRM data, timestamped value changes, task lifecycle records, calibrated time-based validation, access controls and scheduled refresh. Pilot proposed interventions before claiming improvement.
