-- Q01: Current stage inventory (not a conversion funnel).
SELECT stage,COUNT(*) opportunities,SUM(value) value_inr FROM opportunities GROUP BY stage;
-- Q02: Historical stage reach by distinct opportunity.
SELECT stage,COUNT(DISTINCT opportunity_id) reached FROM stage_history GROUP BY stage;
-- Q03: Adjacent-stage conversion; denominator includes unfinished opportunities.
WITH ordered AS (SELECT opportunity_id,stage,LEAD(stage) OVER(PARTITION BY opportunity_id ORDER BY event_date) next_stage FROM stage_history)
SELECT stage,COUNT(*) entered,SUM(next_stage IS NOT NULL AND next_stage!='Closed Lost') advanced,1.0*SUM(next_stage IS NOT NULL AND next_stage!='Closed Lost')/COUNT(*) rate FROM ordered WHERE stage NOT IN ('Closed Won','Closed Lost') GROUP BY stage;
-- Q04: Bookings, accrued revenue, no cash inference from payment labels.
SELECT SUM(contract_value) signed_value,SUM(recognized) recognized_revenue FROM revenue;
-- Q05: Monthly signed value; date is signature, not creation.
SELECT substr(signed_date,1,7) month,COUNT(*) contracts,SUM(contract_value) bookings FROM revenue GROUP BY month;
-- Q06: Territory size and active value at snapshot.
SELECT territory,COUNT(DISTINCT institution_id) prospects,SUM(status='Open') active,SUM(CASE WHEN status='Open' THEN value ELSE 0 END) pipeline FROM analytics GROUP BY territory;
-- Q07: Rep closed-deal win rate and meeting productivity with safe denominator.
SELECT sales_rep,COUNT(*) assigned,SUM(meetings) meetings,SUM(status='Won') wins,1.0*SUM(status='Won')/NULLIF(SUM(status!='Open'),0) win_rate FROM analytics GROUP BY sales_rep;
-- Q08: Open lead queue, explanation preserves auditability.
SELECT opportunity_id,institution_name,score,priority,explanation FROM analytics WHERE status='Open' ORDER BY score DESC,value DESC;
-- Q09: Stalled opportunity aging, calendar-day threshold >30.
SELECT opportunity_id,stage,stage_age_days,inactive_days,value FROM analytics WHERE status='Open' AND stage_age_days>30 ORDER BY stage_age_days DESC;
-- Q10: Latest-action overdue queue, one row per opportunity.
SELECT opportunity_id,sales_rep,next_action,value FROM analytics WHERE status='Open' AND overdue=1 ORDER BY next_action;
-- Q11: Next-quarter baseline inputs, past-due dates excluded.
SELECT stage,COUNT(*) opportunities,SUM(value) gross_value,SUM(value*probability) weighted FROM analytics WHERE status='Open' AND expected_close>'2026-09-30' AND expected_close<='2026-12-31' GROUP BY stage;
-- Q12: Loss reasons, closed lost denominator only.
SELECT reason,COUNT(*) losses FROM opportunities WHERE status='Lost' GROUP BY reason ORDER BY losses DESC;
-- Q13: Won sales cycle, not current opportunity age.
SELECT sales_rep,COUNT(*) wins,AVG(julianday(actual_close)-julianday(created)) average_cycle_days FROM opportunities WHERE status='Won' GROUP BY sales_rep;
-- Q14: Pipeline quality and value tied up in a stage.
SELECT stage,COUNT(*) open_count,SUM(stalled) stalled_count,AVG(stage_age_days) mean_stage_days,SUM(value) value_inr FROM analytics WHERE status='Open' GROUP BY stage;
