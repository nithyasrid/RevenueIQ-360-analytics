import streamlit as st
import plotly.express as px
from src.analytics import load_data,kpis,monthly,rfm,cohorts,category_performance,forecast_baseline
st.set_page_config(page_title='RevenueIQ 360',page_icon='📊',layout='wide')
st.title('RevenueIQ 360 | Retail Intelligence')
st.caption('Portfolio demonstration using synthetic data. All figures are illustrative, not actual company results.')
@st.cache_data
def get_data(): return load_data()
df=get_data()
regions=st.sidebar.multiselect('Region',sorted(df.region.unique()),default=sorted(df.region.unique()))
categories=st.sidebar.multiselect('Category',sorted(df.category.unique()),default=sorted(df.category.unique()))
df=df[df.region.isin(regions)&df.category.isin(categories)]
if df.empty: st.warning('No data for selected filters.');st.stop()
k=kpis(df)
a,b,c,d=st.columns(4)
a.metric('Recognized revenue',f"${k['revenue']:,.0f}")
b.metric('Recognized profit',f"${k['profit']:,.0f}")
c.metric('Profit margin',f"{k['margin_pct']:.1f}%")
d.metric('Completed orders',f"{k['completed_orders']:,}")
tabs=st.tabs(['Overview','Customers & Retention','Profitability','Forecast & Validation'])
with tabs[0]:
 st.plotly_chart(px.line(monthly(df),x='month',y=['recognized_revenue','recognized_profit'],title='Monthly revenue and profit'),use_container_width=True)
 st.dataframe(category_performance(df),use_container_width=True)
with tabs[1]:
 segments=rfm(df).groupby('segment',as_index=False).agg(customers=('customer_id','count'),revenue=('monetary','sum'))
 st.plotly_chart(px.bar(segments,x='segment',y='customers',title='RFM customer segments'),use_container_width=True)
 retention=cohorts(df)
 if not retention.empty: st.plotly_chart(px.imshow(retention.iloc[:,:12],aspect='auto',title='Cohort retention rate (first 12 months)',labels={'x':'Months since first purchase','y':'First purchase month','color':'Retention'},color_continuous_scale='Blues'),use_container_width=True)
with tabs[2]:
 p=category_performance(df)
 st.plotly_chart(px.bar(p,x='category',y='recognized_profit',title='Profit by category'),use_container_width=True)
 st.caption('Profit = discounted completed-order revenue minus product cost; excludes shipping, overhead, and tax.')
with tabs[3]:
 future,mae=forecast_baseline(df)
 if future.empty: st.info('At least 15 months of data required for the seasonal-naive forecast.')
 else:
  st.metric('Seasonal-naive holdout MAE (last 3 months)',f'${mae:,.0f}')
  st.plotly_chart(px.line(future,x='month',y='forecast_revenue',markers=True,title='Next 3 months: seasonal-naive baseline'),use_container_width=True)
 st.write('Quality checks: unique order IDs, required columns, numeric validity, allowed status values, discount range.')
 st.download_button('Download filtered transactions',df.to_csv(index=False),'revenueiq_filtered.csv','text/csv')
