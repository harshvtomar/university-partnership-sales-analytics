"""Partnership Desk: seven-page, read-only sales operations dashboard."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.model import *
from src.load import load
st.set_page_config(page_title='Partnership Desk',page_icon='📊',layout='wide')
st.markdown('''<style>.stApp {background:#f6f8fc} h1,h2,h3 {color:#10283f} [data-testid="stMetric"] {background:white;border:1px solid #dae3ec;border-radius:10px;padding:14px} [data-testid="stSidebar"] {background:#edf3f8} .block-container {padding-top:2rem} </style>''',unsafe_allow_html=True)
@st.cache_data
def dataset():return load()
try:d,h=dataset()
except (FileNotFoundError,Exception) as e:
    st.error(f'Unable to load the dataset: {e}');st.stop()
PAGES=['Executive Overview','Sales Pipeline','Institutional Lead Intelligence','Territory Performance','Salesperson Performance','Revenue Forecasting','Management Recommendations']
st.sidebar.title('Partnership Desk')
st.sidebar.caption('INSTITUTIONAL GROWTH / INDIA')
page=st.sidebar.radio('Workspace',PAGES)
st.sidebar.divider()
st.sidebar.caption('Filters select opportunity creation cohorts. Outcomes and activity are measured through 30 Sep 2026.')
selected=d.copy()
for field,label in [('territory','Territory'),('institution_type','Institution category'),('sales_rep','Salesperson'),('stage','Current stage')]:
    choices=st.sidebar.multiselect(label,sorted(d[field].unique()))
    if choices:selected=selected[selected[field].isin(choices)]
dates=st.sidebar.date_input('Lead creation range',(START.date(),AS_OF.date()),min_value=START.date(),max_value=AS_OF.date())
if isinstance(dates,(list,tuple)) and len(dates)==2:selected=selected[selected.created.between(str(dates[0]),str(dates[1]))]
st.sidebar.caption('No selections in a category means all. Snapshot is fixed for reproducible demonstrations.')
st.title(page)
st.caption('FICTIONAL PORTFOLIO SIMULATION · CampusBridge Demo · 01 Oct 2025–30 Sep 2026 · INR excluding tax')
st.markdown(f'**{len(selected):,} opportunities** in this view · **{selected.institution_id.nunique():,} institutions**')
if selected.empty:st.info('No opportunities match these filters. Clear a filter or widen the date range.');st.stop()
k=kpis(selected)

def chart(fig):
    fig.update_layout(template='plotly_white',font=dict(family='Arial',color='#19354d'),paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=10,r=10,t=45,b=15),colorway=['#087f8c','#2764c5','#e6a23c','#bd5c52'],height=360)
    st.plotly_chart(fig,width='stretch')
def table(df,name):
    st.dataframe(df,hide_index=True,width='stretch');st.download_button('Download CSV',df.to_csv(index=False).encode(),name,'text/csv',key=name)
def cards(items):
    for c,(label,value) in zip(st.columns(len(items)),items):c.metric(label,value)
if page==PAGES[0]:
    cards([('Active opportunities',k['active']),('Active pipeline',inr(k['pipeline'])),('Partnerships won',k['won'])])
    cards([('Recognized revenue',inr(k['recognized'])),('Closed-deal win rate',f"{k['win_rate']:.1%}" if k['win_rate'] is not None else 'N/A'),('Average won deal',inr(k['avg_deal']))])
    st.caption(f"Signed value: {inr(k['bookings'])}. Win rate = {k['won']} won / {k['won']+k['lost']} closed. Recognized revenue accrues daily over each 365-day contract.")
    left,right=st.columns(2)
    with left:
        won=selected[selected.status=='Won'].copy();won['month']=won.actual_close.str[:7]
        monthly=won.groupby('month').value.sum().reindex(pd.date_range(START,AS_OF,freq='MS').strftime('%Y-%m'),fill_value=0).reset_index();monthly.columns=['Month','Signed value (INR)']
        chart(px.bar(monthly,x='Month',y='Signed value (INR)',title='Monthly signed partnership value'))
    with right:
        rows=[]
        for end in pd.date_range(START,AS_OF,freq='ME'):
            hist=h[(h.opportunity_id.isin(selected.opportunity_id))&(h.event_date<=str(end.date()))].sort_values('event_date').groupby('opportunity_id').tail(1)
            snap=hist.merge(selected[['opportunity_id','value']],on='opportunity_id');rows.append({'Month':str(end.date())[:7],'Open value (INR)':snap.loc[~snap.stage.isin(STAGES[6:]),'value'].sum()})
        chart(px.line(pd.DataFrame(rows),x='Month',y='Open value (INR)',markers=True,title='Historical month-end open pipeline'))
    st.subheader('Management brief')
    for rec in recommendations(selected,h)[:3]:st.write(rec)
    with st.expander('KPI definitions and scope'):st.markdown((ROOT/'docs/KPI_DEFINITIONS.md').read_text())
elif page==PAGES[1]:
    f=funnel(h,selected.opportunity_id)
    chart(go.Figure(go.Funnel(y=list(f.stage)+['Closed Won'],x=list(f.reached)+[k['won']],marker_color='#087f8c')).update_layout(title='Cumulative stage reach for selected creation cohort'))
    st.caption('Distinct opportunities that ever entered each stage by the snapshot. Lost records leave the forward path. Recent cohorts are right-censored, so reach ratios are not final conversion probabilities.')
    table(f,'stage_conversion.csv')
    cards([('Stalled >30 days in stage',k['stalled']),('Overdue next actions',k['overdue']),('Qualified ever',int(h[(h.opportunity_id.isin(selected.opportunity_id))&(h.stage=='Qualified')].opportunity_id.nunique()))])
    focus=st.checkbox('Only opportunities needing attention')
    view=selected[selected.stalled|selected.overdue] if focus else selected
    table(view[['opportunity_id','institution_name','stage','status','value','sales_rep','stage_age_days','next_action','stalled','overdue']],'pipeline.csv')
elif page==PAGES[2]:
    st.caption('Open opportunities only. Score is an explainable commercial heuristic, not a predictive model. High ≥70; Medium ≥45; Low <45.')
    q=st.text_input('Search institution');priority=st.multiselect('Priority',['High','Medium','Low'])
    leads=selected[selected.status=='Open'].copy()
    if q:leads=leads[leads.institution_name.str.contains(q,case=False,regex=False)]
    if priority:leads=leads[leads.priority.isin(priority)]
    leads=leads.sort_values(['score','value'],ascending=False)
    table(leads[['institution_name','state','segment','students','stage','value','score','priority','explanation']],'prioritized_leads.csv')
    if len(leads):
        pick=st.selectbox('Explain an institution',leads.opportunity_id.tolist(),format_func=lambda x:leads.set_index('opportunity_id').loc[x,'institution_name'])
        r=leads.set_index('opportunity_id').loc[pick];parts=score_components(r)
        chart(px.bar(x=list(parts.values()),y=list(parts.keys()),orientation='h',labels={'x':'Score contribution','y':'Factor'},title=f'{r.score:.1f} / 100 score breakdown'))
    with st.expander('Weights and assumptions'):st.markdown((ROOT/'docs/SCORING.md').read_text())
elif page==PAGES[3]:
    t=performance(selected,'territory');s=performance(selected,'state')
    chart(px.bar(t,x='territory',y='pipeline',color='territory',title='Active partnership pipeline by territory (INR)'))
    table(s[['state','prospects','active','won','bookings','pipeline','win_rate','overdue','high_priority']],'state_performance.csv')
    st.subheader('Expansion shortlist')
    st.caption('Rank open high-priority opportunities, then pipeline value. This is a synthetic capacity-planning shortlist, not measured market size. No external geographic boundaries are redistributed.')
    table(t.sort_values(['high_priority','pipeline'],ascending=False)[['territory','high_priority','pipeline','overdue','won','lost']],'expansion_shortlist.csv')
elif page==PAGES[4]:
    p=performance(selected,'sales_rep');chart(px.bar(p,x='sales_rep',y='bookings',color='sales_rep',title='Signed partnership value by owner (INR)'))
    table(p[['sales_rep','opportunities','active','meetings','won','lost','win_rate','bookings','cycle_days','overdue']],'salesperson_performance.csv')
    st.info('Simulated representatives only. Compare closed-deal sample sizes, lead mix and cohort maturity before interpreting win rates. Meeting counts cover all recorded activities for the selected opportunities, not just the creation date range.')
elif page==PAGES[5]:
    st.subheader('Oct–Dec 2026 new bookings outlook')
    mult=st.slider('Probability sensitivity multiplier',.5,1.5,1.,.05)
    fc=forecasts(selected,mult);cards([(r.scenario,inr(r.forecast)) for r in fc.itertuples()])
    chart(px.bar(fc,x='scenario',y='forecast',color='scenario',title='Scenario-weighted new signed value (INR)'))
    st.caption('Forecast = eligible open deal value × capped stage probability × scenario multiplier × sensitivity. Conservative 0.7×; base 1.0×; optimistic 1.3×. Probabilities cap at 100%. These are scenarios, not confidence intervals or recognized-revenue forecasts.')
    table(pd.DataFrame({'Stage':STAGES[:6],'Assumed win probability':[PROB[s] for s in STAGES[:6]]}),'forecast_assumptions.csv')
    st.write(recommendations(selected,h)[-1]);table(fc,'forecast_scenarios.csv')
elif page==PAGES[6]:
    for i,rec in enumerate(recommendations(selected,h),1):st.markdown(f'### {i:02} / Action for review');st.write(rec)
    st.download_button('Download management brief','\n\n'.join(recommendations(selected,h)),'management_brief.txt')
    st.caption('Rules generate these findings from filtered project data. Proposed actions have no claimed causal benefit or real-world performance outcome.')
st.divider();st.caption('Harsh Vardhan Tomar · University Partnership & Sales Pipeline Analytics · All institutions, representatives, values and transactions are simulated.')
