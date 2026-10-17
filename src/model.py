"""Shared business rules. All amounts are INR, exclusive of taxes."""
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
AS_OF = pd.Timestamp('2026-09-30')
START = pd.Timestamp('2025-10-01')
STAGES = ['Prospect Identified','Qualified','Initial Contact','Meeting Scheduled','Proposal Sent','Negotiation','Closed Won','Closed Lost']
PROB = dict(zip(STAGES, [.03,.10,.18,.30,.50,.70,1,0]))
GEO = [('Delhi','New Delhi','North'),('Uttar Pradesh','Noida','North'),('Haryana','Gurugram','North'),('Punjab','Ludhiana','North'),('Maharashtra','Pune','West'),('Gujarat','Ahmedabad','West'),('Rajasthan','Jaipur','West'),('Karnataka','Bengaluru','South'),('Tamil Nadu','Chennai','South'),('Telangana','Hyderabad','South'),('West Bengal','Kolkata','East'),('Odisha','Bhubaneswar','East'),('Bihar','Patna','East'),('Assam','Guwahati','Northeast'),('Madhya Pradesh','Indore','Central')]
# Deliberate planning assumptions, not empirical state rankings.
ATTRACTIVENESS = {'North':.85,'South':.90,'West':.80,'East':.65,'Northeast':.55,'Central':.65}

def inr(n):
    if pd.isna(n): return 'N/A'
    n=float(n)
    if abs(n)>=1e7:return f'₹{n/1e7:,.2f} Cr'
    if abs(n)>=1e5:return f'₹{n/1e5:,.2f} L'
    return f'₹{n:,.0f}'

def kpis(df):
    won=df[df.status=='Won']; closed=df[df.status!='Open']; active=df[df.status=='Open']
    return dict(prospects=int(df.institution_id.nunique()),opportunities=len(df),active=len(active),won=len(won),lost=int((df.status=='Lost').sum()),pipeline=int(active.value.sum()),bookings=int(won.value.sum()),win_rate=len(won)/len(closed) if len(closed) else None,avg_deal=float(won.value.mean()) if len(won) else None,cycle_days=float(won.cycle_days.mean()) if len(won) else None,stalled=int(active.stalled.sum()),overdue=int(active.overdue.sum()),recognized=float(df.recognized.sum()))

def score_components(row):
    """0-100 heuristic for OPEN leads only; each component capped independently."""
    clip=lambda x: max(0,min(1,float(x)))
    return {'Size':15*clip(row['students']/15000),'Market':10*clip(row['market_index']), 'Engagement':15*clip(row['activity_count']/12),'Segment':10*{'Enterprise':1,'Growth':.7,'Emerging':.4}[row['segment']], 'Response':15*clip(row['response_rate']), 'Value':15*clip(row['value']/1500000),'Stage':10*clip(PROB[row['stage']]/.70),'Recency':10*clip(1-row['inactive_days']/60)}

def enrich(inst,opp,activities,history,revenue):
    d=opp.merge(inst,on='institution_id',validate='many_to_one')
    ag=activities.groupby('opportunity_id').agg(activity_count=('activity_id','count'),last_activity=('activity_date','max'),response_rate=('responded','mean'),meetings=('activity_type',lambda x:(x=='Meeting').sum()))
    d=d.merge(ag,on='opportunity_id',how='left')
    for c in ['activity_count','response_rate','meetings']:d[c]=d[c].fillna(0)
    d['last_activity']=d.last_activity.fillna(d.created)
    d['inactive_days']=(AS_OF-pd.to_datetime(d.last_activity)).dt.days
    d['age_days']=(AS_OF-pd.to_datetime(d.created)).dt.days
    d['cycle_days']=(pd.to_datetime(d.actual_close)-pd.to_datetime(d.created)).dt.days
    entry=history.groupby('opportunity_id').event_date.max()
    d['stage_age_days']=(AS_OF-pd.to_datetime(d.opportunity_id.map(entry))).dt.days
    d['stalled']=(d.status=='Open') & (d.stage_age_days>30)
    # Only the latest activity owns the next action. Prior tasks are completed/superseded.
    latest=activities.sort_values(['activity_date','activity_id']).groupby('opportunity_id').tail(1).set_index('opportunity_id')
    d['next_action']=d.opportunity_id.map(latest.next_action)
    d['overdue']=(d.status=='Open') & (pd.to_datetime(d.next_action)<AS_OF)
    rec=revenue.set_index('opportunity_id').recognized if len(revenue) else pd.Series(dtype=float)
    d['recognized']=d.opportunity_id.map(rec).fillna(0)
    d['probability']=d.stage.map(PROB)
    components=d.apply(lambda r: score_components(r) if r.status=='Open' else {k:0 for k in ['Size','Market','Engagement','Segment','Response','Value','Stage','Recency']},axis=1)
    for name in ['Size','Market','Engagement','Segment','Response','Value','Stage','Recency']:d['score_'+name.lower()]=components.map(lambda x:x[name])
    d['score']=components.map(lambda x:round(sum(x.values()),2))
    d['priority']=d.score.map(lambda x:'High' if x>=70 else ('Medium' if x>=45 else 'Low'))
    d.loc[d.status!='Open','priority']='Closed'
    d['explanation']=components.map(lambda x:'; '.join(f'{k} {v:.1f}' for k,v in x.items()))
    return d

