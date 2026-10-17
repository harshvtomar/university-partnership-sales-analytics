# Explainable priority scoring
Only open opportunities receive an actionable score. Closed records have score zero and priority Closed, excluded from lead queues. No machine learning is claimed. All inputs are available by the fixed snapshot, and outcomes/reasons/recognized revenue are not score features.

| Factor | Weight | Normalization (clipped 0–1) |
|---|---:|---|
| Size | 15 | Students / 15,000 |
| Market | 10 | Assumed territory index: North .85, South .90, West .80, East .65, Central .65, Northeast .55 |
| Engagement | 15 | Activity count / 12 |
| Segment | 10 | Enterprise 1, Growth .7, Emerging .4 |
| Response | 15 | Responded activities / all activities; zero with none |
| Value | 15 | Potential contract value / INR 1,500,000 |
| Stage | 10 | Assumed stage probability / .70 |
| Recency | 10 | 1 − days since last activity / 60 |

Sum components, round to 2 decimals. High ≥70, Medium ≥45, Low <45. Segment: Enterprise ≥7,000 students, Growth ≥2,000, otherwise Emerging. Market indices are fictional planning assumptions, not measured state rankings. Size, segment and value overlap, so test alternative weights before real use. Repeated low-quality outreach can inflate engagement; this demonstration does not estimate causal lead quality. No predictive holdout experiment is appropriate for outcomes produced by this simulator.
