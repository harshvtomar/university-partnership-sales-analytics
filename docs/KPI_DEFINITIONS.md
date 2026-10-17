All values are INR excluding tax. Snapshot: 30 September 2026. Dashboard filters select opportunities by creation date and current attributes. Related history and activities run through the snapshot; the filter is not an activity-date filter.

| KPI | Formula and denominator |
|---|---|
| Prospects | Distinct institution IDs in the selected opportunity cohort |
| Qualified opportunities | Distinct opportunity IDs with a Qualified stage entry by snapshot |
| Active opportunities | Count with status Open |
| Active pipeline | Sum of estimated value for Open opportunities |
| Signed / closed-won value | Sum of Won opportunity values (bookings, not revenue) |
| Recognized revenue | Sum of contract value × min(365, days from signature through snapshot inclusive) / 365, rounded to paise per contract |
| Win rate | Won / (Won + Lost). N/A if no closed deals |
| Stage conversion | Distinct IDs reaching the next stage divided by distinct IDs entering the current stage; history restricted to selected cohort and snapshot |
| Sales cycle | Mean days from creation to actual closure among Won deals only |
| Average deal size | Sum of Won value / count of Won opportunities. N/A with no wins |
| Weighted forecast | Open deals expected to close 1 Oct–31 Dec 2026 × assumed stage probabilities; excludes past-due and later expected dates |
| Stalled | Open opportunities with >30 calendar days in current stage |
| Overdue follow-up | Open opportunity whose latest activity has next_action before snapshot; due on snapshot is not overdue |
| Meetings | Count of Meeting activities attached to the selected opportunities |

One institution has one opportunity in this release, but distinct institution and opportunity counts remain separate. Funnel ratios are observed-to-date and affected by unfinished sales cycles. Payment status does not govern revenue accrual and is not a cash collection amount. No cash receipts KPI is inferred.