def funnel(history,ids):
    h=history[history.opportunity_id.isin(ids)]
    rows=[]
    for a,b in zip(STAGES[:6],STAGES[1:7]):
        reached=set(h.loc[h.stage==a,'opportunity_id']); advanced=set(h.loc[h.stage==b,'opportunity_id'])
        rows.append(dict(stage=a,reached=len(reached),advanced=len(reached&advanced),conversion=len(reached&advanced)/len(reached) if reached else None))
    return pd.DataFrame(rows)

def forecasts(d,multiplier=1.0):
    """Next-quarter NEW signed value. Past-due expected closes excluded, disclosed."""
    eligible=d[(d.status=='Open') & (d.expected_close>'2026-09-30') & (d.expected_close<='2026-12-31')].copy()
    result=[]
    for name,m in [('Conservative',.7),('Base',1.),('Optimistic',1.3)]:
        result.append({'scenario':name,'forecast':float((eligible.value*(eligible.probability*m*multiplier).clip(0,1)).sum()),'eligible_opportunities':len(eligible)})
    return pd.DataFrame(result)

def performance(d,group):
    rows=[]
    for key,g in d.groupby(group):
        k=kpis(g);k[group]=key;k['meetings']=int(g.meetings.sum());k['high_priority']=int(((g.status=='Open')&(g.priority=='High')).sum());rows.append(k)
    return pd.DataFrame(rows)

def recommendations(d,h):
    if d.empty:return ['No opportunities match the filters.']
    k=kpis(d);f=funnel(h,d.opportunity_id);out=[]
    out.append(f"Sales managers: resolve {k['overdue']} overdue next actions across {k['active']} open opportunities; review the latest activity before assigning outreach.")
    out.append(f"Pipeline review: {k['stalled']} open opportunities have spent over 30 days in their current stage. Requalify these before increasing forecast confidence.")
    valid=f[f.reached>=20]
    if len(valid):
        r=valid.sort_values('conversion').iloc[0];out.append(f"Enablement: {r['stage']} has the lowest observed next-stage conversion among stages with at least 20 entries: {int(r.advanced)}/{int(r.reached)} ({r.conversion:.1%}). Review objections and allow for unfinished sales cycles.")
    t=performance(d,'territory').sort_values('pipeline',ascending=False).iloc[0]
    out.append(f"Territory coverage: {t.territory} holds {inr(t.pipeline)} in active pipeline with {int(t.overdue)} overdue actions. Clear the backlog before allocating additional prospecting capacity.")
    top=d[d.status=='Open'].sort_values(['score','value'],ascending=False).head(1)
    if len(top):
        r=top.iloc[0];out.append(f"Next account review: {r.institution_name} ({r.opportunity_id}) scores {r.score:.1f}/100 and carries {inr(r.value)} potential value. This score is a prioritization heuristic, not a win probability.")
    stale=d[(d.status=='Open')&(d.expected_close<='2026-09-30')]
    out.append(f"Forecast hygiene: {len(stale)} open deals ({inr(stale.value.sum())}) have past-due expected close dates and are excluded from the next-quarter forecast. Owners must revise dates or close the records.")
    return out
