import pytest
from streamlit.testing.v1 import AppTest
from src.model import ROOT
PAGES=['Executive Overview','Sales Pipeline','Institutional Lead Intelligence','Territory Performance','Salesperson Performance','Revenue Forecasting','Management Recommendations']
@pytest.mark.parametrize('page',PAGES)
def test_pages(page):
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run();app.sidebar.radio[0].set_value(page).run();assert not app.exception

def test_filters_search_and_forecast():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    app.sidebar.multiselect[0].set_value(['North']).run();assert not app.exception
    app.sidebar.radio[0].set_value(PAGES[2]).run();app.text_input[0].set_value('no such institution').run();assert not app.exception
    app.sidebar.radio[0].set_value(PAGES[5]).run();before=app.metric[1].value;app.slider[0].set_value(1.3).run();assert app.metric[1].value!=before and not app.exception

def test_empty_filter():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    app.sidebar.multiselect[0].set_value(['Northeast']);app.sidebar.multiselect[2].set_value(['Rep 01']);app.sidebar.date_input[0].set_value(('2025-10-01','2025-10-01'));app.run();assert not app.exception and len(app.info)>0
