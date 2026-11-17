"""RevenueIQ 360: reproducible retail analytics on illustrative synthetic data."""
import pandas as pd
import numpy as np

REQUIRED={'order_id','order_date','customer_id','product_id','category','quantity','unit_price','unit_cost','discount_pct','status','region'}

def load_data(path='data/transactions.csv'):
    df=pd.read_csv(path,parse_dates=['order_date'])
    missing=REQUIRED-set(df.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    if df.order_id.duplicated().any(): raise ValueError('Duplicate order IDs')
    if df[list(['quantity','unit_price','unit_cost'])].isna().any().any(): raise ValueError('Missing numeric fields')
    if (df.quantity<=0).any() or (df[['unit_price','unit_cost']]<0).any().any(): raise ValueError('Invalid price/quantity')
    if (~df.discount_pct.between(0,100)).any(): raise ValueError('Discount outside 0-100')
    if not df.status.isin(['Completed','Returned','Cancelled']).all(): raise ValueError('Unknown order status')
    df['gross_sales']=df.quantity*df.unit_price
    df['net_sales']=df.gross_sales*(1-df.discount_pct/100)
    df['cost']=df.quantity*df.unit_cost
    # Recognize only completed orders as realized revenue; returns and cancellations excluded.
    df['recognized_revenue']=np.where(df.status.eq('Completed'),df.net_sales,0.0)
    df['recognized_profit']=np.where(df.status.eq('Completed'),df.net_sales-df.cost,0.0)
    df['month']=df.order_date.dt.to_period('M').dt.to_timestamp()
    return df

def kpis(df):
    done=df[df.status=='Completed']
    rev=float(done.recognized_revenue.sum()); profit=float(done.recognized_profit.sum())
    return {'orders':int(len(df)),'completed_orders':int(len(done)),'revenue':rev,'profit':profit,'margin_pct':100*profit/rev if rev else 0,'customers':int(done.customer_id.nunique()),'return_rate_pct':100*(df.status=='Returned').mean()}

def monthly(df):
    return df.groupby('month',as_index=False)[['recognized_revenue','recognized_profit']].sum().sort_values('month')

def rfm(df,as_of=None):
    done=df[df.status=='Completed'].copy()
    if done.empty: return pd.DataFrame(columns=['customer_id','recency_days','frequency','monetary','segment'])
    as_of=pd.Timestamp(as_of) if as_of is not None else done.order_date.max()+pd.Timedelta(days=1)
    g=done.groupby('customer_id').agg(last_purchase=('order_date','max'),frequency=('order_id','nunique'),monetary=('recognized_revenue','sum')).reset_index()
    g['recency_days']=(as_of-g.last_purchase).dt.days
    # Quantile ranking with rank(method='first') avoids duplicate bin-edge errors.
    r=pd.qcut(g.recency_days.rank(method='first'),4,labels=[4,3,2,1]).astype(int)
    f=pd.qcut(g.frequency.rank(method='first'),4,labels=[1,2,3,4]).astype(int)
    m=pd.qcut(g.monetary.rank(method='first'),4,labels=[1,2,3,4]).astype(int)
    g['rfm_score']=r+f+m
    g['segment']=np.select([g.rfm_score>=10,g.rfm_score>=7,g.rfm_score>=5],['Champions','Loyal','Developing'],default='At Risk')
    return g.drop(columns='last_purchase')

def cohorts(df):
    done=df[df.status=='Completed'][['customer_id','month']].drop_duplicates()
    if done.empty: return pd.DataFrame()
    done=done.copy();done['cohort']=done.groupby('customer_id').month.transform('min')
    done['age']=(done.month.dt.year-done.cohort.dt.year)*12+(done.month.dt.month-done.cohort.dt.month)
    counts=done.groupby(['cohort','age']).customer_id.nunique().unstack(fill_value=0)
    return counts.div(counts[0],axis=0).round(4)

def category_performance(df):
    return df.groupby('category',as_index=False)[['recognized_revenue','recognized_profit']].sum().sort_values('recognized_revenue',ascending=False)

def forecast_baseline(df,horizon=3):
    """Transparent seasonal-naive forecast: repeat values from 12 months ago; evaluate holdout if possible."""
    m=monthly(df).set_index('month')['recognized_revenue'].asfreq('MS',fill_value=0)
    if len(m)<15: return pd.DataFrame(),None
    holdout=m.iloc[-3:]; train=m.iloc[:-3]
    pred=pd.Series([train.iloc[-12+i] for i in range(3)],index=holdout.index)
    mae=float((pred-holdout).abs().mean())
    future_idx=pd.date_range(m.index[-1]+pd.offsets.MonthBegin(1),periods=horizon,freq='MS')
    future=pd.DataFrame({'month':future_idx,'forecast_revenue':[float(m.iloc[-12+i]) for i in range(horizon)]})
    return future,mae
