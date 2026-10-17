"""Deterministic fictional CRM generator. python -m src.generate"""
import random,sqlite3,json,hashlib
import pandas as pd
from .model import *

def generate(seed=20261017):
    r=random.Random(seed);institutions=[];opps=[];events=[];acts=[];contracts=[]
    for i in range(1,601):
        state,city,territory=GEO[(i-1)%len(GEO)];typ=r.choice(['University','Engineering College','Management Institute','Arts and Science College']);students=r.randint(600,18000) if typ=='University' else r.randint(200,6000)
        institutions.append(dict(institution_id=f'I{i:04}',institution_name=f'Simulated {city} {typ} {i:03}',state=state,city=city,territory=territory,institution_type=typ,ownership=r.choice(['Private','Public','Trust']),students=students,segment='Enterprise' if students>=7000 else ('Growth' if students>=2000 else 'Emerging'),market_index=ATTRACTIVENESS[territory],is_simulated=1))
        oid=f'O{i:04}';created=START+pd.Timedelta(days=r.randint(0,364));rep=f'Rep {1+(i-1)%8:02}';value=int(round((80000+students*r.uniform(20,70))/1000)*1000)
        path=[(STAGES[0],created)];dt=created
        for idx in range(1,7):
            if r.random()<.16:break
            nxt=dt+pd.Timedelta(days=r.randint(5,32) if idx!=5 else r.randint(12,50))
            if nxt>AS_OF:break
            if r.random()<(.12 if idx<5 else .22):path.append(('Closed Lost',nxt));break
            path.append((STAGES[idx],nxt));dt=nxt
        stage,last=path[-1];status='Won' if stage=='Closed Won' else ('Lost' if stage=='Closed Lost' else 'Open');closed=last if status!='Open' else None
        expected=created+pd.Timedelta(days=r.randint(80,150))
        opps.append(dict(opportunity_id=oid,institution_id=f'I{i:04}',sales_rep=rep,lead_source=r.choice(['Conference','Referral','Inbound enquiry','Outbound research','Webinar']),created=created.date().isoformat(),stage=stage,value=value,expected_close=expected.date().isoformat(),actual_close=closed.date().isoformat() if closed is not None else None,status=status,reason=r.choice(['Budget unavailable','Procurement delay','Competitor selected','No strategic fit']) if status=='Lost' else ('Campaign scope agreed' if status=='Won' else None)))
        for s,t in path:events.append(dict(event_id=f'E{len(events)+1:05}',opportunity_id=oid,stage=s,event_date=t.date().isoformat()))
        end=closed if closed is not None else AS_OF;span=(end-created).days
        dates=sorted(created+pd.Timedelta(days=r.randint(0,max(span,0))) for _ in range(r.randint(3,12)))
        for j,t in enumerate(dates):
            pending=status=='Open' and j==len(dates)-1
            acts.append(dict(activity_id=f'A{len(acts)+1:05}',opportunity_id=oid,activity_date=t.date().isoformat(),activity_type=r.choice(['Email','Call','Meeting','Demo','Proposal follow-up']),responded=int(r.random()<.55),follow_up_status='Pending' if pending else 'Completed',next_action=(t+pd.Timedelta(days=r.randint(3,14))).date().isoformat() if pending else None,sales_rep=rep))
        if status=='Won':
            # Service starts at signature, daily straight-line, 365-day term. Accrue inclusive of signature day.
            days=min(365,(AS_OF-closed).days+1)
            contracts.append(dict(contract_id=f'C{len(contracts)+1:04}',opportunity_id=oid,signed_date=closed.date().isoformat(),contract_value=value,payment_status=r.choice(['Paid','Part-paid','Unpaid']),term_days=365,recognized=round(value*days/365,2),recognition_basis='Daily straight-line from signature; 365 days; tax excluded'))
    return dict(institutions=pd.DataFrame(institutions),opportunities=pd.DataFrame(opps),stage_history=pd.DataFrame(events),activities=pd.DataFrame(acts),revenue=pd.DataFrame(contracts))

def build():
    data=generate();folder=ROOT/'data';folder.mkdir(exist_ok=True)
    for name,df in data.items():df.to_csv(folder/f'{name}.csv',index=False)
    db=folder/'partnerships.sqlite';db.unlink(missing_ok=True)
    con=sqlite3.connect(db);con.executescript((ROOT/'sql/schema.sql').read_text())
    for name,df in data.items():df.to_sql(name,con,index=False,if_exists='append')
    d=enrich(data['institutions'],data['opportunities'],data['activities'],data['stage_history'],data['revenue'])
    d.to_sql('analytics',con,index=False,if_exists='replace');d.to_csv(folder/'analytics.csv',index=False)
    months=[]
    for end in pd.date_range(START,AS_OF,freq='ME'):
        hist=data['stage_history'];last=hist[hist.event_date<=end.date().isoformat()].sort_values('event_date').groupby('opportunity_id').tail(1)
        snap=last.merge(data['opportunities'][['opportunity_id','value']],on='opportunity_id');active=snap[~snap.stage.isin(['Closed Won','Closed Lost'])]
        months.append(dict(month=end.date().isoformat(),active=len(active),pipeline=int(active.value.sum()),won=int((snap.stage=='Closed Won').sum())))
    pd.DataFrame(months).to_csv(folder/'monthly_snapshots.csv',index=False)
    summary={'as_of':str(AS_OF.date()),'seed':20261017,'counts':{k:len(v) for k,v in data.items()},'kpis':kpis(d),'forecasts':forecasts(d).to_dict('records'),'recommendations':recommendations(d,data['stage_history'])}
    (folder/'summary.json').write_text(json.dumps(summary,indent=2))
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob('*.csv'))};(folder/'manifest.json').write_text(json.dumps(manifest,indent=2));con.close();print(json.dumps(summary,indent=2))
if __name__=='__main__':build()
