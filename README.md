# RevenueIQ 360

**Advanced Data Analytics & Business Intelligence portfolio project** using Python, Pandas, PostgreSQL SQL, Streamlit, Plotly, Power BI DAX, customer RFM, cohort retention, and seasonal-naive forecasting.

> **Data integrity note:** `data/transactions.csv` is a reproducible **synthetic** dataset of 12,000 order rows, not a public real-world dataset or a real business result. It is included so the project runs offline immediately. Replace it with an appropriately licensed public dataset for a real-world portfolio study, then revalidate assumptions and calculations. Do not claim this synthetic dataset as actual company performance.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Tests: `python -m pytest -q` (run from repository root).

## What is implemented

- 12,000 deterministic example transactions, 1,200 possible customer IDs, 100 products, 2024–2025.
- Schema/quality validation, completed-order revenue recognition, product-cost profitability.
- Monthly trend analysis, category margins, RFM segmentation, customer cohort retention.
- Seasonal-naive 3-month revenue forecast, with 3-month holdout MAE. This is a baseline, not a validated predictive model for real commerce.
- Interactive Streamlit dashboard with filters, KPIs, charts, and CSV export.
- PostgreSQL table definition and advanced SQL analytical queries.
- Power BI import/build instructions and seven DAX measures (Power BI Desktop required to create `.pbix`).
- Automated pytest checks.

## Important limitations

- Synthetic data: results are illustrative, not evidence of business improvements or real consumer behavior.
- Profit is **product-level contribution**: excludes shipping, marketing, overhead, tax and refunds already incurred.
- `Returned` orders are excluded entirely from recognized revenue and cost. Real accounting can require refund timing, returns handling and costs.
- RFM segmentation is relative to selected filtered data, not a universally calibrated scoring model.
- Cohort analysis counts distinct customers active in each month; it does not measure subscription churn.
- Forecast is a simple seasonal baseline, not a claim of high accuracy.
- This repository does not include a `.pbix` binary. See `powerbi/BUILD_GUIDE.md`.

## Resume-ready wording after running and reviewing

**RevenueIQ 360 | Advanced Retail Analytics | Python, SQL, Power BI, Streamlit**
- Built an interactive retail analytics dashboard on **12,000 synthetic transaction records**, tracking revenue, product-level profit, category trends and customer behavior.
- Implemented RFM customer segmentation, monthly cohort retention, and PostgreSQL SQL analyses using CTEs and window functions.
- Developed a seasonal-naive revenue forecast with holdout MAE evaluation and documented Power BI DAX measures for executive reporting.

Clearly label the dataset synthetic on your GitHub and in interviews.

## Folder structure

`app.py`: Streamlit app; `src/analytics.py`: analytics functions; `data/`: sample dataset; `sql/`: PostgreSQL analyses; `powerbi/`: DAX + build guide; `tests/`: quality checks.
