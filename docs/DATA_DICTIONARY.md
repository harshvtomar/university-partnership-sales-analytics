# Data dictionary
Snapshot 2026-09-30. Dates are ISO text in SQLite/CSV. All commercial data is simulated. Nulls occur only where the business event does not apply.

## institutions
| Field | Meaning |
|---|---|
| institution_id | Stable fictional institution key. Foreign key in opportunities. |
| institution_name | Fictional name prefixed Simulated. |
| state | Real Indian state or UT label, geography only. |
| city | Real city label, geography only. |
| territory | Planning region: North, South, West, East, Northeast or Central. |
| institution_type | University, Engineering College, Management Institute or Arts and Science College. |
| ownership | Simulated Public, Private or Trust. |
| students | Positive estimated student count, simulated. |
| segment | Enterprise >=7000, Growth >=2000, otherwise Emerging. |
| market_index | Assumed territory attractiveness 0–1, not market research estimate. |
| is_simulated | Always 1. |
## opportunities
| Field | Meaning |
|---|---|
| opportunity_id | Stable opportunity key; one per institution in this release. |
| institution_id | Stable fictional institution key. Foreign key in opportunities. |
| sales_rep | Fictional owner Rep 01–08. |
| lead_source | Simulated acquisition channel. |
| created | Opportunity creation date (ISO). |
| stage | Current stage from latest history event. |
| value | Estimated contract value INR, integer, tax excluded. |
| expected_close | Planned close date; may be stale for Open deals. |
| actual_close | Won/lost closure date, null for Open. |
| status | Open, Won or Lost. |
| reason | Win/loss reason; null while Open. |
## stage_history
| Field | Meaning |
|---|---|
| event_id | Primary stage-event key. |
| opportunity_id | Stable opportunity key; one per institution in this release. |
| stage | Current stage from latest history event. |
| event_date | Stage-entry date. No repeated entry into a stage. |
## activities
| Field | Meaning |
|---|---|
| activity_id | Primary activity key. |
| opportunity_id | Stable opportunity key; one per institution in this release. |
| activity_date | Completed activity date, no later than closure/snapshot. |
| activity_type | Email, Call, Meeting, Demo or Proposal follow-up. |
| responded | 1 if simulated response occurred, else 0. |
| follow_up_status | Pending only for latest activity on open deal; Completed otherwise. |
| next_action | Due date for pending latest follow-up; null otherwise. |
| sales_rep | Fictional owner Rep 01–08. |
## revenue
| Field | Meaning |
|---|---|
| contract_id | Primary signed contract key. |
| opportunity_id | Stable opportunity key; one per institution in this release. |
| signed_date | Signature date equals won actual close. |
| contract_value | Signed INR value equals won opportunity value. |
| payment_status | Paid, Part-paid, Unpaid. Does not measure cash amounts. |
| term_days | 365 calendar days. |
| recognized | INR accrued through snapshot, inclusive of signature, rounded to 0.01 per contract. |
| recognition_basis | Daily straight-line assumption description. |
## Derived analytics columns
The analytics table is a rebuilt reporting mart, not the authoritative source. Source columns retain definitions above.
| Field | Meaning |
|---|---|
| activity_count | Count of attached activities. |
| last_activity | Latest activity date or creation if none. |
| response_rate | Mean responded flag; zero with no activities. |
| meetings | Count of Meeting activities. |
| inactive_days | Snapshot minus last activity, calendar days. |
| age_days | Snapshot minus creation. |
| cycle_days | Actual close minus creation; null for open. |
| stage_age_days | Snapshot minus latest stage-entry date. |
| stalled | Open and stage_age_days >30. |
| next_action | Due date from latest activity only. |
| overdue | Open and next_action before snapshot. |
| recognized | Accrued contract revenue or zero for non-wins. |
| probability | Assumed probability by current stage, see SCORING.md. |
| score_size | Weighted contribution for size; see SCORING.md. |
| score_market | Weighted contribution for market; see SCORING.md. |
| score_engagement | Weighted contribution for engagement; see SCORING.md. |
| score_segment | Weighted contribution for segment; see SCORING.md. |
| score_response | Weighted contribution for response; see SCORING.md. |
| score_value | Weighted contribution for value; see SCORING.md. |
| score_stage | Weighted contribution for stage; see SCORING.md. |
| score_recency | Weighted contribution for recency; see SCORING.md. |
| score | Sum of eight bounded components rounded to 2 decimals. Closed=0. |
| priority | High >=70, Medium >=45, Low otherwise; Closed for won/lost. |
| explanation | Component contribution string; see SCORING.md. |
## monthly_snapshots
month: month-end ISO date; active: open count using latest historical stage as of that month; pipeline: associated open value in INR; won: cumulative won count. Twelve rows. Values are constant within each opportunity in this release, so historical value changes are not modeled.