"""Inspect cached native spreadsheet results, not authoring or recalculation."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import pytest
from src.load import load
from src.model import ROOT,forecasts,kpis
N={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def cells(sheet):
    with ZipFile(ROOT/'reports/Partnership_Analytics.xlsx') as z:
        doc=ET.fromstring(z.read(f'xl/worksheets/sheet{sheet}.xml'))
    return {e.attrib['r']:e.find('x:v',N).text for e in doc.findall('.//x:c',N) if e.find('x:v',N) is not None}

def test_workbook_headlines():
    d,_=load();k=kpis(d);c=cells(1)
    for cell,key in [('B7','active'),('B8','pipeline'),('B9','won'),('B10','bookings'),('B11','recognized'),('B12','win_rate'),('B13','avg_deal'),('B14','overdue')]:assert float(c[cell])==pytest.approx(k[key])
    assert float(c['B15'])==pytest.approx(forecasts(d).forecast.iloc[1])

def test_workbook_all_lead_scores():
    d,_=load();leads=d[d.status=='Open'].sort_values('score',ascending=False,kind='stable');c=cells(3)
    # Excel table is sorted by score. Compare all numeric totals as a multiset to avoid tie-order assumptions.
    actual=sorted(float(c[f'K{i}']) for i in range(6,len(leads)+6));assert actual==pytest.approx(sorted(leads.score.tolist()))

def test_workbook_contract_accruals():
    d,_=load();c=cells(6);assert sum(float(c[f'H{i}']) for i in range(6,63))==pytest.approx(kpis(d)['recognized'])

def test_workbook_scenarios():
    d,_=load();c=cells(5);assert [float(c[f'L{i}']) for i in range(6,9)]==pytest.approx(forecasts(d).forecast.tolist())
