import sqlite3
import pandas as pd
from .model import ROOT

def load():
    path=ROOT/'data/partnerships.sqlite'
    if not path.exists():raise FileNotFoundError('Dataset missing. Run python -m src.generate from project root.')
    with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as con:
        d=pd.read_sql_query('SELECT * FROM analytics',con)
        h=pd.read_sql_query('SELECT * FROM stage_history',con)
    for c in ['stalled','overdue']:d[c]=d[c].astype(bool)
    return d,h
