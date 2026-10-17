import sqlite3
import pandas as pd
import pytest
from src.generate import generate
from src.model import *
from src.load import load

@pytest.fixture(scope='module')
def raw():return generate()
@pytest.fixture(scope='module')
def data():return load()[0]

def test_reproducible(raw):
    for n,d in raw.items():pd.testing.assert_frame_equal(d,generate()[n])

def test_scope(raw):
    assert len(raw['institutions'])>=500 and len(raw['activities'])>=1500
    assert raw['opportunities'].created.str[:7].nunique()==12
    assert len(pd.read_csv(ROOT/'data/monthly_snapshots.csv'))==12

def test_keys_and_nulls(raw):
    for name,key in [('institutions','institution_id'),('opportunities','opportunity_id'),('activities','activity_id'),('stage_history','event_id'),('revenue','contract_id')]:
        assert raw[name][key].is_unique and raw[name][key].notna().all()
    o=raw['opportunities'];assert set(o.institution_id)<=set(raw['institutions'].institution_id)
    for n in ['activities','stage_history','revenue']:assert set(raw[n].opportunity_id)<=set(o.opportunity_id)
    with sqlite3.connect(ROOT/'data/partnerships.sqlite') as c:assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
    for df,cols in [(raw['institutions'],list(raw['institutions'].columns)),(o,[c for c in o if c not in ['actual_close','reason']])]:assert df[cols].notna().all().all()

def test_database_rejects_orphan():
    with sqlite3.connect(':memory:') as c:
        c.executescript((ROOT/'sql/schema.sql').read_text())
        with pytest.raises(sqlite3.IntegrityError):c.execute("INSERT INTO stage_history VALUES('x','missing','Qualified','2026-01-01')")

def test_dates_and_outcomes(raw):
    o=raw['opportunities'];closed=o[o.status!='Open'];assert (closed.actual_close>=closed.created).all()
    assert o.loc[o.status=='Open','actual_close'].isna().all()
    assert (o.loc[o.status=='Won','stage']=='Closed Won').all();assert (o.loc[o.status=='Lost','stage']=='Closed Lost').all()
    for n,col in [('activities','activity_date'),('stage_history','event_date')]:
        x=raw[n].merge(o,on='opportunity_id');assert (x[col]>=x.created).all();assert (x[col]<=x.actual_close.fillna(str(AS_OF.date()))).all()
    rr=raw['revenue'].merge(o,on='opportunity_id');assert (rr.status=='Won').all();assert (rr.contract_value==rr.value).all();assert (rr.signed_date==rr.actual_close).all()
    assert set(raw['revenue'].opportunity_id)==set(o.loc[o.status=='Won','opportunity_id'])

def test_latest_stage(raw):
    last=raw['stage_history'].sort_values('event_date').groupby('opportunity_id').tail(1).set_index('opportunity_id').stage
    assert (raw['opportunities'].set_index('opportunity_id').stage==last.reindex(raw['opportunities'].opportunity_id)).all()

def test_reconcile(data,raw):
    k=kpis(data)
    with sqlite3.connect(ROOT/'data/partnerships.sqlite') as c:
        bookings,recognized=c.execute('SELECT SUM(contract_value),SUM(recognized) FROM revenue').fetchone()
    assert bookings==k['bookings']==raw['opportunities'].loc[lambda x:x.status=='Won','value'].sum()
    assert recognized==pytest.approx(k['recognized'])
    r=raw['revenue'];days=(AS_OF-pd.to_datetime(r.signed_date)).dt.days.add(1).clip(upper=365)
    assert r.recognized.sum()==pytest.approx((r.contract_value*days/365).round(2).sum())

def test_funnel_fixture():
    h=pd.DataFrame([['a','Prospect Identified'],['a','Qualified'],['b','Prospect Identified'],['b','Closed Lost'],['c','Prospect Identified']],columns=['opportunity_id','stage'])
    f=funnel(h,['a','b','c']);assert f.iloc[0].reached==3 and f.iloc[0].advanced==1 and f.iloc[0].conversion==pytest.approx(1/3)
    assert pd.isna(f.iloc[-1].conversion)

def test_win_rate_fixture(data):
    f=data.iloc[:3].copy();f['status']=['Won','Lost','Open'];f['value']=[100,200,900];f['recognized']=[10,0,0]
    k=kpis(f);assert k['win_rate']==.5 and k['bookings']==100 and k['pipeline']==900 and k['avg_deal']==100
    assert kpis(f.iloc[2:])['win_rate'] is None

def test_score_bounds(data):
    assert data.score.between(0,100).all();assert (data.loc[data.status!='Open','priority']=='Closed').all()
    r=dict(students=999999,market_index=99,activity_count=999,segment='Enterprise',response_rate=99,value=9999999,stage='Negotiation',inactive_days=-5)
    assert sum(score_components(r).values())==100
    r.update(students=-1,market_index=-1,activity_count=-1,response_rate=-1,value=-1,inactive_days=90,stage='Prospect Identified')
    assert all(v>=0 for v in score_components(r).values())

def test_forecast_fixture():
    d=pd.DataFrame([['Open','2026-10-01',100,.7],['Open','2026-09-30',900,.7],['Won','2026-11-01',900,1],['Open','2027-01-01',900,.7]],columns=['status','expected_close','value','probability'])
    f=forecasts(d);assert list(f.forecast)==pytest.approx([49,70,91]);assert forecasts(d,1.5).forecast.iloc[2]==100
    assert forecasts(d.iloc[:0]).forecast.sum()==0

def test_follow_up_and_stall(data,raw):
    a=raw['activities'].sort_values(['activity_date','activity_id']).groupby('opportunity_id').tail(1)
    overdue=set(a.loc[(a.follow_up_status=='Pending')&(a.next_action<'2026-09-30'),'opportunity_id'])
    assert set(data.loc[data.overdue,'opportunity_id'])==overdue
    assert not data.loc[data.status!='Open',['stalled','overdue']].any().any()

def test_sql_queries_execute():
    with sqlite3.connect(ROOT/'data/partnerships.sqlite') as c:
        statements='\n'.join(line for line in (ROOT/'sql/queries.sql').read_text().splitlines() if not line.startswith('--')).split(';')
        for s in statements:
            if s.strip():c.execute(s).fetchall()

def test_funnel_sql_python_agree(data):
    d,h=load();f=funnel(h,d.opportunity_id)
    with sqlite3.connect(ROOT/'data/partnerships.sqlite') as c:
        sql=pd.read_sql_query("WITH x AS (SELECT stage,LEAD(stage) OVER(PARTITION BY opportunity_id ORDER BY event_date) nxt FROM stage_history) SELECT stage,COUNT(*) reached,SUM(nxt IS NOT NULL AND nxt!='Closed Lost') advanced FROM x WHERE stage NOT IN ('Closed Won','Closed Lost') GROUP BY stage",c)
    a=f.merge(sql,on='stage');assert (a.reached_x==a.reached_y).all() and (a.advanced_x==a.advanced_y).all()

def test_no_leakage_inputs(data):
    r=data[data.status=='Open'].iloc[0].copy();s=score_components(r);r['reason']='Won';r['recognized']=9e9;r['actual_close']='2027-01-01';assert s==score_components(r)
