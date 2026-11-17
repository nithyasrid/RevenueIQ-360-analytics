import pandas as pd
from src.analytics import load_data,kpis,rfm,cohorts,forecast_baseline

def test_dataset():
 d=load_data();assert len(d)==12000;assert d.order_id.is_unique

def test_revenue():
 d=load_data();k=kpis(d);assert k['revenue']>0;assert k['completed_orders']<k['orders']

def test_rfm():
 d=load_data();r=rfm(d);assert r.customer_id.is_unique;assert r.segment.notna().all()

def test_cohorts():
 c=cohorts(load_data());assert (c[0]==1).all();assert (c.fillna(0)<=1).all().all()

def test_forecast():
 f,mae=forecast_baseline(load_data());assert len(f)==3;assert mae>=0

def test_duplicate_rejected(tmp_path):
 d=pd.read_csv('data/transactions.csv').head(2);d.loc[1,'order_id']=d.loc[0,'order_id'];path=tmp_path/'bad.csv';d.to_csv(path,index=False)
 try:load_data(path)
 except ValueError as e:assert 'Duplicate' in str(e)
 else:assert False
